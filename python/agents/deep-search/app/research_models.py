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

"""Structured output models used by the research pipeline."""

from typing import Literal

from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """Model representing a specific search query for web search."""

    search_query: str = Field(
        description="A highly specific and targeted query for web search."
    )


class Feedback(BaseModel):
    """Model for evaluating research quality and requesting refinements."""

    grade: Literal["pass", "fail"] = Field(
        description=(
            "Evaluation result. 'pass' if the research is sufficient, "
            "'fail' if it needs revision."
        )
    )
    comment: str = Field(
        description=(
            "Detailed explanation of strengths and weaknesses in the "
            "current research."
        )
    )
    follow_up_queries: list[SearchQuery] | None = Field(
        default=None,
        description=(
            "A list of targeted follow-up search queries needed to fill "
            "research gaps. Should be null or empty if grade is 'pass'."
        ),
    )


class DebateOutcome(BaseModel):
    """Structured outcome from the investment debate facilitator."""

    consensus_reached: bool = Field(
        description="True when the debate has reached a recommendation-ready consensus."
    )
    recommendation: Literal["buy", "hold", "sell"] | None = Field(
        default=None,
        description=(
            "Consensus recommendation if available. Null if no consensus has been reached."
        ),
    )
    confidence_score: int | None = Field(
        default=None,
        ge=0,
        le=100,
        description=(
            "Facilitator confidence score for the consensus recommendation. "
            "Null if no consensus has been reached."
        ),
    )
    rationale: str = Field(
        description="Concise explanation for the current debate status and conclusion."
    )
    unresolved_questions: list[str] = Field(
        default_factory=list,
        description="Outstanding questions that must be resolved before a final recommendation.",
    )


class TraderProposal(BaseModel):
    """Structured proposal from the trader before risk governance."""

    recommendation: Literal["buy", "hold", "sell"] = Field(
        description="Preliminary recommendation based on available research and debate evidence."
    )
    confidence_score: int = Field(
        ge=0,
        le=100,
        description="Trader confidence in the preliminary recommendation.",
    )
    horizon: str = Field(
        description="Investment horizon for the preliminary recommendation."
    )
    key_drivers: list[str] = Field(
        default_factory=list,
        description="Primary evidence-backed drivers supporting the preliminary recommendation.",
    )
    key_risks: list[str] = Field(
        default_factory=list,
        description="Primary downside factors that may invalidate the preliminary recommendation.",
    )


class RiskManagementOutcome(BaseModel):
    """Structured output from the risk management facilitator."""

    consensus_reached: bool = Field(
        description="True when risk managers have reached a governance-ready consensus."
    )
    adjusted_recommendation: Literal["buy", "hold", "sell"] | None = Field(
        default=None,
        description="Risk-adjusted recommendation. Null if no consensus was reached.",
    )
    adjusted_confidence_score: int | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Risk-adjusted confidence score. Null if no consensus was reached.",
    )
    risk_profile_alignment: (
        Literal["aggressive", "balanced", "defensive"] | None
    ) = Field(
        default=None,
        description="Dominant risk posture implied by the current consensus.",
    )
    position_sizing_guidance: str = Field(
        description="Suggested position sizing guidance given current risk conditions."
    )
    unresolved_risks: list[str] = Field(
        default_factory=list,
        description="Material risks that still lack resolution.",
    )


class FundManagerDecision(BaseModel):
    """Final governance decision that can be reported to the user."""

    final_recommendation: Literal["buy", "hold", "sell"] = Field(
        description="Final recommendation after research, debate, and risk governance."
    )
    confidence_score: int = Field(
        ge=0,
        le=100,
        description="Final confidence score after governance review.",
    )
    horizon: str = Field(
        description="Final investment horizon communicated to the user."
    )
    conviction_level: Literal["low", "medium", "high"] = Field(
        description="Manager conviction level in the final recommendation."
    )
    decision_rationale: str = Field(
        description="Concise explanation of why this final decision was selected."
    )
    execution_guardrails: list[str] = Field(
        default_factory=list,
        description="Conditions and guardrails for implementing the recommendation safely.",
    )
