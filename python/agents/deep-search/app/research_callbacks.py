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

"""Callbacks for source collection and citation formatting."""

import logging
import re

from google.adk.agents.callback_context import CallbackContext
from google.genai import types as genai_types


def collect_research_sources_callback(
    callback_context: CallbackContext,
) -> None:
    """Collect web sources and supported claims from grounding metadata."""
    session = callback_context._invocation_context.session
    url_to_short_id = callback_context.state.get("url_to_short_id", {})
    sources = callback_context.state.get("sources", {})
    id_counter = len(url_to_short_id) + 1

    for event in session.events:
        if not (
            event.grounding_metadata
            and event.grounding_metadata.grounding_chunks
        ):
            continue

        chunks_info: dict[int, str] = {}
        for idx, chunk in enumerate(event.grounding_metadata.grounding_chunks):
            if not chunk.web:
                continue

            url = chunk.web.uri
            title = (
                chunk.web.title
                if chunk.web.title != chunk.web.domain
                else chunk.web.domain
            )

            if url not in url_to_short_id:
                short_id = f"src-{id_counter}"
                url_to_short_id[url] = short_id
                sources[short_id] = {
                    "short_id": short_id,
                    "title": title,
                    "url": url,
                    "domain": chunk.web.domain,
                    "supported_claims": [],
                }
                id_counter += 1

            chunks_info[idx] = url_to_short_id[url]

        if not event.grounding_metadata.grounding_supports:
            continue

        for support in event.grounding_metadata.grounding_supports:
            confidence_scores = support.confidence_scores or []
            chunk_indices = support.grounding_chunk_indices or []

            for score_index, chunk_index in enumerate(chunk_indices):
                if chunk_index not in chunks_info:
                    continue

                short_id = chunks_info[chunk_index]
                confidence = (
                    confidence_scores[score_index]
                    if score_index < len(confidence_scores)
                    else 0.5
                )
                text_segment = support.segment.text if support.segment else ""
                sources[short_id]["supported_claims"].append(
                    {
                        "text_segment": text_segment,
                        "confidence": confidence,
                    }
                )

    callback_context.state["url_to_short_id"] = url_to_short_id
    callback_context.state["sources"] = sources


def citation_replacement_callback(
    callback_context: CallbackContext,
) -> genai_types.Content:
    """Replace inline citation tags with markdown hyperlinks."""
    final_report = callback_context.state.get("final_cited_report", "")
    sources = callback_context.state.get("sources", {})

    def tag_replacer(match: re.Match[str]) -> str:
        short_id = match.group(1)
        source_info = sources.get(short_id)
        if not source_info:
            logging.warning(
                "Invalid citation tag found and removed: %s", match.group(0)
            )
            return ""

        display_text = source_info.get(
            "title", source_info.get("domain", short_id)
        )
        return f" [{display_text}]({source_info['url']})"

    processed_report = re.sub(
        r'<cite\s+source\s*=\s*["\']?\s*(src-\d+)\s*["\']?\s*/>',
        tag_replacer,
        final_report,
    )
    processed_report = re.sub(r"\s+([.,;:])", r"\1", processed_report)
    callback_context.state["final_report_with_citations"] = processed_report
    return genai_types.Content(parts=[genai_types.Part(text=processed_report)])
