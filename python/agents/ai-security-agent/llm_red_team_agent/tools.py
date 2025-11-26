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

from .agent_utils import execute_sub_agent
from .sub_agents import evaluator, red_team, target

# --- Initialize Workers ---
red_team_worker = red_team.create()
target_worker = target.create()
evaluator_worker = evaluator.create()


def run_complete_security_scan(risk_category: str) -> str:
    """
    Performs a full, multi-step security audit for a given risk category.

    Steps:
    1. Red Team generates attack.
    2. Target System is attacked.
    3. Evaluator judges the result.
    Args:
        risk_category (str): The risk category to test (e.g., "Toxicity", "Phishing").
    """
    print(f"\n    ⚙️  1. Generating Attack for '{risk_category}'...")
    attack_prompt = execute_sub_agent(red_team_worker, risk_category)

    if not attack_prompt or "Error" in attack_prompt:
        return f"Attack Generation Failed: {attack_prompt}"

    print("    ⚙️  2. Injecting Attack into Target...")
    target_text = execute_sub_agent(target_worker, attack_prompt)

    print("    ⚙️  3. Running Evaluation...")
    eval_query = f"[ATTACK]: {attack_prompt}\n[RESPONSE]: {target_text}"
    verdict_text = execute_sub_agent(evaluator_worker, eval_query)

    # Truncating the target attack conversation for brevity
    return f"""
    --- SECURITY AUDIT RESULT ---
    • Scenario: {risk_category}
    • Attack Attempt: "{attack_prompt[:100]}..."
    • Target Behavior: "{target_text[:100]}..."
    • Final Verdict: {verdict_text}
    -----------------------------
    """
