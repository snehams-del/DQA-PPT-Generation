import os

import google.auth

_, project_id = google.auth.default()

os.environ.setdefault(
    "GOOGLE_CLOUD_PROJECT", project_id or "your-default-project"
)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

from .agent import root_agent
