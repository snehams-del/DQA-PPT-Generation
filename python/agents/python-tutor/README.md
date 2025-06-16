# Software Bug Assistant - ADK Python Sample Agent

## Overview

The **Python Tutor** agent is...

TODO - add Google cloud arch diagram 


This sample agent is designed to showcase ADK's State and Memory concepts and features for folks new to agent development.

TODO - add blog post / video links

This README contains instructions for local and Google Cloud deployment. 

## Agent Details

The key features of the Python Tutor agent are:

| Feature              | Description                     |
| -------------------- | ------------------------------- |
| **Interaction Type** | Conversational                  |
| **Complexity**       | Beginner                        |
| **Agent Type**       | Single Agent                    |
| **Components**       | State, Memory                   |
| **Vertical**         | Education, Software Engineering |

## Agent Architecture

TODO - add SVG 

## Key Features

TODO 


## 💻 Run Locally 

### Prerequisites 

- Python 3.9+
- [uv](https://docs.astral.sh/uv/getting-started/installation) (to manage dependencies)
- Git (for cloning the repository, see [Installation Instructions](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git))
- Google Cloud CLI ([Installation Instructions](https://cloud.google.com/sdk/docs/install))


### Steps

1. Clone the repository:

```bash
git clone https://github.com/google/adk-samples.git
cd adk-samples/python/agents/python-tutor
```

2. Configure Gemini API Key: 

Get an API Key from Google AI Studio: https://aistudio.google.com/apikey

3. Set environment variables:

```sh
export "GOOGLE_API_KEY=<your_api_key_here>"
export "GOOGLE_GENAI_USE_VERTEXAI=FALSE" 
```

4. Run via ADK web: 

```sh
cd python-tutor

uv run adk web
```



## ☁️ Deploy to Google Cloud 

**TODO- show deployment to Cloud Run** 