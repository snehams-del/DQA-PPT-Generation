
import os
import sys
import unittest
import asyncio

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from podcast_agent.agent import podcast_agent as PodcastAgent
from podcast_agent.sub_agents.podcast_audio_generator.agent import gemini_tts_tool
from google.adk.runners import InMemoryRunner
from google.genai import types

# Set credentials for REAL execution if available
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "ag-llm-test-proj")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
os.environ["GOOGLE_CLOUD_LOCATION"] = LOCATION
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "1"

class TestMusicBioPodcastReal(unittest.TestCase):
    def test_voice_randomization_check(self):
        """Checks the voice randomization (just config check, no API)."""
        print("\n--- Checking Voice Randomization ---")
        host = gemini_tts_tool.speaker_voice_map.get("Host")
        expert = gemini_tts_tool.speaker_voice_map.get("Expert")
        print(f"Host: {host}")
        print(f"Expert: {expert}")
        self.assertNotEqual(host, expert)

    def test_end_to_end_real(self):
        """
        Runs the full PodcastAgent end-to-end against real Gemini APIs.
        Requires GOOGLE_CLOUD_PROJECT or valid ADC.
        """
        print("\n--- Starting REAL End-to-End Test: Killing Joke History ---")
        
        artifact_path = os.path.join(os.path.dirname(__file__), "test_artifacts", "killing_joke.txt")
        if not os.path.exists(artifact_path):
            self.fail(f"Test artifact not found: {artifact_path}")
            
        with open(artifact_path, 'r') as f:
            artifact_content = f.read()[:2000] # Limit content for speed/cost if large

        combined_input = f"The History Of Killing Joke\n\nHere is the source material:\n{artifact_content}"

        print(f"Artifact Size: {len(artifact_content)} chars")

        try:
            runner = InMemoryRunner(agent=PodcastAgent)
            
            # Create session (async)
            asyncio.run(runner.session_service.create_session(
                app_name=runner.app_name,
                user_id="real_user", 
                session_id="real_session_1"
            ))
            
            # Create the message content
            text_part = types.Part(text=combined_input)
            content = types.Content(parts=[text_part], role="user")
            
            print("Running agent with InMemoryRunner (Real APIs)...")
            events = runner.run(
                user_id="real_user",
                session_id="real_session_1",
                new_message=content
            )
            
            final_response = ""
            for event in events:
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            print(f"[{event.author}] {part.text}")
                            final_response += part.text
            
            print(f"\nFinal Result: {final_response}")
            
            if ".wav" in final_response:
                print("SUCCESS: Audio file path detected in response.")
            else:
                self.fail("Audio file path NOT found in response.")

        except Exception as e:
            print(f"Real execution failed: {e}")
            self.fail(f"Execution failed: {e}")

if __name__ == "__main__":
    unittest.main()
