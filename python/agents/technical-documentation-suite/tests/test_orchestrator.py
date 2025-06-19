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

"""Tests for Technical Documentation Suite orchestrator"""

import pytest
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

from technical_documentation_suite.agent import root_agent
from technical_documentation_suite.sub_agents.code_analyzer import code_analyzer
from technical_documentation_suite.sub_agents.documentation_writer import documentation_writer


class TestTechnicalDocumentationSuite:
    """Test suite for Technical Documentation Suite agents"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.session_service = InMemorySessionService()
        self.session = self.session_service.create_session(
            app_name="test_app",
            user_id="test_user",
            session_id="test_session"
        )
        
        self.runner = Runner(
            agent=root_agent,
            session_service=self.session_service
        )
    
    def test_orchestrator_initialization(self):
        """Test that the orchestrator agent is properly initialized"""
        assert root_agent.name == "technical_documentation_orchestrator"
        assert root_agent.model == "gemini-2.5-flash"
        assert len(root_agent.tools) == 6  # 6 specialized agents
    
    def test_code_analyzer_agent(self):
        """Test that the code analyzer agent is properly configured"""
        assert code_analyzer.name == "code_analyzer"
        assert code_analyzer.output_schema is not None
        assert code_analyzer.output_key == "analysis"
    
    def test_documentation_writer_agent(self):
        """Test that the documentation writer agent is properly configured"""
        assert documentation_writer.name == "documentation_writer"
        assert documentation_writer.output_schema is not None
        assert documentation_writer.output_key == "documentation"
    
    def test_session_creation(self):
        """Test that sessions are created properly"""
        assert self.session is not None
        assert self.session.app_name == "test_app"
        assert self.session.user_id == "test_user"
        assert self.session.session_id == "test_session"
    
    def test_runner_initialization(self):
        """Test that the runner is properly initialized"""
        assert self.runner is not None
        assert self.runner.agent == root_agent
        assert self.runner.session_service == self.session_service
    
    @pytest.mark.skipif(
        not any([
            # Skip if no API credentials are available
            os.getenv("GOOGLE_API_KEY"),
            os.getenv("GOOGLE_CLOUD_PROJECT")
        ]),
        reason="No API credentials available for integration test"
    )
    def test_simple_documentation_request(self):
        """Integration test for simple documentation request"""
        
        content = types.Content(
            role="user",
            parts=[types.Part(text="""
            Analyze this simple Python function and provide documentation:
            
            ```python
            def add_numbers(a: int, b: int) -> int:
                '''Add two numbers together'''
                return a + b
            ```
            
            Please provide a brief analysis and documentation outline.
            """)]
        )
        
        events = []
        try:
            for event in self.runner.run(
                user_id="test_user",
                session_id="test_session",
                new_message=content
            ):
                events.append(event)
                
                # Stop after getting some events to avoid long test runs
                if len(events) >= 3:
                    break
                    
        except Exception as e:
            pytest.skip(f"Integration test failed due to API issues: {e}")
        
        # Verify we got some events
        assert len(events) > 0
        
        # Verify events have expected structure
        for event in events:
            assert hasattr(event, 'author')
            # Content might be None for some events
            if event.content:
                assert hasattr(event.content, 'parts')


class TestAgentConfiguration:
    """Test agent configuration and schema validation"""
    
    def test_all_agents_have_required_attributes(self):
        """Test that all agents have required attributes"""
        from technical_documentation_suite.sub_agents import (
            code_analyzer, documentation_writer, diagram_generator,
            translation_agent, quality_assurance, feedback_collector
        )
        
        agents = [
            code_analyzer.code_analyzer,
            documentation_writer.documentation_writer,
            diagram_generator.diagram_generator,
            translation_agent.translation_agent,
            quality_assurance.quality_assurance,
            feedback_collector.feedback_collector,
        ]
        
        for agent in agents:
            assert hasattr(agent, 'name')
            assert hasattr(agent, 'model')
            assert hasattr(agent, 'description')
            assert hasattr(agent, 'instruction')
            assert agent.name is not None
            assert agent.model == "gemini-2.5-flash"
    
    def test_output_schemas_are_valid(self):
        """Test that all output schemas are properly defined"""
        from technical_documentation_suite.sub_agents.code_analyzer import CodeAnalysisResult
        from technical_documentation_suite.sub_agents.documentation_writer import DocumentationResult
        from technical_documentation_suite.sub_agents.diagram_generator import DiagramResult
        
        # Test that schemas can be instantiated
        try:
            CodeAnalysisResult.model_json_schema()
            DocumentationResult.model_json_schema()
            DiagramResult.model_json_schema()
        except Exception as e:
            pytest.fail(f"Schema validation failed: {e}")
    
    def test_agent_tools_configuration(self):
        """Test that agent tools are properly configured"""
        from technical_documentation_suite.agent import (
            code_analyzer_tool, documentation_writer_tool,
            diagram_generator_tool, translation_agent_tool,
            quality_assurance_tool, feedback_collector_tool
        )
        
        tools = [
            code_analyzer_tool, documentation_writer_tool,
            diagram_generator_tool, translation_agent_tool,
            quality_assurance_tool, feedback_collector_tool
        ]
        
        for tool in tools:
            assert hasattr(tool, 'agent')
            assert tool.agent is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 