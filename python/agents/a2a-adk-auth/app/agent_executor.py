# Copyright 2026 Google LLC
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

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    Part,
    TaskState,
    TextPart,
)
from a2a.utils import new_agent_text_message, new_task
from google.adk.runners import Runner
from google.genai import types

import logging

logger = logging.getLogger(__name__)


class CustomAgentExecutor(AgentExecutor):
    def __init__(
        self,
        runner: Runner
    ):
        self.runner = runner


    def _get_user_id(self, request_context: RequestContext) -> str:
        if (
            request_context.call_context
            and request_context.call_context.user
            and request_context.call_context.user.user_name
        ):
            return request_context.call_context.user.user_name

        return f'A2A_USER_{request_context.context_id}'
    

    async def cancel(
        self,
        request_context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Cancel the execution of a specific task."""
        raise NotImplementedError(
            'Cancellation is not implemented for ADKAgentExecutor.'
        )


    async def execute(
        self,
        request_context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        
        logger.info(f"Call Context: User Name: {request_context.call_context.user.user_name}")
        
        query = request_context.get_user_input()
        task = request_context.current_task or new_task(request_context.message)
        await event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue, task.id, task.context_id)
        user_id = self._get_user_id(request_context)

        try:
            await updater.update_status(
                TaskState.working,
                new_agent_text_message(
                    "Processing Request", task.context_id, task.id
                ),
            )
            
            session = await self.runner.session_service.get_session(
                app_name=self.runner.app_name,
                user_id=user_id,
                session_id=request_context.context_id,
            )

            if session is None:
            # Process with ADK agent
                session = await self.runner.session_service.create_session(
                    app_name=self.runner.app_name,
                    user_id=user_id,
                    state={"user:AUTH_TOKEN": request_context.call_context.state["headers"]["authorization"][len("Bearer "):]},
                    session_id=request_context.context_id,
                )
                logger.info(f"Created Session Id: {session.id}.")
                logger.info(f"App name:   {self.runner.app_name}")
                logger.info(f"User name:  {user_id}")
                logger.info(f"Session Id: {request_context.context_id}")
            else:
                logger.info(f"Custom agent executor: Session Id {session.id} already exists.")

            content = types.Content(
                role="user", parts=[types.Part.from_text(text=query)]
            )

            response_text = ""
            async for event in self.runner.run_async(
                user_id=user_id, session_id=session.id, new_message=content
            ):
                if (
                    event.is_final_response()
                    and event.content
                    and event.content.parts
                ):
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            response_text += part.text + "\n"
                        elif hasattr(part, "function_call"):
                            pass

            # Add response as artifact with custom name
            await updater.add_artifact(
                [Part(root=TextPart(text=response_text))],
                name="Response",
            )

            await updater.complete()

        except Exception as e:
            await updater.update_status(
                TaskState.failed,
                new_agent_text_message(
                    f"Error: {e!s}", task.context_id, task.id
                ),
                final=True,
            )
