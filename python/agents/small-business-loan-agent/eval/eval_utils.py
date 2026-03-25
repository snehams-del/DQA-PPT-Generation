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

"""Utility functions for ADK evaluation of the Small Business Loan Agent."""

import base64
import os
import random
import string
from datetime import UTC, datetime
from pathlib import Path

from google.cloud import firestore


def load_file_as_base64(file_path: str) -> str:
    """Load a file and return its base64-encoded content."""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_mime_type(file_path: str) -> str:
    """Get MIME type from file extension."""
    ext = Path(file_path).suffix.lower()
    mime_types = {
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }
    return mime_types.get(ext, "application/octet-stream")


def generate_random_sbl_id() -> str:
    """Generate a random SBL loan request ID."""
    return f"SBL-2025-{''.join(random.choices(string.digits, k=5))}"


def create_pre_repaired_state_in_firestore(loan_request_id: str, session_id: str = "eval-session") -> dict:
    """
    Create a pre-repaired state in Firestore for testing the resume flow.

    This simulates a scenario where:
    - DocumentExtractionAgent completed with repaired data (missing fields were added after offline repair)
    - The process is ready to resume from UnderwritingAgent

    The data structure matches LoanApplicationData from document_extraction/models.py
    """
    db_name = os.getenv("GCP_FIRESTORE_DB", "session-states")
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-project-id")
    db = firestore.Client(project=project_id, database=db_name)
    now = datetime.now(UTC)

    document_extraction_data = {
        "business_name": "Cymbal Coffee Roasters LLC",
        "business_type": "LLC",
        "ein": "00-1234567",
        "industry": "Food & Beverage",
        "years_in_business": "6",
        "number_of_employees": "12",
        "business_address": {
            "street": "742 Evergreen Terrace",
            "city": "Springfield",
            "state": "IL",
            "zip_code": "62704",
        },
        "owner_name": "Jane Doe",
        "owner_email": "jane.doe@example.com",
        "owner_phone": "(555) 010-0100",
        "annual_revenue": "$850,000",
        "net_profit": "$120,000",
        "existing_debt": "None",
        "loan_amount_requested": "$150,000",
        "loan_purpose": "Equipment",
        "loan_term_months": "60",
        "collateral_offered": "Commercial coffee roasting equipment",
    }

    all_steps = [
        "DocumentExtractionAgent",
        "UnderwritingAgent",
        "PricingAgent",
        "LoanDecisionAgent",
    ]
    steps = {}
    for step_name in all_steps:
        if step_name == "DocumentExtractionAgent":
            steps[step_name] = {
                "status": "completed",
                "completed_at": now,
                "data": document_extraction_data,
                "human_review_notes": "Missing fields added during offline repair",
                "approved_by": "admin@example.com",
                "approved_at": now,
            }
        else:
            steps[step_name] = {
                "status": "not_started",
                "completed_at": None,
                "data": None,
                "human_review_notes": None,
                "approved_by": None,
                "approved_at": None,
            }

    process_state = {
        "loan_request_id": loan_request_id,
        "session_id": session_id,
        "current_step": "UnderwritingAgent",
        "overall_status": "active",
        "created_at": now,
        "updated_at": now,
        "steps": steps,
        "issues": [
            {
                "step": "DocumentExtractionAgent",
                "issue_type": "requires_review",
                "description": "Missing 2 critical field(s): annual_revenue, loan_amount_requested",
                "missing_fields": ["annual_revenue", "loan_amount_requested"],
                "raised_at": now,
                "resolved": True,
                "resolved_at": now,
                "resolved_by": "admin@example.com",
            }
        ],
    }

    doc_ref = db.collection("process_states").document(loan_request_id)
    doc_ref.set(process_state)
    print(f"Created pre-repaired state for {loan_request_id}")
    return process_state
