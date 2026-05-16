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

"""Callbacks for ensuring context variables are properly set before sub-agents run.

This module provides callbacks that capture LLM text output and store it in
session state, handling the case where output_key doesn't capture text when
the response also contains function calls.
"""

from typing import Optional

from google.genai import types

from google.adk.models.llm_response import LlmResponse


def _extract_text_from_content(content: Optional[types.Content]) -> Optional[str]:
    """Extract text from a Content object, ignoring non-text parts."""
    if not content or not content.parts:
        return None

    text_parts = []
    for part in content.parts:
        if part.text:
            text_parts.append(part.text)

    return "\n".join(text_parts) if text_parts else None


def capture_seminal_paper_after_model(
    callback_context, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """Capture the coordinator's text output and store it in session state.

    This after_model_callback fires after the LLM responds but BEFORE function
    calls are executed. This allows us to capture the text output even when
    the response contains both text and function calls (which would normally
    prevent output_key from working).

    Args:
        callback_context: The callback context providing access to state.
        llm_response: The LLM response containing text and/or function calls.

    Returns:
        None to continue with the original response (no modification).
    """
    text = _extract_text_from_content(llm_response.content)

    if text:
        callback_context.state["seminal_paper"] = text

    return None
