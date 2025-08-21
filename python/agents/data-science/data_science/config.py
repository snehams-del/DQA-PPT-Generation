"""
Configuration module for Data Science Agent.

This module sets up default environment variables for the data science multi-agent system.
"""

import os

import google.auth
import vertexai

# To use AI Studio credentials instead of Vertex AI:
# 1. Create a .env file in the project root with:
#    GOOGLE_GENAI_USE_VERTEXAI=0
#    GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
# 2. This will override the default Vertex AI configuration

# =============================================================================
# DEFAULT CONFIGURATION VALUES
# =============================================================================
# Model configurations - update these values as needed
DEFAULT_ROOT_AGENT_MODEL = "gemini-2.5-flash"
DEFAULT_ANALYTICS_AGENT_MODEL = "gemini-2.5-flash"
DEFAULT_BIGQUERY_AGENT_MODEL = "gemini-2.5-flash"
DEFAULT_BASELINE_NL2SQL_MODEL = "gemini-2.5-flash"
DEFAULT_CHASE_NL2SQL_MODEL = "gemini-2.5-flash"
DEFAULT_BQML_AGENT_MODEL = "gemini-2.5-flash"

# Location configurations
# us-east4 is preferred for Vertex AI RAG as it has better feature availability
DEFAULT_LOCATION = "us-central1"
DEFAULT_RAG_LOCATION = "us-east4"

# Other default values
DEFAULT_NL2SQL_METHOD = "BASELINE"
DEFAULT_AGENT_NAME = "data-science"

# Auto-detect project from Google Cloud credentials
try:
    _, project_id = google.auth.default()
except Exception:
    project_id = None

vertexai.init(project=project_id, location=DEFAULT_LOCATION)


def discover_rag_corpus() -> str:
    """Discover RAG corpus by looking for BQML-related corpora."""
    try:
        from google.cloud.aiplatform import initializer
        from google.cloud.aiplatform_v1 import ListRagCorporaRequest
        from vertexai.rag.utils import _gapic_utils

        # List available corpora using underlying implementation
        parent = initializer.global_config.common_location_path(
            project=project_id, location=DEFAULT_RAG_LOCATION
        )
        request = ListRagCorporaRequest(
            parent=parent,
            page_size=None,
            page_token=None,
        )
        client = _gapic_utils.create_rag_data_service_client()
        try:
            pager = client.list_rag_corpora(request=request)
        except Exception as e:
            raise RuntimeError("Failed in listing the RagCorpora due to: ", e) from e

        # Look for a corpus with 'bqml' or 'data-science' in the name
        for corpus in pager:
            display_name = corpus.display_name.lower()
            if "bqml" in display_name or "data-science" in display_name:
                return corpus.name

        return ""
    except Exception:
        # If anything goes wrong, return empty string
        return ""


# Set default environment variables for Google Cloud only
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id or "")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", DEFAULT_LOCATION)
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
            # Model configurations using centralized defaults
            self.root_agent_model = os.getenv(
                "ROOT_AGENT_MODEL", DEFAULT_ROOT_AGENT_MODEL
            )
            self.analytics_agent_model = os.getenv(
                "ANALYTICS_AGENT_MODEL", DEFAULT_ANALYTICS_AGENT_MODEL
            )
            self.bigquery_agent_model = os.getenv(
                "BIGQUERY_AGENT_MODEL", DEFAULT_BIGQUERY_AGENT_MODEL
            )
            self.baseline_nl2sql_model = os.getenv(
                "BASELINE_NL2SQL_MODEL", DEFAULT_BASELINE_NL2SQL_MODEL
            )
            self.chase_nl2sql_model = os.getenv(
                "CHASE_NL2SQL_MODEL", DEFAULT_CHASE_NL2SQL_MODEL
            )
            self.bqml_agent_model = os.getenv(
                "BQML_AGENT_MODEL", DEFAULT_BQML_AGENT_MODEL
            )

            # BigQuery configurations with defaults
            agent_name = os.getenv("AGENT_NAME", DEFAULT_AGENT_NAME)
            default_dataset_id = agent_name.replace("-", "_")
            self.bq_dataset_id = os.getenv("BQ_DATASET_ID", default_dataset_id)
            self.bq_data_project_id = os.getenv(
                "BQ_DATA_PROJECT_ID", os.getenv("GOOGLE_CLOUD_PROJECT", "")
            )
            self.bq_compute_project_id = os.getenv(
                "BQ_COMPUTE_PROJECT_ID", os.getenv("GOOGLE_CLOUD_PROJECT", "")
            )

            # Other configurations using centralized defaults
            self.nl2sql_method = os.getenv("NL2SQL_METHOD", DEFAULT_NL2SQL_METHOD)
            self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "")
            self.location = os.getenv("GOOGLE_CLOUD_LOCATION", DEFAULT_LOCATION)
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
