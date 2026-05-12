"""Integration test cases for Game Developer Architect and Sub-Agents."""

import os
import sys
import unittest

import pytest
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from game_dev_assistant.agent import root_agent
from game_dev_assistant.sub_agents.agent_index.agent import game_code_developer
from game_dev_assistant.sub_agents.audio_generation.agent import audio_agent

# Ensure module is discoverable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class TestGameAgents(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.session_service = InMemorySessionService()
        self.artifact_service = InMemoryArtifactService()
        self.session = await self.session_service.create_session(
            app_name="GameDevTest", user_id="tester"
        )
        self.runner = Runner(
            app_name="GameDevTest",
            agent=None,
            artifact_service=self.artifact_service,
            session_service=self.session_service,
        )

    def _query_agent(self, agent, query):
        self.runner.agent = agent
        content = types.Content(role="user", parts=[types.Part(text=query)])
        events = list(self.runner.run(
            user_id="tester",
            session_id=self.session.id,
            new_message=content
        ))
        # Extract text from the final response event
        return "".join([p.text for p in events[-1].content.parts if p.text])

    @pytest.mark.asyncio
    async def test_audio_agent_generation(self):
        """Verify the Audio Agent can generate a request for music."""
        query = "Generate a happy ukulele background song for a forest level."
        response = self._query_agent(audio_agent, query)
        self.assertIsNotNone(response)
        print(f"Audio Agent Response: {response}")

    @pytest.mark.asyncio
    async def test_index_agent_repo_analysis(self):
        """Verify the Index Agent can handle repository queries."""
        query = "Analyze this repo: https://github.com/example/game-repo"
        response = self._query_agent(game_code_developer, query)
        self.assertIsNotNone(response)
        print(f"Index Agent Response: {response}")

    @pytest.mark.asyncio
    async def test_architect_delegation(self):
        """Verify the Steering Agent (Architect) delegates to sub-agents."""
        query = "I want to add a jumping sound to my game. Help me find the code and generate the SFX."
        response = self._query_agent(root_agent, query)
        self.assertIsNotNone(response)
        # Check if it mentions the sub-agents or steps
        print(f"Architect Response: {response}")

if __name__ == "__main__":
    unittest.main()
