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

import datetime
import logging
import re
from typing import Any

from google.adk.agents.callback_context import CallbackContext
from google.genai import types as genai_types

from .config import config


def _extract_text_from_content(content: genai_types.Content | None) -> str:
    """Extracts text parts from ADK content."""
    if not content or not content.parts:
        return ""
    return " ".join(part.text or "" for part in content.parts if part.text)


def _extract_first_approval_keyword(text: str) -> str | None:
    """Returns the first configured approval keyword found in text."""
    normalised_text = text.lower()
    for keyword in config.approval_keywords:
        keyword_pattern = rf"(^|\W){re.escape(keyword.lower())}($|\W)"
        if re.search(keyword_pattern, normalised_text):
            return keyword
    return None


def prepare_runtime_metadata_callback(
    callback_context: CallbackContext,
) -> None:
    """Adds invocation-level runtime metadata to session state."""
    callback_context.state["current_date"] = (
        datetime.datetime.now(datetime.UTC).date().isoformat()
    )
    callback_context.state["runtime_profile"] = config.runtime_profile


def enforce_execution_approval_callback(
    callback_context: CallbackContext,
) -> genai_types.Content | None:
    """Requires explicit user approval before running autonomous research."""
    if not config.planning_requires_explicit_approval:
        return None

    previously_approved = bool(callback_context.state.get("execution_approved"))
    approved_invocation_id = callback_context.state.get(
        "execution_approved_invocation_id"
    )
    if previously_approved and approved_invocation_id == callback_context.invocation_id:
        return None

    user_text = _extract_text_from_content(callback_context.user_content)
    matched_keyword = _extract_first_approval_keyword(user_text)
    if matched_keyword:
        callback_context.state["execution_approved"] = True
        callback_context.state["execution_approved_invocation_id"] = (
            callback_context.invocation_id
        )
        callback_context.state["execution_approval_phrase"] = matched_keyword
        return None

    callback_context.state["execution_approved"] = False
    callback_context.state["execution_approved_invocation_id"] = ""
    callback_context.state["execution_approval_phrase"] = ""
    callback_context.state["execution_approval_required"] = True
    allowed_keywords = ", ".join(config.approval_keywords)
    return genai_types.Content(
        parts=[
            genai_types.Part(
                text=(
                    "The research plan is ready, but execution is locked. "
                    f"Please approve explicitly with one of: {allowed_keywords}."
                )
            )
        ]
    )


def collect_research_sources_callback(
    callback_context: CallbackContext,
) -> None:
    """Collect web sources and supported claims from grounding metadata."""
    session = callback_context.session
    url_to_short_id = callback_context.state.get("url_to_short_id", {})
    sources = callback_context.state.get("sources", {})
    ingestion_errors = callback_context.state.get("sources_ingestion_errors", [])
    last_event_index = int(
        callback_context.state.get("sources_cursor_last_event_index", -1)
    )
    id_counter = len(url_to_short_id) + 1
    new_last_event_index = last_event_index

    for event_index, event in enumerate(session.events):
        if event_index <= last_event_index:
            continue

        new_last_event_index = event_index
        try:
            id_counter = _collect_sources_from_event(
                event=event,
                url_to_short_id=url_to_short_id,
                sources=sources,
                id_counter=id_counter,
            )
        except Exception as error:
            logging.warning(
                "Failed to collect source metadata from event index %d: %s",
                event_index,
                error,
            )
            ingestion_errors.append(
                {
                    "event_index": event_index,
                    "error": str(error),
                }
            )

    callback_context.state["url_to_short_id"] = url_to_short_id
    callback_context.state["sources"] = sources
    callback_context.state["sources_ingestion_errors"] = ingestion_errors
    callback_context.state["sources_cursor_last_event_index"] = new_last_event_index


def _collect_sources_from_event(
    *,
    event: Any,
    url_to_short_id: dict[str, str],
    sources: dict[str, dict[str, Any]],
    id_counter: int,
) -> int:
    """Extracts and stores source metadata from a single grounded event."""
    if not (event.grounding_metadata and event.grounding_metadata.grounding_chunks):
        return id_counter

    chunks_info: dict[int, str] = {}
    for chunk_index, chunk in enumerate(event.grounding_metadata.grounding_chunks):
        if not chunk.web or not chunk.web.uri:
            continue

        url = chunk.web.uri
        title = (
            chunk.web.title
            if chunk.web.title and chunk.web.title != chunk.web.domain
            else chunk.web.domain
        )

        if url not in url_to_short_id:
            short_id = f"src-{id_counter}"
            url_to_short_id[url] = short_id
            sources[short_id] = {
                "short_id": short_id,
                "title": title or chunk.web.domain or short_id,
                "url": url,
                "domain": chunk.web.domain or "",
                "supported_claims": [],
            }
            id_counter += 1

        chunks_info[chunk_index] = url_to_short_id[url]

    if not event.grounding_metadata.grounding_supports:
        return id_counter

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
    return id_counter


def citation_replacement_callback(
    callback_context: CallbackContext,
) -> genai_types.Content:
    """Replace inline citation tags with markdown hyperlinks."""
    final_report = str(callback_context.state.get("final_cited_report", ""))
    sources: dict[str, dict[str, Any]] = callback_context.state.get("sources", {})

    def tag_replacer(match: re.Match[str]) -> str:
        short_id = match.group(1)
        source_info = sources.get(short_id)
        if not source_info:
            logging.warning(
                "Invalid citation tag found and removed: %s", match.group(0)
            )
            return ""

        source_url = source_info.get("url")
        if not source_url:
            logging.warning(
                "Citation source '%s' is missing URL and was removed.", short_id
            )
            return ""

        display_text = source_info.get(
            "title", source_info.get("domain", short_id)
        )
        return f" [{display_text}]({source_url})"

    processed_report = re.sub(
        r'<cite\s+source\s*=\s*["\']?\s*(src-\d+)\s*["\']?\s*/>',
        tag_replacer,
        final_report,
    )
    processed_report = re.sub(r"\s+([.,;:])", r"\1", processed_report)
    callback_context.state["final_report_with_citations"] = processed_report
    return genai_types.Content(parts=[genai_types.Part(text=processed_report)])
