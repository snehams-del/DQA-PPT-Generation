# Python Tutor Agent - Deploy and Monitor on Cloud Run

A Python programming tutor agent built with Google's Agent Development Kit (ADK) that helps users learn Python programming concepts through interactive conversations. This agent is designed to provide personalized coding assistance, explanations, and educational support for Python learners at all levels.

## Features

- **Interactive Python Tutoring**: Provides comprehensive Python programming guidance and explanations
- **Educational Focus**: Specialized in teaching Python concepts, syntax, and best practices
- **Real-time Assistance**: Offers instant feedback and help with Python code
- **ADK Integration**: Built using Google's Agent Development Kit with Gemini 2.0 Flash model
- **Stateful Conversations**: Maintains context across tutoring sessions for personalized learning
- **Cloud-Native**: Designed for scalable deployment on Google Cloud Run
- **Simple Tool Integration**: Includes utility tools like current date retrieval

## Deploy Agent to Cloud Run

### Prerequisites

- Python 3.9+
- [uv](https://docs.astral.sh/uv/getting-started/installation) (for dependency management)
- Google Cloud CLI ([Installation Instructions](https://cloud.google.com/sdk/docs/install))
- Google Cloud project with billing enabled

### Environment Setup

Set up your environment variables:

```bash
# Set your Google Cloud Project ID
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"

# Set your desired Google Cloud Location
export GOOGLE_CLOUD_LOCATION="us-central1"

# Configure Gemini API access
export GOOGLE_GENAI_USE_VERTEXAI="True"  # Use Vertex AI
# OR
export GOOGLE_API_KEY="your-api-key"     # Use AI Studio API key
export GOOGLE_GENAI_USE_VERTEXAI="False"
```

### Method 1: Deploy with ADK CLI (Recommended)

The simplest way to deploy your Python tutor agent:

```bash
# Navigate to the project root
cd python-tutor

# Deploy using ADK CLI
adk deploy cloud_run \
    --project=$GOOGLE_CLOUD_PROJECT \
    --region=$GOOGLE_CLOUD_LOCATION \
    --service_name=python-tutor-agent \
    --app_name=python-tutor \
    --with_ui \
    python-tutor/
```

### Method 2: Deploy with gcloud CLI

For more control over the deployment configuration:

#### Create Deployment Files

First, create the necessary deployment files in the project root:

**server.py**

```python
import os
import uvicorn
from google.adk.cli.fast_api import get_fast_api_app
from pathlib import Path

# Get the directory where server.py is located
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Configure session service (optional)
SESSION_DB_URL = "sqlite:///./sessions.db"  # For local storage
# For production, consider using PostgreSQL:
# SESSION_DB_URL = "postgresql://user:pass@host:port/dbname"

# Configure CORS for web interface
ALLOWED_ORIGINS = ["*"]  # Adjust for production

# Create FastAPI app with ADK
app = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_service_uri=SESSION_DB_URL,
    allow_origins=ALLOWED_ORIGINS,
    web=True,  # Enable web UI
)

if __name__ == "__main__":
    # Use PORT environment variable for Cloud Run compatibility
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

**requirements.txt**

```
google-adk==1.2.1
uvicorn
```

**Dockerfile**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user for security
RUN adduser --disabled-password --gecos "" pythonuser && \
    chown -R pythonuser:pythonuser /app

# Copy application code
COPY . .

# Switch to non-root user
USER pythonuser
ENV PATH="/home/pythonuser/.local/bin:$PATH"

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "server.py"]
```

#### Deploy to Cloud Run

```bash
gcloud run deploy python-tutor-agent \
    --source . \
    --port 8080 \
    --project $GOOGLE_CLOUD_PROJECT \
    --region $GOOGLE_CLOUD_LOCATION \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI=$GOOGLE_GENAI_USE_VERTEXAI" \
    --min-instances 0 \
    --max-instances 10 \
    --concurrency 10 \
    --memory 1Gi \
    --cpu 1
```

## Configure for Production

Deploy with optimized settings for production workloads:

```bash
gcloud run deploy python-tutor-agent \
    --source . \
    --port 8080 \
    --project $GOOGLE_CLOUD_PROJECT \
    --region $GOOGLE_CLOUD_LOCATION \
    --allow-unauthenticated \
    --concurrency 20 \
    --memory 2Gi \
    --cpu 2 \
    --min-instances 1 \
    --max-instances 50 \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI=$GOOGLE_GENAI_USE_VERTEXAI"
```

## Deploy with Traffic Control

Deploy a new revision without traffic for testing:

```bash
gcloud run deploy python-tutor-agent \
    --source . \
    --port 8080 \
    --project $GOOGLE_CLOUD_PROJECT \
    --region $GOOGLE_CLOUD_LOCATION \
    --allow-unauthenticated \
    --no-traffic
```

Then gradually shift traffic via the Cloud Console or:

```bash
gcloud run services update-traffic python-tutor-agent \
    --to-revisions=REVISION-NAME=50 \
    --region=$GOOGLE_CLOUD_LOCATION
```

## Local Development

Run the agent locally for development:

```bash
# Install dependencies
uv sync

# Run locally with ADK web interface
uv run adk web --port 8080

# Or run the server directly
uv run python server.py
```

The agent will be available at `http://localhost:8080`

## Agent Capabilities

The Python tutor agent provides educational assistance for:

1. **Python Fundamentals**: Variables, data types, operators, control structures
2. **Functions and Modules**: Function definition, parameters, scope, imports
3. **Data Structures**: Lists, dictionaries, sets, tuples
4. **Object-Oriented Programming**: Classes, inheritance, encapsulation
5. **Error Handling**: Try/except blocks, debugging techniques
6. **File Operations**: Reading/writing files, working with paths
7. **Libraries and Frameworks**: Popular Python libraries and their usage
8. **Best Practices**: Code style, documentation, testing

### Available Tools

- **get_current_date**: Retrieves the current date for date-related programming examples

## Testing Your Deployment

### Web Interface Testing

If deployed with `--with_ui` flag:

- Navigate to your Cloud Run service URL
- Select "python_tutor" from the agent dropdown
- Start a conversation about Python programming

### API Testing

```bash
# Set your service URL
export APP_URL="YOUR_CLOUD_RUN_SERVICE_URL"

# Get identity token (if authentication required)
export TOKEN=$(gcloud auth print-identity-token)

# Test the agent
curl -X POST -H "Authorization: Bearer $TOKEN" \
    $APP_URL/run_sse \
    -H "Content-Type: application/json" \
    -d '{
    "app_name": "python_tutor",
    "user_id": "test_user",
    "session_id": "test_session",
    "new_message": {
        "role": "user",
        "parts": [{"text": "Explain Python variables"}]
    },
    "streaming": false
    }'
```

## Monitoring and Observability

### Cloud Logging

Monitor agent interactions:

```bash
# View logs
gcloud logs read "resource.type=cloud_run_revision" \
    --project=$GOOGLE_CLOUD_PROJECT \
    --filter="resource.labels.service_name=python-tutor-agent"
```

### Cloud Monitoring

Set up alerts for:

- High error rates
- Increased latency
- Resource utilization
- Request volume

### Performance Metrics

Key metrics to monitor:

- Response time for Python questions
- Tool execution time
- Session duration
- User engagement patterns

## Architecture

- **Stateless Core**: Agent logic runs stateless for easy scaling
- **Session Management**: User conversations maintained via ADK session service
- **Containerized**: Docker-based deployment for consistency
- **Auto-scaling**: Cloud Run handles traffic spikes automatically
- **Observable**: Integrated logging and monitoring
- **Secure**: Non-root container execution

## Advanced Configuration

### Database Session Service

For production, use PostgreSQL for session persistence:

```bash
# Create Cloud SQL instance
gcloud sql instances create python-tutor-db \
    --database-version=POSTGRES_14 \
    --cpu=1 \
    --memory=3840MB \
    --region=$GOOGLE_CLOUD_LOCATION

# Update deployment with database connection
gcloud run deploy python-tutor-agent \
    --add-cloudsql-instances=$GOOGLE_CLOUD_PROJECT:$GOOGLE_CLOUD_LOCATION:python-tutor-db \
    --set-env-vars="SESSION_SERVICE_URI=postgresql://user:pass@/dbname?host=/cloudsql/$GOOGLE_CLOUD_PROJECT:$GOOGLE_CLOUD_LOCATION:python-tutor-db" \
    # ... other flags
```

### Security Best Practices

- Use IAM for authentication in production
- Store API keys in Secret Manager
- Enable VPC connectors for private resources
- Implement rate limiting
- Use HTTPS only

## Troubleshooting

### Common Issues

1. **Agent not responding**: Check Cloud Run logs for errors
2. **Tool execution failures**: Verify environment variables
3. **Session persistence issues**: Check database connectivity
4. **Memory/CPU limits**: Adjust Cloud Run resource allocation

### Debug Commands

```bash
# Check service status
gcloud run services describe python-tutor-agent \
    --region=$GOOGLE_CLOUD_LOCATION

# View recent logs
gcloud logs tail "resource.type=cloud_run_revision" \
    --filter="resource.labels.service_name=python-tutor-agent"

# Test local deployment
docker run -p 8080:8080 -e PORT=8080 gcr.io/$GOOGLE_CLOUD_PROJECT/python-tutor-agent
```

This deployment guide provides a complete pathway to getting your Python tutor agent running on Google Cloud Run with monitoring and production-ready configurations.
