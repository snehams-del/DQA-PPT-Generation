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

"""Shared types and schemas for Japan Helpdesk agents."""

from typing import List, Optional
from pydantic import BaseModel, Field
from google.genai import types


# Configuration for JSON response generation
json_response_config = types.GenerateContentConfig(
    response_mime_type="application/json",
    temperature=0.1,
)


class ScopeCheckResult(BaseModel):
    """Result of scope checking for legal queries."""
    
    is_in_scope: bool = Field(description="Whether the query is within our supported scope")
    category: Optional[str] = Field(description="Category of the query (visa, housing, tax, etc.)")
    reason: Optional[str] = Field(description="Reason for rejection if out of scope")
    confidence: float = Field(description="Confidence score between 0 and 1")


class LegalAdviceCheck(BaseModel):
    """Result of legal advice detection."""
    
    contains_legal_advice: bool = Field(description="Whether the response contains unauthorized legal advice")
    problematic_phrases: List[str] = Field(description="List of phrases that constitute legal advice")
    suggested_replacements: List[str] = Field(description="Suggested neutral replacements")
    confidence: float = Field(description="Confidence score between 0 and 1")


class ContactInfo(BaseModel):
    """Contact information for government offices or agencies."""
    
    name: str = Field(description="Name of the office or agency")
    phone: Optional[str] = Field(default=None, description="Phone number")
    address: Optional[str] = Field(default=None, description="Physical address")
    website: Optional[str] = Field(default=None, description="Website URL")
    hours: Optional[str] = Field(default=None, description="Operating hours")
    notes: Optional[str] = Field(default=None, description="Additional notes or requirements")


class LegalResponse(BaseModel):
    """Structured response for legal queries."""
    
    summary: str = Field(description="Brief summary of the issue and guidance")
    disclaimers: List[str] = Field(description="Important disclaimers and limitations")
    next_steps: List[str] = Field(description="Recommended next steps for the user")
    useful_offices: List[ContactInfo] = Field(description="Relevant government offices or agencies")
    useful_phrases: List[str] = Field(description="Useful Japanese phrases related to the topic")
    confidence_level: str = Field(description="Confidence level: high, medium, or low")
    sources: List[str] = Field(description="Sources of information used")


class UserQuery(BaseModel):
    """User query with metadata."""
    
    query: str = Field(description="The user's question or request")
    language: str = Field(description="Detected language of the query")
    urgency: Optional[str] = Field(description="Urgency level if mentioned")
    location: Optional[str] = Field(description="Location mentioned in the query")
    user_nationality: Optional[str] = Field(description="User's nationality if mentioned")


# Supported categories for legal queries
SUPPORTED_CATEGORIES = [
    "visa",
    "immigration", 
    "housing",
    "tax",
    "employment",
    "healthcare",
    "banking",
    "education",
    "marriage",
    "driving_license",
    "residence_card",
    "pension",
    "insurance",
    "business_registration",
    "general_procedures"
]

# Common Japanese phrases for different categories
USEFUL_PHRASES = {
    "visa": [
        "ビザの更新をお願いします (Biza no kōshin o onegaishimasu) - Please renew my visa",
        "在留カードを紛失しました (Zairyū kādo o funshitsu shimashita) - I lost my residence card",
        "入国管理局はどこですか (Nyūkoku kanrikyoku wa doko desu ka) - Where is the immigration office?"
    ],
    "housing": [
        "賃貸契約について相談したいです (Chintai keiyaku ni tsuite sōdan shitai desu) - I want to consult about rental contracts",
        "住民票が必要です (Jūminhyō ga hitsuyō desu) - I need a residence certificate",
        "市役所はどこですか (Shiyakusho wa doko desu ka) - Where is the city hall?"
    ],
    "tax": [
        "税金の申告をしたいです (Zeikin no shinkoku o shitai desu) - I want to file a tax return",
        "住民税について教えてください (Jūminzei ni tsuite oshiete kudasai) - Please tell me about resident tax",
        "税務署はどこですか (Zeimusho wa doko desu ka) - Where is the tax office?"
    ]
}
