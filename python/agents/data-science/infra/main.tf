terraform {
  required_version = ">= 1.0"
  backend "gcs" {
    # bucket and prefix will be provided via backend-config in Makefile
  }
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

# Local values for project ID unification
locals {
  bq_data_project_id    = var.bq_data_project_id != "" ? var.bq_data_project_id : var.project_id
  bq_compute_project_id = var.bq_compute_project_id != "" ? var.bq_compute_project_id : var.project_id
}

# Data Science Agent Infrastructure Module
module "data_science_agent" {
  source = "./modules/data-science-agent"
  
  # Project Configuration
  project_id   = var.project_id
  project_name = var.agent_name
  region       = var.region
  
  # BigQuery Configuration  
  bq_data_project_id    = local.bq_data_project_id
  bq_compute_project_id = local.bq_compute_project_id
  
  
  # Data Configuration
  train_csv_path = var.train_csv_path
  test_csv_path  = var.test_csv_path
  
  # RAG Configuration
  rag_data_sources = var.rag_data_sources
  
  # Code Interpreter
  create_code_interpreter = var.create_code_interpreter
  
  # Deployment Configuration
  create_staging_bucket = var.create_staging_bucket
  
}