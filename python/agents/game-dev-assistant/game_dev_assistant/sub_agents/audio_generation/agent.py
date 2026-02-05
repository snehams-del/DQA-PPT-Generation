import os
import sys

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from google.genai import types

from .prompt import instruction

# Load environment variables from the parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


# Try relative import for ADK execution, fallback to absolute for script execution
try:
    from .audio import generate_audio_agent
    from .sound import generate_music as generate_audio_func
except ImportError:
    from audio import generate_audio_agent
    from sound import generate_music as generate_audio_func


async def generate_music_tool(tool_context: ToolContext, prompt: str) -> str:
    """Generates music based on the prompt."""
    try:
        generate_audio_func(prompt, "output.wav")
    except Exception as e:
        return f"An error occurred during music generation: {e}"

    filename = "output.wav"
    if not os.path.exists(filename):
        return "Music generation failed, the output file was not created."

    with open(filename, "rb") as f:
        audio_bytes = f.read()

    artifact_part = types.Part(
        inline_data=types.Blob(data=audio_bytes, mime_type="audio/wav")
    )

    if tool_context:
        await tool_context.save_artifact(filename=filename, artifact=artifact_part)
        return f"Music generated. Download '{filename}' from the Artifacts tab."

    return f"Music generated locally as {filename} (No ADK context found)."


async def generate_sfx_tool(tool_context: ToolContext, prompt: str) -> str:
    """Generates SFX and makes it downloadable."""
    generate_audio_agent(prompt)

    filename = "generated_sfx.wav"
    with open(filename, "rb") as f:
        audio_bytes = f.read()

    artifact_part = types.Part(
        inline_data=types.Blob(data=audio_bytes, mime_type="audio/wav")
    )

    if tool_context:
        await tool_context.save_artifact(filename=filename, artifact=artifact_part)
        return f"SFX generated. Download '{filename}' from the Artifacts tab."

    return f"SFX generated locally as {filename}."

model_name = os.getenv("MODAL_AUDIO_GEN", "gemini-2.5-pro")

audio_agent = Agent(
    name="audio_expert_agent",
    model=model_name,
    description="Agent to generate audio based on user requirements.",
    instruction=instruction,
    tools=[generate_music_tool, generate_sfx_tool],
)

root_agent = audio_agent

if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
    else:
        prompt = "a light and happy ukulele song"

    generate_music_tool(prompt)
