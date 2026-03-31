"""An Earth Engine enabled agent."""

import logging
import os

import ee
import google
from google.adk.agents import llm_agent
import vertexai

from . import prompts
from . import tools

_vertex_initialized = False
_ee_initialized = False
_PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT')
_REGION = os.environ.get('GOOGLE_CLOUD_LOCATION')


def _initialize_earth_engine():
  """Initializes the Earth Engine client if not already done."""
  global _ee_initialized
  if _ee_initialized:
    return

  try:
    if not _PROJECT_ID:
      raise ValueError('GOOGLE_CLOUD_PROJECT environment variable not set.')

    scopes = [
        'https://www.googleapis.com/auth/earthengine',
        'https://www.googleapis.com/auth/cloud-platform',
    ]
    # Get Application Default Credentials
    credentials, _ = google.auth.default(scopes=scopes)

    ee.Initialize(
        credentials,
        project=_PROJECT_ID,
        opt_url='https://earthengine-highvolume.googleapis.com',
    )
    logging.info(
        'Earth Engine initialized successfully for project: %s', _PROJECT_ID
    )

    _ee_initialized = True
    logging.info('Earth Engine initialized successfully.')
  except Exception as e:
    logging.exception('Failed to initialize Earth Engine: %s', e)
    raise


def _initialize_vertex_ai():
  """Initializes the Vertex AI client if not already done."""
  global _vertex_initialized
  if _vertex_initialized:
    return
  try:
    logging.info(
        'Initializing Vertex AI for project: %s in location: %s',
        _PROJECT_ID,
        _REGION,
    )
    vertexai.init(project=_PROJECT_ID, location=_REGION)
    _vertex_initialized = True
    logging.info('Vertex AI initialized successfully.')
  except Exception as e:
    logging.exception('Failed to initialize Vertex AI: %s', e)
    raise


def root_agent() -> llm_agent.Agent:
  # Initialize Earth Engine and Vertex when the agent is being created.
  _initialize_earth_engine()
  _initialize_vertex_ai()

  return llm_agent.Agent(
      name='ee_agent',
      model='gemini-2.5-pro',
      description='Agent to answer geo questions using Google Earth Engine.',
      tools=[
          tools.get_2017_2025_annual_changes,
      ],
      instruction=prompts.root_agent_prompt,
  )

root_agent = root_agent()
History
References
Warnings
