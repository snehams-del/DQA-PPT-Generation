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


import logging
import os

from google import genai
from google.genai.types import (
    HttpOptions,
)

from . import order_flow_agent

# This code is for the ADK web dev UI. (https://github.com/google/adk-web)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

genai_client = genai.Client(
    vertexai=True,
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location=os.environ["GOOGLE_CLOUD_LOCATION"],
    http_options=HttpOptions(api_version="v1"))

root_agent = order_flow_agent.create_agent(
    genai_client=genai_client)
