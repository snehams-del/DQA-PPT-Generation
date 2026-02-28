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
