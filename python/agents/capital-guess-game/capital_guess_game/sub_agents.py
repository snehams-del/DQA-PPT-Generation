import logging

from typing import AsyncGenerator, Any, Optional

from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.genai import types
from .config import AI_MODEL, LOGGING_LEVEL
from google.adk.agents import LlmAgent, BaseAgent
from typing import override
from .shared_libraries.callbacks import *
from .shared_libraries.tools import *

logger = logging.getLogger(__name__)
logger.setLevel(LOGGING_LEVEL)


# --- AGENTS ---

# STEP 1: Ask Country Agent
country_ask_agent = LlmAgent(
    name="country_ask_agent",
    model=AI_MODEL,
    generate_content_config=types.GenerateContentConfig(temperature=0.4),
    # include_contents='none',
    instruction="""
    You are the Country Ask Agent. You will ask the user to choose a country from this list only: "france", "germany", "india", "usa", "japan".

    ## Rules:
    * You will not process the user input. This is done by country_process_agent.
    * You will keep your message short and concise.
    * You will do only as told and not display any random message to the end user.

    ## Execution:
    1. Display a message to ask the user to choose a country from this list only: "france", "germany", "india", "usa", "japan". You can be creative here and say something like "Let's start with some easy country, choose one from this list: France, Germany, India, USA, Japan".
    2. End
    """,
    description="You will ask the user for the country for which the Capital Guess Game is to be played",
)

# STEP 2: This agent will process the user input and set the country name in the state
country_process_agent = LlmAgent(
    name="country_process_agent",
    model=AI_MODEL,
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
    # include_contents='none',
    instruction="""
    You are the Country Process Agent.

    ## Input Data:
    * `user_input`: This is the input from the user of the country guessed by the user. Its current value in state is `{{user_input}}`.

    ## Available Tools:
    * `set_country_tool`: This tool is used to set the country in the state. You will need the name of the country (string) to call this tool.

    ## Role:
    You are part of a bigger workflow. In this workflow, your job is to only process the `user_input` and it it contains a country's name, then call `set_country_tool` tool to set the country in the state.

    ## Rules:
    * The `user_input` should not contain names of more than one country.
    * The `user_input` can contain a country name in a sentence or a phrase. Examples: "I choose France", "I will go with Germany", "go with India", etc.
    * The country name deciphered by you should be one of these: "france", "germany", "india", "usa", "japan".
    * You will not ask the user to choose a country. This is done by country_ask_agent.
    * You will not ask the user to guess the capital. This is done by capital_guess_agent.
    * You will not verify the capital entered by the user. This is done by capital_verify_agent.
    * You will do only as told and not display any random message to the end user.

    ## Execution:
    1. Analyse the `user_input` and see if it contains the name of a country as per the rules mentioned above.
        a. If you think it contains a valid country name, then extract the country name and use it to call `set_country_tool` tool.
        b. If you think it does not contain a valid country name, then do not call `set_country_tool` tool and instead go to step 3.
    2. Analyse the response of `set_country_tool` tool. Whether the tool returned True or False, go to step 3.
    3. End
    """,
    description="You will process and set the country name for which the Capital Guess Game is to be played",
    tools=[
      set_country_tool, 
    ],
    before_model_callback=before_model_cb,
    # before_tool_callback=before_tool_cb
)


# STEP 3: Guess Capital Agent
capital_guess_agent = LlmAgent(
    name="capital_guess_agent",
    model=AI_MODEL,
    generate_content_config=types.GenerateContentConfig(temperature=0.8),
    include_contents='none',
    instruction="""
    You are the Capital Guess Agent.

    ## Input Data:
    * `country`: This is the country for which the capital is to be guessed. Its current value in state is `{{country}}`.
    * `hint`: This is the hint for the capital of the country. Its current value in state is `{{hint}}`.

    ## Role:
    * You are supposed to guess the capital of the country {country} using the allowed list of capitals.

    ## Allowed list of capitals:
    * Paris
    * New Delhi
    * Berlin
    * Washington
    * Tokyo
    * London
    * Rome
    * Madrid
    * Amsterdam
    * Moscow
    * Beijing
    * Seoul

    ## Rules:
    * **[Strict Rule]**: You are not supposed to use your intelligence and knowledge to guess the capital. You will only use the allowed list of capitals and the hint given by the user.
    * If there is no hint, then you can pick a random capital from the allowed list of capitals.
    * You can use the hint: {hint} given by the user to filter some capitals from the allowed list of capitals and then pick one capital randomly from that list.
    * You will randomly pick a capital from the allowed list of capitals if there is no hint.
    * You will not ask the user to choose a country. This is done by country_ask_agent.


    ## Some examples of hints:
    * "I think the first letter of the capital is P"
    * "I think the last letter of the capital is e"
    * "I think the capital is in Europe"
    * "You are very close, it starts from the same letter"
    * "The first letter of the capital is a vowel"

    ## Execution:
    1. Guess the capital using the above rules and display a message to the user on the lines of: "I think the capital of {country} is X" where X is the capital you guessed.
    2. End
    """,
    description="You will guess the capital of a country using the allowed list of capitals and user hint.",
)


class GameplayAgent(LlmAgent):
    @override
    async def run_async(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:

        logger.info(f"\n\n $$$$$$$$$$$$$$$\nStarting GameplayAgent execution for agent: {self.name}")
        
        country = ctx.session.state.get("country", "")
        logger.info(f"State check - country: {country}, workflow_stage: {ctx.session.state.get("workflow_stage")}")

        user_message = ""
        user_content_parts = ctx.user_content.parts
        if len(user_content_parts) > 0:
            user_last_message = user_content_parts.pop()
            if user_last_message.text and user_last_message.text != "":
                user_message = user_last_message.text

        logger.info(f"User message: {user_message}")
        
        # --- Phase 0: Check for Exit message from the user ---
        if user_message != "" and (user_message.lower() == "exit" or user_message.lower() == "quit" or user_message.lower() == "end" or user_message.lower() == "finish" or user_message.lower() == "bye" or user_message.lower() == "goodbye"):
            logger.info(f"User message is a completion message. Workflow stage set to completed.")
            yield Event(
                invocation_id=ctx.invocation_id,
                author="capital_guess_workflow_agent",
                content={"parts": [
                    {"function_call": {"name": "transfer_to_agent", "args": {"agent_name": "game_arcade_agent"}}},
                    {"text": "Okay I will end the game now. Thank you for playing!"}
                ]},
                actions=EventActions(
                    transfer_to_agent="game_arcade_agent",
                    state_delta={
                        "workflow_stage": "completed",
                        "country": "",
                        "hint": ""
                    }
                ) # Optional hint for orchestration
            )
            return
        
        # --- Phase 1: Validate the Guessed Capital ---
        if user_message != "" and ctx.session.state.get("workflow_stage") == "validate_capital":
            logger.info(f"Workflow stage: {ctx.session.state.get("workflow_stage")} and hence user will validate the guessed capital")
            
            # Check if user is satisfied with agent's answer and finish the game
            if user_message.lower() == "bravo" or user_message.lower() == "nice" or user_message.lower() == "correct" or user_message.lower() == "right" or user_message.lower() == "correct answer" or user_message.lower() == "right answer" or user_message.lower() == "yes" or user_message.lower() == "perfect":
                logger.info(f"User is satisfied with agent's answer. Setting workflow stage to completed.")
                yield Event(
                    invocation_id=ctx.invocation_id,
                    author="capital_guess_workflow_agent",
                    content={"parts": [
                        {"text": "I am a champ, I got the capital right. This was fun. Thank you!"}
                    ]},
                    actions=EventActions(
                        state_delta={
                            "workflow_stage": "completed",
                            "country": "",
                            "hint": "",
                            "user_input": ""
                        }
                    ) 
                )

                yield Event(
                    invocation_id=ctx.invocation_id,
                    author="game_arcade_agent",
                    content={"parts": [
                        {"text": "Transferring control to the root agent!"},
                    ]},
                )
                
                logger.info(f"Yielding events of root agent!")

                async for event in ctx.agent.parent_agent.run_async(ctx):
                    yield event

                logger.info(f"Yielded all events of root agent!")
                return


            else:
                # Game goes on
                logger.info(f"User is not satisfied with agent's answer. Setting workflow stage to guess_capital and hint to user's input.")
                yield Event(
                    invocation_id=ctx.invocation_id,
                    author="capital_guess_workflow_agent",
                    actions=EventActions(
                        state_delta={
                            "workflow_stage": "guess_capital",
                            "hint": user_message,
                        }
                    )
                )
                # Do not return here. Let the agent guess the capital again as the flow will continue.

        # --- Phase 2: Ask Country ---
        if ctx.session.state.get("workflow_stage") == "ask_country":
            logger.info(f"Workflow stage: {ctx.session.state.get("workflow_stage")} and hence asking user for the country.")
            async for event in self.sub_agents[0].run_async(ctx):
                yield event
            logger.info("Country ask agent asked for country...")

            # Set the workflow stage to process_country
            yield Event(
                invocation_id=ctx.invocation_id,
                author="capital_guess_workflow_agent",
                actions=EventActions(
                    state_delta={
                        "workflow_stage": "process_country",
                        "country": "",
                        "user_input": ""
                    }
                ) # Optional hint for orchestration
            )

            # Wait for user input
            logger.info("Waiting for user input for country...")
            return        

        # --- Phase 3: Process Country ---
        if ctx.session.state.get("workflow_stage") == "process_country":
            logger.info(f"Workflow stage: {ctx.session.state.get("workflow_stage")} and hence processing the country.")

            logger.info(f"User has given the input for a country. Setting user_input in state.")
            yield Event(
                invocation_id=ctx.invocation_id,
                author="capital_guess_workflow_agent",
                actions=EventActions(
                    state_delta={
                        "user_input": user_message
                    }
                ) 
            )
            
            async for event in self.sub_agents[1].run_async(ctx):
                yield event
            logger.info("Country process agent processed the country...")
            
            # Will change the workflow stage only if `set_country_tool` tool was not called and country was not set. This means user_input did not contain a country name.
            if ctx.session.state.get("country") == "":
                logger.info(f"Country was not set. Setting workflow stage to ask_country and user_input to empty string.")
                yield Event(
                    invocation_id=ctx.invocation_id,
                    author="capital_guess_workflow_agent",
                    content={"parts": [{"text": "Please choose a country from this list only: france, germany, india, usa, japan."}]},
                    actions=EventActions(
                        state_delta={
                            "workflow_stage": "process_country",
                            "user_input": "",
                            "country": "",
                            "hint": ""
                        }
                    ) # Optional hint for orchestration
                )
                return
            else:
                logger.info(f"Country was set. Setting workflow stage to guess_capital and user_input to empty string.")
                yield Event(
                    invocation_id=ctx.invocation_id,
                    author="capital_guess_workflow_agent",
                    actions=EventActions(
                        state_delta={
                            "workflow_stage": "guess_capital",
                            "hint": ""
                        }
                    ) # Optional hint for orchestration
                )


        # --- Phase 4: Guess Capital ---
        if ctx.session.state.get("workflow_stage") == "guess_capital":
            logger.info(f"Workflow stage: {ctx.session.state.get("workflow_stage")} and hence agent will guess capital")
            async for event in self.sub_agents[2].run_async(ctx):
                yield event
            logger.info("Capital guess agent guessed the capital...")

            # Set the workflow stage to validate_capital
            yield Event(
                invocation_id=ctx.invocation_id,
                author="capital_guess_workflow_agent",
                content={"parts": [{"text": "Do you think my guess is correct?"}]},
                actions=EventActions(
                        state_delta={
                            "workflow_stage": "validate_capital",
                            "hint": ""
                        }
                    ) # Optional hint for orchestration
            )

            # Wait for user input
            logger.info("Waiting for user's input for hint/validation of capital...")
            return  
                

        # --- Fallback ---
        if ctx.session.state.get("workflow_stage") == "completed":
            logger.warning(f"Completed workflow stage. Ending the game.")
            yield Event(
                        invocation_id=ctx.invocation_id,
                        author="capital_guess_workflow_agent",
                        content={"parts": [
                            {"function_call": {"name": "transfer_to_agent", "args": {"agent_name": "game_arcade_agent"}}},
                        ]},
                        actions=EventActions(
                            transfer_to_agent="game_arcade_agent",
                            state_delta={
                                "workflow_stage": "completed",
                                "country": "",
                                "hint": ""
                            }
                        ) # Optional hint for orchestration
                    )
            return


capital_guess_workflow_agent = GameplayAgent(
    name="capital_guess_workflow_agent",
    sub_agents=[country_ask_agent, country_process_agent, capital_guess_agent],
    after_agent_callback=after_agent_cb
)
