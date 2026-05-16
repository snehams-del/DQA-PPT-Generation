import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from google.api_core.exceptions import NotFound
from google.cloud import bigquery, dataplex_v1, resourcemanager_v3

# 1. Setup Cloud Logging
# This ensures logs appear correctly in GCP Explorer (Info vs Error)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class DataplexRetentionAgent:
    """Agent for analyzing BigQuery dataset retention using Dataplex and BQ INFORMATION_SCHEMA"""

    def __init__(self):
        # Use .get() to avoid immediate crashes if env vars are missing during testing
        self.organization_id = os.environ.get("ORGANIZATION_ID")
        self.project_id = os.environ.get("BQ_EXECUTION_PROJECT_ID")
        self.location = os.environ.get("LOCATION", "us-central1")

        # Initialize clients
        if self.project_id:
            self.bq_client = bigquery.Client(project=self.project_id)
        else:
            self.bq_client = bigquery.Client()

        self.dataplex_client = dataplex_v1.CatalogServiceClient()

        if self.organization_id:
            self.projects_client = resourcemanager_v3.ProjectsClient()

    def get_all_projects(self) -> List[List[str]]:
        """
        Get all active projects in the organization.
        Returns: List of [project_number, project_id]
        """
        if not self.organization_id:
            logger.info("No Organization ID provided. Scoping to single project.")
            return [[self.project_id, self.project_id]] if self.project_id else []

        projects = []

        try:
            # FIX for 400 Error: Ensure correct parent format
            parent_string = self.organization_id
            if not parent_string.startswith("organizations/"):
                parent_string = f"organizations/{parent_string}"

            logger.info(f"Discovering projects in: {parent_string}")

            request = resourcemanager_v3.ListProjectsRequest(
                parent=parent_string, show_deleted=False
            )

            page_result = self.projects_client.list_projects(request=request)

            for project in page_result:
                if project.state == resourcemanager_v3.Project.State.ACTIVE:
                    # project.name format is 'projects/12345'
                    project_num = project.name.split("/")[-1]
                    project_id = project.project_id
                    projects.append([project_num, project_id])

            logger.info(f"Total active projects found: {len(projects)}")

        except Exception as e:
            logger.error(f"Error listing projects in organization: {e}", exc_info=True)
            # Fallback
            if self.project_id:
                projects = [[self.project_id, self.project_id]]

        return projects

    def get_dataplex_datasets(self) -> List[Dict[str, Any]]:
        """Fetch all BigQuery datasets from Dataplex Universal Catalog"""
        datasets = []

        logger.info("--- Starting Dataset Discovery ---")

        projects = self.get_all_projects()

        for project_num, project_id in projects:
            try:
                # Try Dataplex catalog first
                datasets_in_project = self._get_dataplex_datasets_for_project(
                    project_num, project_id
                )

                if not datasets_in_project:
                    # Fallback to direct BigQuery listing
                    datasets_in_project = self._fallback_list_bq_datasets_for_project(
                        project_num, project_id
                    )

                if datasets_in_project:
                    datasets.extend(datasets_in_project)
                    logger.info(
                        f"Project {project_id}: Found {len(datasets_in_project)} datasets"
                    )

            except Exception as e:
                logger.warning(f"Skipping project {project_id} due to error: {e}")

        logger.info(f"Total datasets discovered across organization: {len(datasets)}")
        return datasets

    def _get_dataplex_datasets_for_project(
        self, project_num: str, project_id: str
    ) -> List[Dict[str, Any]]:
        datasets = []
        try:
            parent = f"projects/{project_num}/locations/{self.location}"

            request = dataplex_v1.SearchEntriesRequest(
                name=parent, query="system=bigquery AND type=dataset", page_size=100
            )

            page_result = self.dataplex_client.search_entries(request=request)

            for entry in page_result:
                datasets.append(
                    {
                        "project_num": project_num,
                        "project_id": project_id,
                        "dataset_id": self._extract_dataset_from_entry(entry),
                        "region": self._extract_region_from_entry(entry),
                        "retention_period_days": self._extract_retention_period(entry),
                        "entry_name": entry.name,
                    }
                )
        except Exception:
            pass  # Allow fallback
        return datasets

    def _fallback_list_bq_datasets_for_project(
        self, project_num: str, project_id: str
    ) -> List[Dict[str, Any]]:
        datasets = []
        try:
            # Use project_id (string name) for client, usually safer/clearer than number
            bq_client = bigquery.Client(project=project_id)

            for dataset in bq_client.list_datasets():
                dataset_ref = bq_client.get_dataset(dataset.reference)

                retention_days = None
                if dataset_ref.default_table_expiration_ms:
                    retention_days = dataset_ref.default_table_expiration_ms / (
                        1000 * 60 * 60 * 24
                    )

                datasets.append(
                    {
                        "project_num": project_num,
                        "project_id": project_id,
                        "dataset_id": dataset.dataset_id,
                        "region": dataset_ref.location,
                        "retention_period_days": retention_days,
                        "entry_name": f"{project_num}.{dataset.dataset_id}",
                    }
                )
        except Exception:
            pass
        return datasets

    def _extract_dataset_from_entry(self, entry) -> str:
        if hasattr(entry, "fully_qualified_name"):
            parts = entry.fully_qualified_name.split("/")
            if len(parts) >= 4:
                return parts[3]
        return entry.name.split("/")[-1]

    def _extract_region_from_entry(self, entry) -> str:
        if hasattr(entry, "source_system_timestamps"):
            return getattr(entry, "location", "unknown")
        return "unknown"

    def _extract_retention_period(self, entry) -> Optional[float]:
        if hasattr(entry, "aspects"):
            for aspect_key, aspect_value in entry.aspects.items():
                if "retention" in aspect_key.lower():
                    return aspect_value.get("retention_days")
        return None

    def get_last_access_timestamp(
        self, project_id: str, dataset_id: str, region: str
    ) -> Optional[datetime]:
        """
        Queries INFORMATION_SCHEMA.JOBS_BY_ORGANIZATION or JOBS_BY_PROJECT
        """
        try:
            client = bigquery.Client(project=project_id)

            # NOTE: JOBS_BY_ORGANIZATION requires strict permissions.
            # If this fails, you might need to fallback to JOBS_BY_PROJECT
            query = f"""
                SELECT last_access_time AS last_access from (
                SELECT
                LOWER(referenced_tables.project_id) AS project_id,
                LOWER(referenced_tables.dataset_id) AS dataset_id,
                MAX(creation_time) AS last_access_time
                FROM `{project_id}.region-{region}.INFORMATION_SCHEMA.JOBS_BY_ORGANIZATION`
                CROSS JOIN UNNEST(referenced_tables) AS referenced_tables
                WHERE state = 'DONE'
                AND referenced_tables.project_id IS NOT NULL
                AND referenced_tables.dataset_id IS NOT NULL
                AND referenced_tables.table_id NOT LIKE 'INFORMATION_SCHEMA%'
                GROUP BY 1, 2 )
                where dataset_id = @dataset_id
            """

            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("dataset_id", "STRING", dataset_id)
                ]
            )

            query_job = client.query(query, job_config=job_config)
            results = query_job.result()

            for row in results:
                return row.last_access

            return None

        except NotFound:
            logger.warning(
                f"Dataset '{project_id}.{dataset_id}' not found or no access info."
            )
            return None
        except Exception as e:
            logger.error(f"Error checking access for {dataset_id}: {e}")
            return None

    def analyze_datasets(self, retention_threshold_days: int) -> List[Dict[str, str]]:
        """
        Analyze datasets and identify those exceeding retention threshold.
        Returns a list of dictionaries where ALL values are strings.
        """
        threshold_date = datetime.now(timezone.utc) - timedelta(
            days=retention_threshold_days
        )
        datasets_exceeding_threshold = []

        logger.info(
            f"--- Starting Analysis: Threshold {retention_threshold_days} days ---"
        )

        dataplex_datasets = self.get_dataplex_datasets()

        for dataset in dataplex_datasets:
            project_id = dataset["project_id"]
            project_num = dataset["project_num"]
            dataset_id = dataset["dataset_id"]
            region = dataset["region"]

            last_access = self.get_last_access_timestamp(
                project_num, dataset_id, region
            )

            # Logic to decide if it goes in the report
            should_report = False
            last_access_str = "Unknown"

            if last_access:
                if last_access < threshold_date:
                    should_report = True
                    last_access_str = last_access.strftime("%Y-%m-%d %H:%M:%S")
            else:
                # If no access found, assume it's old/unused
                should_report = True
                last_access_str = "No access history found (assumed > 180 days)"

            if should_report:
                # Construct strict Dict[str, str]
                datasets_exceeding_threshold.append(
                    {
                        "Project Id": str(project_id),
                        "Project Number": str(project_num),
                        "Dataset": str(dataset_id),
                        "Region": str(region),
                        "Last Access": last_access_str,
                        "Exceeds Threshold": "Yes",
                    }
                )

        logger.info(
            f"Analysis Complete. Found {len(datasets_exceeding_threshold)} violations."
        )
        return datasets_exceeding_threshold
