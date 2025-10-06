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

"""
This script runs an evaluation harness for ADK agents against Tau2-Bench tasks.

It orchestrates the interaction between an ADK agent and a Tau2-Bench environment,
simulating a user conversation and evaluating the agent's performance based on
the Tau2-Bench reward system.

Key functionalities include:
- Loading an ADK agent dynamically from a specified path.
- Initializing a Tau2-Bench environment for a given domain and task.
- Injecting Tau2-Bench domain policies into the ADK agent's instructions.
- Simulating user interactions using a specified LLM.
- Mapping ADK tool calls to Tau2-Bench tool calls and executing them.
- Logging detailed trajectories and results for each task.
- Generating a summary of the evaluation run, including average reward.
"""


import asyncio
import argparse
import importlib
import json
import sys
import os
import csv
import warnings
from pathlib import Path
from contextlib import redirect_stderr
from dotenv import load_dotenv
from copy import deepcopy
from datetime import datetime
from tqdm.asyncio import tqdm
from loguru import logger as loguru_logger

# Disable the default loguru handler to clean up console output from tau2-bench
# This must be done before importing any tau2 modules
loguru_logger.remove()
loguru_logger.add(sys.stderr, level="WARNING")

# Suppress ResourceWarning, which can be triggered by unclosed aiohttp client sessions
warnings.filterwarnings("ignore", category=ResourceWarning)

# --- ADK Imports ---
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.events import Event
from google.genai.types import Content, Part, FunctionResponse, FunctionCall

# --- Tau2-Bench Imports ---
from tau2.run import get_tasks
from tau2.registry import registry
from tau2.evaluator.evaluator_env import EnvironmentEvaluator
from tau2.data_model.simulation import SimulationRun, TerminationReason
from tau2.data_model.message import UserMessage, AssistantMessage, ToolCall, ToolMessage
from tau2.user.user_simulator import UserSimulator

# --- Harness Imports ---
from harness.tool_mapper import get_tool_mapping


class FileLogger:
    """A simple logger to write to a file and optionally to stdout."""

    def __init__(self, log_path, to_stdout=True):
        self.terminal = sys.stdout
        self.log_file = open(log_path, "w", encoding="utf-8")
        self.to_stdout = to_stdout

    def log(self, message):
        """Log a message to the configured outputs."""
        if self.to_stdout:
            # This is now only used for high-level status in main
            print(message, file=self.terminal, flush=True)

        # Always write to the task-specific log file
        print(message, file=self.log_file, flush=True)

    def __del__(self):
        if self.log_file:
            self.log_file.close()

    def task_start(self, task_id):
        """Logs the start of a task."""
        self.log(f"--- Running Task: {task_id} ---")

    def info(self, message):
        """Logs an informational message."""
        self.log(f"\n[INFO] {message}")

    def user_simulator(self, message, is_stop=False):
        """Logs a message from the user simulator."""
        stop_signal = " (STOP SIGNAL)" if is_stop else ""
        self.log(f"\n[USER SIMULATOR]: {message}{stop_signal}")

    def turn_start(self, turn_number):
        """Logs the start of a new turn."""
        self.log(f"\n>>> Turn {turn_number}: ADK Agent processing...")

    def agent_to_harness_tool_call(self, tool_name, args):
        """Logs a tool call from the ADK agent to the harness."""
        self.log(f"  [ADK AGENT -> Harness]: Tool Call: {tool_name}({args})")

    def harness_to_env(self, tool_name):
        """Logs a tool execution in the Tau2 environment."""
        self.log(f"  [Harness -> Tau2 Env]: Executed {tool_name}.")

    def agent_to_user(self, message):
        """Logs a text response from the ADK agent to the user."""
        self.log(f"  [ADK AGENT -> User]: {message}")

    def evaluation_result(self, task_id, reward, db_check):
        """Logs the final evaluation result for a task."""
        self.log("\n--- EVALUATION RESULT ---")
        self.log(f"✅ Task: {task_id}")
        self.log(f"🏆 Reward: {reward:.2f}")
        if db_check:
            self.log(f"🗃️ DB Match: {db_check.db_match}")
        self.log("----------------------------\n")


def _find_tool_call_in_events(events: list) -> FunctionCall | None:
    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.function_call:
                    return part.function_call
    return None


def _get_final_text_from_events(events: list) -> str | None:
    final_text = ""
    for event in events:
        if (
            event.is_final_response()
            and event.content
            and event.content.parts
            and event.content.parts[0].text
        ):
            final_text += event.content.parts[0].text
    return final_text if final_text else None


async def run_evaluation_for_task(
    domain: str,
    task,
    adk_agent,
    user_llm: str,
    run_path: Path,
    max_turns: int,
):
    """Orchestrates the evaluation of a single task, logging its detailed output to its
    own file."""
    task_path = run_path / "trajectories" / f"task_{task.id}"
    os.makedirs(task_path, exist_ok=True)

    task_logger = FileLogger(task_path / "console.log", to_stdout=False)

    task_logger.task_start(task.id)

    env_constructor = registry.get_env_constructor(domain)
    tau2_env = env_constructor()
    if task.initial_state:
        tau2_env.set_state(
            initialization_data=task.initial_state.initialization_data,
            initialization_actions=task.initial_state.initialization_actions,
            message_history=task.initial_state.message_history or [],
        )

    domain_policy = tau2_env.get_policy()
    adk_agent_with_policy = deepcopy(adk_agent)
    original_instruction = adk_agent_with_policy.instruction
    adk_agent_with_policy.instruction = (
        "You must strictly follow the policies provided below.\n\n"
        "<policy>\n"
        f"{domain_policy}\n"
        "</policy>\n\n"
        "--- Your Original Instructions ---\n"
        f"{original_instruction}"
    )
    task_logger.info(
        "Injected Tau2 domain policy into ADK agent's instructions for this run."
    )

    adk_session_service = InMemorySessionService()
    adk_runner = Runner(
        agent=adk_agent_with_policy,
        app_name="adk_eval_harness",
        session_service=adk_session_service,
    )
    adk_session = await adk_session_service.create_session(
        app_name="adk_eval_harness", user_id="eval_user"
    )

    user_simulator = UserSimulator(instructions=str(task.user_scenario), llm=user_llm)
    user_sim_state = user_simulator.get_init_state()

    tau2_trajectory = []

    initial_assistant_msg = AssistantMessage(
        role="assistant", content="Hello! How can I help you today?"
    )
    user_response_msg, user_sim_state = user_simulator.generate_next_message(
        initial_assistant_msg, user_sim_state
    )

    task_logger.user_simulator(user_response_msg.content)
    tau2_trajectory.append(user_response_msg)
    current_adk_message = Content(
        role="user", parts=[Part(text=user_response_msg.content)]
    )

    # Main interaction loop: ADK Agent <-> User Simulator
    for turn in range(max_turns):
        task_logger.turn_start(turn + 1)

        # Run the ADK agent for one turn with the user's message
        adk_events = [
            event
            async for event in adk_runner.run_async(
                session_id=adk_session.id,
                user_id="eval_user",
                new_message=current_adk_message,
            )
        ]

        # Check if the agent responded with a tool call or a text message
        adk_tool_call = _find_tool_call_in_events(adk_events)

        if adk_tool_call:
            # Agent wants to use a tool.
            # Map the ADK tool call to the corresponding Tau2 tool, execute it,
            # and feed the result back to the agent in the next turn.
            tool_map_config = get_tool_mapping(domain)
            adk_tool_name = adk_tool_call.name
            adk_args = dict(adk_tool_call.args)
            adk_tool_call_id = adk_tool_call.id or f"adk_tool_call_{turn}"

            task_logger.agent_to_harness_tool_call(adk_tool_name, adk_args)

            tau2_tool_name = tool_map_config["tool_map"].get(adk_tool_name)
            tau2_args = tool_map_config["arg_mapper"](adk_tool_name, adk_args)

            tau2_trajectory.append(
                AssistantMessage(
                    role="assistant",
                    tool_calls=[
                        ToolCall(
                            id=adk_tool_call_id,
                            name=tau2_tool_name,
                            arguments=tau2_args,
                        )
                    ],
                )
            )

            tool_result = tau2_env.use_tool(tool_name=tau2_tool_name, **tau2_args)
            task_logger.harness_to_env(tau2_tool_name)

            if hasattr(tool_result, "model_dump"):
                tool_result_for_adk = tool_result.model_dump()
                tool_result_for_eval = tool_result.model_dump()
            elif isinstance(tool_result, dict):
                tool_result_for_adk = tool_result
                tool_result_for_eval = tool_result
            else:
                tool_result_for_adk = {"result": tool_result}
                tool_result_for_eval = tool_result

            tau2_trajectory.append(
                ToolMessage(
                    id=adk_tool_call_id,
                    role="tool",
                    content=json.dumps(tool_result_for_eval),
                    requestor="assistant",
                )
            )

            current_adk_message = Content(
                role="user",
                parts=[
                    Part(
                        function_response=FunctionResponse(
                            id=adk_tool_call_id,
                            name=adk_tool_name,
                            response=tool_result_for_adk,
                        )
                    )
                ],
            )
            continue

        else:
            # Agent responded with a text message.
            # Get the user simulator's response and check if the conversation should end.
            final_text = _get_final_text_from_events(adk_events)
            if not final_text:
                final_text = "(Agent produced no text response)"

            task_logger.agent_to_user(final_text)

            agent_response_msg = AssistantMessage(role="assistant", content=final_text)
            tau2_trajectory.append(agent_response_msg)

            user_response_msg, user_sim_state = user_simulator.generate_next_message(
                agent_response_msg, user_sim_state
            )

            # The user simulator signals the end of the conversation
            if UserSimulator.is_stop(user_response_msg):
                task_logger.user_simulator(user_response_msg.content, is_stop=True)
                tau2_trajectory.append(user_response_msg)
                break

            task_logger.user_simulator(user_response_msg.content)
            tau2_trajectory.append(user_response_msg)
            current_adk_message = Content(
                role="user", parts=[Part(text=user_response_msg.content)]
            )

    dummy_sim_run = SimulationRun(
        id=f"{run_path.name}_task_{task.id}",
        task_id=task.id,
        start_time="",
        end_time="",
        duration=0,
        termination_reason=TerminationReason.USER_STOP,
        messages=tau2_trajectory,
    )

    reward_info = EnvironmentEvaluator.calculate_reward(
        environment_constructor=env_constructor,
        task=task,
        full_trajectory=dummy_sim_run.messages,
    )

    task_logger.evaluation_result(task.id, reward_info.reward, reward_info.db_check)

    # Save detailed task files
    traj_path = task_path / "trajectory.json"
    with open(traj_path, "w", encoding="utf-8") as f:
        json.dump(dummy_sim_run.model_dump(mode="json"), f, indent=4)

    result_path = task_path / "result.json"
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(reward_info.model_dump(mode="json"), f, indent=4)

    return {
        "task_id": task.id,
        "reward": reward_info.reward,
        "passed": reward_info.reward == 1.0,
        "trajectory_file": str(traj_path),
        "result_file": str(result_path),
        "console_log_file": str(task_logger.log_file.name),
    }


def write_summary_files(run_path: Path, all_task_results: list, args, adk_agent):
    """Writes the run_summary.json and results.csv files."""
    # Write results.csv
    csv_path = run_path / "results.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["task_id", "reward", "passed"])
        writer.writeheader()
        for result in all_task_results:
            writer.writerow(
                {
                    "task_id": result["task_id"],
                    "reward": result["reward"],
                    "passed": result["passed"],
                }
            )

    # Write run_summary.json
    summary_path = run_path / "run_summary.json"
    total_reward = sum(r["reward"] for r in all_task_results)
    avg_reward = total_reward / len(all_task_results) if all_task_results else 0

    summary_data = {
        "run_id": run_path.name,
        "domain": args.domain,
        "num_tasks_run": len(all_task_results),
        "agent_config": {
            "path": args.adk_agent_path,
            "model": adk_agent.model,
            "description": adk_agent.description,
        },
        "user_llm": args.user_llm,
        "average_reward": avg_reward,
        "tasks": all_task_results,
    }
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=4)


async def main(args):
    # --- Setup Logging and Directories ---
    run_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_id = f"run_{run_timestamp}_{args.domain}"
    run_path = Path("evaluation_logs") / run_id
    os.makedirs(run_path / "trajectories", exist_ok=True)

    print(f"Starting evaluation run: {run_id}")
    print(f"Saving results to: {run_path.resolve()}")

    # --- Load ADK Agent ---
    agent_path_str = args.adk_agent_path
    try:
        file_path_str, agent_variable_name = agent_path_str.split(":")
    except ValueError:
        raise ValueError(
            f"Invalid --adk_agent_path format."
            f"Expected 'path/to/agent.py:variable_name', but got '{agent_path_str}'"
        )

    agent_file_path = Path(file_path_str).resolve()
    if not agent_file_path.is_file():
        raise FileNotFoundError(f"Agent file not found at: {agent_file_path}")

    agent_dir = agent_file_path.parent
    sys.path.insert(0, str(agent_dir))

    try:
        module_name = agent_file_path.stem
        agent_module = importlib.import_module(module_name)
        adk_agent = getattr(agent_module, agent_variable_name)
    except (ImportError, AttributeError) as e:
        raise ImportError(
            f"Could not import agent '{agent_variable_name}'"
            f"from '{agent_file_path}'. Error: {e}"
        )
    finally:
        sys.path.pop(0)

    # --- Run Evaluation Tasks ---
    tasks = get_tasks(args.domain, num_tasks=args.num_tasks)

    task_coroutines = [
        run_evaluation_for_task(
            args.domain, task, adk_agent, args.user_llm, run_path, args.max_turns
        )
        for task in tasks
    ]
    all_task_results = []

    print(f"\nRunning {len(tasks)} tasks in parallel...")
    # Temporarily redirect stderr to /dev/null to suppress aiohttp warnings and keep the
    # progress bar clean
    with open(os.devnull, "w") as devnull:
        with redirect_stderr(devnull):
            for future in tqdm.as_completed(
                task_coroutines,
                total=len(tasks),
                desc=f"Evaluating {args.domain} domain",
                file=sys.stdout,
            ):
                try:
                    result = await future
                    all_task_results.append(result)
                except Exception as e:
                    # Print exceptions to stdout to ensure they are not silenced
                    print(f"\nA task failed with an exception: {e}\n")

    # --- Write Summary Files ---
    if all_task_results:
        write_summary_files(run_path, all_task_results, args, adk_agent)

    print(f"\nEvaluation run {run_id} finished.")
    print(f"Results saved in: {run_path.resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run Conversational ADK Agent Evaluation Harness"
    )
    parser.add_argument(
        "--domain", type=str, required=True, help="Tau2-Bench domain to evaluate"
    )
    parser.add_argument(
        "--num-tasks",
        type=int,
        default=None,
        help="Number of tasks to run (default: all).",
    )
    parser.add_argument(
        "--adk_agent_path",
        type=str,
        required=True,
        help="Path to ADK agent. e.g. "
        "'sample_adk_agents/airline/agent.py:variable_name'",
    )
    parser.add_argument(
        "--user-llm", type=str, required=True, help="LLM to use for the user simulator."
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        default=15,
        help="Maximum number of turns per task (default: 15).",
    )

    args = parser.parse_args()

    load_dotenv(dotenv_path=Path(__file__).parent / ".env")

    asyncio.run(main(args))
