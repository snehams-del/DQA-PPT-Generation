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

"""Configuration mapper"""

import os
import json
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class Config:
    def __init__(self):
        # Google Cloud Configuration
        self.project_id: Optional[str] = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv(
            "GCP_PROJECT_ID"
        )
        self.location: Optional[str] = os.getenv(
            "GOOGLE_CLOUD_LOCATION", "us-central1"
        ).lower()
        self.use_vertex_ai: bool = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0") == "1"

        # Model and Service Configuration
        self.flash_model: str = os.getenv("DEFAULT_FLASH_MODEL", "gemini-2.5-flash")
        self.pro_model: str = os.getenv("DEFAULT_PRO_MODEL", "gemini-2.5-pro")
        
        # Sub-Agent Specific Models
        self.extractor_model: str = os.getenv("EXTRACTOR_MODEL", self.pro_model)
        self.nl2sql_model: str = os.getenv("NL2SQL_MODEL", self.pro_model)
        self.summarizer_model: str = os.getenv("SUMMARIZER_MODEL", self.flash_model)
        
        self.bucket_name: str = os.getenv("CIA_BUCKET_NAME", "cia_bucket")
        self.max_response_rows: int = int(os.getenv("MAX_RESPONSE_ROWS", "10"))
        self.gcs_download_pdf_dirpath: str = os.getenv("GCS_DOWNLOAD_PDF_DIRPATH", "cia_dowanloaded_pdf/")

        # New: Temporary directory path (needs to be configured)
        self.temp_dir_path: str = "/tmp/adk_temp_files"

        # LLM Retry Parameters
        self.genai_max_retries: int = 3
        self.genai_initial_delay: int = 2

        # LLM Generation Parameters
        self.temperature: float = 0.0
        self.top_p: float = 1.0
        self.max_output_tokens: int = 65535
        self.seed: int = 123
        
        # Domain-Aware Search Constraints
        self.industry_domain: str = os.getenv("INDUSTRY_DOMAIN", "general")
        self.domain_targets_json: str = os.getenv("DOMAIN_SEARCH_TARGETS_JSON", '{"insurance": ["irdai.gov.in", "policybazaar.com", "coverfox.com"]}')
        try:
            targets_dict = json.loads(self.domain_targets_json)
            self.domain_search_targets = targets_dict.get(self.industry_domain, [])
        except json.JSONDecodeError:
            self.domain_search_targets = []

    def validate(self) -> bool:
        """Validate that all required configuration is present."""
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is required")
        return True

    @property
    def project_location(self) -> str:
        """Get the project location in the format required by BigQuery and Dataform."""
        return f"{self.project_id}.{self.location}"

    @property
    def vertex_project_location(self) -> str:
        """Get the project location in the format required by Vertex AI."""
        return f"{self.project_id}.{self.location}"


# Create a global config instance
config = Config()
