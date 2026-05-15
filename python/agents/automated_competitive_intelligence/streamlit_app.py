# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Streamlit UI with an in-process ADK Runner."""

import os
import sys
import logging
import uuid
import warnings
import json

# Add the project root to Python's system path to guarantee 'src' can be found.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

# Google ADK and Agent Imports
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from backend.agent import root_agent

warnings.filterwarnings("ignore")

# Configure logging for the application.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Core Agent Logic & Initialization ---


@st.cache_resource
def initialize_agent_runner():
    """Initializes the ADK Runner, which will execute the agent."""
    logger.info("Application starting up... Initializing ADK Runner.")
    try:
        session_service = InMemorySessionService()
        app_name = "competitive-intelligence-engine"
        runner = Runner(
            agent=root_agent, app_name=app_name, session_service=session_service
        )
        logger.info(f"Runner created for app: '{app_name}'")
        return runner
    except Exception as e:
        logger.error(f"Failed to initialize agent runner: {e}", exc_info=True)
        st.error(f"Fatal Error: Could not initialize the AI Agent. Error: {e}")
        st.stop()


def get_message_role(event: object) -> str:
    """Determines the role of a chat message by accessing object attributes."""
    role = event.content.role
    if role == "model":
        return "assistant"
    return "user"


def is_sql_or_json(text: str) -> bool:
    """
    A simple heuristic to check if a string is likely a SQL query or a JSON object.
    """
    stripped_text = text.strip()
    sql_keywords = ("SELECT", "WITH", "INSERT", "UPDATE", "DELETE", "CREATE")
    if stripped_text.upper().startswith(sql_keywords):
        return True
    if (stripped_text.startswith("{") and stripped_text.endswith("}")) or (
        stripped_text.startswith("[") and stripped_text.endswith("]")
    ):
        try:
            json.loads(stripped_text)
            return True
        except json.JSONDecodeError:
            return False
    return False

def get_final_agent_response(history_generator) -> str:
    """Extracts the final valid response from the history generator stream."""
    updated_history = list(history_generator)
    if not updated_history:
        return ""
    
    # Iterate backwards to find the last displayable text from the model
    for event in reversed(updated_history):
        if get_message_role(event) == "assistant" and event.content and event.content.parts:
            last_part_text = event.content.parts[0].text
            if last_part_text and not is_sql_or_json(last_part_text):
                return last_part_text
    return ""

def generate_csv_from_markdown(markdown_text: str) -> tuple[str, str]:
    """Parses markdown table into CSV string and determines filename."""
    if "|" not in markdown_text or "-|-" not in markdown_text.replace(" ", ""):
        return "", ""
        
    import csv
    import io
    import re
    
    lines = markdown_text.strip().split('\n')
    table_lines = [line.strip() for line in lines if line.strip().startswith('|') and line.strip().endswith('|')]
    if not table_lines:
        return "", ""
        
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    product_name = "Product"
    
    for i, line in enumerate(table_lines):
        # Skip the markdown separator row
        if i == 1 and all(c in '|-: ' for c in line):
            continue
            
        row = [cell.strip() for cell in line.split('|')[1:-1]]
        writer.writerow(row)
        
        # Extract product name from header (first row) dynamically alongside writing
        if i == 0 and len(row) > 1 and row[1]:
            clean_name = re.sub(r'[^A-Za-z0-9_\- ]+', '', row[1])
            if clean_name:
                product_name = clean_name.replace(" ", "_").upper()
                
    csv_data = csv_buffer.getvalue()
    file_name = f"{product_name}_CompetitorComparison.csv"
    
    return csv_data, file_name


# --- Streamlit UI ---
st.set_page_config(
    page_title="Competitive Intelligence Chat",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",  # Keep sidebar visible by default
)

runner = initialize_agent_runner()

st.title("🤖 Competitive Intelligence Engine")

# --- Session State Initialization ---
if "user_id" not in st.session_state:
    st.session_state.user_id = f"user_{str(uuid.uuid4())}"
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{str(uuid.uuid4())}"
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar with Static Introductory Text ---
with st.sidebar:
    st.header("About This App")
    st.markdown("""
    I am your dedicated **Competitive Intelligence Analyst**.

    My purpose is to help you analyze entities across any industry by following a structured, multi-step process:

    1.  **Find Source Documents:** I can search our database for source document URLs based on an entity name or unique identifier.
    2.  **Extract & Analyze:** With your approval, I will dynamically extract key intelligence attributes from a document and perform a web search to find and compare market competitors.
    3.  **Summarize (Optional):** Finally, if you ask, I can generate a concise summary of the entire analysis.
    """)
    st.markdown("---")
    st.subheader("Session Information")
    st.markdown(f"**Session ID:** `{st.session_state.session_id}`")
    if st.button("🔄 Start New Chat Session"):
        # Clear the history for the new session
        st.session_state.session_id = f"session_{str(uuid.uuid4())}"
        st.session_state.messages = []
        st.success("New chat session started!")
        st.rerun()

# --- Main Chat Interface ---

# Display the entire chat history from session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle new user input
if prompt := st.chat_input("Ask me to find product information..."):
    # Add user message to history and display it immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Now, run the agent and display its response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            try:
                # Pre-create the session synchronously to prevent race conditions.
                session = runner.session_service.get_session_sync(
                    app_name=runner.app_name,
                    user_id=st.session_state.user_id,
                    session_id=st.session_state.session_id,
                )
                if not session:
                    runner.session_service.create_session_sync(
                        app_name=runner.app_name,
                        user_id=st.session_state.user_id,
                        session_id=st.session_state.session_id,
                    )

                # The runner.run() method returns a generator of the full history.
                history_generator = runner.run(
                    user_id=st.session_state.user_id,
                    session_id=st.session_state.session_id,
                    new_message=types.Content(
                        role="user", parts=[types.Part(text=prompt)]
                    ),
                )

                final_agent_response = get_final_agent_response(history_generator)

                if final_agent_response:
                    st.markdown(final_agent_response)
                    # Add the final response to the message history for future reruns
                    st.session_state.messages.append(
                        {"role": "assistant", "content": final_agent_response}
                    )

                    # Extract tabular markdown data and offer a CSV download
                    try:
                        csv_data, file_name = generate_csv_from_markdown(final_agent_response)
                        if csv_data:
                            st.download_button(
                                label="📥 Download Comparison as CSV",
                                data=csv_data,
                                file_name=file_name,
                                mime="text/csv",
                                key=f"download_{len(st.session_state.messages)}"
                            )
                    except Exception as e:
                        logger.error(f"Failed to parse table for CSV download: {e}")
                else:
                    # This handles cases where the agent's only output was filtered
                    warning_message = (
                        "The agent's turn is complete. What would you like to do next?"
                    )
                    st.warning(warning_message)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": warning_message}
                    )

            except Exception as e:
                logger.error(
                    f"Error in Streamlit UI during agent call: {e}", exc_info=True
                )
                st.error(f"An error occurred: {e}")
