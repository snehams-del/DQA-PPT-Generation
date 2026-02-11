"""
This script launches a Google Dataflow Flex Template using the Dataflow REST API.

It is designed to be fully encapsulated, with all configuration and launch
logic contained within the `DataflowFlexTemplateLauncher` class.
"""

import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

import google.auth
import requests
from google.auth.transport.requests import AuthorizedSession

# --- Configure Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)


class DataflowFlexTemplateLauncher:
    """
    Handles all aspects of launching and monitoring a Dataflow Flex Template.

    This class encapsulates authentication, all job configuration,
    payload building, job name generation, API requests, and error handling.
    """

    API_BASE_URL = "https://dataflow.googleapis.com/v1b3"

    def __init__(
        self,
        delete_source_data: bool,
        bigquery_dataset: str,
    ):
        """
        Initializes the launcher with project and template metadata.

        All job-specific parameters and environment settings are hardcoded
        within this class.

        Args:
            project_id: The Google Cloud project ID.
            location: The region for the Dataflow job (e.g., "us-central1").
            template_gcs_path: The GCS path to the Flex Template spec.
            job_name_prefix: The prefix for the unique job name (e.g., "my-job").
        """
        self.project_id = os.environ["PROJECT_ID"].strip('"').strip("'")
        self.location = os.environ["LOCATION"].strip('"').strip("'")
        self.template_gcs_path = os.environ["TEMPLATE_GCS_PATH"]
        self.archive_storage_bucket = os.environ["ARCHIVE_BUCKET_ASSET_NAME"]
        self.staging_bucket = os.environ["DATAFLOW_TEMP_BUCKET"]
        self.service_account = os.environ["DATAFLOW_SERVICE_ACCOUNT"]
        self.network = os.environ["NETWORK"]
        self.sub_network = os.environ["SUB_NETWORK"]
        self.job_name_prefix = os.environ["JOB_NAME_PREFIX"]
        self.bigquery_dataset = bigquery_dataset
        self.delete_source_data = str(delete_source_data)

        self.api_endpoint = (
            f"{self.API_BASE_URL}/projects/{self.project_id}/locations/"
            f"{self.location}/flexTemplates:launch"
        )

        # --- Job Configuration ---
        # Template-specific parameters are now defined inside the class
        self.parameters: Dict[str, str] = {
            "sourceBigQueryDataset": self.bigquery_dataset,
            "destinationStorageBucketAssetName": self.archive_storage_bucket,
            "maxParallelBigQueryMetadataRequests": "5",
            "fileFormat": "PARQUET",
            "fileCompression": "SNAPPY",
            "writeDisposition": "OVERWRITE",
            "enforceSamePartitionKey": "true",
            "deleteSourceData": "true",
            "updateDataplexMetadata": "false",
            "stagingLocation": f"gs://{self.staging_bucket}/stage",
            "autoscalingAlgorithm": "NONE",
            "serviceAccount": self.service_account,
        }

        # Dataflow environment settings are also defined inside the class
        self.environment: Optional[Dict[str, Any]] = {
            "numWorkers": 2,
            "tempLocation": f"gs://{self.staging_bucket}/temp",
            "subnetwork": self.sub_network,
            "network": self.network,
            "ipConfiguration": "WORKER_IP_PRIVATE",
            "additionalExperiments": ["use_runner_v2"],
            "additionalUserLabels": {},
        }

        # Authenticate on initialization
        try:
            self.session = self._get_authed_session()
            logging.info(
                f"Launcher initialized for project '{self.project_id}' in '{self.location}'."
            )
        except ConnectionError as auth_err:
            logging.error(f"Authentication failed during initialization: {auth_err}")
            sys.exit(1)  # Exit immediately if auth fails

    def _get_authed_session(self) -> requests.Session:
        """
        Gets application default credentials and creates an authorized session.
        """
        try:
            logging.info("Getting Google Cloud application default credentials...")
            credentials, _ = google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            authed_session = AuthorizedSession(credentials)
            logging.info("Authentication successful.")
            return authed_session

        except Exception as e:
            logging.error(f"Error getting credentials: {e}", exc_info=True)
            raise ConnectionError(
                "Failed to authenticate. Ensure you have run "
                "'gcloud auth application-default login' or set "
                "GOOGLE_APPLICATION_CREDENTIALS."
            )

    def _generate_job_name(self) -> str:
        """
        Generates a unique Dataflow job name using the prefix and a timestamp.
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        job_name = f"{self.job_name_prefix}-{timestamp}"

        # Cleanup for Dataflow job name requirements
        job_name = job_name.lower().replace("_", "-")
        return job_name[:63]

    def _build_payload(
        self,
        job_name: str,
    ) -> Dict[str, Any]:
        """
        Constructs the final JSON payload from the class's attributes.
        """
        payload = {
            "launch_parameter": {
                "jobName": job_name,
                "containerSpecGcsPath": self.template_gcs_path,
                "parameters": self.parameters,
            }
        }

        if self.environment:
            payload["launch_parameter"]["environment"] = self.environment

        return payload

    def _launch_job(self, job_name: str):
        """
        (Internal) Sends the POST request to the Dataflow API.
        """

        payload = self._build_payload(job_name)

        logging.info(f"Sending POST request to Dataflow API for job '{job_name}'...")

        response = self.session.post(self.api_endpoint, json=payload)
        response.raise_for_status()  # Raise an error for bad responses

        response_json = response.json()
        job_id = response_json.get("job", {}).get("id", "UNKNOWN_ID")

        logging.info("\nSuccessfully launched job!")
        logging.info(f"Job ID: {job_id}")
        logging.info(
            f"View job: https://console.cloud.google.com/dataflow/jobs/"
            f"{self.location}/{job_id}?project={self.project_id}"
        )

        job_link = f"https://console.cloud.google.com/dataflow/jobs/{self.location}/{job_id}?project={self.project_id}"

        return job_link

    def execute_pipeline(self):
        """
        Public method to run the entire job launch process.
        """
        print(self.parameters)
        print(self.environment)
        try:
            job_name = self._generate_job_name()
            response = self._launch_job(job_name)

            logging.info("Script finished successfully.")
            return response

        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}", exc_info=True)
            logging.error(f"Response content: {http_err.response.text}")
            raise
        except Exception as e:
            logging.error(
                f"Job launch failed with an unexpected error: {e}", exc_info=True
            )
            raise
