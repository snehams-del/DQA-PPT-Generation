import json
import os


def test_blogger_eval_fixture_schema() -> None:
    """Validates that the local eval fixture matches supported schema formats."""
    dataset_path = os.path.join(
        os.path.dirname(__file__), "data", "blog_eval.test.json"
    )
    with open(dataset_path, encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        # Legacy invocation list schema used by older evaluator paths.
        assert data, "Eval dataset must be a non-empty list"
        for invocation in data:
            assert isinstance(invocation, dict)
            assert invocation.get("query")
            assert "reference" in invocation
            assert "expected_tool_use" in invocation
            assert "expected_intermediate_agent_responses" in invocation
        return

    if isinstance(data, dict):
        # EvalSet-style schema.
        assert data.get("eval_set_id")
        assert data.get("name")
        eval_cases = data.get("eval_cases")
        assert isinstance(eval_cases, list) and eval_cases, (
            "EvalSet must contain a non-empty eval_cases list"
        )
        for eval_case in eval_cases:
            assert isinstance(eval_case, dict)
            assert eval_case.get("eval_id")
            conversation = eval_case.get("conversation")
            assert isinstance(conversation, list) and conversation, (
                "Each eval_case must contain a non-empty conversation"
            )
        return

    raise AssertionError(
        "Eval dataset must be either a legacy invocation list or an EvalSet object"
    )
