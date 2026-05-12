"""Deployment script for Game Developer Architect agent."""

import logging
import os

import vertexai
from absl import app, flags
from dotenv import load_dotenv
from google.cloud import storage
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

from game_dev_assistant.agent import root_agent

FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP project ID.")
flags.DEFINE_string("location", None, "GCP location.")
flags.DEFINE_string("bucket", None, "GCS bucket for staging (without gs://).")
flags.DEFINE_bool("create", True, "Create/Deploy the agent.")
flags.DEFINE_bool("delete", False, "Delete the agent.")

# The .whl file generated for your project
AGENT_WHL_FILE = "game_dev_assistant-0.1.0-py3-none-any.whl"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_staging_bucket(project_id, location, bucket_name):
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.lookup_bucket(bucket_name)
    if not bucket:
        bucket = storage_client.create_bucket(bucket_name, location=location)
        logger.info(f"Created bucket gs://{bucket_name}")
    return f"gs://{bucket_name}"

def create_agent(env_vars):
    """Deploys the agent using AdkApp wrapper."""
    adk_app = AdkApp(agent=root_agent, enable_tracing=True)

    if not os.path.exists(AGENT_WHL_FILE):
        raise FileNotFoundError(f"Missing wheel file: {AGENT_WHL_FILE}. Build it using 'uv build' or 'poetry build'.")

    remote_agent = agent_engines.create(
        adk_app,
        requirements=[AGENT_WHL_FILE],
        extra_packages=[AGENT_WHL_FILE],
        env_vars=env_vars,
    )
    print(f"🚀 Agent Deployed: {remote_agent.resource_name}")

def main(argv):
    load_dotenv()
    project_id = FLAGS.project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
    location = FLAGS.location or os.getenv("GOOGLE_CLOUD_LOCATION")
    bucket_name = FLAGS.bucket or f"{project_id}-adk-staging"

    # Map required environment variables from your .env
    env_vars = {
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN"),
        "GOOGLE_GENAI_USE_VERTEXAI": os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "True"),
    }

    staging_uri = setup_staging_bucket(project_id, location, bucket_name)
    vertexai.init(project=project_id, location=location, staging_bucket=staging_uri)

    if FLAGS.create:
        create_agent(env_vars)

if __name__ == "__main__":
    app.run(main)
