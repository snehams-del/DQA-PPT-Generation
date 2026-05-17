#!/usr/bin/env python3
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Standalone Universal Deployment Script for Vertex AI Agents and Gemini Enterprise.

This script manages the lifecycle of agents on Vertex AI (Reasoning Engine) and
integrates them with Gemini Enterprise (Discovery Engine Agent Space).

Usage:
    python deploy_agent.py [command] --config config.json

Commands:
    deploy-agent            Deploy a new agent or update an existing one.
    delete-agent            Delete an existing agent.
    test-agent              Interactive chat with the deployed agent.
    build                   Build the agent artifacts (wheels).
    create-datastore        Create a Discovery Engine Data Store.
    list-datastores         List Discovery Engine Data Stores.
    create-app              Create a Discovery Engine Application.
    update-app              Update a Discovery Engine Application.
    delete-app              Delete a Discovery Engine Application.
    list-apps               List Discovery Engine Applications.
    link-agent              Link a Vertex AI Agent to an App.
    unlink-agent            Unlink an agent from an App.
    list-linked-agents      List agents linked to an App.
    rename-linked-agent     Rename a linked agent.
"""

import argparse
import asyncio
import importlib
import json
import logging
import os
import subprocess
import sys
from typing import Any, Dict, Optional

import google.auth
import google.auth.transport.requests
import requests
import vertexai
from dotenv import dotenv_values, load_dotenv
from google.adk.sessions import VertexAiSessionService
from google.api_core import exceptions as google_exceptions
from google.cloud import storage
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("deploy_agent")


def setup_staging_bucket(project_id: str, location: str, bucket_name: str) -> str:
    """
    Checks if the staging bucket exists, creates it if not.
    Returns the full bucket path (gs://<bucket_name>).
    """
    storage_client = storage.Client(project=project_id)
    try:
        bucket = storage_client.lookup_bucket(bucket_name)
        if bucket:
            logger.info(f"Staging bucket gs://{bucket_name} already exists.")
        else:
            logger.info(f"Staging bucket gs://{bucket_name} not found. Creating...")
            new_bucket = storage_client.create_bucket(
                bucket_name, project=project_id, location=location
            )
            logger.info(
                f"Successfully created staging bucket gs://{new_bucket.name} in {location}."
            )

            # Enable uniform bucket-level access
            new_bucket.iam_configuration.uniform_bucket_level_access_enabled = True
            new_bucket.patch()
            logger.info(
                f"Enabled uniform bucket-level access for gs://{new_bucket.name}."
            )

    except google_exceptions.Forbidden as e:
        logger.error(
            f"Permission denied for bucket gs://{bucket_name}. Ensure Service Account has 'Storage Admin'. Error: {e}"
        )
        raise
    except google_exceptions.Conflict as e:
        logger.warning(
            f"Bucket gs://{bucket_name} likely exists but owned by another project. Error: {e}"
        )
    except Exception as e:
        logger.error(f"Failed to access/create bucket gs://{bucket_name}. Error: {e}")
        raise

    return f"gs://{bucket_name}"


def init_vertex_ai(config: Dict[str, Any]) -> None:
    project_id = config["project_id"]
    location = config["reasoning_engine_location"]
    bucket_name = config.get("bucket")

    staging_bucket_uri = None
    if bucket_name:
        staging_bucket_uri = setup_staging_bucket(project_id, location, bucket_name)

    logger.info(
        f"Initializing Vertex AI with project={project_id}, location={location}, staging_bucket={staging_bucket_uri}"
    )
    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=staging_bucket_uri,
    )


def load_config(config_path: str) -> Dict[str, Any]:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file: {e}")

    # Required fields
    required_fields = [
        "project_id",
        "reasoning_engine_location",
        "agent_path",
        "reasoning_engine_agent_name",
        "reasoning_engine_agent_sa",
    ]

    missing = [f for f in required_fields if f not in config]
    if missing:
        raise ValueError(f"Missing required config fields: {', '.join(missing)}")

    return config


def run_command(
    command: list[str], cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None
) -> None:
    """Runs a shell command and raises an error if it fails."""
    logger.info(f"Running command: {' '.join(command)}")
    try:
        subprocess.run(
            command,
            cwd=cwd,
            env=env,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.stderr}")
        raise RuntimeError(f"Command failed: {' '.join(command)}\nError: {e.stderr}")


def build_agent(agent_path: str) -> None:
    """
    Builds the agent package into a wheel using 'build'.

    If you use a different build tool (like poetry, uv, flit), modify this function
    to call your specific build command.
    """
    logger.info("Building agent artifacts...")

    # Build agent
    if os.path.exists(agent_path):
        logger.info(f"Building {agent_path}...")
        # We use 'python -m build' as a standard way to build wheels.
        # Ensure 'build' is installed: pip install build
        try:
            run_command(
                [sys.executable, "-m", "build", "--wheel", agent_path, "--no-isolation"]
            )
        except RuntimeError as e:
            logger.error(
                "Build failed. Ensure 'build' is installed (pip install build) or modify this function to use your preferred build tool."
            )
            raise e
    else:
        raise FileNotFoundError(f"Agent path not found: {agent_path}")

    logger.info("Build complete.")


def get_git_commit_hash() -> str:
    """Gets the current git commit hash."""
    try:
        commit_hash_bytes = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.STDOUT
        )
        return commit_hash_bytes.decode("utf-8").strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def prepare_agent_deployment(
    config: Dict[str, Any],
) -> tuple[AdkApp, Dict[str, str], str]:
    """Prepares agent for deployment: loads code, env vars, and finds wheel."""
    agent_path = config["agent_path"]
    agent_module_name = config.get("agent_module", agent_path)

    # Ensure agent_path is in sys.path so we can import the module
    abs_agent_path = os.path.abspath(agent_path)
    if abs_agent_path not in sys.path:
        sys.path.insert(0, abs_agent_path)

    # Load the agent
    try:
        agent_module = importlib.import_module(f"{agent_module_name}.agent")
        root_agent = getattr(agent_module, "root_agent")
    except (ImportError, AttributeError) as e:
        raise ValueError(
            f"Could not load 'root_agent' from {agent_module_name}.agent: {e}\nEnsure agent_path points to the directory containing your python package."
        )

    adk_app = AdkApp(
        agent=root_agent,
        # session_service_builder=session_builder # inject prefered session service builder
    )

    # Prepare environment variables
    env_vars = {}
    # Load from .env if exists
    env_path = os.path.join(agent_path, ".env")
    if os.path.exists(env_path):
        env_vars.update(dotenv_values(env_path))

    # recomended to track deployed versions
    env_vars["GIT_COMMIT_HASH"] = get_git_commit_hash()

    # Filter out system env vars that shouldn't be deployed
    env_vars = {
        k: v for k, v in env_vars.items() if v and not k.startswith("GOOGLE_CLOUD_")
    }

    # Path to the built wheel
    dist_dir = os.path.join(agent_path, "dist")
    if not os.path.exists(dist_dir):
        raise FileNotFoundError(
            f"Dist directory not found: {dist_dir}. Did you build the agent?"
        )

    wheels = [f for f in os.listdir(dist_dir) if f.endswith(".whl")]
    if not wheels:
        raise FileNotFoundError(f"No wheels found in {dist_dir}")

    agent_wheel = os.path.join(dist_dir, wheels[0])
    logger.info(f"Using agent wheel: {agent_wheel}")

    return adk_app, env_vars, agent_wheel


def update_config_file(config_path: str, updates: Dict[str, Any]) -> None:
    """Updates the config file with new values."""
    try:
        with open(config_path, "r") as f:
            config = json.load(f)

        config.update(updates)

        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        logger.info(f"Updated config file {config_path} with {updates}")
    except Exception as e:
        logger.error(f"Failed to update config file: {e}")


#
# Interactions with Reasoning Engine
#
def create_agent(config: Dict[str, Any], config_path: str) -> None:
    """Creates a new agent in Vertex AI."""
    agent_name = config["reasoning_engine_agent_name"]
    agent_sa = config["reasoning_engine_agent_sa"]

    logger.info(f"Creating agent '{agent_name}'...")
    adk_app, env_vars, agent_wheel = prepare_agent_deployment(config)

    try:
        remote_agent = agent_engines.create(
            adk_app,
            display_name=agent_name,
            requirements=[agent_wheel],
            extra_packages=[agent_wheel],
            env_vars=env_vars,
            service_account=agent_sa,
        )

        logger.info(f"Successfully created agent: {remote_agent.resource_name}")
        logger.info(f"Agent Resource ID: {remote_agent.resource_name}")

        # Update config with new ID
        update_config_file(
            config_path, {"reasoning_engine_id": remote_agent.resource_name}
        )

    except Exception as e:
        logger.error(e)
        raise e


def update_agent(config: Dict[str, Any]) -> None:
    """Updates an existing agent in Vertex AI."""
    resource_id = config.get("reasoning_engine_id")
    if not resource_id:
        raise ValueError("reasoning_engine_id is required for update-agent")

    agent_name = config["reasoning_engine_agent_name"]
    agent_sa = config["reasoning_engine_agent_sa"]

    logger.info(f"Updating agent {resource_id}...")
    adk_app, env_vars, agent_wheel = prepare_agent_deployment(config)

    remote_agent = agent_engines.update(
        resource_id,
        agent_engine=adk_app,
        display_name=agent_name,
        requirements=[agent_wheel],
        extra_packages=[agent_wheel],
        env_vars=env_vars,
        service_account=agent_sa,
    )

    logger.info(f"Successfully updated agent: {remote_agent.resource_name}")


def deploy_agent(config: Dict[str, Any], args: argparse.Namespace) -> None:
    """Deploys (Create or Update) the agent."""
    init_vertex_ai(config)

    # Check if we have a resource ID to update
    resource_id = config.get("reasoning_engine_id")

    if resource_id:
        try:
            update_agent(config)
        except google_exceptions.NotFound:
            logger.warning(f"Agent {resource_id} not found. Creating new one...")
            create_agent(config, args.config)
        except Exception as e:
            logger.error(f"Update failed: {e}")
            raise
    else:
        create_agent(config, args.config)


def delete_agent(config: Dict[str, Any]) -> None:
    init_vertex_ai(config)
    resource_id = config.get("reasoning_engine_id")
    if not resource_id:
        raise ValueError("reasoning_engine_id is required for delete-agent")

    logger.info(f"Deleting agent {resource_id}...")
    try:
        remote_agent = agent_engines.get(resource_id)
        remote_agent.delete(force=True)
        logger.info(f"Successfully deleted agent: {resource_id}")
    except google_exceptions.NotFound:
        logger.warning(f"Agent {resource_id} not found.")
    except Exception as e:
        logger.error(f"Delete failed: {e}")
        raise


#
# Interactions with Gemini Enterpise
#


def get_access_token() -> str:
    """Gets a valid access token for Google Cloud API."""
    creds, _ = google.auth.default()
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    return creds.token


def get_discovery_engine_base_url(
    location: str, project_id: str, version: str = "v1"
) -> str:
    """Constructs the base URL for Discovery Engine API."""
    return f"https://{location}-discoveryengine.googleapis.com/{version}/projects/{project_id}/locations/{location}/collections/default_collection"


def get_discovery_engine_client(
    config: Dict[str, Any], version: str = "v1", use_project_number: bool = False
) -> tuple[str, Dict[str, str]]:
    """Returns the base URL and headers for Discovery Engine API calls."""
    project_id = config["project_id"]
    location = config.get("agent_space_location", "global")

    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": project_id,
    }

    url_project_id = project_id
    if use_project_number:
        url_project_id = config.get("project_number")
        if not url_project_id:
            raise ValueError("project_number is required for this operation")

    base_url = get_discovery_engine_base_url(location, url_project_id, version)
    return base_url, headers


def list_datastores(config: Dict[str, Any]) -> None:
    """Lists Discovery Engine Data Stores."""
    base_url, headers = get_discovery_engine_client(config)
    url = f"{base_url}/dataStores"

    logger.info("Listing Data Stores...")
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            datastores = resp.json().get("dataStores", [])
            if not datastores:
                logger.info("No Data Stores found.")
            else:
                logger.info(f"Found {len(datastores)} Data Stores:")
                for ds in datastores:
                    logger.info(
                        f"- {ds.get('name')} (Display Name: {ds.get('displayName')})"
                    )
        else:
            logger.error(f"Failed to list Data Stores: {resp.status_code} {resp.text}")
            raise RuntimeError(f"Failed to list Data Stores: {resp.text}")
    except Exception as e:
        logger.error(f"Error listing Data Stores: {e}")
        raise e


def create_datastore(config: Dict[str, Any], config_path: str) -> None:
    """Creates a Discovery Engine Data Store."""
    datastore_id = config.get("datastore_id")

    if not datastore_id:
        raise ValueError("datastore_id is required for create-datastore")

    base_url, headers = get_discovery_engine_client(config)
    url = f"{base_url}/dataStores?dataStoreId={datastore_id}"

    payload = {
        "displayName": datastore_id,
        "industryVertical": "GENERIC",
        "solutionTypes": ["SOLUTION_TYPE_SEARCH"],
        "contentConfig": "CONTENT_REQUIRED",
    }

    logger.info(f"Creating Data Store {datastore_id}...")
    try:
        resp = requests.post(url, headers=headers, json=payload)
        if resp.status_code == 409:
            logger.info(f"Data Store {datastore_id} already exists.")
            update_config_file(config_path, {"datastore_id": datastore_id})
        elif resp.status_code == 200:
            logger.info(f"Data Store {datastore_id} creation initiated.")
            update_config_file(config_path, {"datastore_id": datastore_id})
        else:
            logger.error(f"Failed to create Data Store: {resp.status_code} {resp.text}")
            raise RuntimeError(f"Failed to create Data Store: {resp.text}")
    except Exception as e:
        logger.error(f"Error creating Data Store: {e}")
        raise e


def create_app(config: Dict[str, Any]) -> None:
    """Creates a Vertex AI Application (Discovery Engine Engine)."""
    project_number = config.get("project_number")
    app_id = config.get("agent_space_app")
    datastore_id = config.get("datastore_id")

    if not all([project_number, app_id, datastore_id]):
        raise ValueError(
            "project_number, agent_space_app, and datastore_id are required for create-app"
        )

    base_url, headers = get_discovery_engine_client(
        config, version="v1alpha", use_project_number=True
    )
    url = f"{base_url}/engines?engineId={app_id}"

    payload = {
        "displayName": app_id,
        "dataStoreIds": [datastore_id],
        "solutionType": "SOLUTION_TYPE_SEARCH",
        "searchEngineConfig": {
            "searchTier": "SEARCH_TIER_ENTERPRISE",
            "searchAddOns": ["SEARCH_ADD_ON_LLM"],
        },
        "industryVertical": "GENERIC",
        "appType": "APP_TYPE_INTRANET",
    }

    logger.info(f"Creating App {app_id}...")
    try:
        resp = requests.post(url, headers=headers, json=payload)
        if resp.status_code == 409:
            logger.info(f"App {app_id} already exists.")
        elif resp.status_code == 200:
            logger.info(f"App {app_id} creation initiated.")
            logger.info(f"App Operation: {resp.json().get('name')}")
        else:
            logger.error(f"Failed to create App: {resp.status_code} {resp.text}")
            raise RuntimeError(f"Failed to create App: {resp.text}")
    except Exception as e:
        logger.error(f"Error creating App: {e}")
        raise e


def update_app(config: Dict[str, Any]) -> None:
    """Updates a Vertex AI Application."""
    project_number = config.get("project_number")
    app_id = config.get("agent_space_app")
    datastore_id = config.get("datastore_id")

    if not all([project_number, app_id, datastore_id]):
        raise ValueError(
            "project_number, agent_space_app, and datastore_id are required for update-app"
        )

    base_url, headers = get_discovery_engine_client(
        config, version="v1alpha", use_project_number=True
    )
    url = f"{base_url}/engines/{app_id}"

    payload = {
        "displayName": app_id,
        "dataStoreIds": [datastore_id],
        "solutionType": "SOLUTION_TYPE_SEARCH",
        "searchEngineConfig": {
            "searchTier": "SEARCH_TIER_ENTERPRISE",
            "searchAddOns": ["SEARCH_ADD_ON_LLM"],
        },
        "industryVertical": "GENERIC",
        "appType": "APP_TYPE_INTRANET",
    }

    logger.info(f"Updating App {app_id}...")
    try:
        resp = requests.patch(url, headers=headers, json=payload)
        if resp.status_code == 200:
            logger.info(f"App {app_id} update initiated.")
            logger.info(f"App Operation: {resp.json().get('name')}")
        else:
            logger.error(f"Failed to update App: {resp.status_code} {resp.text}")
            raise RuntimeError(f"Failed to update App: {resp.text}")
    except Exception as e:
        logger.error(f"Error updating App: {e}")
        raise e


def delete_app(config: Dict[str, Any]) -> None:
    """Deletes a Vertex AI Application."""
    project_number = config.get("project_number")
    app_id = config.get("agent_space_app")

    if not all([project_number, app_id]):
        raise ValueError(
            "project_number and agent_space_app are required for delete-app"
        )

    base_url, headers = get_discovery_engine_client(
        config, version="v1alpha", use_project_number=True
    )
    url = f"{base_url}/engines/{app_id}"

    logger.info(f"Deleting App {app_id}...")
    try:
        resp = requests.delete(url, headers=headers)
        if resp.status_code == 200:
            logger.info(f"App {app_id} deletion initiated.")
            logger.info(f"App Operation: {resp.json().get('name')}")
        else:
            logger.error(f"Failed to delete App: {resp.status_code} {resp.text}")
            raise RuntimeError(f"Failed to delete App: {resp.text}")
    except Exception as e:
        logger.error(f"Error deleting App: {e}")
        raise e


def list_apps(config: Dict[str, Any]) -> None:
    """Lists Vertex AI Applications."""
    project_number = config.get("project_number")

    if not project_number:
        raise ValueError("project_number is required for list-apps")

    base_url, headers = get_discovery_engine_client(
        config, version="v1alpha", use_project_number=True
    )
    url = f"{base_url}/engines"

    logger.info("Listing Apps...")
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            apps = resp.json().get("engines", [])
            if not apps:
                logger.info("No Apps found.")
            else:
                logger.info(f"Found {len(apps)} Apps:")
                for app in apps:
                    logger.info(
                        f"- {app.get('name')} (Display Name: {app.get('displayName')})"
                    )
        else:
            logger.error(f"Failed to list Apps: {resp.status_code} {resp.text}")
            raise RuntimeError(f"Failed to list Apps: {resp.text}")
    except Exception as e:
        logger.error(f"Error listing Apps: {e}")
        raise e


def test_agent(config: Dict[str, Any]) -> None:
    """Interactive chat with the agent."""
    init_vertex_ai(config)
    resource_id = config.get("reasoning_engine_id")
    project_id = config["project_id"]
    location = config["reasoning_engine_location"]

    if not resource_id:
        raise ValueError("reasoning_engine_id is required for test-agent")

    logger.info(f"Connecting to agent {resource_id}...")

    try:
        session_service = VertexAiSessionService(project_id, location)
        user_id = "test-user"  # Or make it configurable

        # Create session
        session = asyncio.run(
            session_service.create_session(app_name=resource_id, user_id=user_id)
        )

        remote_agent = agent_engines.get(resource_id)
        logger.info(f"Connected to agent: {resource_id}")
        logger.info(f"Session ID: {session.id}")
        logger.info("Type 'quit' or 'exit' to stop.")

        while True:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit"]:
                break

            try:
                # Stream query like in test.py
                for event in remote_agent.stream_query(
                    user_id=user_id, session_id=session.id, message=user_input
                ):
                    if "content" in event:
                        if "parts" in event["content"]:
                            parts = event["content"]["parts"]
                            for part in parts:
                                if "text" in part:
                                    logger.info(f"Agent: {part['text']}")
            except Exception as e:
                logger.error(f"Query failed: {e}")

        # Cleanup session
        asyncio.run(
            session_service.delete_session(
                app_name=resource_id, user_id=user_id, session_id=session.id
            )
        )
        logger.info("Session deleted.")

    except google_exceptions.NotFound:
        logger.error(f"Agent {resource_id} not found.")
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


def link_agent(config: Dict[str, Any]) -> None:
    """Links a Vertex AI Agent to a Discovery Engine App."""
    project_id = config["project_id"]
    project_number = config.get("project_number")
    app_id = config.get("agent_space_app")
    agent_name = config["reasoning_engine_agent_name"]
    agent_description = config.get(
        "agent_space_agent_description", f"Agent {agent_name}"
    )
    reasoning_engine_id = config.get("reasoning_engine_id")
    reasoning_engine_location = config["reasoning_engine_location"]

    if not all([project_number, app_id, reasoning_engine_id]):
        raise ValueError(
            "project_number, agent_space_app, and reasoning_engine_id are required for link-agent"
        )

    base_url, headers = get_discovery_engine_client(
        config, version="v1alpha", use_project_number=True
    )
    url = f"{base_url}/engines/{app_id}/assistants/default_assistant/agents"

    if reasoning_engine_id.startswith("projects/"):
        reasoning_engine_resource = reasoning_engine_id
    else:
        reasoning_engine_resource = f"projects/{project_id}/locations/{reasoning_engine_location}/reasoningEngines/{reasoning_engine_id}"

    payload = {
        "displayName": agent_name,
        "description": agent_description,
        "icon": {
            "uri": "https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/corporate_fare/default/24px.svg"
        },
        "adk_agent_definition": {
            "tool_settings": {
                "toolDescription": agent_description,
            },
            "provisioned_reasoning_engine": {
                "reasoningEngine": reasoning_engine_resource
            },
        },
    }

    logger.info(f"Linking Agent {agent_name} to App {app_id}...")
    try:
        resp = requests.post(url, headers=headers, json=payload)
        if resp.status_code == 200:
            logger.info(f"Agent {agent_name} linking initiated.")
            logger.info(f"Link Operation: {resp.json().get('name')}")
        else:
            logger.error(f"Failed to link Agent: {resp.status_code} {resp.text}")
            raise RuntimeError(f"Failed to link Agent: {resp.text}")
    except Exception as e:
        logger.error(f"Error linking Agent: {e}")
        raise e


def unlink_agent(config: Dict[str, Any]) -> None:
    """Unlinks an agent from Discovery Engine App."""
    project_number = config.get("project_number")
    app_id = config.get("agent_space_app")
    agent_id = config.get("agent_space_agent_id")

    if not all([project_number, app_id, agent_id]):
        raise ValueError(
            "project_number, agent_space_app, and agent_space_agent_id are required for unlink-agent"
        )

    base_url, headers = get_discovery_engine_client(
        config, version="v1alpha", use_project_number=True
    )
    url = f"{base_url}/engines/{app_id}/assistants/default_assistant/agents/{agent_id}"

    logger.info(f"Unlinking Agent {agent_id} from App {app_id}...")
    try:
        resp = requests.delete(url, headers=headers)
        if resp.status_code == 200:
            logger.info(f"Agent {agent_id} unlinking initiated.")
            logger.info(f"Unlink Operation: {resp.json().get('name')}")
        else:
            logger.error(f"Failed to unlink Agent: {resp.status_code} {resp.text}")
            raise RuntimeError(f"Failed to unlink Agent: {resp.text}")
    except Exception as e:
        logger.error(f"Error unlinking Agent: {e}")
        raise e


def list_linked_agents(config: Dict[str, Any]) -> None:
    """Lists agents linked to Discovery Engine App."""
    project_number = config.get("project_number")
    app_id = config.get("agent_space_app")

    if not all([project_number, app_id]):
        raise ValueError(
            "project_number and agent_space_app are required for list-linked-agents"
        )

    base_url, headers = get_discovery_engine_client(
        config, version="v1alpha", use_project_number=True
    )
    url = f"{base_url}/engines/{app_id}/assistants/default_assistant/agents"

    logger.info(f"Listing Linked Agents for App {app_id}...")
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            agents = resp.json().get("agents", [])
            if not agents:
                logger.info("No Linked Agents found.")
            else:
                logger.info(f"Found {len(agents)} Linked Agents:")
                for agent in agents:
                    logger.info(
                        f"- {agent.get('name')} (Display Name: {agent.get('displayName')})"
                    )
        else:
            logger.error(
                f"Failed to list Linked Agents: {resp.status_code} {resp.text}"
            )
            raise RuntimeError(f"Failed to list Linked Agents: {resp.text}")
    except Exception as e:
        logger.error(f"Error listing Linked Agents: {e}")
        raise e


def rename_linked_agent(config: Dict[str, Any]) -> None:
    """Renames a linked agent."""
    project_number = config.get("project_number")
    app_id = config.get("agent_space_app")
    agent_id = config.get("agent_space_agent_id")
    new_name = config["reasoning_engine_agent_name"]

    if not all([project_number, app_id, agent_id]):
        raise ValueError(
            "project_number, agent_space_app, and agent_space_agent_id are required for rename-linked-agent"
        )

    base_url, headers = get_discovery_engine_client(
        config, version="v1alpha", use_project_number=True
    )
    url = f"{base_url}/engines/{app_id}/assistants/default_assistant/agents/{agent_id}?updateMask=displayName"

    payload = {"displayName": new_name}

    logger.info(f"Renaming Linked Agent {agent_id} to {new_name}...")
    try:
        resp = requests.patch(url, headers=headers, json=payload)
        if resp.status_code == 200:
            logger.info(f"Agent {agent_id} rename initiated.")
            logger.info(f"Rename Operation: {resp.json().get('name')}")
        else:
            logger.error(
                f"Failed to rename Linked Agent: {resp.status_code} {resp.text}"
            )
            raise RuntimeError(f"Failed to rename Linked Agent: {resp.text}")
    except Exception as e:
        logger.error(f"Error renaming Linked Agent: {e}")
        raise e


def main():
    parser = argparse.ArgumentParser(description="Deploy and manage Vertex AI Agents.")
    parser.add_argument(
        "command",
        choices=[
            "deploy-agent",
            "delete-agent",
            "test-agent",
            "create-datastore",
            "list-datastores",
            "create-app",
            "update-app",
            "delete-app",
            "list-apps",
            "link-agent",
            "unlink-agent",
            "list-linked-agents",
            "rename-linked-agent",
            "build",
        ],
        help="Command to execute",
    )
    parser.add_argument(
        "--config", required=True, help="Path to the configuration JSON file"
    )

    args = parser.parse_args()
    config = load_config(args.config)

    # Load environment variables
    load_dotenv()

    try:
        if args.command == "deploy-agent":
            build_agent(config["agent_path"])  # Always build before deploy
            deploy_agent(config, args)
        elif args.command == "delete-agent":
            delete_agent(config)
        elif args.command == "test-agent":
            test_agent(config)
        elif args.command == "build":
            build_agent(config["agent_path"])
        elif args.command == "create-app":
            create_app(config)
        elif args.command == "update-app":
            update_app(config)
        elif args.command == "delete-app":
            delete_app(config)
        elif args.command == "list-apps":
            list_apps(config)
        elif args.command == "create-datastore":
            create_datastore(config, args.config)
        elif args.command == "list-datastores":
            list_datastores(config)
        elif args.command == "link-agent":
            link_agent(config)
        elif args.command == "unlink-agent":
            unlink_agent(config)
        elif args.command == "list-linked-agents":
            list_linked_agents(config)
        elif args.command == "rename-linked-agent":
            rename_linked_agent(config)

    except Exception as e:
        logger.error(f"Operation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
