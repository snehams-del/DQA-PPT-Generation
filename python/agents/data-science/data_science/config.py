"""
Configuration module for Data Science Agent.

This module sets up default environment variables for the data science multi-agent system.
"""

import os

import google.auth

# To use AI Studio credentials instead of Vertex AI:
# 1. Create a .env file in the project root with:
#    GOOGLE_GENAI_USE_VERTEXAI=0
#    GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
# 2. This will override the default Vertex AI configuration

# Auto-detect project from Google Cloud credentials
try:
    _, project_id = google.auth.default()
except Exception:
    project_id = None


def discover_rag_corpus() -> str:
    """Discover RAG corpus by looking for BQML-related corpora."""
    try:
        import vertexai
        from vertexai import rag

        if not project_id:
            return ""

        # Initialize Vertex AI
        vertexai.init(project=project_id, location="us-central1")

        # List available corpora
        corpora = rag.list_corpora()

        # Look for a corpus with 'bqml' or 'data-science' in the name
        for corpus in corpora:
            display_name = corpus.display_name.lower()
            if "bqml" in display_name or "data-science" in display_name:
                return corpus.name

        return ""
    except Exception:
        # If anything goes wrong, return empty string
        return ""


# Set default environment variables for Google Cloud only
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id or "")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "1")

# Discovery for RAG corpus
_rag_corpus_name = ""
if not os.environ.get("BQML_RAG_CORPUS_NAME"):
    _rag_corpus_name = discover_rag_corpus()
    if _rag_corpus_name:
        os.environ.setdefault("BQML_RAG_CORPUS_NAME", _rag_corpus_name)

# Code Interpreter defaults
os.environ.setdefault("CODE_INTERPRETER_EXTENSION_NAME", "")


def get_config():  # type: ignore[no-untyped-def]
    """Get configuration values from environment variables.

    This function is kept for backwards compatibility.
    Now returns a simple dict-like object with the configuration values.
    """

    class ConfigDict:
        def __init__(self) -> None:
            # Model configurations with defaults
            self.root_agent_model = os.getenv("ROOT_AGENT_MODEL", "gemini-2.5-flash")
            self.analytics_agent_model = os.getenv(
                "ANALYTICS_AGENT_MODEL", "gemini-2.5-flash"
            )
            self.bigquery_agent_model = os.getenv(
                "BIGQUERY_AGENT_MODEL", "gemini-2.5-flash"
            )
            self.baseline_nl2sql_model = os.getenv(
                "BASELINE_NL2SQL_MODEL", "gemini-2.5-flash"
            )
            self.chase_nl2sql_model = os.getenv(
                "CHASE_NL2SQL_MODEL", "gemini-2.5-flash"
            )
            self.bqml_agent_model = os.getenv("BQML_AGENT_MODEL", "gemini-2.5-flash")

            # BigQuery configurations with defaults
            agent_name = os.getenv("AGENT_NAME", "data-science")
            default_dataset_id = agent_name.replace("-", "_")
            self.bq_dataset_id = os.getenv("BQ_DATASET_ID", default_dataset_id)
            self.bq_data_project_id = os.getenv(
                "BQ_DATA_PROJECT_ID", os.getenv("GOOGLE_CLOUD_PROJECT", "")
            )
            self.bq_compute_project_id = os.getenv(
                "BQ_COMPUTE_PROJECT_ID", os.getenv("GOOGLE_CLOUD_PROJECT", "")
            )

            # Other configurations with defaults
            self.nl2sql_method = os.getenv("NL2SQL_METHOD", "BASELINE")
            self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "")
            self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
            self.bqml_rag_corpus_name = os.getenv("BQML_RAG_CORPUS_NAME", "")
            self.code_interpreter_extension_name = os.getenv(
                "CODE_INTERPRETER_EXTENSION_NAME", ""
            )

        def get_model_for_agent(self, agent_type: str) -> str:
            """Get model name for specific agent type."""
            model_map = {
                "root": self.root_agent_model,
                "analytics": self.analytics_agent_model,
                "bigquery": self.bigquery_agent_model,
                "baseline_nl2sql": self.baseline_nl2sql_model,
                "chase_nl2sql": self.chase_nl2sql_model,
                "bqml": self.bqml_agent_model,
            }
            return model_map.get(agent_type, self.root_agent_model)

    return ConfigDict()
