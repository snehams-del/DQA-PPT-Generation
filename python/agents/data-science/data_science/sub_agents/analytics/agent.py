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

"""Data Science Agent V2: generate nl2py and use code interpreter to run the code."""

import logging

from google.adk.agents import Agent
from google.adk.code_executors import VertexAiCodeExecutor
from vertexai.preview.extensions import Extension

from ...config import get_config
from .prompts import return_instructions_ds

logger = logging.getLogger(__name__)
config = get_config()


def get_extension_if_exists() -> str | None:
    """Get any available code interpreter extension."""
    try:
        extensions = Extension.list(location=config.location)
        for extension in extensions:
            if "Code Interpreter" in extension.gca_resource.display_name:
                resource_name = extension.gca_resource.name
                logger.info(f"Using code interpreter extension: {resource_name}")
                return resource_name

        logger.info("No code interpreter extension found")
        return None

    except Exception as e:
        logger.warning(f"Could not list extensions: {e}")
        return None


# Determine which extension to use
extension_name = get_extension_if_exists()

root_agent = Agent(
    model=config.analytics_agent_model,
    name="data_science_agent",
    instruction=return_instructions_ds(),
    code_executor=VertexAiCodeExecutor(
        resource_name=extension_name or config.code_interpreter_extension_name,
        optimize_data_file=True,
        stateful=True,
    ),
)
