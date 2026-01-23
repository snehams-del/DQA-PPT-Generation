
import asyncio
import json
import logging
import uuid
import sys
from google.genai import types
from podcast_transcript_agent.agent import podcast_transcript_agent
from tools.gemini_tts_tool import GeminiTtsTool
from podcast_transcript_agent.config import TTS_MODEL_NAME, TTS_LOCATION

from google.adk.runners import InMemoryRunner

class PodcastAgent:
    def __init__(self):
        self.transcript_agent = podcast_transcript_agent
        self.runner = InMemoryRunner(agent=self.transcript_agent)
        self.tts_tool = GeminiTtsTool(model_name=TTS_MODEL_NAME, location=TTS_LOCATION)

    async def _generate_transcript(self, topic: str, input_files: list[str] = None):
        # Create a session for the runner
        session = await self.runner.session_service.create_session(
            app_name=self.runner.app_name, user_id="podcast_user"
        )
        
        parts = [types.Part(text=f"Create a podcast about: {topic}")]
        
        if input_files:
            import mimetypes
            from pathlib import Path
            for file_path in input_files:
                path_obj = Path(file_path)
                if not path_obj.exists():
                    print(f"Warning: File not found: {file_path}")
                    continue
                    
                mime_type, _ = mimetypes.guess_type(file_path)
                if not mime_type:
                    mime_type = "application/pdf" # Default to PDF if unknown, or maybe text/plain?
                
                print(f"Loading file: {file_path} ({mime_type})")
                file_bytes = path_obj.read_bytes()
                parts.append(types.Part(
                    inline_data=types.Blob(
                        mime_type=mime_type,
                        data=file_bytes
                    )
                ))

        content = types.Content(parts=parts)
        
        transcript_data = None
        
        # Call the agent via the runner
        async for event in self.runner.run_async(
            session_id=session.id,
            user_id=session.user_id,
            new_message=content,
        ):
            # Check for final output from the writer
            if event.is_final_response() and event.author == "podcast_transcript_writer_agent":
                 if event.content and event.content.parts:
                     for part in event.content.parts:
                         if part.text:
                             try:
                                 # Clean code blocks if present
                                 text = part.text
                                 if text.startswith("```json"):
                                     text = text.replace("```json", "").replace("```", "")
                                 elif text.startswith("```"):
                                     text = text.replace("```", "")
                                     
                                 transcript_data = json.loads(text)
                             except json.JSONDecodeError:
                                 pass
        
        return transcript_data

    def run(self, topic: str, input_files: list[str] = None) -> str:
        print(f"Generating transcript for: {topic}...")
        if input_files:
            print(f"Including {len(input_files)} input files.")

        try:
            transcript_dict = asyncio.run(self._generate_transcript(topic, input_files))
        except Exception as e:
            return f"Transcript generation failed with error: {e}"
        
        if not transcript_dict:
            return "Failed to generate transcript (no valid JSON returned)."
            
        print("Transcript generated. Generating audio...")
        
        try:
            segments = transcript_dict.get("segments", [])
            import os
            output_file = "podcast_output.wav"
            output_path = self.tts_tool.generate_audio(segments, output_file)
            abs_path = os.path.abspath(output_path)
            return f"Podcast about '{topic}' is ready! Listen here: {abs_path}"
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"Podcast transcript generated, but audio creation failed. Error: {e}"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate a podcast from a topic and optional files.")
    parser.add_argument("topic", nargs="?", default="Coffee history", help="The topic of the podcast")
    parser.add_argument("--file", action="append", dest="files", help="Path to input file (PDF, TXT, etc.)")
    
    args = parser.parse_args()
    print(PodcastAgent().run(args.topic, input_files=args.files))
