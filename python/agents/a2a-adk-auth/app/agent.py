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

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from google.cloud import storage

import os
import google.auth
import logging

_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

logger = logging.getLogger(__name__)


from google.oauth2.credentials import Credentials
# from app.utils import http_authorization_token


def list_gcs_folder(query: str, tool_context: ToolContext) -> str:
    """Lists files and subfolders within a specified Google Cloud Storage (GCS) path.

    This tool takes a GCS path (e.g., `gs://bucket-name/folder/`) and returns a
    formatted list of its contents, including both files and subfolders.

    Args:
        query: The GCS path (e.g., `gs://my-bucket/my-folder/`) to list.
        tool_context: A dictionary containing contextual information passed by the agent runtime.
                      This can include session IDs, request headers, and other relevant data.

    Returns:
        A string containing a formatted list of files and folders found, or an error
        message if the path is invalid or inaccessible.
    """
    
    SESSION_TOKEN = tool_context.session.state.get("user:AUTH_TOKEN")

    logger.info(f"Project Id: {project_id}")

    if not query.startswith("gs://"):
        return "Error: Invalid GCS path format. Path must start with 'gs://'."

    try:

        # Split the path into bucket name and prefix
        path_without_scheme = query[len("gs://"):]
        path_parts = path_without_scheme.split('/', 1)
        bucket_name = path_parts[0]
        prefix = path_parts[1] if len(path_parts) > 1 else ''

        if not bucket_name:
            return "Error: GCS path must specify a bucket name (e.g., 'gs://bucket-name/')."

        # client = storage.Client()
        creds = Credentials(token=SESSION_TOKEN)
        client = storage.Client(project=project_id, credentials=creds)
        
        bucket = client.bucket(bucket_name)

        results = []
        # Use delimiter='/' to list contents at the current level, treating common prefixes as folders
        blobs = client.list_blobs(bucket_name, prefix=prefix, delimiter='/')

        # Add subfolders (common prefixes)
        for p in blobs.prefixes:
            results.append(f"Folder: {p[len(prefix):]}")

        # Add files (blobs at the current prefix level)
        for blob in blobs:
            results.append(f"File: {blob.name[len(prefix):]}")

        return f"Contents of '{query}':\n" + "\n".join(sorted(results)) if results else f"No files or folders found in '{query}'."
    except Exception as e:
        return f"An error occurred while listing GCS path '{query}': {e}"


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-3-flash-preview",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="An agent that can list files and folders in a specified Google Cloud Storage (GCS) path.",
    instruction="You are a helpful AI assistant designed to list files and folders from Google Cloud Storage paths when requested. Focus on providing accurate and useful information regarding GCS contents.",
    tools=[
        list_gcs_folder
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
