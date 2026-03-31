# Core Evaluation Suite

This folder contains a baseline ADK evaluation package for the financial deep-search workflow.

## Files

- `eval_config.core.json`: core criteria and thresholds.
- `eval_set.core.json`: five baseline evaluation cases.
- `session_input.json`: shared session bootstrap.

## Criteria included

- `tool_trajectory_avg_score` with `IN_ORDER` matching.
- `rubric_based_final_response_quality_v1`.
- `rubric_based_tool_use_quality_v1`.
- `hallucinations_v1`.
- `safety_v1`.

## Run

From `adk-samples/python/agents/deep-search`:

```bash
adk eval app \
  --config_file_path evals/core/eval_config.core.json \
  evals/core/eval_set.core.json \
  --print_detailed_results
```

## Notes

- `safety_v1` requires Vertex AI configuration (`GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION`).
- Treat these cases as a starting baseline. Update prompts, expected trajectories, and rubrics as your workflow evolves.
