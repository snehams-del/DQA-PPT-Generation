"""
Centralized configuration for the NexShift Agent.

All configurable parameters that are shared across modules should be defined here.
"""
import os

# =============================================================================
# LLM Model Names
# =============================================================================
# Models used by each agent. Override via environment variables if needed.

MODEL_COORDINATOR = os.environ.get("NEXSHIFT_MODEL_COORDINATOR", "gemini-2.5-flash")
MODEL_CONTEXT_GATHERER = os.environ.get("NEXSHIFT_MODEL_CONTEXT_GATHERER", "gemini-2.5-flash")
MODEL_SOLVER = os.environ.get("NEXSHIFT_MODEL_SOLVER", "gemini-2.5-flash")
MODEL_COMPLIANCE = os.environ.get("NEXSHIFT_MODEL_COMPLIANCE", "gemini-2.5-pro")
MODEL_EMPATHY = os.environ.get("NEXSHIFT_MODEL_EMPATHY", "gemini-2.5-pro")
MODEL_PRESENTER = os.environ.get("NEXSHIFT_MODEL_PRESENTER", "gemini-2.5-flash")
