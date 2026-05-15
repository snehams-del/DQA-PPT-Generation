terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}

provider "google" {
  region                = var.gcp_region
  user_project_override = true
  billing_project       = var.billing_project_id
}

provider "google-beta" {
  region                = var.gcp_region
  user_project_override = true
  billing_project       = var.billing_project_id
}

data "google_project" "project" {
  project_id = var.project_id
}

# Enable APIs
resource "google_project_service" "services" {
  for_each = toset([
    "compute.googleapis.com",
    "storage.googleapis.com",
    "run.googleapis.com",
    "cloudscheduler.googleapis.com",
    "firestore.googleapis.com",
    "discoveryengine.googleapis.com",
    "aiplatform.googleapis.com",
    "iam.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "serviceusage.googleapis.com",
    "workflows.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "drive.googleapis.com",
  ])

  project                    = data.google_project.project.project_id
  service                    = each.key
  disable_on_destroy         = false
  disable_dependent_services = false
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# Cloud Storage Bucket
resource "google_storage_bucket" "contracts_bucket" {
  name          = "contracts-bucket-${random_id.bucket_suffix.hex}"
  location      = var.gcp_region
  project       = data.google_project.project.project_id
  force_destroy = true

  uniform_bucket_level_access = true

  depends_on = [google_project_service.services]
}

# Firestore Database (Native Mode)
resource "google_firestore_database" "database" {
  project     = data.google_project.project.project_id
  name        = "contract-metadata"
  location_id = var.gcp_region
  type        = "FIRESTORE_NATIVE"

  depends_on      = [google_project_service.services]
  deletion_policy = "DELETE"
}

# Vertex AI Search Data Store
resource "google_discovery_engine_data_store" "contracts_search" {
  project           = data.google_project.project.project_id
  location          = "global"
  data_store_id     = "contracts-search-ds"
  display_name      = "Contracts Search"
  industry_vertical = "GENERIC"
  content_config    = "CONTENT_REQUIRED"
  solution_types    = ["SOLUTION_TYPE_SEARCH"]
  document_processing_config {
    default_parsing_config {
      digital_parsing_config {}
    }
  }

  create_advanced_site_search = false

  depends_on = [google_project_service.services]
}

# Service Account for Cloud Run Jobs
resource "google_service_account" "cloud_run_sa" {
  project      = data.google_project.project.project_id
  account_id   = "contracts-cloud-run-sa"
  display_name = "Cloud Run Jobs Service Account"

  depends_on = [google_project_service.services]
}

# IAM permissions for Cloud Run SA
resource "google_project_iam_member" "cloud_run_firestore" {
  project = data.google_project.project.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "cloud_run_storage" {
  project = data.google_project.project.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "cloud_run_discoveryengine" {
  project = data.google_project.project.project_id
  role    = "roles/discoveryengine.admin"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "cloud_run_vertex_ai" {
  project = data.google_project.project.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "cloud_run_workflow_invoker" {
  project = data.google_project.project.project_id
  role    = "roles/workflows.invoker"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Cloud Run Job for Contract Ingestion
resource "google_cloud_run_v2_job" "ingestion_job" {
  project  = data.google_project.project.project_id
  name     = "contract-ingestion-job"
  location = var.gcp_region

  template {
    template {
      service_account = google_service_account.cloud_run_sa.email
      containers {
        image = "${var.gcp_region}-docker.pkg.dev/${data.google_project.project.project_id}/contract-agent/processor:latest"
        args  = ["poll-drive"]
        env {
          name  = "GCP_PROJECT_ID"
          value = data.google_project.project.project_id
        }
        env {
          name  = "GCP_REGION"
          value = var.gcp_region
        }
        env {
          name  = "DRIVE_FOLDER_ID"
          value = var.drive_folder_id
        }
        env {
          name  = "GCS_BUCKET"
          value = google_storage_bucket.contracts_bucket.name
        }
        env {
          name  = "FIRESTORE_DB"
          value = google_firestore_database.database.name
        }
        env {
          name  = "VERTEX_AI_SEARCH_DATA_STORE_ID"
          value = google_discovery_engine_data_store.contracts_search.data_store_id
        }
      }
    }
  }

  depends_on = [google_project_service.services]
}

# Cloud Run Job for Expiry Check
resource "google_cloud_run_v2_job" "expiry_check_job" {
  project  = data.google_project.project.project_id
  name     = "contract-expiry-check-job"
  location = var.gcp_region

  template {
    template {
      service_account = google_service_account.cloud_run_sa.email
      containers {
        image = "${var.gcp_region}-docker.pkg.dev/${data.google_project.project.project_id}/contract-agent/processor:latest"
        args  = ["check-alerts", "--type", "expiration"]
        env {
          name  = "GCP_PROJECT_ID"
          value = data.google_project.project.project_id
        }
        env {
          name  = "GCP_REGION"
          value = var.gcp_region
        }
        env {
          name  = "DRIVE_FOLDER_ID"
          value = var.drive_folder_id
        }
        env {
          name  = "GCS_BUCKET"
          value = google_storage_bucket.contracts_bucket.name
        }
        env {
          name  = "FIRESTORE_DB"
          value = google_firestore_database.database.name
        }
      }
    }
  }

  depends_on = [google_project_service.services]
}

# Service Account for Cloud Scheduler
resource "google_service_account" "scheduler_sa" {
  project      = data.google_project.project.project_id
  account_id   = "scheduler-sa"
  display_name = "Cloud Scheduler Service Account"

  depends_on = [google_project_service.services]
}

# IAM Permission for Scheduler to Invoke Jobs
resource "google_project_iam_member" "scheduler_run_invoker" {
  project = data.google_project.project.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.scheduler_sa.email}"
}

# Cloud Scheduler Trigger for Ingestion Job (Hourly)
resource "google_cloud_scheduler_job" "ingestion_trigger" {
  project     = data.google_project.project.project_id
  region      = var.gcp_region
  name        = "trigger-ingestion-hourly"
  description = "Trigger contract ingestion hourly"
  schedule    = "0 * * * *"
  time_zone   = "UTC"

  http_target {
    http_method = "POST"
    uri         = "https://${var.gcp_region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${data.google_project.project.project_id}/jobs/${google_cloud_run_v2_job.ingestion_job.name}:run"

    oauth_token {
      service_account_email = google_service_account.scheduler_sa.email
    }
  }

  depends_on = [google_project_service.services]
}

# Cloud Scheduler Trigger for Expiry Check Job (Daily at 2 AM)
resource "google_cloud_scheduler_job" "expiry_trigger" {
  project     = data.google_project.project.project_id
  region      = var.gcp_region
  name        = "trigger-expiry-daily"
  description = "Trigger contract expiry check daily"
  schedule    = "0 2 * * *"
  time_zone   = "UTC"

  http_target {
    http_method = "POST"
    uri         = "https://${var.gcp_region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${data.google_project.project.project_id}/jobs/${google_cloud_run_v2_job.expiry_check_job.name}:run"

    oauth_token {
      service_account_email = google_service_account.scheduler_sa.email
    }
  }

  depends_on = [google_project_service.services]
}

# Cloud Run Job for Spend Forecast Check
resource "google_cloud_run_v2_job" "forecast_check_job" {
  project  = data.google_project.project.project_id
  name     = "contract-forecast-check-job"
  location = var.gcp_region

  template {
    template {
      service_account = google_service_account.cloud_run_sa.email
      containers {
        image = "${var.gcp_region}-docker.pkg.dev/${data.google_project.project.project_id}/contract-agent/processor:latest"
        args  = ["check-alerts", "--type", "forecast"]
        env {
          name  = "GCP_PROJECT_ID"
          value = data.google_project.project.project_id
        }
        env {
          name  = "GCP_REGION"
          value = var.gcp_region
        }
        env {
          name  = "DRIVE_FOLDER_ID"
          value = var.drive_folder_id
        }
        env {
          name  = "GCS_BUCKET"
          value = google_storage_bucket.contracts_bucket.name
        }
        env {
          name  = "FIRESTORE_DB"
          value = google_firestore_database.database.name
        }
      }
    }
  }

  depends_on = [google_project_service.services]
}

# Cloud Scheduler Trigger for Forecast Check Job (Daily at 3 AM)
resource "google_cloud_scheduler_job" "forecast_trigger" {
  project     = data.google_project.project.project_id
  region      = var.gcp_region
  name        = "trigger-forecast-daily"
  description = "Trigger contract spend forecast check daily"
  schedule    = "0 3 * * *"
  time_zone   = "UTC"

  http_target {
    http_method = "POST"
    uri         = "https://${var.gcp_region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${data.google_project.project.project_id}/jobs/${google_cloud_run_v2_job.forecast_check_job.name}:run"

    oauth_token {
      service_account_email = google_service_account.scheduler_sa.email
    }
  }

  depends_on = [google_project_service.services]
}

# Cloud Run Job for Fetch Spend
resource "google_cloud_run_v2_job" "fetch_spend_job" {
  project  = data.google_project.project.project_id
  name     = "contract-fetch-spend-job"
  location = var.gcp_region

  template {
    template {
      service_account = google_service_account.cloud_run_sa.email
      containers {
        image = "${var.gcp_region}-docker.pkg.dev/${data.google_project.project.project_id}/contract-agent/processor:latest"
        args  = ["fetch-spend"]
        env {
          name  = "GCP_PROJECT_ID"
          value = data.google_project.project.project_id
        }
        env {
          name  = "GCP_REGION"
          value = var.gcp_region
        }
        env {
          name  = "DRIVE_FOLDER_ID"
          value = var.drive_folder_id
        }
        env {
          name  = "GCS_BUCKET"
          value = google_storage_bucket.contracts_bucket.name
        }
        env {
          name  = "FIRESTORE_DB"
          value = google_firestore_database.database.name
        }
      }
    }
  }

  depends_on = [google_project_service.services]
}

# Cloud Scheduler Trigger for Fetch Spend Job (Daily at 1 AM)
resource "google_cloud_scheduler_job" "fetch_spend_trigger" {
  project     = data.google_project.project.project_id
  region      = var.gcp_region
  name        = "trigger-fetch-spend-daily"
  description = "Trigger contract fetch spend daily"
  schedule    = "0 1 * * *"
  time_zone   = "UTC"

  http_target {
    http_method = "POST"
    uri         = "https://${var.gcp_region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${data.google_project.project.project_id}/jobs/${google_cloud_run_v2_job.fetch_spend_job.name}:run"

    oauth_token {
      service_account_email = google_service_account.scheduler_sa.email
    }
  }

  depends_on = [google_project_service.services]
}

# Service Account for Cloud Workflows
resource "google_service_account" "workflow_sa" {
  project      = data.google_project.project.project_id
  account_id   = "workflow-sa"
  display_name = "Cloud Workflows Service Account"

  depends_on = [google_project_service.services]
}

# IAM permission for Workflow to invoke/run Jobs
resource "google_project_iam_member" "workflow_run" {
  project = data.google_project.project.project_id
  role    = "roles/run.developer"
  member  = "serviceAccount:${google_service_account.workflow_sa.email}"
}

# Cloud Workflow for Ingestion Pipeline
resource "google_workflows_workflow" "ingestion_workflow" {
  project     = data.google_project.project.project_id
  name        = "contract-ingestion-workflow"
  region      = var.gcp_region
  description = "Orchestrates contract ingestion pipeline"

  service_account = google_service_account.workflow_sa.email
  source_contents = file("${path.module}/workflows/ingestion.yaml")

  user_env_vars = {
    GCS_BUCKET = google_storage_bucket.contracts_bucket.name
  }

  depends_on = [google_project_service.services]
}

# Artifact Registry Repository for Docker images
resource "google_artifact_registry_repository" "contract_agent" {
  project       = data.google_project.project.project_id
  location      = var.gcp_region
  repository_id = "contract-agent"
  description   = "Docker repository for procurement agent"
  format        = "DOCKER"

  depends_on = [google_project_service.services]
}

# Grant Storage Reader to Compute Default SA (often used by Cloud Build)
resource "google_project_iam_member" "compute_sa_storage" {
  project = data.google_project.project.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
}

# Grant Artifact Registry Writer to Cloud Build SA
resource "google_project_iam_member" "cloudbuild_sa_writer" {
  project = data.google_project.project.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-cloudbuild.iam.gserviceaccount.com"
}

# Grant Artifact Registry Writer to Compute Default SA (often used by Cloud Build)
resource "google_project_iam_member" "compute_sa_writer" {
  project = data.google_project.project.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
}
