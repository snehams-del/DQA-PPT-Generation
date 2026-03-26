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

"""Specialist agents for synthesizing research into a presentation deck spec."""

import asyncio
import json
from typing import Any, Dict, List, Optional

from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool, FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

from ...shared_libraries.config import ROOT_MODEL, initialize_genai_client, get_logger
from ...shared_libraries.models import SlideSpec, SynthesizerResponse, PresentationOutline
from .prompt import SYNTHESIZER_OUTLINE_INSTRUCTION, SYNTHESIZER_SLIDE_INSTRUCTION

# Agent 1: The Outliner (Creates the structural plan)
outline_specialist_agent = LlmAgent(
    model=ROOT_MODEL,
    name="outline_specialist",
    description="A specialist agent that creates the high-level outline and strategic briefing for a presentation.",
    instruction=SYNTHESIZER_OUTLINE_INSTRUCTION,
    output_schema=SynthesizerResponse,
)

# Agent 2: The Slide Writer (Writes individual slides)
slide_writer_agent = LlmAgent(
    model=ROOT_MODEL,
    name="slide_writer_specialist",
    description="A specialist agent that writes the detailed content (bullets, titles, visual prompts) for a single presentation slide.",
    instruction=SYNTHESIZER_SLIDE_INSTRUCTION,
    output_schema=SlideSpec,
)

async def generate_and_save_outline(
    topic: str,
    slide_count: int,
    narrative_outline: str,
    research_summary: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Consolidated tool that generates a presentation outline AND saves it to session state.
    Use this instead of calling outline_specialist and save_deck_spec separately.
    """
    log = get_logger("generate_and_save_outline")
    client = initialize_genai_client()
    
    # 1. Prepare the strategic prompt for the outliner
    prompt = (
        f"Topic: {topic}\n"
        f"Desired Slide Count: {slide_count}\n"
        f"Narrative Strategy: {narrative_outline}\n"
        f"Research Data: {research_summary}"
    )
    
    try:
        # 2. Call the Outliner directly via the GenAI client for maximum control
        config = types.GenerateContentConfig(
            system_instruction=SYNTHESIZER_OUTLINE_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=SynthesizerResponse,
        )
        
        response = await client.aio.models.generate_content(
            model=ROOT_MODEL,
            contents=prompt,
            config=config
        )
        
        if not response or not response.text:
            raise RuntimeError("Outliner returned an empty response.")
            
        res_obj = SynthesizerResponse.model_validate_json(response.text)
        outline = res_obj.outline
        
        # 3. SAVE TO STATE (Invisible persistence)
        # This keeps the huge JSON out of the Orchestrator's immediate context
        tool_context.state["current_deck_spec"] = outline.model_dump()
        log.info("Outline generated and saved to session state successfully.")
        
        # 3.5 SAVE TO ARTIFACT (Persistence for Enterprise)
        from ...shared_libraries.config import PRESENTATION_SPEC_ARTIFACT
        spec_bytes = json.dumps(outline.model_dump(), indent=2).encode("utf-8")
        # Use Part wrapper for Enterprise stability
        artifact = types.Part(
            inline_data=types.Blob(
                data=spec_bytes,
                mime_type="application/json"
            )
        )
        await tool_context.save_artifact(PRESENTATION_SPEC_ARTIFACT, artifact)
        log.info(f"Outline also saved to artifact '{PRESENTATION_SPEC_ARTIFACT}'.")
        
        # 4. Return ONLY the data needed for the Markdown summary
        return {
            "status": "Success",
            "message": "Outline generated and securely saved to session state.",
            "strategic_briefing": outline.strategic_briefing,
            "cover": outline.cover.model_dump(),
            "slides": [s.model_dump() for s in outline.slides],
            "closing_title": outline.closing_title
        }
        
    except Exception as e:
        log.error(f"Consolidated outline generation FAILED: {e}")
        return {"status": "Error", "message": str(e)}


async def batch_generate_slides(
    tool_context: ToolContext,
    research_summary: str,
    *,
    slides: Optional[List[Dict[str, Any]]] = None,
    spec_artifact_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generates detailed content for MULTIPLE slides in parallel with performance tuning.
    Prioritizes: 1. Direct 'slides' list, 2. Session STATE, 3. ARTIFACT fallback.
    """
    log = get_logger("batch_generate_slides")
    client = initialize_genai_client()
    from ...shared_libraries.config import PRESENTATION_SPEC_ARTIFACT
    
    # 1. Resolve Slides (Priority: Direct List > Session State > Named Artifact > Default Artifact)
    active_slides = slides or []
    
    # Check Session State (Invisible persistence)
    if not active_slides and not spec_artifact_name:
        state_spec = tool_context.state.get("current_deck_spec")
        if state_spec:
            active_slides = state_spec.get("slides", [])
            log.info(f"Loaded {len(active_slides)} slides from session state.")

    # Check Explicitly Named Artifact
    if not active_slides and spec_artifact_name:
        try:
            artifact = await tool_context.load_artifact(spec_artifact_name)
            if artifact:
                spec_json = artifact.inline_data.data if isinstance(artifact, types.Part) else artifact
                if isinstance(spec_json, (str, bytes, bytearray)):
                    spec_dict = json.loads(spec_json)
                else:
                    spec_dict = spec_json
                
                active_slides = spec_dict.get("slides", [])
                log.info(f"Loaded {len(active_slides)} slides from artifact '{spec_artifact_name}'.")
        except Exception as e:
            log.error(f"Failed to load named spec artifact: {e}")

    # Check Default Artifact Fallback (Enterprise reliability)
    if not active_slides:
        log.info(f"Checking default artifact '{PRESENTATION_SPEC_ARTIFACT}'...")
        try:
            artifact = await tool_context.load_artifact(PRESENTATION_SPEC_ARTIFACT)
            if artifact:
                spec_json = artifact.inline_data.data if isinstance(artifact, types.Part) else artifact
                if isinstance(spec_json, (str, bytes, bytearray)):
                    spec_dict = json.loads(spec_json)
                else:
                    spec_dict = spec_json
                
                active_slides = spec_dict.get("slides", [])
                log.info("Loaded slides from default artifact.")
        except Exception as e:
            log.warning(f"Could not load fallback artifact: {e}")

    if not active_slides:
        return {"status": "Error", "message": "No slide plan found. Please provide slides or ensure an outline was generated."}

    # 2. Performance Tuning: Allow 5 concurrent generations
    semaphore = asyncio.Semaphore(5)

    config = types.GenerateContentConfig(
        system_instruction=SYNTHESIZER_SLIDE_INSTRUCTION,
        response_mime_type="application/json",
        response_schema=SlideSpec,
    )

    async def _generate_single_slide(topic: dict) -> dict:
        async with semaphore:
            t_title = topic.get("title", "Slide Content")
            t_layout = topic.get("layout_name", "Title and Content")
            bullets_field = topic.get("bullets", [])
            t_focus = bullets_field[0] if bullets_field else "Focus on the topic provided in the title."
            
            # --- RELIABILITY SANITIZATION ---
            visual_prompt = topic.get("visual_prompt")
            if isinstance(visual_prompt, str) and visual_prompt.lower() in ["none", "null", "n/a", ""]:
                visual_prompt = None

            prompt = (
                f"Topic Focus: {t_focus}\n"
                f"Title: {t_title}\n"
                f"Planned Layout: {t_layout}\n"
                f"Planned Visual: {visual_prompt}\n"
                f"Research Summary: {research_summary}"
            )
            
            try:
                response = await client.aio.models.generate_content(
                    model=ROOT_MODEL,
                    contents=prompt,
                    config=config
                )
                
                if response and response.text:
                    res_dict = SlideSpec.model_validate_json(response.text).model_dump(
                        exclude_none=True
                    )
                    
                    # MANDATORY LAYOUT SAFETY: If visual exists
                    res_v = res_dict.get("visual_prompt")
                    if visual_prompt or (isinstance(res_v, str) and res_v.lower() not in ["none", "null", "n/a", ""]):
                        res_dict["layout_name"] = "Title and Image"
                    else:
                        res_dict["layout_name"] = "Title and Content"
                    
                    res_dict["title"] = t_title
                    return res_dict
            except Exception as e:
                return {
                    "title": t_title,
                    "layout_name": t_layout,
                    "visual_prompt": visual_prompt,
                    "bullets": [f"Error generating content: {e}"],
                }

        return {
            "title": t_title,
            "layout_name": t_layout,
            "visual_prompt": visual_prompt,
            "bullets": ["Error: Received empty response from model."],
        }

    # Execute all slide generations in parallel
    tasks = [_generate_single_slide(s) for s in active_slides]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    final_slides = []
    for r in results:
        if isinstance(r, Exception):
            final_slides.append(
                {
                    "title": "Error",
                    "layout_name": "Title and Content",
                    "bullets": [f"Error: {str(r)}"],
                }
            )
        else:
            final_slides.append(r)
            
    # 3. SAVE TO STATE (Invisible persistence)
    # This replaces the placeholder slides from the outline with fully written content.
    if tool_context:
        # Load full spec to ensure we don't overwrite other fields (cover, briefing)
        state_spec = tool_context.state.get("current_deck_spec")
        if not state_spec:
            # Fallback check artifact if state is empty (Distributed Enterprise context)
            try:
                artifact = await tool_context.load_artifact(PRESENTATION_SPEC_ARTIFACT)
                if artifact:
                    spec_bytes = artifact.inline_data.data if isinstance(artifact, types.Part) else artifact
                    state_spec = json.loads(spec_bytes.decode("utf-8"))
            except Exception:
                pass 
        
        # FINAL FALLBACK: Ensure state_spec is never None before assignment
        if not state_spec:
             state_spec = {"cover": {"title": "Presentation"}, "closing_title": "Thank You"}

        state_spec["slides"] = final_slides
        tool_context.state["current_deck_spec"] = state_spec
        log.info(f"Successfully saved {len(final_slides)} slides to session state.")
        
        # SAVE TO ARTIFACT (Persistence for Enterprise)
        spec_bytes = json.dumps(state_spec, indent=2).encode("utf-8")
        # Use Part wrapper for Enterprise stability
        artifact = types.Part(
            inline_data=types.Blob(
                data=spec_bytes,
                mime_type="application/json"
            )
        )
        await tool_context.save_artifact(PRESENTATION_SPEC_ARTIFACT, artifact)
        log.info(f"Slides also saved to artifact '{PRESENTATION_SPEC_ARTIFACT}'.")

    return {
        "status": "Success",
        "message": f"Successfully generated content for {len(final_slides)} slides and saved to session state.",
        "slides_count": len(final_slides)
    }

# Create the tools to expose to the Orchestrator
outline_specialist_tool = AgentTool(agent=outline_specialist_agent)
generate_outline_and_save_tool = FunctionTool(func=generate_and_save_outline)
slide_writer_specialist_tool = AgentTool(agent=slide_writer_agent)
batch_slide_writer_tool = FunctionTool(func=batch_generate_slides)
