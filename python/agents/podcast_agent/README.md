# Podcast Transcript Agent

**The Podcast Transcript Agent is a powerful tool that automates the creation of podcast transcripts from any PDF, Markdown, or Text document.** By leveraging a series of specialized AI agents, it can take a source document and generate a complete, conversational podcast transcript.

## Agent Details

7.  The Podcast Transcript Agent is a sequential agent that orchestrates a series of sub-agents to perform the task of generating a podcast transcript. It takes a user-provided document and guides it through a pipeline of four specialized agents:
8.  
9.  1.  **Podcast Topics Agent**: Extracts the key topics and information from the source document.
10. 2.  **Podcast Episode Planner Agent**: Structures the extracted information into a coherent podcast episode plan.
11. 3.  **Podcast Transcript Writer Agent**: Writes a full conversational script based on the episode plan.
12. 4.  **Podcast Audio Generator Agent**: Converts the generated transcript into an audio file using Gemini TTS.
13. 
14. ## Agent Architecture
15. 
16. The Podcast Transcript Agent operates as a sequential process, where each step is handled by a dedicated sub-agent. The output of one agent becomes the input for the next, ensuring a smooth and logical workflow from topic extraction to the final audio.
17. 
18. ```mermaid
19. graph LR
20.     A[Source Document] --> B(podcast_topics_agent);
21.     B --> C(podcast_episode_planner_agent);
22.     C --> D(podcast_transcript_writer_agent);
23.     D --> E(podcast_audio_generator_agent);
24.     E --> F[Podcast Audio];
25. ```

## Key Features

*   **Automated Content Repurposing**: Transform existing documents (PDFs, text files) into engaging podcast episodes.
*   **Conversational Script Generation**: Creates natural-sounding dialogue between a host and an expert persona.
*   **Structured Episode Planning**: Automatically generates a well-structured episode plan with an introduction, main segments, and a conclusion.
*   **Customizable Personas**: Easily define the names and roles of the podcast host and expert.
*   **Extensible Architecture**: The sequential nature of the agent makes it easy to add new steps or modify existing ones.

## Setup and Installation

### Prerequisites

*   Python 3.13 or higher
*   An active Google Gemini API key or a configured Google Cloud project with Vertex AI enabled.

### 1. Clone the Repository

```bash
git clone https://github.com/google/adk-samples.git
cd adk-samples/python/agents/podcast_transcript_agent
```

### 2. Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

This project uses `uv` to manage dependencies. `uv` is an extremely fast Python package installer and resolver. It provides a more efficient and reliable way to manage your project's dependencies.

To install the dependencies, run the following command:

```bash
uv sync
```

### 4. Configure Environment Variables

Create a `.env` file in the root of the project. You can copy the provided `sample.env` as a starting point:

```bash
cp sample.env .env
```

Edit the `.env` file and add your Google Cloud Project details:

```ini
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
GOOGLE_CLOUD_LOCATION="us-central1"
MODEL_GOOGLE_CLOUD_LOCATION="global"
# Optional overrides
TTS_MODEL_NAME="gemini-2.5-pro-tts"
TTS_LOCATION="us-central1"
```

If you are using Vertex AI, make sure you are authenticated with `gcloud`:

```bash
gcloud auth application-default login
```

## Running the Agent

You can run the agent through the ADK Web interface, which provides a convenient way to interact with the agent during development.

### Prerequisites

Ensure you have your environment variables set, especially for Vertex AI and the TTS model:

```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_GENAI_USE_VERTEXAI=1
# Optional: Override default TTS model or location
# export TTS_MODEL_NAME="gemini-2.5-pro-tts"
# export TTS_LOCATION="us-central1"
```

### Using ADK Web

To start the web interface and API server, run the following command from the root of the project (where `pyproject.toml` is located):

```bash
adk web --port 8000 src
```

This will start the server on port 8000. You can then interact with the agent via the API.

#### 1. Create a Session

First, create a new session for your interaction:

```bash
curl -X POST http://localhost:8000/apps/podcast_agent/users/test_user/sessions \
-H "Content-Type: application/json" \
-d '{}'
```

This will return a session ID (e.g., `9a4993a4...`).

#### 2. Run the Agent (Generate Podcast)

Use the returned session ID to send a prompt to the agent. For example, to generate a podcast about a specific topic:

```bash
curl -X POST http://localhost:8000/run \
-H "Content-Type: application/json" \
-d '{
  "app_name": "podcast_agent",
  "user_id": "test_user",
  "session_id": "YOUR_SESSION_ID_HERE",
  "new_message": {
    "parts": [
      {
        "text": "Topic: Killing Joke band history"
      }
    ],
    "role": "user"
  },
  "streaming": false
}'
```

The agent will process the request, generate the transcript, synthesize the audio, and return the path to the generated `.wav` file in the response.

## Testing

To run the included tests, use `pytest`:

```bash
.venv/bin/pytest
```

## Evaluation

The project includes an evaluation suite leveraging the Vertex AI Rapid Evaluation SDK to measure agent performance across metrics like Groundedness, Fluency, and Coherence.

### Running Evaluations

You can run evaluations in two modes: `fast` (smaller subset) or `detailed` (full dataset).

To run the fast evaluation suite:
```bash
.venv/bin/python evals/run_eval.py --mode fast
```

To run the detailed evaluation suite:
```bash
.venv/bin/python evals/run_eval.py --mode detailed
```

### Metrics Explained
- **Groundedness**: Measures how well the transcript is supported by the source document.
- **Fluency**: Evaluates the grammatical correctness and natural flow of the dialogue.
- **Coherence**: Assesses the logical structure and consistency of the podcast segments.

Evaluation results are logged to the console and also tracked as Experiments in the Vertex AI console in your GCP project.

## Customization

This agent is designed to be easily customizable:

*   **Prompts**: You can modify the prompts for each sub-agent to change the style and tone of the generated podcast.
*   **Personas**: The host and expert personas can be changed by modifying the prompt in the `podcast_transcript_writer_agent`.
*   **Sub-Agents**: You can add new sub-agents to the sequence to perform additional tasks, such as generating show notes or social media posts.

## Troubleshooting

*   **Authentication Errors**: Ensure that your API key or Vertex AI environment variables are correctly set in the `.env` file.
*   **Dependency Issues**: Make sure you have installed all the required dependencies from `requirements.txt` in your virtual environment.
*   **File Not Found**: The example scripts use relative paths. Make sure you are running them from the root of the `podcast_transcript_agent` directory.
