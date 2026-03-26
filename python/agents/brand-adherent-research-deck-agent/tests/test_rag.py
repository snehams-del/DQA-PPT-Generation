import os
import importlib
from unittest.mock import patch
import presentation_agent.sub_agents.rag.agent as rag_module

def test_dummy_search():
    # Test dummy_search directly
    assert rag_module.dummy_search("test") == "Internal database is not configured or is unavailable."

def test_rag_agent_exists():
    assert rag_module.rag_agent is not None

def test_rag_agent_tool_selection():
    # Patch config and reload the module to test the else block
    with patch("presentation_agent.shared_libraries.config.DATASTORE_ID", ""):
        importlib.reload(rag_module)
        from google.adk.tools import FunctionTool
        assert isinstance(rag_module.vertex_search_tool, FunctionTool)
        # FunctionTool will use the function's name by default
        assert rag_module.vertex_search_tool.name == "dummy_search"
        
    # Patch config and reload to test the if block
    with patch("presentation_agent.shared_libraries.config.DATASTORE_ID", "some_id"):
        importlib.reload(rag_module)
        from google.adk.tools import VertexAiSearchTool
        assert isinstance(rag_module.vertex_search_tool, VertexAiSearchTool)
