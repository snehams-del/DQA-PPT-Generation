# Podcast Transcript Agent

**The Podcast Transcript Agent is a powerful tool that automates the creation of podcast transcripts and audio from any source document.** By leveraging a series of specialized AI agents and Gemini TTS, it turns documents into engaging, multi-speaker conversational podcasts.

## Agent Details

The Podcast Transcript Agent is a sequential agent that orchestrates a pipeline of four specialized sub-agents:

1.  **Podcast Topics Agent**: Extracts the key topics and information from the source document.
2.  **Podcast Episode Planner Agent**: Structures the extracted information into a coherent podcast episode plan.
3.  **Podcast Transcript Writer Agent**: Writes a full conversational script based on the episode plan, featuring distinct Host and Expert personas.
4.  **Podcast Audio Generator Agent**: Converts the generated transcript into a multi-speaker audio file using Google's Gemini TTS.

## Agent Architecture

The agent operates sequentially, passing data from one stage to the next to transform raw text into a polished audio production.

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
GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
GOOGLE_CLOUD_LOCATION="us-central1"

# Optional: TTS Configuration
TTS_MODEL_NAME="gemini-2.5-pro-tts"
TTS_LOCATION="us-central1"
```

Authenticate with Google Cloud:

```bash
gcloud auth application-default login
```

## Running the Agent

You can interact with the agent via the ADK Web interface or the API server.

### Using ADK Web

Start the web server:

```bash
adk web --port 8000 src
```

The server will start at `http://localhost:8000`.

#### 1. Create a Session

```bash
curl -X POST http://localhost:8000/apps/podcast_agent/users/test_user/sessions \
-H "Content-Type: application/json" \
-d '{}'
```

#### 2. Generate Podcast

Use the returned session ID to run the agent:

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

## Testing

Run the included tests using `pytest`:

```bash
.venv/bin/pytest
```

## Evaluation

The project includes an evaluation suite using Vertex AI Rapid Evaluation SDK to measure Groundedness, Fluency, and Coherence.

Run fast evaluation:
```bash
.venv/bin/python evals/run_eval.py --mode fast
```

Run detailed evaluation:
```bash
.venv/bin/python evals/run_eval.py --mode detailed
```

## Troubleshooting

*   **400 Bad Request (TTS)**: This often happens if the transcript chunks don't have enough turns for multi-speaker synthesis. The agent should handle this automatically.
*   **502 Bad Gateway**: Can occur if TTS chunks are too large. The tool is configured to chunk text conservatively to avoid this.
*   **Authentication Errors**: Verify `GOOGLE_CLOUD_PROJECT` matches your authenticated `gcloud` account.
