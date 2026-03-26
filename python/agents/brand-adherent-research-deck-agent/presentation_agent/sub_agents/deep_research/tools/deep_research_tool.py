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

import asyncio
import logging
import re

from google import genai
from google.adk.tools import FunctionTool

from ....shared_libraries.config import PROJECT_NUMBER

# Logger for capturing Interaction IDs
logger = logging.getLogger(__name__)

DEEP_RESEARCH_AGENT = "deep-research-pro-preview-12-2025"
LOCATION = "global"


def latex_to_text(text: str) -> str:
    """
    Converts LaTeX-style math blocks frequently returned by Deep Research
    into plain Unicode text for better readability in PowerPoint.
    """

    def replace_math(match):
        content = match.group(1)
        content = re.sub(r"\\text\{([^}]+)\}", r"\1", content)
        replacements = {
            r"\times": "×",
            r"\approx": "≈",
            r"\le": "≤",
            r"\ge": "≥",
            r"\frac": "",
        }
        for latex, char in replacements.items():
            content = content.replace(latex, char)
        return content

    # Regex to find double dollar sign blocks
    return re.sub(r"\$\$(.*?)\$\$", replace_math, text, flags=re.DOTALL)


def _parse_deep_research_stream(response_stream) -> tuple[str, list[str], str]:
    """
    Helper to parse the Deep Research SSE stream.
    Returns: (report_text, citations_list, interaction_id)
    """
    report_parts = []
    citations = []
    interaction_id = None

    for chunk in response_stream:
        # 1. Capture Interaction ID (usually in the first chunk)
        if hasattr(chunk, "interaction") and chunk.interaction:
            if hasattr(chunk.interaction, "id") and chunk.interaction.id:
                if interaction_id is None:
                    interaction_id = chunk.interaction.id

        # 2. Capture Content
        if getattr(chunk, "event_type", None) == "content.delta":
            delta = getattr(chunk, "delta", None)
            if not delta:
                continue

            delta_type = getattr(delta, "type", None)
            if delta_type == "text":
                text_part = getattr(delta, "text", None)
                if text_part:
                    report_parts.append(text_part)

                annotations = getattr(delta, "annotations", None)
                if annotations:
                    for citation in annotations:
                        url = getattr(citation, "source", None) or getattr(
                            citation, "url", None
                        )
                        if url:
                            citations.append(url)

    full_report = "".join(report_parts)
    # Clean LaTeX formatting
    full_report = latex_to_text(full_report)

    return full_report, citations, interaction_id


def _deep_research_sync_impl(query: str) -> str:
    """
    Internal synchronous implementation of Deep Research with retry logic.
    Follows Vertex AI Deep Research API SDK best practices.
    """
    client = genai.Client(vertexai=True, project=PROJECT_NUMBER, location=LOCATION)

    logger.info(f"Starting Deep Research for: {query}")

    try:
        # The API requires background=True and stream=True
        response = client.interactions.create(
            agent=DEEP_RESEARCH_AGENT, input=query, background=True, stream=True
        )

        report, citations, interaction_id = _parse_deep_research_stream(response)

        if interaction_id:
            logger.info(f"Deep Research Interaction ID: {interaction_id}")

        # Append collected citations as a reference section
        if citations:
            unique_citations = list(dict.fromkeys(citations))  # preserve order
            report += "\n\n### Extracted Sources:\n"
            for i, url in enumerate(unique_citations, 1):
                report += f"{i}. {url}\n"

        return report

    except Exception as e:
        logger.warning(
            f"Deep Research task encountered an error: {e}. Attempting recovery.",
            exc_info=True,
        )
        # Recovery path is handled here if needed, but for a tool call,
        # we usually return the error to the agent to retry or pivot.
        return f"Error: Deep Research failed. Reason: {e}"


async def deep_research_search(query: str) -> str:
    """
    Async wrapper for Deep Research to prevent blocking the main app loop.
    Includes a timeout and conciseness injection for performance.
    """
    # Enforcing 'Fast Mode' via strict behavioral constraints
    optimized_query = (
        f"{query}\n\n"
        "CRITICAL TIME & SCOPE CONSTRAINT (FAST MODE): You must execute this research quickly. "
        "1. Limit your search depth. Do NOT perform exhaustive, multi-layered deep dives.\n"
        "2. Limit your reading to a MAXIMUM of 3 to 4 high-quality sources.\n"
        "3. Synthesize the data immediately once you have baseline statistics.\n"
        "Return a highly concise, bulleted summary of ONLY the most important facts, numbers, and statistics. "
        "Limit output to 800 words maximum."
    )

    loop = asyncio.get_running_loop()
    try:
        # Strict 4-minute timeout for fast mode
        return await asyncio.wait_for(
            loop.run_in_executor(None, _deep_research_sync_impl, optimized_query),
            timeout=240.0,
        )
    except asyncio.TimeoutError:
        logger.warning(f"Deep Research timed out after 240s for query: {query}")
        return "Deep Research timed out. Please rely on the Google Research and RAG tools for this specific query."


# Create the FunctionTool wrapper
deep_research_tool = FunctionTool(func=deep_research_search)
