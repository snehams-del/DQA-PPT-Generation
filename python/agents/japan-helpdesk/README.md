# Japan Helpdesk

An AI-powered helpdesk system designed to help foreigners in Japan navigate legal and administrative procedures. This system uses multiple specialized agents to provide accurate, helpful information while ensuring compliance with legal advice restrictions.

## Overview

The Japan Helpdesk provides general information and guidance on various legal and administrative matters that foreigners commonly encounter in Japan. The system is designed with multiple safety layers to ensure responses are appropriate, accurate, and do not constitute unauthorized practice of law.

## Agent Details

The key features of the Japan Helpdesk include:

| Feature | Description |
| --- | --- |
| **Interaction Type:** | Conversational |
| **Complexity:**  | Advanced |
| **Agent Type:**  | Multi Agent |
| **Components:**  | Tools, AgentTools, Safety Layers |
| **Vertical:**  | Legal/Administrative Guidance |

### Agent Architecture

The Japan Helpdesk uses a multi-agent architecture with the following workflow:

1. **Scope Check Agent (5%)** - Validates that queries are within supported scope and appropriate
2. **RAG Agent (90%)** - Retrieves and synthesizes information from vetted sources
3. **Legal Advice Detector (5%)** - Ensures responses don't constitute unauthorized legal advice

### Component Details

**Agents:**
- `scope_check_agent` - Determines if queries are within supported scope and checks for content safety
- `rag_agent` - Retrieves relevant information using Google Search Grounding and synthesizes responses
- `legal_advice_detector_agent` - Reviews responses to ensure they don't cross into legal advice territory

**Supported Categories:**
- Visa and immigration procedures
- Housing and rental matters
- Tax obligations and procedures  
- Employment regulations
- Healthcare system navigation
- Banking and financial services
- Education system
- Marriage and family registration
- Driving license procedures
- Residence card matters
- Pension and insurance
- Business registration
- General administrative procedures

**Safety Features:**
- Language validation (Japanese/English only)
- Content safety filtering
- Legal advice detection and prevention
- Confidence scoring
- Source citation requirements

## Setup and Installation

### Folder Structure
```
.
├── README.md
├── pyproject.toml
├── japan_helpdesk/
│   ├── shared_libraries/
│   │   └── types.py
│   ├── sub_agents/
│   │   ├── scope_check/
│   │   ├── rag/
│   │   └── legal_advice_detector/
│   ├── agent.py
│   └── prompt.py
├── tests/
│   └── test_agents.py
├── eval/
│   └── test_eval.py
└── deployment/
    └── deploy.py
```

### Prerequisites

- Python 3.11+
- Google Cloud Project (for Vertex AI integration)
- Google Agent Development Kit 1.0+
- Poetry: Install Poetry by following the instructions on the official Poetry [website](https://python-poetry.org/docs/)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/google/adk-samples.git
   cd adk-samples/python/agents/japan-helpdesk
   ```

2. Install dependencies using Poetry:

   ```bash
   poetry install
   ```

3. Set up Google Cloud credentials:

   Create a `.env` file with the following environment variables:
   ```
   # Choose Model Backend: 0 -> ML Dev, 1 -> Vertex
   GOOGLE_GENAI_USE_VERTEXAI=1
   
   # Vertex backend config
   GOOGLE_CLOUD_PROJECT=__YOUR_CLOUD_PROJECT_ID__
   GOOGLE_CLOUD_LOCATION=us-central1
   
   # GCS Storage Bucket name - for Agent Engine deployment
   GOOGLE_CLOUD_STORAGE_BUCKET=YOUR_BUCKET_NAME_HERE
   ```

4. Authenticate your GCloud account:
   ```bash
   gcloud auth application-default login
   ```

5. Activate the virtual environment:
   ```bash
   eval $(poetry env activate)
   ```

## Running the Agent

### Using `adk`

You can interact with the agent using the CLI:

```bash
# Under the japan-helpdesk directory:
adk run japan_helpdesk
```

or via the web interface:
```bash
# Under the japan-helpdesk directory:
adk web
```

This will start a local web server. Select "japan_helpdesk" in the drop-down menu to access the chatbot interface.

### Sample Queries to Try

**In-Scope Queries:**
- "How do I renew my tourist visa in Japan?"
- "What documents do I need for apartment rental?"
- "Do I need to file a tax return as a foreign worker?"
- "How do I register my marriage in Japan?"
- "What is the process for getting a Japanese driver's license?"

**Japanese Queries:**
- "ビザの更新について教えてください"
- "住民票の取得方法を知りたいです"
- "税金の申告について相談したいです"

### Programmatic Access

Start a development API server:
```bash
adk api_server japan_helpdesk
```

This starts a FastAPI server at http://127.0.0.1:8000 with API docs at http://127.0.0.1:8000/docs

## Running Tests

To run the tests:

```bash
poetry install --with dev
pytest
```

Run specific test suites:

```bash
# Unit tests
pytest tests/

# Evaluation tests  
pytest eval/
```

### Test Coverage

The test suite includes:
- Agent initialization tests
- Scope checking functionality
- Legal advice detection
- Phone number validation for Japanese government offices
- Language support validation
- End-to-end evaluation scenarios

## Key Features

### Multi-Language Support
- Accepts queries in Japanese and English
- Provides useful Japanese phrases for common procedures
- Politely redirects non-Japanese/English queries

### Safety Layers
- **Scope Validation**: Ensures queries are within supported legal/administrative topics
- **Content Safety**: Filters out requests for illegal or unethical activities  
- **Legal Advice Prevention**: Detects and prevents unauthorized practice of law
- **Confidence Scoring**: Provides transparency about information reliability

### Structured Responses
All responses include:
- Clear summary of the issue and guidance
- Important disclaimers and limitations
- Concrete next steps
- Contact information for relevant government offices
- Useful Japanese phrases
- Confidence level indicators
- Source citations

### Phone Number Validation
The system includes validation for Japanese government office phone numbers, supporting common formats:
- Tokyo area: 03-1234-5678
- Osaka area: 06-1234-5678
- Toll-free: 0120-123-456

## Limitations and Disclaimers

**Important:** This system provides general information only and does not constitute legal advice. Users should:

- Verify all information with official sources
- Consult qualified professionals for specific situations
- Understand that procedures may vary by location and circumstances
- Be aware that information may become outdated

**Out of Scope:**
- Specific legal advice requiring a licensed attorney
- Personal medical advice
- Investment or financial advice beyond basic banking
- Assistance with illegal or unethical activities
- Queries in languages other than Japanese or English

## Customization

### Adding New Categories
To add support for new legal/administrative categories:

1. Update `SUPPORTED_CATEGORIES` in `shared_libraries/types.py`
2. Add relevant phrases to `USEFUL_PHRASES`
3. Update agent prompts to include the new category
4. Add test cases for the new category

### Integrating External Knowledge Sources
The RAG agent can be enhanced with:
- Custom document retrieval systems
- Integration with official government APIs
- Specialized legal databases (with appropriate licensing)

### Enhancing Safety Layers
Additional safety measures can be implemented:
- Rate limiting and abuse prevention
- Adversarial input detection
- Enhanced prompt injection filtering
- Audit logging for flagged inputs

## Deployment

To deploy the agent to Vertex AI Agent Engine:

```bash
poetry install --with deployment
python deployment/deploy.py --create
```

## Contributing

When contributing to this project:

1. Ensure all tests pass
2. Add tests for new functionality
3. Update documentation as needed
4. Follow the existing code style and structure
5. Consider the legal and ethical implications of changes

## Disclaimer

This agent sample is provided for illustrative purposes only and is not intended for production use without proper legal review and compliance validation. Users are solely responsible for ensuring compliance with applicable laws and regulations in their jurisdiction.
