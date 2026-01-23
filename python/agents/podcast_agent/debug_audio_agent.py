
import asyncio
import json
from google.adk.runners import InMemoryRunner
from google.genai import types
from podcast_agent.sub_agents.podcast_audio_generator.agent import podcast_audio_generator_agent

async def main():
    runner = InMemoryRunner(agent=podcast_audio_generator_agent)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="debug_user"
    )

    # Mock transcript
    transcript = {
        "segments": [
            {
                "speaker_dialogues": [
                    {"speaker_id": "Host", "text": "Hello and welcome to the show."},
                    {"speaker_id": "Expert", "text": "Thanks for having me."}
                ]
            }
        ]
    }
    transcript_text = json.dumps(transcript)

    content = types.Content(parts=[types.Part(text=transcript_text)])

    print("Running audio generator agent...")
    async for event in runner.run_async(
        session_id=session.id,
        user_id=session.user_id,
        new_message=content
    ):
        print(f"Event: {event.author} ({event.type})")
        if event.content:
            print(f"Content: {event.content.parts[0].text if event.content.parts else 'No Text'}")

if __name__ == "__main__":
    asyncio.run(main())
