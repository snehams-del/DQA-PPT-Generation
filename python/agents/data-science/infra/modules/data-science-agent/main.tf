# Configure providers
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 6.0"
    }
  }
}

# Enable required APIs (always enabled - not configurable)
resource "google_project_service" "required_apis" {
  for_each = toset([
    "bigquery.googleapis.com",
    "storage-api.googleapis.com", 
    "storage.googleapis.com",
    "aiplatform.googleapis.com",
    "notebooks.googleapis.com",
    "ml.googleapis.com",
    "cloudbuild.googleapis.com"
  ])

  project = var.project_id
  service = each.value

  disable_on_destroy = false
}

# Create BigQuery dataset
resource "google_bigquery_dataset" "dataset" {
  project                     = var.bq_data_project_id
  dataset_id                  = local.dataset_id
  friendly_name              = "${var.project_name} Data Science Dataset"
  description                = "Dataset for ${var.project_name} Data Science Agent containing training and test data"
  location                   = "US"
  default_table_expiration_ms = null


  depends_on = [google_project_service.required_apis]
}

# Create BigQuery tables (structure only)
resource "google_bigquery_table" "train" {
  project    = var.bq_data_project_id
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = "train"

  description = "Training data for sticker sales forecasting"
  deletion_protection = false

  schema = jsonencode([
    {
      name = "id"
      type = "INTEGER"
      mode = "REQUIRED"
    },
    {
      name = "date"
      type = "DATE"
      mode = "REQUIRED"
    },
    {
      name = "country"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "store"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "product"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "num_sold"
      type = "INTEGER"
      mode = "REQUIRED"
    }
  ])
}

resource "google_bigquery_table" "test" {
  project    = var.bq_data_project_id
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = "test"

  description = "Test data for sticker sales forecasting"
  deletion_protection = false

  schema = jsonencode([
    {
      name = "id"
      type = "INTEGER"
      mode = "REQUIRED"
    },
    {
      name = "date"
      type = "DATE"
      mode = "REQUIRED"
    },
    {
      name = "country"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "store"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "product"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "num_sold"
      type = "INTEGER"
      mode = "REQUIRED"
    }
  ])
}

# Create staging bucket
resource "google_storage_bucket" "staging" {
  count    = var.create_staging_bucket ? 1 : 0
  project  = var.project_id
  name     = local.staging_bucket_name
  location = var.region

  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30  # Delete objects older than 30 days
    }
  }

  depends_on = [google_project_service.required_apis]
}

# Get current user info
data "google_client_openid_userinfo" "me" {}

# Local values
locals {
  staging_bucket_name = "${var.project_id}-${var.project_name}-staging"
  dataset_id         = "${replace(var.project_name, "-", "_")}"
  rag_corpus_name    = "${var.project_name}-bqml-corpus"
}