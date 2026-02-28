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
3. `parallel_specialist_research` runs specialist analysts in staged parallel waves:
   - Wave 1: `section_researcher` (news and catalysts), `technical_analyst`
   - Wave 2: `sentiment_analyst`, `valuation_analyst`, `risk_analyst`
4. `specialist_synthesizer` merges specialist outputs into `section_research_findings`.
5. `iterative_refinement_loop` runs research QA and follow-up search until pass or max iterations.
6. `investment_debate_loop` runs:
   - `bull_case_analyst`
   - `bear_case_analyst`
   - `debate_facilitator`
   - `debate_consensus_checker`
7. `debate_summary_writer` prepares debate output for reporting.
8. `trader_agent` produces a structured preliminary recommendation.
9. `risk_management_loop` runs:
   - `risk_aggressive_manager`
   - `risk_balanced_manager`
   - `risk_defensive_manager`
   - `risk_management_facilitator`
   - `risk_consensus_checker`
10. `risk_management_summary_writer` prepares risk governance output.
11. `fund_manager_agent` makes the final governance decision.
12. `report_composer_with_citations` builds the final report.
13. Citation callback replaces internal citation tags with markdown links.

## Design principles

- Keep ADK entrypoints stable (`root_agent`, `app`) to avoid runtime breakage.
- Keep agent names stable to preserve frontend integration.
- Separate schemas and callbacks from orchestration logic.
- Prefer explicit, typed outputs for evaluator, debate, and governance stages.
- Reduce burst load with staged parallelism and retry-aware high-volume agents.
