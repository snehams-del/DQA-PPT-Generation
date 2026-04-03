import ast
from pathlib import Path

AGENT_PY = Path(__file__).parent.parent / "blogger_agent" / "agent.py"
SOCIAL_MEDIA_PY = Path(__file__).parent.parent / "blogger_agent" / "sub_agents" / "social_media_writer.py"


def _source(path):
    return path.read_text()


def test_save_tool_on_main_agent():
    source = _source(AGENT_PY)
    assert "save_blog_post_to_file" in source


def test_social_media_writer_description_excludes_file_saving():
    source = _source(SOCIAL_MEDIA_PY)
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.keyword) and node.arg == "description":
            desc = ast.literal_eval(node.value).lower()
            assert "save" in desc or "file" in desc or "export" in desc, (
                "description should mention it doesn't handle file saving"
            )
            assert "not" in desc or "only" in desc, (
                "description should explicitly exclude file operations"
            )


def test_main_agent_instruction_handles_export():
    source = _source(AGENT_PY)
    assert "never delegate" in source.lower() or "always handle" in source.lower()
    assert "save_blog_post_to_file" in source
