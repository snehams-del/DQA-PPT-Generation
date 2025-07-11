import logging
from ..config import LOGGING_LEVEL
from datetime import datetime
from typing import Any, Dict, Optional
from google.adk.tools import ToolContext

from google.adk.tools.base_tool import BaseTool
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from typing import Optional

from google.genai import types

logger = logging.getLogger(__name__)
logger.setLevel(LOGGING_LEVEL)

def before_tool_cb(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext) -> Optional[bool]:
    """
    Inspects/modifies the tool call or skips the call.
    """
    agent_name = tool_context.agent_name
    tool_name = tool.name
    logger.info(f"\n \n##############\n Before tool callback for Agent: {agent_name} , Tool: {tool_name} , [Timestamp] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if agent_name == "country_process_agent" and tool_name == "set_country_tool":
        if tool_context.state["workflow_stage"] != "process_country":
            logger.info(f"Will not call set_country_tool, country already set.")
            return True
        else:
            logger.info(f"Will call set_country_tool")
            return None
        
    if agent_name == "capital_verify_agent" and tool_name == "verify_capital_tool":
        if tool_context.state["attempted_capital_verification"] == True:
            logger.info(f"Will not call verify_capital_tool, capital already verified.")
            return True
        else:
            logger.info(f"Will call verify_capital_tool")
            return None

    return None



def before_agent_cb(callback_context: CallbackContext) -> Optional[types.Content]:
    """Inspects/modifies the LLM request or skips the call."""
    agent_name = callback_context.agent_name
    logger.info(f"\n##############\n Before agent call for agent: {agent_name}, [Timestamp] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if agent_name == "game_arcade_agent":
        logger.info("--- Executing before_root_agent_cb ---")
        logger.info(f"--- User content: {callback_context.user_content} ---")
        
        # Initialize the state over here if not already initialized
        callback_context.state["user_name"] = "Anuj"
        
        callback_context.state["workflow_stage"] = "ask_country"
        callback_context.state["country"] = ""
        callback_context.state["hint"] = ""
        callback_context.state["user_input"] = ""
        
        # if(callback_context.state.get("state_initalized", False) == False):
        #   await prepare_initial_state(callback_context)
        # else:
        #   logger.info("--- State is already set in the root_agent ---")
        logger.info("--- Finished before_root_agent_cb ---")
        return None

    if agent_name == "capital_game_agent":
        if callback_context.state["workflow_stage"] == "completed":
            logger.info(f"Agent: {agent_name} - The game is completed. Skipping the agent workflow.")
            return types.Content(
                role="model",
                parts=[
                    types.Part(text=f"The game is complete. We will go back to onesync agent."),
                    types.Part(function_call={"name": "transfer_to_agent", "args": {"agent_name": "onesync_agent"}}),
                ]
            )
        else:
            logger.info(f"Agent: {agent_name} - Workflow stage is not completed. Will go through with the agent call.")

    # --- Country Process Agent ---
    # if agent_name == "country_process_agent":
    #     if callback_context.state["country"] != "":
    #         logger.info(f"Agent: {agent_name} - Country already set. Skipping the agent call.")
    #         return types.Content(
    #             role="model",
    #             parts=[
    #                 types.Part(text=f"Country already set. Skipping the agent call."),
    #             ]
    #         )


    # # --- Capital Verify Agent ---
    # if agent_name == "capital_verify_agent":
    #     if callback_context.state["attempted_capital_verification"] == True:
    #         logger.info(f"Agent: {agent_name} - Capital already verified. Skipping the agent call.")
    #         return types.Content(
    #             role="model",
    #             parts=[
    #                 types.Part(text=f"Capital already verified. Skipping the agent call."),
    #             ]
    #         )
    
    return None

def after_agent_cb(callback_context: CallbackContext) -> Optional[types.Content]:
    """Inspects/modifies the LLM request or skips the call."""
    agent_name = callback_context.agent_name
    logger.info(f"\n##############\n After agent call for agent: {agent_name} , [Timestamp] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return None


def before_model_cb(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Inspects/modifies the LLM request or skips the call."""
    agent_name = callback_context.agent_name
    logger.info(f"\n##############\n Before model callback for agent: {agent_name} , [Timestamp] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if agent_name == "capital_game_agent":
        workflow_stage = callback_context.state["workflow_stage"]
        logger.info(f"Agent: {agent_name}, and workflow_stage: {workflow_stage}")

        # Inspect the workflow stage
        if workflow_stage == "completed":
            logger.info(f"Agent: {agent_name} - Workflow stage is completed. Skipping the model call.")
            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[
                        types.Part(text=f"Game is finished. We will go back to onesync agent."),
                        types.Part(function_call={"name": "transfer_to_agent", "args": {"agent_name": "onesync_agent"}}),
                        
                    ],
                )
            )
        else:
            logger.info(f"Agent: {agent_name} - Workflow stage is not completed. Will transfer control to the gameplay agent.")
            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[
                        types.Part(function_call={"name": "transfer_to_agent", "args": {"agent_name": "gameplay_agent"}}),
                    ],
                )
            )
        
    elif agent_name == "country_process_agent":
        logger.info(f"Agent: {agent_name} - Country processing attempted. Skipping the model call.")
        if callback_context.state["country"] != "":
            logger.info(f"Agent: {agent_name} - Country already set. Skipping the model call.")
            return LlmResponse(content=None)

    elif agent_name == "capital_verify_agent" and callback_context.state["attempted_capital_verification"] == True:
        logger.info(f"Agent: {agent_name} - Capital verification attempted. Skipping the model call.")
        capital = callback_context.state["capital"]
        country = callback_context.state["country"]
        logger.info(f"Capital: {capital}, Country: {country}")
        
        if callback_context.state["capital_verified"] == True:
            
            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[types.Part(text=f"I have already verified the capital. `{capital}` is the capital of `{country}`. Finishing the game :)")],
                )
            )
        else:
            logger.info(f"[capital_verify_before_model_cb] Capital was incorrect.. Skipping the model call.")
            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[types.Part(text=f"Capital '{capital}' guessed by the user for country '{country}' was incorrect :(")],
                )
            )
    
    return None