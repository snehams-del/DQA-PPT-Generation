# Copyright 2025 Google LLC
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

import os
import logging

import google.auth

project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get(
    "GCP_PROJECT"
)

if not project_id:
    try:
        _, detected_project_id = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        project_id = detected_project_id
    except Exception as e:  # pragma: no cover - defensive init fallback
        logging.warning(
            "Unable to infer project ID from ADC during package init: %s", e
        )

os.environ.setdefault(
    "GOOGLE_CLOUD_PROJECT", project_id or "your-default-project"
)
os.environ.setdefault(
    "GOOGLE_CLOUD_LOCATION", os.environ.get("GCP_LOCATION", "global")
)
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "1")

if os.environ.get("CI", "").lower() == "true":
    # In CI, disable background telemetry exporters that can trigger
    # credential scope exchange errors unrelated to agent functionality.
    os.environ.setdefault("OTEL_SDK_DISABLED", "true")
    os.environ.setdefault("OTEL_TRACES_EXPORTER", "none")
    os.environ.setdefault("OTEL_METRICS_EXPORTER", "none")
    os.environ.setdefault("OTEL_LOGS_EXPORTER", "none")

from .agent import app, root_agent

__all__ = ["app", "root_agent"]
