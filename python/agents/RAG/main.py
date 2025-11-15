
import os
import vertexai
from vertexai import agent_engines
from google.adk.sessions import VertexAiSessionService
from dotenv import load_dotenv
import json
import asyncio
from fastapi import FastAPI, Depends, HTTPException, Security, UploadFile, File
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
import firebase_admin
from firebase_admin import auth, credentials
from google.cloud import firestore
from vertexai.preview import rag

# Initialize FastAPI app
app = FastAPI()

# Load environment variables
load_dotenv()

# --- Firebase Initialization ---
# You need to download your Firebase service account key and set the GOOGLE_APPLICATION_CREDENTIALS env var
# For example: export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/serviceAccountKey.json"
try:
    firebase_admin.initialize_app()
except ValueError as e:
    # This can happen if initialization is attempted more than once.
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

# --- Security Schemes ---
# For API Key (Ingestion)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)
SERVICE_API_KEY = os.getenv("SERVICE_API_KEY") # You must set this in your .env file

# For JWT (Query)
bearer_scheme = HTTPBearer()

async def get_service_api_key(api_key: str = Security(api_key_header)):
    """Dependency to validate the service API key."""
    if api_key != SERVICE_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

async def get_current_user(cred: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """Dependency to validate Firebase JWT token."""
    if not cred:
        raise HTTPException(status_code=403, detail="Invalid authorization credentials")
    try:
        decoded_token = auth.verify_id_token(cred.credentials)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Invalid auth token: {e}")

# --- API Endpoints ---

@app.post("/ingest", dependencies=[Depends(get_service_api_key)])
async def ingest_data(file: UploadFile = File(...)):
    """
    Ingestion endpoint to upload a file to the RAG corpus and a Firestore vault.
    Requires a valid service API key in the 'X-API-Key' header.
    """
    
    # 1. Save to Vector DB (RAG Corpus)
    rag_corpus_id = os.getenv("RAG_CORPUS")
    if not rag_corpus_id:
        raise HTTPException(status_code=500, detail="RAG_CORPUS environment variable not set.")

    try:
        contents = await file.read()
        
        # We need to save the file temporarily to upload it via path
        with open(file.filename, "wb") as f:
            f.write(contents)
        
        rag.upload_file(
            corpus_name=rag_corpus_id,
            path=file.filename,
            display_name=file.filename,
        )
        os.remove(file.filename) # Clean up the temporary file

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload to RAG corpus: {e}")

    # 2. Save to Firestore Vault
    try:
        # We'll use the filename as the document ID for simplicity
        doc_ref = db.collection("rag_vault").document(file.filename)
        doc_ref.set({
            "content": contents.decode('utf-8', errors='ignore'), # Store content as string
            "upload_time": firestore.SERVER_TIMESTAMP,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save to Firestore: {e}")
        
    return {"message": f"Successfully ingested and vaulted {file.filename}"}


@app.post("/query")
async def query_agent(query: str, user: dict = Depends(get_current_user)):
    """
    Query endpoint to chat with the RAG agent.
    Requires a valid Firebase JWT in the 'Authorization' header.
    """
    agent_engine_id = os.getenv("AGENT_ENGINE_ID")
    if not agent_engine_id:
        raise HTTPException(status_code=500, detail="AGENT_ENGINE_ID environment variable not set.")
    
    # Use the Firebase UID as the user_id for the agent session
    user_id = user.get("uid")
    
    try:
        # This is a simplified interaction. Production apps would manage sessions.
        agent_engine = agent_engines.get(agent_engine_id)
        response_stream = agent_engine.stream_query(
            user_id=user_id,
            message=query,
        )
        
        # For simplicity, we'll collect and return the full response.
        # A production app might stream this back to the client via WebSockets or SSE.
        full_response = ""
        for event in response_stream:
            if "content" in event and "parts" in event["content"]:
                for part in event["content"]["parts"]:
                    if "text" in part:
                        full_response += part["text"]

        return {"response": full_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying agent: {e}")

