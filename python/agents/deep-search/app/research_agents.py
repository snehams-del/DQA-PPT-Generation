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
from contextlib import aclosing
from typing import Any

from google.adk.agents import (
    BaseAgent,
    LlmAgent,
    ParallelAgent,
    SequentialAgent,
)
from google.adk.agents.invocation_context import InvocationContext
from google.adk.apps.app import App
from google.adk.events import Event
from google.adk.planners import BuiltInPlanner
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.genai import types as genai_types

from .config import config
from .research_callbacks import (
    citation_replacement_callback,
    collect_research_sources_callback,
)
from .research_models import (
    DebateOutcome,
    Feedback,
    FundManagerDecision,
    MonitoringPlan,
    PortfolioConstructionPlan,
    RiskManagementOutcome,
    TraderProposal,
)


def _get_state_path_value(state: dict[str, Any], path: str) -> Any:
    """Returns a nested state value from a dot-separated path."""
    current: Any = state
    for segment in path.split("."):
        if not isinstance(current, dict) or segment not in current:
            return None
        current = current[segment]
    return current


class StateDrivenLoopAgent(BaseAgent):
    """Loops over sub-agents until state condition is met or max iterations reached."""

    max_iterations: int
    stop_state_path: str
    stop_state_value: str | bool

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        if not self.sub_agents:
            return

        for iteration in range(self.max_iterations):
            logging.info("[%s] Starting iteration %d", self.name, iteration + 1)
            should_stop = False
            for sub_agent in self.sub_agents:
                async with aclosing(sub_agent.run_async(ctx)) as event_stream:
                    async for event in event_stream:
                        yield event

                state_value = _get_state_path_value(
                    ctx.session.state, self.stop_state_path
                )
                if state_value == self.stop_state_value:
                    logging.info(
                        "[%s] Stop condition met (%s == %s).",
                        self.name,
                        self.stop_state_path,
                        self.stop_state_value,
                    )
                    should_stop = True
                    break

            if should_stop:
                return

            # Reset sub-agent states before next iteration.
            ctx.reset_sub_agent_states(self.name)


# --- AGENT DEFINITIONS ---
# Retry settings reduce transient 429 failures under bursty multi-agent load.
RETRY_GENERATE_CONTENT_CONFIG = genai_types.GenerateContentConfig(
    http_options=genai_types.HttpOptions(
        retry_options=genai_types.HttpRetryOptions(
            attempts=3,
            initial_delay=1,
            max_delay=8,
            http_status_codes=[429, 500, 503],
        )
    )
)

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
    model=config.high_throughput_model,
    name="section_researcher",
    description="Specialist analyst for news flow and near-term catalysts.",
    planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(include_thoughts=True)
    ),
    instruction="""
    You are the News and Catalyst Analyst for Stockholmsborsen.
    Focus only on:
    - latest company-specific and sector news
    - earnings and guidance changes
    - management statements and corporate actions
    - macro events likely to move Swedish equities

    Execution rules:
    1. Generate 5-7 targeted `google_search` queries with explicit date context.
    2. Prioritise official disclosures and reputable financial sources.
    3. Summarise findings as: key catalyst, directional impact, expected time horizon.
    4. Avoid technical indicator analysis, valuation modelling, and final recommendation.
    5. Explicitly flag uncertain or conflicting signals.
    """,
    tools=[google_search],
    generate_content_config=RETRY_GENERATE_CONTENT_CONFIG,
    output_key="news_catalyst_findings",
    after_agent_callback=collect_research_sources_callback,
)

technical_analyst = LlmAgent(
    model=config.high_throughput_model,
    name="technical_analyst",
    description="Specialist analyst for technical price structure and momentum signals.",
    planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(include_thoughts=True)
    ),
    instruction="""
    You are the Technical Analyst for Stockholmsborsen securities.
    Focus only on technical structure:
    - trend direction and structure
    - support and resistance
    - moving average context
    - momentum and breakout or mean-reversion conditions

    Execution rules:
    1. Run 4-6 targeted `google_search` queries for price-action context and chart commentary.
    2. Provide technical interpretation with explicit bullish and bearish triggers.
    3. Include invalidation levels when possible.
    4. Do not provide final buy or sell recommendations.
    5. Mark all low-confidence observations clearly.
    """,
    tools=[google_search],
    generate_content_config=RETRY_GENERATE_CONTENT_CONFIG,
    output_key="technical_analysis_findings",
    after_agent_callback=collect_research_sources_callback,
)

sentiment_analyst = LlmAgent(
    model=config.high_throughput_model,
    name="sentiment_analyst",
    description="Specialist analyst for analyst positioning and market sentiment.",
    planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(include_thoughts=True)
    ),
    instruction="""
    You are the Sentiment Analyst for Stockholmsborsen securities.
    Focus on:
    - analyst recommendation shifts
    - institutional positioning signals
    - media and market narrative tone
    - risk-on and risk-off context affecting Swedish equities

    Execution rules:
    1. Run 4-6 targeted `google_search` queries with recency emphasis.
    2. Report sentiment drivers and whether sentiment is accelerating or fading.
    3. Separate evidence from interpretation.
    4. Do not perform valuation modelling or final recommendation.
    5. Explicitly note where sentiment evidence is sparse.
    """,
    tools=[google_search],
    generate_content_config=RETRY_GENERATE_CONTENT_CONFIG,
    output_key="sentiment_analysis_findings",
    after_agent_callback=collect_research_sources_callback,
)

valuation_analyst = LlmAgent(
    model=config.high_throughput_model,
    name="valuation_analyst",
    description="Specialist analyst for valuation context and peer-relative positioning.",
    planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(include_thoughts=True)
    ),
    instruction="""
    You are the Valuation Analyst for Stockholmsborsen securities.
    Focus on:
    - relative valuation vs peers
    - valuation regime vs own history
    - key assumptions driving upside or downside

    Execution rules:
    1. Run 4-6 `google_search` queries targeting valuation commentary and comparable context.
    2. Provide valuation interpretation with explicit bull and bear assumptions.
    3. Avoid unsupported numerical precision.
    4. Do not issue final buy or sell recommendation.
    5. Mark stale data and unknown datapoints clearly.
    """,
    tools=[google_search],
    generate_content_config=RETRY_GENERATE_CONTENT_CONFIG,
    output_key="valuation_analysis_findings",
    after_agent_callback=collect_research_sources_callback,
)

risk_analyst = LlmAgent(
    model=config.high_throughput_model,
    name="risk_analyst",
    description="Specialist analyst for downside drivers, fragilities, and regime risks.",
    planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(include_thoughts=True)
    ),
    instruction="""
    You are the Risk Analyst for Stockholmsborsen securities.
    Focus on:
    - downside catalysts and tail risks
    - balance-sheet and funding fragilities
    - macro sensitivity and scenario stress points
    - thesis break conditions

    Execution rules:
    1. Run 4-6 `google_search` queries centred on risks and counter-cases.
    2. Produce a ranked risk register with likelihood and impact labels.
    3. Separate structural risks from short-term event risks.
    4. Do not provide final recommendation.
    5. Call out unknowns that materially reduce decision confidence.
    """,
    tools=[google_search],
    generate_content_config=RETRY_GENERATE_CONTENT_CONFIG,
    output_key="risk_analysis_findings",
    after_agent_callback=collect_research_sources_callback,
)

parallel_specialist_research = SequentialAgent(
    name="parallel_specialist_research",
    description=(
        "Runs specialist analysts in staged parallel waves to reduce peak model concurrency."
    ),
    sub_agents=[
        ParallelAgent(
            name="specialist_parallel_wave_one",
            sub_agents=[
                section_researcher,
                technical_analyst,
            ],
        ),
        ParallelAgent(
            name="specialist_parallel_wave_two",
            sub_agents=[
                sentiment_analyst,
                valuation_analyst,
                risk_analyst,
            ],
        ),
    ],
)

specialist_synthesizer = LlmAgent(
    model=config.worker_model,
    name="specialist_synthesizer",
    description="Synthesises specialist outputs into a single research package.",
    include_contents="none",
    instruction="""
    You are a synthesis analyst consolidating specialist findings into one coherent research package.

    Inputs:
    - News and catalysts: {news_catalyst_findings}
    - Technical analysis: {technical_analysis_findings}
    - Sentiment analysis: {sentiment_analysis_findings}
    - Valuation analysis: {valuation_analysis_findings}
    - Risk analysis: {risk_analysis_findings}

    Output requirements:
    1. Preserve disagreements across specialists.
    2. Highlight the top 5 evidence-backed claims.
    3. List key uncertainties and missing information.
    4. Do not produce a final buy, hold, or sell call.
    """,
    output_key="section_research_findings",
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
    model=config.high_throughput_model,
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
    generate_content_config=RETRY_GENERATE_CONTENT_CONFIG,
    output_key="section_research_findings",
    after_agent_callback=collect_research_sources_callback,
)

bull_case_analyst = LlmAgent(
    model=config.worker_model,
    name="bull_case_analyst",
    description="Builds the strongest possible bullish case from available evidence.",
    include_contents="none",
    instruction="""
    You are the Bull Case Analyst.
    Build the strongest evidence-backed bullish thesis using only:
    - section_research_findings: {section_research_findings}
    - research_evaluation: {research_evaluation}

    Requirements:
    - Present 3-5 strongest bullish arguments.
    - Include expected catalysts and horizon.
    - Explicitly cite the largest uncertainties that could weaken the bull case.
    - Do not provide the final recommendation.
    """,
    output_key="bull_case_notes",
)

bear_case_analyst = LlmAgent(
    model=config.worker_model,
    name="bear_case_analyst",
    description="Builds the strongest possible bearish and risk-focused case.",
    include_contents="none",
    instruction="""
    You are the Bear Case Analyst.
    Build the strongest evidence-backed bearish thesis using only:
    - section_research_findings: {section_research_findings}
    - research_evaluation: {research_evaluation}

    Requirements:
    - Present 3-5 strongest bearish arguments.
    - Include key downside catalysts and thesis-break scenarios.
    - Explicitly note where the bear case is weak or uncertain.
    - Do not provide the final recommendation.
    """,
    output_key="bear_case_notes",
)

debate_facilitator = LlmAgent(
    model=config.critic_model,
    name="debate_facilitator",
    description="Facilitates bull vs bear debate and decides if consensus is recommendation-ready.",
    include_contents="none",
    instruction="""
    You are the debate facilitator.
    Inputs:
    - section_research_findings: {section_research_findings}
    - bull_case_notes: {bull_case_notes}
    - bear_case_notes: {bear_case_notes}
    - previous debate outcome (if any): {debate_outcome?}

    Task:
    1. Evaluate whether current evidence supports a recommendation-ready consensus.
    2. If consensus exists, set consensus_reached=true and provide recommendation plus confidence.
    3. If not, set consensus_reached=false and provide unresolved questions that should be addressed next round.
    4. Keep rationale concise and decision-oriented.
    """,
    output_schema=DebateOutcome,
    output_key="debate_outcome",
)

debate_summary_writer = LlmAgent(
    model=config.high_throughput_model,
    name="debate_summary_writer",
    description="Converts structured debate outcome into a concise narrative summary.",
    include_contents="none",
    instruction="""
    Summarise the facilitator result for downstream reporting.
    Input:
    - debate_outcome: {debate_outcome}

    Output requirements:
    - State whether consensus was reached.
    - If reached, state recommendation and confidence.
    - List unresolved questions if consensus was not reached.
    """,
    output_key="debate_summary",
)

trader_agent = LlmAgent(
    model=config.high_throughput_model,
    name="trader_agent",
    description="Creates a structured preliminary recommendation before risk governance.",
    include_contents="none",
    instruction="""
    You are the Trader.
    Build a preliminary, evidence-backed recommendation from:
    - section_research_findings: {section_research_findings}
    - debate_summary: {debate_summary}
    - debate_outcome: {debate_outcome}

    Requirements:
    1. Select one recommendation: buy, hold, or sell.
    2. Set confidence_score (0-100) reflecting evidence strength and uncertainty.
    3. Provide an investment horizon suitable for the thesis.
    4. List key_drivers and key_risks grounded in available findings.
    5. Do not finalise portfolio governance decisions.
    """,
    output_schema=TraderProposal,
    output_key="trader_proposal",
)

risk_aggressive_manager = LlmAgent(
    model=config.high_throughput_model,
    name="risk_aggressive_manager",
    description="Risk manager with aggressive posture focusing on upside capture.",
    include_contents="none",
    instruction="""
    You are the Aggressive Risk Manager.
    Inputs:
    - trader_proposal: {trader_proposal}
    - section_research_findings: {section_research_findings}
    - risk_management_outcome (if any): {risk_management_outcome?}

    Output:
    - Provide a concise aggressive risk view with:
      1) stance on recommendation,
      2) acceptable drawdown and volatility tolerance,
      3) what would justify increasing exposure,
      4) key failure conditions.
    - Do not provide final governance approval.
    """,
    output_key="risk_aggressive_view",
)

risk_balanced_manager = LlmAgent(
    model=config.high_throughput_model,
    name="risk_balanced_manager",
    description="Risk manager with balanced posture for risk-adjusted returns.",
    include_contents="none",
    instruction="""
    You are the Balanced Risk Manager.
    Inputs:
    - trader_proposal: {trader_proposal}
    - section_research_findings: {section_research_findings}
    - risk_management_outcome (if any): {risk_management_outcome?}

    Output:
    - Provide a concise balanced risk view with:
      1) stance on recommendation,
      2) preferred exposure range,
      3) required confirmation signals,
      4) risk controls needed before execution.
    - Do not provide final governance approval.
    """,
    output_key="risk_balanced_view",
)

risk_defensive_manager = LlmAgent(
    model=config.high_throughput_model,
    name="risk_defensive_manager",
    description="Risk manager with defensive posture focusing on capital preservation.",
    include_contents="none",
    instruction="""
    You are the Defensive Risk Manager.
    Inputs:
    - trader_proposal: {trader_proposal}
    - section_research_findings: {section_research_findings}
    - risk_management_outcome (if any): {risk_management_outcome?}

    Output:
    - Provide a concise defensive risk view with:
      1) stance on recommendation,
      2) maximum acceptable downside,
      3) reasons to reduce or avoid exposure,
      4) strict stop conditions.
    - Do not provide final governance approval.
    """,
    output_key="risk_defensive_view",
)

risk_management_facilitator = LlmAgent(
    model=config.critic_model,
    name="risk_management_facilitator",
    description="Facilitates risk-manager views and produces risk-adjusted consensus.",
    include_contents="none",
    instruction="""
    You are the Risk Management Facilitator.
    Inputs:
    - trader_proposal: {trader_proposal}
    - risk_aggressive_view: {risk_aggressive_view}
    - risk_balanced_view: {risk_balanced_view}
    - risk_defensive_view: {risk_defensive_view}
    - previous risk outcome (if any): {risk_management_outcome?}

    Task:
    1. Determine whether risk governance consensus is reached.
    2. If reached:
       - set consensus_reached=true,
       - set adjusted_recommendation and adjusted_confidence_score,
       - select risk_profile_alignment,
       - provide practical position_sizing_guidance.
    3. If not reached:
       - set consensus_reached=false,
       - keep recommendation/confidence/profile as null,
       - provide unresolved_risks that next round must resolve.
    4. Keep output strictly aligned with the schema.
    """,
    output_schema=RiskManagementOutcome,
    output_key="risk_management_outcome",
)

risk_management_summary_writer = LlmAgent(
    model=config.high_throughput_model,
    name="risk_management_summary_writer",
    description="Converts structured risk governance outcome into a concise narrative.",
    include_contents="none",
    instruction="""
    Summarise the risk governance status for downstream reporting.
    Input:
    - risk_management_outcome: {risk_management_outcome}

    Output requirements:
    - State whether consensus was reached.
    - If reached, state risk-adjusted recommendation, confidence, and profile alignment.
    - Include position sizing guidance.
    - List unresolved risks if consensus was not reached.
    """,
    output_key="risk_management_summary",
)

fund_manager_agent = LlmAgent(
    model=config.critic_model,
    name="fund_manager_agent",
    description="Makes the final portfolio decision after debate and risk governance.",
    include_contents="none",
    instruction="""
    You are the Fund Manager with final investment authority.
    Inputs:
    - trader_proposal: {trader_proposal}
    - debate_outcome: {debate_outcome}
    - risk_management_outcome: {risk_management_outcome}
    - section_research_findings: {section_research_findings}

    Decision rules:
    1. Use risk_management_outcome when consensus is reached.
    2. If risk consensus is not reached, default to a conservative final stance unless evidence is overwhelmingly clear.
    3. Return one final recommendation (buy/hold/sell), final confidence, and horizon.
    4. Set conviction_level based on evidence quality and unresolved risks.
    5. Provide execution_guardrails that reduce implementation risk.
    """,
    output_schema=FundManagerDecision,
    output_key="fund_manager_decision",
)

portfolio_constructor = LlmAgent(
    model=config.worker_model,
    name="portfolio_constructor",
    description="Converts the final decision into a concrete portfolio implementation plan.",
    include_contents="none",
    instruction="""
    You are the Portfolio Construction Manager.
    Inputs:
    - fund_manager_decision: {fund_manager_decision}
    - risk_management_outcome: {risk_management_outcome}
    - section_research_findings: {section_research_findings}

    Task:
    1. Convert the final recommendation into explicit sizing and implementation guidance.
    2. Keep position and risk budgets conservative when confidence is low or risks are unresolved.
    3. Define practical entry and exit approaches.
    4. Provide objective stop conditions tied to thesis invalidation.
    5. Keep all outputs consistent with the structured schema.
    """,
    output_schema=PortfolioConstructionPlan,
    output_key="portfolio_construction_plan",
)

monitoring_planner = LlmAgent(
    model=config.high_throughput_model,
    name="monitoring_planner",
    description="Defines a post-decision monitoring and escalation plan.",
    include_contents="none",
    instruction="""
    You are the Monitoring Planner.
    Inputs:
    - fund_manager_decision: {fund_manager_decision}
    - portfolio_construction_plan: {portfolio_construction_plan}
    - section_research_findings: {section_research_findings}

    Task:
    1. Define review cadence appropriate to horizon and risk.
    2. List key indicators that should be monitored continuously.
    3. Build a catalyst watchlist for upcoming decision-relevant events.
    4. Define escalation triggers that require immediate reassessment.
    5. Keep output concise and schema-compliant.
    """,
    output_schema=MonitoringPlan,
    output_key="monitoring_plan",
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
    *   Debate Summary: `{debate_summary}`
    *   Debate Outcome: `{debate_outcome}`
    *   Trader Proposal: `{trader_proposal}`
    *   Risk Governance Summary: `{risk_management_summary}`
    *   Risk Governance Outcome: `{risk_management_outcome}`
    *   Fund Manager Decision: `{fund_manager_decision}`
    *   Portfolio Construction Plan: `{portfolio_construction_plan}`
    *   Monitoring Plan: `{monitoring_plan}`
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
    Use `fund_manager_decision` as the authoritative final call.
    Include one concise final recommendation block with:
    - Recommendation: Kop / Behall / Salj (mapped from buy / hold / sell)
    - Confidence score: 0-100
    - Investment horizon
    - Conviction level
    - Position sizing guidance
    - Target and maximum position size
    - Entry and exit approach
    - 3 strongest supporting arguments
    - 3 strongest counter-arguments and risks
    - Key catalysts to monitor
    - Execution guardrails
    Include a short monitoring block with review cadence, key indicators, and escalation triggers.
    If data is uncertain or stale, state that explicitly.
    Do not include a separate references section; citations must be in-line.
    End with: "Detta ar informationsmaterial och inte personlig finansiell radgivning."
    """,
    output_key="final_cited_report",
    after_agent_callback=citation_replacement_callback,
)

research_pipeline = SequentialAgent(
    name="research_pipeline",
    description=(
        "Executes a pre-approved research plan using specialist parallel analysis, "
        "iterative refinement, debate-driven recommendation synthesis, and risk governance."
    ),
    sub_agents=[
        section_planner,
        parallel_specialist_research,
        specialist_synthesizer,
        StateDrivenLoopAgent(
            name="iterative_refinement_loop",
            max_iterations=config.max_search_iterations,
            stop_state_path="research_evaluation.grade",
            stop_state_value="pass",
            sub_agents=[
                research_evaluator,
                enhanced_search_executor,
            ],
        ),
        StateDrivenLoopAgent(
            name="investment_debate_loop",
            max_iterations=config.max_debate_iterations,
            stop_state_path="debate_outcome.consensus_reached",
            stop_state_value=True,
            sub_agents=[
                bull_case_analyst,
                bear_case_analyst,
                debate_facilitator,
            ],
        ),
        debate_summary_writer,
        trader_agent,
        StateDrivenLoopAgent(
            name="risk_management_loop",
            max_iterations=config.max_risk_iterations,
            stop_state_path="risk_management_outcome.consensus_reached",
            stop_state_value=True,
            sub_agents=[
                risk_aggressive_manager,
                risk_balanced_manager,
                risk_defensive_manager,
                risk_management_facilitator,
            ],
        ),
        risk_management_summary_writer,
        fund_manager_agent,
        portfolio_constructor,
        monitoring_planner,
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
