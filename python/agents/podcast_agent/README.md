# Podcast Transcript Agent

**The Podcast Transcript Agent is a powerful tool that automates the creation of podcast transcripts and audio from any source document.** By leveraging a series of specialized AI agents and Gemini TTS, it turns documents into engaging, multi-speaker conversational podcasts.

## Agent Details

The Podcast Transcript Agent is a sequential agent that orchestrates a pipeline of four specialized sub-agents:

1.  **Podcast Topics Agent**: Extracts the key topics and information from the source document.
2.  **Podcast Episode Planner Agent**: Structures the extracted information into a coherent podcast episode plan.
3.  **Podcast Transcript Writer Agent**: Writes a full conversational script based on the episode plan, featuring distinct Host and Expert personas.
4.  **Podcast Audio Generator Agent**: Converts the generated transcript into a multi-speaker audio file using Google's Gemini TTS.

## Agent Architecture

The agent operates sequentially, passing data from one stage to the next to transform raw text into a polished audio production. Each step is handled by a specialized sub-agent:

1.  **Input**: The user provides a source document (PDF or text).
2.  **Topic Extraction**: The `podcast_topics_agent` analyzes the document and extracts key themes and interesting facts.
3.  **Planning**: The `podcast_episode_planner_agent` takes these topics and creates a structured outline for the episode, defining the flow of conversation.
4.  **Scripting**: The `podcast_transcript_writer_agent` writes the actual dialogue based on the plan, assigning lines to a Host ("Charlotte") and an Expert ("Dr. Joe Sponge").
5.  **Audio Generation**: Finally, the `podcast_audio_generator_agent` uses Gemini TTS to convert the text transcript into a multi-speaker audio file (`.wav`).

```mermaid
graph LR
    A[Source Document] --> B(podcast_topics_agent);
    B --> C(podcast_episode_planner_agent);
    C --> D(podcast_transcript_writer_agent);
    D --> E(podcast_audio_generator_agent);
    E --> F[Podcast Audio (.wav)];
```

## Setup and Installation

### Prerequisites

*   Python 3.13 or higher
*   Google Cloud Project with Vertex AI enabled
*   `uv` for dependency management

### 1. Clone the Repository

```bash
git clone https://github.com/google/adk-samples.git
cd adk-samples/python/agents/podcast_transcript_agent
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
TTS_MODEL_NAME="gemini-2.5-pro-tts"
TTS_LOCATION="us-central1"
```

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

## Testing vs Evaluation

It's important to distinguish between **Testing** and **Evaluation** in this project:

*   **Testing** ensures the code is functionally correct. It verifies that the agents run without errors, tools are called correctly, and files are generated as expected.
*   **Evaluation** measures the *quality* of the AI model's output. It assesses how well the generated transcript reflects the source material (Groundedness), how natural it sounds (Fluency), and how logically it flows (Coherence).

## Testing

The project includes both unit tests and end-to-end (E2E) tests to verify functional correctness.

### Running Tests

Use `pytest` to run the test suite:

```bash
.venv/bin/pytest
```

### Key Test Files

*   `tests/test_agents.py`: Verifies the basic logic and configuration of the agents.
*   `tests/test_music_bio_e2e.py`: Runs a full end-to-end test using a sample music biography. This is a crucial test to verify the entire pipeline from input text to audio generation.

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
.venv/bin/python evals/run_eval.py --mode fast
```

**Run a detailed evaluation:**
```bash
.venv/bin/python evals/run_eval.py --mode detailed
```

## Troubleshooting

*   **400 Bad Request (TTS)**: This often happens if the transcript chunks don't have enough turns for multi-speaker synthesis. The agent should handle this automatically.
*   **502 Bad Gateway**: Can occur if TTS chunks are too large. The tool is configured to chunk text conservatively to avoid this.
*   **Authentication Errors**: Verify `GOOGLE_CLOUD_PROJECT` matches your authenticated `gcloud` account.
