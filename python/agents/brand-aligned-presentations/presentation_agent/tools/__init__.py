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

"""
Tool exports + ADK FunctionTool registration for the DQA PPT Generation Agent.

DQA workflow changes supported here:
- Separate buckets:
  - TEMPLATE_BUCKET (pptx templates)
  - DATA_BUCKET (xlsx input files)
  - OUTPUT_BUCKET (generated pptx outputs)
- No external research tools are registered here.
"""

from google.adk.tools import FunctionTool

# ------------------------------------------------------------------------------
# Artifact/GCS utilities (bucket listing + download/upload + artifact helpers)
# ------------------------------------------------------------------------------
from .artifact_utils import (
    get_artifact_as_local_path,
    get_gcs_file_as_local_path,
    list_available_artifacts,
    read_file_content,
    save_deck_spec,
    save_presentation,
    update_slide_in_spec,
    # NEW (we will add these in artifact_utils.py next)
    list_templates_in_gcs,
    list_excels_in_gcs,
    make_output_pptx_gcs_uri,
)

# ------------------------------------------------------------------------------
# PPTX editor tools (read/edit slides, inspect template)
# ------------------------------------------------------------------------------
from .pptx_editor import (
    add_slide_to_end,
    delete_slide,
    edit_slide_text,
    extract_images_from_slide,
    extract_slide_content,
    inspect_template_style,
    read_presentation_details,
    read_presentation_outline,
    replace_slide_visual,
    update_element_layout,
)

# ------------------------------------------------------------------------------
# Orchestration tools (render deck from spec)
# ------------------------------------------------------------------------------
from .presentation_orchestrator import (
    generate_and_render_deck,
    render_deck_from_spec,
)

# ------------------------------------------------------------------------------
# Visual generation (optional; Excel-driven prompts only)
# ------------------------------------------------------------------------------
from .visual_generator import generate_visual


__all__ = [
    # --- Create workflow helpers ---
    "list_templates_in_gcs",
    "list_excels_in_gcs",
    "make_output_pptx_gcs_uri",

    # --- Core artifact helpers ---
    "list_available_artifacts",
    "get_artifact_as_local_path",
    "get_gcs_file_as_local_path",
    "read_file_content",
    "save_deck_spec",
    "update_slide_in_spec",
    "save_presentation",

    # --- Template inspection ---
    "inspect_template_style",

    # --- Render ---
    "generate_and_render_deck",
    "render_deck_from_spec",

    # --- Editing ---
    "add_slide_to_end",
    "delete_slide",
    "edit_slide_text",
    "replace_slide_visual",
    "update_element_layout",
    "read_presentation_outline",
    "read_presentation_details",
    "extract_slide_content",
    "extract_images_from_slide",

    # --- Optional visuals ---
    "generate_visual",
]


# ------------------------------------------------------------------------------
# Tool registration sets (used by agent.py via ALL_STANDARD_TOOLS)
# ------------------------------------------------------------------------------

# Tools needed for "Create PPT from Template + Excel"
CORE_TOOLS = [
    FunctionTool(func=list_templates_in_gcs),
    FunctionTool(func=list_excels_in_gcs),
    FunctionTool(func=make_output_pptx_gcs_uri),

    FunctionTool(func=list_available_artifacts),
    FunctionTool(func=get_artifact_as_local_path),
    FunctionTool(func=get_gcs_file_as_local_path),
    FunctionTool(func=inspect_template_style),

    FunctionTool(func=save_deck_spec),
    FunctionTool(func=update_slide_in_spec),

    FunctionTool(func=generate_and_render_deck),
    FunctionTool(func=save_presentation),
    FunctionTool(func=read_file_content),
]

# Tools needed for "Edit existing deck"
EDITING_TOOLS = [
    FunctionTool(func=add_slide_to_end),
    FunctionTool(func=delete_slide),
    FunctionTool(func=edit_slide_text),
    FunctionTool(func=replace_slide_visual),
    FunctionTool(func=update_element_layout),
    FunctionTool(func=read_presentation_outline),
    FunctionTool(func=read_presentation_details),
    FunctionTool(func=extract_slide_content),
    FunctionTool(func=extract_images_from_slide),

    # Optional: keep if you still want Imagen visuals
    FunctionTool(func=generate_visual),
]

ALL_STANDARD_TOOLS = CORE_TOOLS + EDITING_TOOLS