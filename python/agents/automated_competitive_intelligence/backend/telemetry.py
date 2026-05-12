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
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.resources import Resource

_logger = logging.getLogger(__name__)

def initialize_telemetry():
    """Initializes OpenTelemetry Tracing with Google Cloud Trace."""
    try:
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            _logger.warning("GOOGLE_CLOUD_PROJECT environment variable is not set. Telemetry might fallback.")

        # Resource attributes identify the service in console dashboards
        resource = Resource.create(attributes={
            "service.name": "competitive-intelligence-engine-backend",
            "environment": os.getenv("ENVIRONMENT", "development")
        })

        provider = TracerProvider(resource=resource)
        
        # Setup Google Cloud Trace exporter
        exporter = CloudTraceSpanExporter()
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)
        
        # Set global provider
        trace.set_tracer_provider(provider)
        _logger.info("OpenTelemetry Tracing initialized with Google Cloud Trace.")
        
    except Exception as e:
        _logger.error(f"Failed to initialize OpenTelemetry: {e}", exc_info=True)
