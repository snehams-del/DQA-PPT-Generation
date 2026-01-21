import os
import argparse
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd
import dotenv
dotenv.load_dotenv()

from google.adk.runners import InMemoryRunner
from google.genai import types
from podcast_transcript_agent.agent import podcast_transcript_agent
from podcast_transcript_agent.config import PODCAST_MODEL_GOOGLE_CLOUD_LOCATION, GOOGLE_CLOUD_LOCATION as EVAL_LOCATION, PODCAST_TRANSCRIPT_MODEL_NAME
from evals.eval_utils import init_vertex_eval, get_pointwise_metrics
from vertexai.preview.evaluation import EvalTask

print(f"DEBUG: Config PODCAST_TRANSCRIPT_MODEL_NAME={PODCAST_TRANSCRIPT_MODEL_NAME}")
print(f"DEBUG: Config PODCAST_MODEL_GOOGLE_CLOUD_LOCATION={PODCAST_MODEL_GOOGLE_CLOUD_LOCATION}")
print(f"DEBUG: Config EVAL_LOCATION={EVAL_LOCATION}")
# Inspect agent model if possible
try:
    from podcast_transcript_agent.sub_agents.podcast_transcript_writer.agent import podcast_transcript_writer_agent
    print(f"DEBUG: Agent podcast_transcript_writer_agent.model={getattr(podcast_transcript_writer_agent, 'model', 'cloud-not-found')}")
except ImportError:
    print("DEBUG: Could not import podcast_transcript_writer_agent directly")

async def run_agent(source_text: str) -> str:
    """Runs the podcast agent on the source text and returns the transcript."""
    # Temporarily switch to Model Location for Agent
    original_loc = os.environ.get("GOOGLE_CLOUD_LOCATION")
    os.environ["GOOGLE_CLOUD_LOCATION"] = PODCAST_MODEL_GOOGLE_CLOUD_LOCATION
    
    transcript_text = ""
    try:
        runner = InMemoryRunner(agent=podcast_transcript_agent)
        session = await runner.session_service.create_session(
            app_name=runner.app_name, user_id="eval_user"
        )

        content = types.Content(
            parts=[
                types.Part(
                    text=(
                        "Generate podcast from this document. Podcast host name is"
                        " Charlotte, expert's name is Dr Joe Sponge"
                    )
                ),
                types.Part(
                    inline_data=types.Blob(
                        mime_type="text/plain", data=source_text.encode("utf-8")
                    )
                ),
            ]
        )

        
        # Run the agent
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content,
        ):
            if event.is_final_response() and event.author == "podcast_transcript_writer_agent":
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            try:
                                data = json.loads(part.text)
                                # Convert structured transcript to linear text for evaluation
                                if "segments" in data:
                                    for segment in data["segments"]:
                                        for dial in segment.get("speaker_dialogues", []):
                                            transcript_text += f"{dial['speaker_id']}: {dial['text']}\n"
                            except json.JSONDecodeError:
                                print("Warning: Could not decode JSON from agent response")
                                transcript_text += part.text # Fallback
    finally:
        # Restore Eval Location
        if original_loc:
            os.environ["GOOGLE_CLOUD_LOCATION"] = original_loc
        else:
            del os.environ["GOOGLE_CLOUD_LOCATION"]

    return transcript_text

async def main():
    parser = argparse.ArgumentParser(description="Run Podcast Agent Evaluation")
    parser.add_argument("--mode", choices=["fast", "detailed"], default="fast", help="Evaluation mode")
    args = parser.parse_args()

    # Init Vertex AI
    init_vertex_eval()

    # Load Dataset
    dataset_path = Path(f"evals/datasets/{args.mode}.jsonl")
    if not dataset_path.exists():
        print(f"Error: Dataset {dataset_path} not found.")
        return

    eval_data = []
    print(f"Loading dataset from {dataset_path}...")
    with open(dataset_path, "r") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                eval_data.append(item)

    print(f"Running evaluation on {len(eval_data)} examples...")
    
    # Run Agent and Collect Results
    results = []
    for item in eval_data:
        context = item["context"]
        print("Running agent on item...")
        response = await run_agent(context)
        if not response:
             print("Warning: Empty response from agent.")
             response = "No transcript generated."
        
        results.append({
            "context": context,
            "response": response,
            # "instruction" is sometimes required by Faithfulness but context/response usually sufficient for RAG style
        })

    # Evaluate using Vertex AI
    metrics = get_pointwise_metrics()
    
    print("Starting Vertex AI Evaluation...")
    # Re-init to ensure correct location for Eval Service
    from podcast_transcript_agent.config import GOOGLE_CLOUD_LOCATION
    print(f"Re-initializing Vertex AI for Eval in {GOOGLE_CLOUD_LOCATION}...")
    init_vertex_eval()
    
    eval_task = EvalTask(
        dataset=pd.DataFrame(results),
        metrics=metrics,
        experiment=f"podcast-eval-{args.mode}"
    )
    
    eval_result = eval_task.evaluate()
    
    print("\n--- Evaluation Results ---")
    print(eval_result.summary_metrics)

if __name__ == "__main__":
    asyncio.run(main())
