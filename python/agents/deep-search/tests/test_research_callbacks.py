from __future__ import annotations

from types import SimpleNamespace

from google.genai import types as genai_types

from app.research_callbacks import (
    collect_research_sources_callback,
    enforce_execution_approval_callback,
    prepare_runtime_metadata_callback,
)


class DummyCallbackContext:
    def __init__(
        self,
        *,
        state: dict | None = None,
        session: SimpleNamespace | None = None,
        user_content: genai_types.Content | None = None,
        invocation_id: str = "inv-1",
    ) -> None:
        self.state = state if state is not None else {}
        self.session = session if session is not None else SimpleNamespace(events=[])
        self.user_content = user_content
        self.invocation_id = invocation_id


EXPECTED_SOURCE_COUNT = 2
ISO_DATE_LENGTH = 10


def _build_grounded_event(
    *,
    url: str,
    title: str,
    domain: str,
    text_segment: str,
) -> SimpleNamespace:
    chunk = SimpleNamespace(
        web=SimpleNamespace(uri=url, title=title, domain=domain),
    )
    support = SimpleNamespace(
        confidence_scores=[0.9],
        grounding_chunk_indices=[0],
        segment=SimpleNamespace(text=text_segment),
    )
    grounding_metadata = SimpleNamespace(
        grounding_chunks=[chunk],
        grounding_supports=[support],
    )
    return SimpleNamespace(grounding_metadata=grounding_metadata)


def test_collect_research_sources_callback_is_incremental() -> None:
    first_event = _build_grounded_event(
        url="https://example.com/one",
        title="Example One",
        domain="example.com",
        text_segment="First claim",
    )
    session = SimpleNamespace(events=[first_event])
    callback_context = DummyCallbackContext(state={}, session=session)

    collect_research_sources_callback(callback_context)  # type: ignore[arg-type]
    sources = callback_context.state["sources"]
    assert len(sources) == 1
    assert callback_context.state["sources_cursor_last_event_index"] == 0

    # Running again with no new events must not duplicate claims.
    collect_research_sources_callback(callback_context)  # type: ignore[arg-type]
    first_source = next(iter(sources.values()))
    assert len(first_source["supported_claims"]) == 1

    second_event = _build_grounded_event(
        url="https://example.com/two",
        title="Example Two",
        domain="example.com",
        text_segment="Second claim",
    )
    session.events.append(second_event)
    collect_research_sources_callback(callback_context)  # type: ignore[arg-type]
    assert len(callback_context.state["sources"]) == EXPECTED_SOURCE_COUNT
    assert callback_context.state["sources_cursor_last_event_index"] == 1


def test_enforce_execution_approval_callback_requires_keyword() -> None:
    user_content = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text="Planen ser bra ut, gor analysen nu.")],
    )
    callback_context = DummyCallbackContext(user_content=user_content)

    callback_result = enforce_execution_approval_callback(  # type: ignore[arg-type]
        callback_context
    )
    assert callback_result is not None
    assert callback_context.state["execution_approved"] is False
    assert callback_context.state["execution_approval_required"] is True


def test_enforce_execution_approval_callback_accepts_keyword() -> None:
    user_content = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text="Kor exekvering nu.")],
    )
    callback_context = DummyCallbackContext(user_content=user_content)

    callback_result = enforce_execution_approval_callback(  # type: ignore[arg-type]
        callback_context
    )
    assert callback_result is None
    assert callback_context.state["execution_approved"] is True
    assert callback_context.state["execution_approval_phrase"].lower() == "kor"


def test_prepare_runtime_metadata_callback_sets_current_date() -> None:
    callback_context = DummyCallbackContext(state={})
    prepare_runtime_metadata_callback(callback_context)  # type: ignore[arg-type]

    assert "current_date" in callback_context.state
    assert len(callback_context.state["current_date"]) == ISO_DATE_LENGTH
    assert "runtime_profile" in callback_context.state
