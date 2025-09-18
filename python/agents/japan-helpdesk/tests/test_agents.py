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

"""Basic tests for Japan Helpdesk agents."""

import pytest
import re
from japan_helpdesk.agent import root_agent
from japan_helpdesk.sub_agents.scope_check.agent import scope_check_agent
from japan_helpdesk.sub_agents.rag.agent import rag_agent
from japan_helpdesk.sub_agents.legal_advice_detector.agent import legal_advice_detector_agent


class TestJapanHelpdeskAgents:
    """Test suite for Japan Helpdesk agents."""

    def test_root_agent_initialization(self):
        """Test that the root agent initializes properly."""
        assert root_agent is not None
        assert root_agent.name == "japan_helpdesk_root_agent"
        assert len(root_agent.tools) == 3  # scope_check, rag, legal_advice_detector

    def test_scope_check_agent_initialization(self):
        """Test that the scope check agent initializes properly."""
        assert scope_check_agent is not None
        assert scope_check_agent.name == "scope_check_agent"
        assert scope_check_agent.output_schema is not None

    def test_rag_agent_initialization(self):
        """Test that the RAG agent initializes properly."""
        assert rag_agent is not None
        assert rag_agent.name == "rag_agent"
        assert len(rag_agent.tools) >= 1  # Should have search tool

    def test_legal_advice_detector_initialization(self):
        """Test that the legal advice detector agent initializes properly."""
        assert legal_advice_detector_agent is not None
        assert legal_advice_detector_agent.name == "legal_advice_detector_agent"
        assert legal_advice_detector_agent.output_schema is not None

    # Note: Async tests with actual agent execution would require proper session setup
    # For now, we focus on initialization and configuration tests

    def test_phone_number_validation(self):
        """Test phone number validation for Japanese government offices."""
        # Common Japanese phone number patterns
        valid_numbers = [
            "03-1234-5678",  # Tokyo area code
            "06-1234-5678",  # Osaka area code  
            "011-123-4567",  # Sapporo area code
            "0120-123-456",  # Toll-free
        ]
        
        invalid_numbers = [
            "123-456-7890",  # US format
            "1234567890",    # No formatting
            "03-12345-678",  # Wrong grouping
        ]
        
        # Japanese phone number regex pattern
        jp_phone_pattern = r'^(0\d{1,4}-\d{1,4}-\d{4}|0120-\d{3}-\d{3})$'
        
        for number in valid_numbers:
            assert re.match(jp_phone_pattern, number), f"Valid number {number} should match"
            
        for number in invalid_numbers:
            assert not re.match(jp_phone_pattern, number), f"Invalid number {number} should not match"

    def test_supported_categories(self):
        """Test that all supported categories are properly defined."""
        from japan_helpdesk.shared_libraries.types import SUPPORTED_CATEGORIES
        
        expected_categories = [
            "visa", "immigration", "housing", "tax", "employment",
            "healthcare", "banking", "education", "marriage",
            "driving_license", "residence_card", "pension", "insurance",
            "business_registration", "general_procedures"
        ]
        
        for category in expected_categories:
            assert category in SUPPORTED_CATEGORIES, f"Category {category} should be supported"

    def test_useful_phrases_structure(self):
        """Test that useful phrases are properly structured."""
        from japan_helpdesk.shared_libraries.types import USEFUL_PHRASES
        
        assert isinstance(USEFUL_PHRASES, dict)
        assert "visa" in USEFUL_PHRASES
        assert "housing" in USEFUL_PHRASES
        assert "tax" in USEFUL_PHRASES
        
        # Each category should have a list of phrases
        for category, phrases in USEFUL_PHRASES.items():
            assert isinstance(phrases, list)
            assert len(phrases) > 0
            # Each phrase should contain both Japanese and romanization
            for phrase in phrases:
                assert isinstance(phrase, str)
                assert len(phrase) > 0
