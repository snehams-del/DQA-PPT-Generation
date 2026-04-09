# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging
import sys
import json
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# guarantee 'src' can be found in parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.agent import root_agent
from backend.config import config
from backend.telemetry import initialize_telemetry
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Initialize OpenTelemetry before generating App references
initialize_telemetry()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Competitive Intelligence Engine API",
    description="FastAPI backend orchestrating Google ADK Agents and Distributed Tracing.",
    version="1.0.0"
)

# Instrument FastAPI for Automatic Inbound Tracing
FastAPIInstrumentor.instrument_app(app)

# Initialize standard ADK Runner orchestrator
session_service = InMemorySessionService()
runner = Runner(agent=root_agent, app_name="competitive-intelligence-api", session_service=session_service)

class ChatInput(BaseModel):
    message: str
    user_id: str = "default_user"
    session_id: str = "default_session"

@app.get("/api/health")
async def health_check():
    """Returns health status of the backend API tier."""
    return {"status": "online", "engine": "operational"}

@app.post("/api/chat")
async def chat_endpoint(item: ChatInput):
    """
    Runs the Orchestrator Root Agent to processes competitive queries.
    Sends back responses synchronously (Streaming setup described below).
    """
    try:
        # Pre-create session triggers to match streamlit setups
        session = runner.session_service.get_session_sync(
            app_name=runner.app_name,
            user_id=item.user_id,
            session_id=item.session_id
        )
        if not session:
            runner.session_service.create_session_sync(
                app_name=runner.app_name,
                user_id=item.user_id,
                session_id=item.session_id
            )

        # Execute Agent turn
        history_generator = runner.run(
            user_id=item.user_id,
            session_id=item.session_id,
            new_message=types.Content(
                role="user", parts=[types.Part(text=item.message)]
            )
        )
        
        # Replicate display extractor from streamlit logic
        updated_history = list(history_generator)
        final_response = ""
        
        for event in reversed(updated_history):
            content = getattr(event, "content", None)
            if not content or getattr(content, "role", None) != "model":
                continue
                
            parts = getattr(content, "parts", [])
            if not parts:
                continue
                
            text = getattr(parts[0], "text", "")
            if not text:
                continue
                
            stripped_text = text.strip()
            if not (stripped_text.startswith("SELECT") or stripped_text.startswith("{")):
                final_response = text
                break
                            
        return {"response": final_response or "Agent turn completed without visible text replies."}
        
    except Exception as e:
        logger.error(f"Error running Agentic workflow endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/stream")
async def stream_chat_endpoint(item: ChatInput):
    """
    Streams orchestrator turns via Server-Sent Events (SSE).
    Required for interactive React frontends displaying incremental triggers.
    """
    def event_stream():
        try:
            # Pre-create session triggers to match streamlit setups
            session = runner.session_service.get_session_sync(
                app_name=runner.app_name,
                user_id=item.user_id,
                session_id=item.session_id
            )
            if not session:
                runner.session_service.create_session_sync(
                    app_name=runner.app_name,
                    user_id=item.user_id,
                    session_id=item.session_id
                )

            history_generator = runner.run(
                user_id=item.user_id,
                session_id=item.session_id,
                new_message=types.Content(
                    role="user", parts=[types.Part(text=item.message)]
                )
            )
            
            allowed_authors = {
                "competitive_intelligence_router",
                "query_execution_agent", 
                "specs_extractor_agent",
                "summarizer_agent"
            }
            
            for event in history_generator:
                if getattr(event, "author", None) not in allowed_authors:
                    continue
                    
                content = getattr(event, "content", None)
                if not content or getattr(content, "role", None) != "model":
                    continue
                    
                parts = getattr(content, "parts", [])
                if not parts:
                    continue
                
                # O(P) linear aggregation using join compiler
                content_str = "".join(
                    getattr(part, "text", "") 
                    for part in parts if hasattr(part, "text") and part.text
                )
                
                if not content_str:
                    continue
                        
                payload = {"role": "assistant", "content": content_str}
                yield f"data: {json.dumps(payload)}\n\n"
                
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

# ==========================================
# React Frontend Static Serving Integrations
# ==========================================

# 1. Mount Webpack/Vite static JS and CSS compilations directly
# (This ensures resources load natively avoiding 404s when executing within the final container)
app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

# 2. Setup catch-all evaluation router resolving Client-Side Routing logic (React-Router)
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    """
    Fallback routing serving index.html natively for any unhandled application routes.
    (Warning: Must be loaded at the exact bottom of the script to prevent intercepting /api calls)
    """
    file_path = os.path.join("frontend/dist", full_path) if full_path else "frontend/dist/index.html"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return FileResponse("frontend/dist/index.html")
