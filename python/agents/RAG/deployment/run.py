
import os
import vertexai
from vertexai import agent_engines
from google.adk.sessions import VertexAiSessionService
from dotenv import load_dotenv
import json
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
import firebase_admin
from firebase_admin import auth, credentials
from google.cloud import firestore
from vertexai.preview import rag
import cgi

# Load environment variables
load_dotenv()

# --- Firebase Initialization ---
try:
    firebase_admin.initialize_app()
except ValueError as e:
    if "The default Firebase app already exists" not in str(e):
        raise

# --- Vertex AI Initialization ---
vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
)

# --- Firestore Initialization ---
db = firestore.Client(
    project=os.getenv("GOOGLE_CLOUD_PROJECT")
)

# --- Security ---
SERVICE_API_KEY = os.getenv("SERVICE_API_KEY")

class RAGHandler(BaseHTTPRequestHandler):
    def _send_response(self, status_code, message):
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(message).encode('utf-8'))

    def do_POST(self):
        if self.path == '/ingest':
            # --- Ingestion Endpoint ---
            api_key = self.headers.get('X-API-Key')
            if api_key != SERVICE_API_KEY:
                self._send_response(403, {"detail": "Invalid API Key"})
                return
            
            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                file_content = fields.get('file')[0]
                filename = 'uploaded_file'

                # 1. Save to Vector DB (RAG Corpus)
                rag_corpus_id = os.getenv("RAG_CORPUS")
                if not rag_corpus_id:
                    self._send_response(500, {"detail": "RAG_CORPUS environment variable not set."})
                    return
                try:
                    with open(filename, "wb") as f:
                        f.write(file_content)
                    rag.upload_file(
                        corpus_name=rag_corpus_id,
                        path=filename,
                        display_name=filename,
                    )
                    os.remove(filename)
                except Exception as e:
                    self._send_response(500, {"detail": f"Failed to upload to RAG corpus: {e}"})
                    return

                # 2. Save to Firestore Vault
                try:
                    doc_ref = db.collection("rag_vault").document(filename)
                    doc_ref.set({
                        "content": file_content.decode('utf-8', errors='ignore'),
                        "upload_time": firestore.SERVER_TIMESTAMP,
                    })
                except Exception as e:
                    self._send_response(500, {"detail": f"Failed to save to Firestore: {e}"})
                    return

                self._send_response(200, {"message": f"Successfully ingested and vaulted {filename}"})
            else:
                self._send_response(400, {"detail": "Invalid content-type"})

        elif self.path == '/query':
            # --- Query Endpoint ---
            auth_header = self.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                self._send_response(403, {"detail": "Invalid authorization credentials"})
                return
            
            token = auth_header.split('Bearer ')[1]
            try:
                decoded_token = auth.verify_id_token(token)
            except Exception as e:
                self._send_response(403, {"detail": f"Invalid auth token: {e}"})
                return

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            body = json.loads(post_data)
            query = body.get('query')

            agent_engine_id = os.getenv("AGENT_ENGINE_ID")
            if not agent_engine_id:
                self._send_response(500, {"detail": "AGENT_ENGINE_ID environment variable not set."})
                return

            user_id = decoded_token.get("uid")
            try:
                agent_engine = agent_engines.get(agent_engine_id)
                response_stream = agent_engine.stream_query(
                    user_id=user_id,
                    message=query,
                )
                
                full_response = ""
                for event in response_stream:
                    if "content" in event and "parts" in event["content"]:
                        for part in event["content"]["parts"]:
                            if "text" in part:
                                full_response += part["text"]
                self._send_response(200, {"response": full_response})
            except Exception as e:
                self._send_response(500, {"detail": f"Error querying agent: {e}"})
        else:
            self._send_response(404, {"detail": "Not Found"})

def run(server_class=HTTPServer, handler_class=RAGHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
