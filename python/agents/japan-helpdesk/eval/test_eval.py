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

"""Evaluation tests for Japan Helpdesk agents."""

import pytest
from japan_helpdesk.agent import root_agent


class TestJapanHelpdeskEvaluation:
    """Evaluation test suite for Japan Helpdesk."""

    def test_agent_configuration(self):
        """Test that the root agent is properly configured."""
        assert root_agent is not None
        assert root_agent.name == "japan_helpdesk_root_agent"
        assert len(root_agent.tools) == 3
        
        # Verify the agent has the expected description
        assert "helpdesk" in root_agent.description.lower()
        assert "japan" in root_agent.description.lower()
        
    def test_agent_instruction_content(self):
        """Test that the agent instruction contains key elements."""
        instruction = root_agent.instruction
        assert "Japan Helpdesk" in instruction
        assert "scope_check_agent" in instruction
        assert "rag_agent" in instruction
        assert "legal_advice_detector_agent" in instruction
        
    # Note: Full end-to-end tests would require proper session setup and API credentials
    # These tests focus on agent configuration and structure validation
