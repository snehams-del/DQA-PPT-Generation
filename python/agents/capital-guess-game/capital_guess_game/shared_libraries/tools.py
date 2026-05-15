import logging
from typing import Any, Dict, Optional

from google.adk.tools import ToolContext
from ..config import LOGGING_LEVEL
from google.adk.tools.base_tool import BaseTool


logger = logging.getLogger(__name__)
logger.setLevel(LOGGING_LEVEL)


def verify_capital_tool(tool_context: ToolContext, capital: str) -> bool:
    """
    Verify if the capital given as input by the user is correct for the country set in the game.
    Sets the capital_verified key in the state to True if the capital is correct, False otherwise.

    Args:
        capital: The capital of a country guessed by the user.

    Returns:
        True if the capital set in the state is correct for the country, False otherwise
    """
    COUNTRY_CAPITALS = {
        "france": "paris",
        "germany": "berlin",
        "india": "new delhi",
        "usa": "washington",
        "japan": "tokyo",
    }
    country = tool_context.state["country"]
    tool_context.state["capital"] = capital.lower()
    expected = COUNTRY_CAPITALS.get(country.lower())
    

    logger.info(f"Verifying capital for country: {country} with capital: {capital} and expected: {expected}")

    tool_context.state["attempted_capital_verification"] = True
    
    if not expected:
        return False
    if capital.strip().lower() == expected.lower():
        tool_context.state["workflow_stage"] = "completed"
        tool_context.state["capital_verified"] = True
        return True
    
    tool_context.state["workflow_stage"] = "verify_capital"
    tool_context.state["capital_verified"] = False
    return False


def set_country_tool(tool_context: ToolContext, country: str) -> bool:
    """
    Set the country for which the Capital Guess Game is to be played in the state.
    Args:
        country: The country for which the Capital Guess Game is to be played.
    Returns:
        True if the country is set in the state, False otherwise.
    """
    tool_context.state["country"] = country.lower()
    tool_context.state["workflow_stage"] = "ask_capital"
    return True


def set_capital_tool(tool_context: ToolContext, capital: str) -> bool:
    """
    Set the capital of a country guessed by the user in the state.
    Args:
        capital: The capital of a country guessed by the user.
    Returns:
        True if the capital is set in the state, False otherwise.
    """
    tool_context.state["capital"] = capital
    return True


def capital_verify_before_tool_cb(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext) -> Optional[bool]:
    """
    Inspects/modifies the tool call or skips the call.
    """
    if tool_context.state["workflow_stage"] != "verify_capital":
        logger.info(f"Will not call verify_capital_tool, verification already done.")
        return True
    
    logger.info(f"Will call verify_capital_tool")
    return None