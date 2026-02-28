# Deep Search Financial Agent Architecture

This package is organised to keep responsibilities clear and maintenance simple.

## Module layout

- `agent.py`: ADK entrypoint compatibility layer. Exposes `root_agent` and `app`.
- `research_agents.py`: Main multi-agent definitions and orchestration pipeline.
- `research_callbacks.py`: Callback logic for source collection and citation replacement.
- `research_models.py`: Pydantic schemas for structured outputs (for example evaluator feedback).
- `config.py`: Runtime and model configuration.
- `__init__.py`: Package exports for ADK runtime discovery.

## Runtime flow

1. `interactive_planner_agent` creates and refines a tagged plan.
2. On approval, control passes to `research_pipeline`.
3. `section_researcher` executes initial research.
4. `research_evaluator` grades quality.
5. `iterative_refinement_loop` runs follow-up research until pass or max iterations.
6. `report_composer_with_citations` builds the final report.
7. Citation callback replaces internal citation tags with markdown links.

## Design principles

- Keep ADK entrypoints stable (`root_agent`, `app`) to avoid runtime breakage.
- Keep agent names stable to preserve frontend integration.
- Separate schemas and callbacks from orchestration logic.
- Prefer explicit, typed outputs for evaluator and refinement stages.
