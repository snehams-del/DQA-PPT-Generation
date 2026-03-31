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

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

# Load environment variables from .env file in the app directory
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Authentication Configuration:
# By default, uses AI Studio with GOOGLE_API_KEY from .env file.
# To use Vertex AI instead, set GOOGLE_GENAI_USE_VERTEXAI=TRUE in your .env
# and ensure you have Google Cloud credentials configured.

if os.getenv("GOOGLE_API_KEY"):
    # AI Studio mode (default): Use API key authentication
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "False")
else:
    # Vertex AI mode: Fall back to Google Cloud credentials
    import google.auth
    from google.auth.exceptions import DefaultCredentialsError

    try:
        _, project_id = google.auth.default()
        if project_id:
            os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
    except DefaultCredentialsError:
        # Keep going so local configuration can still be supplied via env vars.
        pass
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


def _env_bool(name: str, default: bool) -> bool:
    """Parses a boolean environment variable."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    """Parses an integer environment variable."""
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value.strip())
    except ValueError:
        return default


def _normalise_runtime_profile(
    value: str,
) -> Literal["balanced", "debug", "production"]:
    """Normalises runtime profile values to supported options."""
    normalised = value.strip().lower()
    if normalised in {"balanced", "debug", "production"}:
        return normalised
    return "balanced"


def _env_csv_tuple(name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    """Parses a comma-separated environment variable into a tuple."""
    value = os.getenv(name)
    if value is None:
        return default
    items = tuple(item.strip() for item in value.split(",") if item.strip())
    return items if items else default


def _apply_vertex_location_fallback_for_gemini_preview_models() -> None:
    """Applies a safe default endpoint for Gemini 3 preview models on Vertex AI.

    Some projects do not have access to Gemini 3 preview models in every region,
    which can trigger `404 NOT_FOUND` model errors at runtime. By default, this
    guardrail uses the `global` endpoint when Gemini 3 preview models are
    configured.

    Set `DEEP_SEARCH_AUTO_VERTEX_LOCATION_FALLBACK=false` to disable this
    behaviour and keep the explicit `GOOGLE_CLOUD_LOCATION` value.
    """
    if not _env_bool("GOOGLE_GENAI_USE_VERTEXAI", False):
        return
    if not _env_bool("DEEP_SEARCH_AUTO_VERTEX_LOCATION_FALLBACK", True):
        return

    configured_critic_model = os.getenv(
        "DEEP_SEARCH_CRITIC_MODEL", "gemini-3.1-pro-preview"
    ).strip()
    configured_worker_model = os.getenv(
        "DEEP_SEARCH_WORKER_MODEL", "gemini-3.1-pro-preview"
    ).strip()
    configured_models = {
        configured_critic_model.lower(),
        configured_worker_model.lower(),
    }
    gemini_preview_models = {
        "gemini-3-pro-preview",
        "gemini-3.1-pro-preview",
    }

    current_location = os.getenv("GOOGLE_CLOUD_LOCATION", "").strip().lower()
    if current_location != "global" and configured_models.intersection(
        gemini_preview_models
    ):
        os.environ["GOOGLE_CLOUD_LOCATION"] = "global"


_apply_vertex_location_fallback_for_gemini_preview_models()

DEFAULT_REASONING_MODEL = "gemini-3.1-pro-preview"


@dataclass
class ResearchConfiguration:
    """Configuration for research-related models and parameters.

    Attributes:
        critic_model (str): Model for evaluation tasks.
        worker_model (str): Model for working/generation tasks.
        high_throughput_model (str): Model for high-volume and search-heavy tasks.
        max_search_iterations (int): Maximum search iterations allowed.
        max_debate_iterations (int): Maximum debate rounds before forcing completion.
        max_risk_iterations (int): Maximum risk management rounds before forcing completion.
    """

    critic_model: str = DEFAULT_REASONING_MODEL
    worker_model: str = DEFAULT_REASONING_MODEL
    high_throughput_model: str = "gemini-2.5-flash"
    max_search_iterations: int = 5
    max_debate_iterations: int = 3
    max_risk_iterations: int = 3
    runtime_profile: Literal["balanced", "debug", "production"] = "balanced"
    enable_context_caching: bool = True
    context_cache_min_tokens: int = 2048
    context_cache_ttl_seconds: int = 900
    context_cache_intervals: int = 5
    enable_context_compaction: bool = True
    compaction_interval: int = 4
    compaction_overlap_size: int = 1
    compaction_summariser_model: str = "gemini-2.5-flash"
    planning_requires_explicit_approval: bool = True
    approval_keywords: tuple[str, ...] = (
        "kör",
        "kor",
        "go",
        "execute",
        "run",
    )
    include_thoughts_debug: bool = True
    include_thoughts_non_debug: bool = False

    @property
    def include_thoughts(self) -> bool:
        """Returns whether planner thought traces should be included."""
        if self.runtime_profile == "debug":
            return self.include_thoughts_debug
        return self.include_thoughts_non_debug


config = ResearchConfiguration(
    critic_model=os.getenv("DEEP_SEARCH_CRITIC_MODEL", DEFAULT_REASONING_MODEL),
    worker_model=os.getenv("DEEP_SEARCH_WORKER_MODEL", DEFAULT_REASONING_MODEL),
    high_throughput_model=os.getenv(
        "DEEP_SEARCH_HIGH_THROUGHPUT_MODEL", "gemini-2.5-flash"
    ),
    max_search_iterations=_env_int("DEEP_SEARCH_MAX_SEARCH_ITERATIONS", 5),
    max_debate_iterations=_env_int("DEEP_SEARCH_MAX_DEBATE_ITERATIONS", 3),
    max_risk_iterations=_env_int("DEEP_SEARCH_MAX_RISK_ITERATIONS", 3),
    runtime_profile=_normalise_runtime_profile(
        os.getenv("DEEP_SEARCH_RUNTIME_PROFILE", "balanced")
    ),
    enable_context_caching=_env_bool("DEEP_SEARCH_ENABLE_CONTEXT_CACHING", True),
    context_cache_min_tokens=_env_int("DEEP_SEARCH_CONTEXT_CACHE_MIN_TOKENS", 2048),
    context_cache_ttl_seconds=_env_int("DEEP_SEARCH_CONTEXT_CACHE_TTL_SECONDS", 900),
    context_cache_intervals=_env_int("DEEP_SEARCH_CONTEXT_CACHE_INTERVALS", 5),
    enable_context_compaction=_env_bool(
        "DEEP_SEARCH_ENABLE_CONTEXT_COMPACTION", True
    ),
    compaction_interval=_env_int("DEEP_SEARCH_COMPACTION_INTERVAL", 4),
    compaction_overlap_size=_env_int("DEEP_SEARCH_COMPACTION_OVERLAP_SIZE", 1),
    compaction_summariser_model=os.getenv(
        "DEEP_SEARCH_COMPACTION_SUMMARISER_MODEL", "gemini-2.5-flash"
    ),
    planning_requires_explicit_approval=_env_bool(
        "DEEP_SEARCH_REQUIRES_EXPLICIT_APPROVAL", True
    ),
    approval_keywords=_env_csv_tuple(
        "DEEP_SEARCH_APPROVAL_KEYWORDS",
        ("kör", "kor", "go", "execute", "run"),
    ),
    include_thoughts_debug=_env_bool("DEEP_SEARCH_INCLUDE_THOUGHTS_DEBUG", True),
    include_thoughts_non_debug=_env_bool(
        "DEEP_SEARCH_INCLUDE_THOUGHTS_NON_DEBUG", False
    ),
)
