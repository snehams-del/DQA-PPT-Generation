# Podcast Transcript Agent

**The Podcast Transcript Agent is a powerful tool that automates the creation of podcast transcripts and audio from any source document.** By leveraging a series of specialized AI agents and Gemini TTS, it turns documents into engaging, multi-speaker conversational podcasts.

## Agent Details

The Podcast Transcript Agent is a sequential agent that orchestrates a pipeline of four specialized sub-agents:

1.  **Podcast Topics Agent**: Extracts the key topics and information from the source document.
2.  **Podcast Episode Planner Agent**: Structures the extracted information into a coherent podcast episode plan.
3.  **Podcast Transcript Writer Agent**: Writes a full conversational script based on the episode plan, featuring distinct Host and Expert personas.
4.  **Podcast Audio Generator Agent**: Converts the generated transcript into a multi-speaker audio file using Google's Gemini TTS.


## Agent Architecture & Processing Flow

The agent operates sequentially, passing data from one stage to the next to transform raw text into a polished audio production. Each step is handled by a specialized sub-agent:

1.  **Input**: The user provides a source document (PDF or text).
2.  **Topic Extraction**: The `podcast_topics_agent` analyzes the document and extracts key themes and interesting facts.
3.  **Planning**: The `podcast_episode_planner_agent` takes these topics and creates a structured outline for the episode, defining the flow of conversation.
4.  **Scripting**: The `podcast_transcript_writer_agent` writes the actual dialogue based on the plan, assigning lines to a Host ("Charlotte") and an Expert ("Dr. Joe Sponge").
5.  **Audio Generation & Chunking**: The `podcast_audio_generator_agent` processes the transcript. It synthesizes the speech and assembles the parts into a high-fidelity multi-speaker audio file (`.wav`).


### High-Level Architecture

```mermaid
sequenceDiagram
    participant User
    participant Root as Podcast Agent (Sequential)
    participant Topics as Topics Agent
    participant Planner as Episode Planner Agent
    participant Writer as Transcript Writer Agent
    participant Audio as Audio Generator Agent

    User->>Root: Topic / Source Document
    activate Root
    Root->>Topics: Source Content
    activate Topics
    Topics-->>Root: List of Themes/Topics
    deactivate Topics
    
    Root->>Planner: Themes/Topics
    activate Planner
    Planner-->>Root: Episode Outline
    deactivate Planner
    
    Root->>Writer: Episode Outline
    activate Writer
    Writer-->>Root: Conversational Transcript
    deactivate Writer
    
    Root->>Audio: Transcript (Writers lines)
    activate Audio
    Note over Audio: Uses GeminiTtsTool
    Audio-->>Root: Path to .wav
    deactivate Audio
    
    Root-->>User: Final Podcast (.wav)
    deactivate Root
```

## Voice Selection
Note: The agent intentionally alternates between Male and Female voices for the Host and Expert characters. Each time the agent runs, it randomly selects a "Studio" voice from a curated list of high-quality speakers. This ensures that every generated podcast has a unique acoustic profile while maintaining a consistent two-person conversational dynamic.

## Setup and Installation

### Prerequisites

*   Python 3.13 or higher
*   Google Cloud Project with Vertex AI and **Cloud Text-to-Speech API** enabled
*   `uv` for dependency management

### 1. Clone the Repository

```bash
git clone https://github.com/google/adk-samples.git
cd adk-samples/python/agents/podcast_agent
```

### 2. Install Dependencies

Use `uv` to create a virtual environment and install dependencies:

```bash
uv sync
source .venv/bin/activate
```

### 3. Configure Environment Variables

Create a `.env` file in the root of the project. You can use the provided `sample.env` as a template:

```bash
cp sample.env .env
```

Ensure your `.env` includes the following:

```ini
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT="your-google-cloud-project-id"
GOOGLE_CLOUD_LOCATION="us-central1"
MODEL_GOOGLE_CLOUD_LOCATION="global"
PODCAST_TRANSCRIPT_MODEL_NAME="gemini-2.5-flash"
TTS_MODEL_NAME="en-US-Studio-MultiSpeaker"
TTS_LOCATION="us-central1"
```

> [!IMPORTANT]
> The `TTS_MODEL_NAME` must be set to `en-US-Studio-MultiSpeaker` for high-quality multi-speaker support.

Authenticate with Google Cloud:

```bash
gcloud auth application-default login
```

## Running the Agent

You can interact with the agent via the ADK Web interface (browser-based) or the ADK API server (command-line/curl).

### Option 1: Using ADK Web (Browser UI)

1.  **Start the web server**:

    ```bash
    adk web --port 8000 src
    ```

2.  **Open your browser**:
    Navigate to `http://localhost:8000`. You will see the ADK Web interface where you can interact with the Podcast Agent directly.

---

### Option 2: Using ADK API (Command Line)

If you prefer to work with the API directly (e.g., for automation or testing), you can use `adk api_server`.

1.  **Start the API server**:

    ```bash
    adk api_server --port 8000 src
    ```

2.  **Create a Session**:

    ```bash
    curl -X POST http://localhost:8000/apps/podcast_agent/users/test_user/sessions \
    -H "Content-Type: application/json" \
    -d '{}'
    ```

3.  **Generate Podcast**:

    Use the `session_id` returned from the previous step to run the agent:

    ```bash
    curl -X POST http://localhost:8000/run \
    -H "Content-Type: application/json" \
    -d '{
      "app_name": "podcast_agent",
      "user_id": "test_user",
      "session_id": "YOUR_SESSION_ID",
      "new_message": {
        "parts": [{"text": "Topic: [Your Topic Here]"}],
        "role": "user"
      },
      "streaming": false
    }'
    ```

    The response will contain the path to the generated `podcast_output.wav` file.


## Running Tests

Use `pytest` to run the test suite:

```bash
uv run pytest
```

### Key Test Files

*   `tests/test_agents.py`: Verifies the basic logic and configuration of the agents.
*   `tests/test_gemini_tts_tool.py`: Unit tests for audio generation and assembly.
*   `tests/test_music_bio_e2e.py`: Runs a full end-to-end test using a sample music biography. This verifies the entire pipeline from input text to audio generation.

## Evaluation

We use the **Vertex AI Rapid Evaluation SDK** to quantitatively measure the quality of the generated podcasts.

### Approach

The evaluation process focuses on the **textual transcript** generated by the agent.
> [!NOTE]
> The audio output itself is not currently evaluated for quality in this release, only the underlying script.

We use **Pointwise Metrics** evaluated by a "judge" model (Gemini) to score each transcript on specific criteria.

### Metrics

*   **Groundedness**: Does the podcast transcript accurately reflect the information in the source document?
*   **Fluency**: Is the dialogue natural and grammatically correct?
*   **Coherence**: Does the conversation flow logically?

### Data

Evaluation data is stored in `.jsonl` files in the `evals/datasets/` directory. Each line contains a JSON object with a `context` field (the source text).

*   `evals/datasets/detailed.jsonl`: Contains a diverse set of source documents (e.g., technical papers, biographies) to test the agent's robustness across different domains.

### Running Evaluation

The primary script for running evaluations is `evals/run_eval.py`.

**Run a fast evaluation (smaller dataset):**
```bash
uv run python evals/run_eval.py --mode fast
```

**Run a detailed evaluation:**
```bash
uv run python evals/run_eval.py --mode detailed
```

## Troubleshooting

*   **Ratelimit Errors (429 Too Many Requests)**: The agent includes automatic retry logic for transient errors. If you hit persistent quota limits, consider increasing your Cloud TTS API quota.
*   **Audio Quality**: The current version performs high-fidelity audio merging. For more advanced post-processing, ensure your segments aren't ending in mid-sentence.
*   **Authentication Errors**: Verify `GOOGLE_CLOUD_PROJECT` matches your authenticated `gcloud` account and that Application Default Credentials (ADC) are set.
