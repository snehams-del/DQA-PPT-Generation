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

import datetime
import logging
from collections.abc import AsyncGenerator

from google.adk.agents import BaseAgent, LlmAgent, LoopAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.apps.app import App
from google.adk.events import Event, EventActions
from google.adk.planners import BuiltInPlanner
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.genai import types as genai_types

from .config import config
from .research_callbacks import (
    citation_replacement_callback,
    collect_research_sources_callback,
)
from .research_models import Feedback


# --- Custom Agent for Loop Control ---
class EscalationChecker(BaseAgent):
    """Checks research evaluation and escalates to stop the loop if grade is 'pass'."""

    def __init__(self, name: str):
        super().__init__(name=name)

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        evaluation_result = ctx.session.state.get("research_evaluation")
        if evaluation_result and evaluation_result.get("grade") == "pass":
            logging.info(
                f"[{self.name}] Research evaluation passed. Escalating to stop loop."
            )
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            logging.info(
                f"[{self.name}] Research evaluation failed or not found. Loop will continue."
            )
            # Yielding an event without content or actions just lets the flow continue.
            yield Event(author=self.name)


# --- AGENT DEFINITIONS ---
plan_generator = LlmAgent(
    model=config.worker_model,
    name="plan_generator",
    description="Generates or refines a Stockholm-focused equity research plan with explicit analysis pillars.",
    instruction=f"""
    You are a senior equity research strategist focused on Stockholmsborsen (Nasdaq Stockholm).
    Your job is to create a high-level RESEARCH PLAN, not a summary.
    If there is already a RESEARCH PLAN in the session state, improve it based on user feedback.

    RESEARCH PLAN(SO FAR):
    {{ research_plan? }}

    **DOMAIN AND SCOPE RULES**
    - Prioritise Swedish-listed equities and indices on Stockholmsborsen.
    - If the user does not provide a ticker, include a goal to identify the correct Stockholm-listed instrument first.
    - Keep the plan aligned to practical investing decisions for the user's requested horizon.
    - Do not use external APIs. You may only use the provided `google_search` tool when needed.

    **GENERAL INSTRUCTION: CLASSIFY TASK TYPES**
    Your plan must clearly classify each goal for downstream execution. Each bullet point should start with a task type prefix:
    - **`[RESEARCH]`**: For goals that primarily involve information gathering, investigation, analysis, or data collection (these require search tool usage by a researcher).
    - **`[DELIVERABLE]`**: For goals that involve synthesizing collected information, creating structured outputs (e.g., tables, charts, summaries, reports), or compiling final output artifacts (these are executed AFTER research tasks, often without further search).
    - **Tag language lock:** Never translate or localise these tags. They must always be exactly `[RESEARCH]` and `[DELIVERABLE]`.
    - Status tags must also remain exact and untranslated: `[NEW]`, `[MODIFIED]`, `[IMPLIED]`.

    **INITIAL RULE: Your initial output MUST start with a bulleted list of 6 action-oriented goals, followed by any *inherently implied* deliverables.**
    - At least 5 of the initial goals must be `[RESEARCH]`.
    - The initial `[RESEARCH]` goals must cover these pillars:
      1) company and business quality,
      2) latest news and catalysts,
      3) technical analysis,
      4) sentiment analysis,
      5) valuation and relative positioning.
    - A good goal starts with a verb such as "Analyse", "Identify", "Investigate", "Compare", or "Evaluate".
    - **Proactive Implied Deliverables (Initial):** Add deliverables such as a recommendation matrix, risk register, and scenario table when implied by the request.

    **REFINEMENT RULE**:
    - **Integrate Feedback & Mark Changes:** When incorporating user feedback, make targeted modifications to existing bullet points. Add `[MODIFIED]` to the existing task type and status prefix (e.g., `[RESEARCH][MODIFIED]`). If the feedback introduces new goals:
        - If it's an information gathering task, prefix it with `[RESEARCH][NEW]`.
        - If it's a synthesis or output creation task, prefix it with `[DELIVERABLE][NEW]`.
    - **Proactive Implied Deliverables (Refinement):** Beyond explicit user feedback, proactively add any implied investment deliverable such as buy/hold/sell recommendations, confidence scoring, and downside scenarios.
    - **Maintain Order:** Strictly maintain the original sequential order of existing bullet points. New bullets, whether `[NEW]` or `[IMPLIED]`, should generally be appended to the list, unless the user explicitly instructs a specific insertion point.
    - **Flexible Length:** The refined plan is not constrained by the initial bullet count and may include more goals as needed.

    **TOOL USE IS STRICTLY LIMITED:**
    Your goal is to create a high-quality plan without unnecessary searching.
    Only use `google_search` if the ticker, company identity, or market context is ambiguous.
    You are forbidden from deep content research at this stage; detailed analysis is the next agent's job.
    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
    tools=[google_search],
)


section_planner = LlmAgent(
    model=config.worker_model,
    name="section_planner",
    description="Breaks down the research plan into a structured markdown outline for Stockholm equity analysis.",
    instruction="""
    You are an expert equity research report architect.
    Using the topic and the plan from `research_plan`, design a logical outline for a final report about Stockholmsborsen securities.
    Ignore planning tags such as [MODIFIED], [NEW], [RESEARCH], and [DELIVERABLE] when building the structure.
    Create a markdown outline with 6-8 sections, clear and non-overlapping.
    The outline must include sections for:
    - Company and business quality
    - News and catalyst analysis
    - Technical analysis
    - Sentiment analysis
    - Valuation and peer context
    - Risks and counter-case
    - Final recommendation (buy/hold/sell) with confidence and horizon
    You may add subsections for each analysed stock or index.
    Do not include a "References" or "Sources" section in your outline. Citations will be handled in-line.
    """,
    output_key="report_sections",
)


section_researcher = LlmAgent(
    model=config.worker_model,
    name="section_researcher",
    description="Performs the first comprehensive pass of Stockholm-focused financial research.",
    planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(include_thoughts=True)
    ),
    instruction="""
    You are a highly capable financial research and synthesis agent focused on Stockholmsborsen.
    Execute the provided plan with absolute fidelity: gather evidence first, then build deliverables.

    You will be provided with a sequential list of research plan goals, stored in the `research_plan` state key. Each goal will be clearly prefixed with its primary task type: `[RESEARCH]` or `[DELIVERABLE]`.

    **Hard constraints**
    - Do not use external APIs. Only use the built-in `google_search` tool.
    - Prioritise primary and credible sources: company reports, exchange notices, reputable financial newspapers, broker commentary with dates, and official macro data pages.
    - Never invent numbers or indicators. If a datapoint cannot be validated, explicitly mark it as unavailable.
    - When reporting time-sensitive data, always include date context.

    Your execution process must strictly adhere to these two distinct and sequential phases:

    ---

    **Phase 1: Information Gathering (`[RESEARCH]` Tasks)**

    *   **Execution Directive:** You **MUST** process every goal prefixed with `[RESEARCH]` before proceeding to Phase 2.
    *   For each `[RESEARCH]` goal:
        *   **Query Generation:** Formulate 4-6 targeted search queries that cover multiple angles of the goal.
        *   **Execution:** Use `google_search` to execute all generated queries for the current goal.
        *   **Summarisation:** Produce a detailed summary that directly addresses the goal.
        *   **Coverage rule:** Ensure research spans news flow, technical context, sentiment cues, and fundamentals where relevant.
        *   **Internal Storage:** Store each summary, clearly tied to its goal, for Phase 2.

    ---

    **Phase 2: Synthesis and Output Creation (`[DELIVERABLE]` Tasks)**

    *   **Execution Prerequisite:** This phase must only start once all `[RESEARCH]` goals are completed.
    *   **Execution Directive:** You **MUST** process every `[DELIVERABLE]` goal and produce the requested artifact.
    *   For each `[DELIVERABLE]` goal:
        *   **Instruction Interpretation:** Treat each goal as a direct instruction to produce a concrete artifact.
        *   **Data Consolidation:** Use only Phase 1 summaries to fulfil each deliverable. Do not perform new searches.
        *   **Output Generation:** Based on the specific instruction of the `[DELIVERABLE]` goal:
            *   Carefully extract and synthesise relevant information.
            *   Always produce explicit recommendation outputs when requested, including buy/hold/sell stance, confidence, and major risks.
        *   **Output Accumulation:** Maintain and accumulate all generated deliverables.

    ---

    **Final Output:** Return the complete set of processed research summaries and all generated deliverables, clearly separated.
    """,
    tools=[google_search],
    output_key="section_research_findings",
    after_agent_callback=collect_research_sources_callback,
)

research_evaluator = LlmAgent(
    model=config.critic_model,
    name="research_evaluator",
    description="Critically evaluates financial research quality and generates follow-up queries.",
    instruction=f"""
    You are a meticulous quality assurance analyst evaluating the research findings in 'section_research_findings'.

    **CRITICAL RULES:**
    1. Your only job is to assess quality, depth, and completeness of the financial research.
    2. Evaluate coverage across all required pillars: news, technical analysis, sentiment, fundamentals/valuation, risk, and recommendation logic.
    3. Verify that claims are evidence-based and source-backed, with adequate recency for market-sensitive statements.
    4. If recommendation logic is weak, contradictory, or unsupported, assign "fail".
    5. Follow-up queries must deepen or repair gaps; they must be specific and directly actionable.

    Be strict on quality. If there are meaningful gaps, assign grade "fail", explain what is missing, and generate 5-8 follow-up queries.
    Only assign "pass" when the research is decision-grade and recommendation-ready.

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    Your response must be a single, raw JSON object validating against the 'Feedback' schema.
    """,
    output_schema=Feedback,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_key="research_evaluation",
)

enhanced_search_executor = LlmAgent(
    model=config.worker_model,
    name="enhanced_search_executor",
    description="Executes follow-up searches and integrates improved financial findings.",
    planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(include_thoughts=True)
    ),
    instruction="""
    You are a specialist financial researcher running a refinement pass because the prior draft was graded 'fail'.

    1. Review `research_evaluation` to understand exact gaps.
    2. Execute every query in `follow_up_queries` using `google_search`.
    3. Synthesis rule: combine new evidence with existing `section_research_findings` into one improved set.
    4. Do not use external APIs. Do not invent missing datapoints.
    5. Your output must be complete, corrected, and recommendation-ready.
    """,
    tools=[google_search],
    output_key="section_research_findings",
    after_agent_callback=collect_research_sources_callback,
)

report_composer = LlmAgent(
    model=config.critic_model,
    name="report_composer_with_citations",
    include_contents="none",
    description="Transforms findings into a final, cited Stockholm equity investment memo.",
    instruction="""
    Transform the provided data into a polished, professional, and meticulously cited investment memo for Stockholmsborsen securities.

    ---
    ### INPUT DATA
    *   Research Plan: `{research_plan}`
    *   Research Findings: `{section_research_findings}`
    *   Citation Sources: `{sources}`
    *   Report Structure: `{report_sections}`

    ---
    ### CRITICAL: Citation System
    To cite a source, you MUST insert a special citation tag directly after the claim it supports.

    **The only correct format is:** `<cite source="src-ID_NUMBER" />`

    ---
    ### Final Instructions
    Generate a comprehensive report using ONLY the `<cite source="src-ID_NUMBER" />` tag system for citations.
    The report must follow the provided **Report Structure** outline.
    Write in Swedish unless the user explicitly asks for another language.
    Include a concise recommendation block per analysed stock with:
    - Recommendation: Kop / Behall / Salj
    - Confidence score: 0-100
    - Investment horizon
    - 3 strongest supporting arguments
    - 3 strongest counter-arguments and risks
    - Key catalysts to monitor
    If data is uncertain or stale, state that explicitly.
    Do not include a separate references section; citations must be in-line.
    End with: "Detta ar informationsmaterial och inte personlig finansiell radgivning."
    """,
    output_key="final_cited_report",
    after_agent_callback=citation_replacement_callback,
)

research_pipeline = SequentialAgent(
    name="research_pipeline",
    description="Executes a pre-approved research plan. It performs iterative research, evaluation, and composes a final, cited report.",
    sub_agents=[
        section_planner,
        section_researcher,
        LoopAgent(
            name="iterative_refinement_loop",
            max_iterations=config.max_search_iterations,
            sub_agents=[
                research_evaluator,
                EscalationChecker(name="escalation_checker"),
                enhanced_search_executor,
            ],
        ),
        report_composer,
    ],
)

interactive_planner_agent = LlmAgent(
    name="interactive_planner_agent",
    model=config.worker_model,
    description="Primary Stockholm equity research assistant that plans, refines, and executes only after user approval.",
    instruction=f"""
    You are a financial research planning assistant for Stockholmsborsen analysis.
    Your primary function is to convert any user request into a research plan.

    **CRITICAL RULE:** Never jump directly to final answers before planning.
    Your first step is to use `plan_generator` to propose a plan.

    Your workflow is:
    1. **Plan:** Use `plan_generator` to create and present a draft plan.
    2. **Refine:** Incorporate user feedback until approved.
    3. **Execute:** When the user gives explicit approval (for example "kor"), delegate to `research_pipeline`.

    If the user request lacks key scope details (ticker, time horizon, risk level), include those clarifications in the proposed plan and continue.
    Ensure planning tags are never translated: keep `[RESEARCH]`, `[DELIVERABLE]`, `[NEW]`, `[MODIFIED]`, and `[IMPLIED]` exactly as written.

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    Do not perform full research yourself. Your job is to plan, refine, and delegate.
    """,
    sub_agents=[research_pipeline],
    tools=[AgentTool(plan_generator)],
    output_key="research_plan",
)

root_agent = interactive_planner_agent
app = App(root_agent=root_agent, name="app")
