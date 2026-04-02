"""Script to prepare the ADK BigQuery analytics dataset."""
import os
import sys

from google.cloud import bigquery
from google.api_core import exceptions
import google.auth

def main():
    try:
        credentials, project_id = google.auth.default()
    except Exception as e:
        print(f"Error authenticating: {e}")
        sys.exit(1)

    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", project_id)
    if not project_id:
        print("Error: GOOGLE_CLOUD_PROJECT is not set and could not be determined.")
        sys.exit(1)

    # Use default name if not provided
    dataset_id = os.environ.get("BQ_ANALYTICS_DATASET_ID", "adk_agent_analytics")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

    print(f"Preparing ADK BigQuery Dataset: {project_id}.{dataset_id} in {location}...")

    try:
        client = bigquery.Client(project=project_id, credentials=credentials)
        dataset_ref = f"{project_id}.{dataset_id}"
        
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = location
        
        try:
            existing_dataset = client.get_dataset(dataset_ref)
            if existing_dataset.location.upper() != location.upper():
                print(f"❌ Error: Dataset {dataset_id} already exists in location {existing_dataset.location}, but we need it in {location}.")
                print("Please run 'make backend' again and specify a different dataset ID when prompted.")
                sys.exit(1)
            print(f"✅ Dataset {dataset_ref} already exists in the correct location ({location}).")
        except exceptions.NotFound:
            client.create_dataset(dataset)
            print(f"✅ Successfully created BigQuery dataset {dataset_ref} in {location}.")
        
    except Exception as e:
        print(f"❌ Failed to create or confirm BigQuery dataset: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
