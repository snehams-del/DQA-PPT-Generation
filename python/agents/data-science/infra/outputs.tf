output "project_id" {
  description = "The GCP project ID"
  value       = var.project_id
}

output "region" {
  description = "The GCP region"
  value       = var.region
}

output "bigquery_dataset" {
  description = "BigQuery dataset details"
  value = {
    dataset_id      = module.data_science_agent.dataset_id
    data_project    = local.bq_data_project_id
    compute_project = local.bq_compute_project_id
    location        = module.data_science_agent.dataset_location
    naming_pattern  = "${replace(var.agent_name, "-", "_")}"
  }
}

output "bigquery_tables" {
  description = "BigQuery tables created"
  value       = module.data_science_agent.table_ids
}

output "rag_corpus" {
  description = "RAG corpus details"
  value = {
    corpus_name = module.data_science_agent.rag_corpus_name
    location    = module.data_science_agent.rag_corpus_location
  }
  sensitive = false
}

output "staging_bucket" {
  description = "Staging bucket details"
  value = {
    name = module.data_science_agent.staging_bucket_name
    url  = module.data_science_agent.staging_bucket_url
  }
}

output "code_interpreter_extension" {
  description = "Code interpreter extension details"
  value = {
    name      = module.data_science_agent.code_interpreter_name
    resource  = module.data_science_agent.code_interpreter_resource_name
    created   = module.data_science_agent.code_interpreter_created
  }
  sensitive = false
}

output "environment_variables" {
  description = "Infrastructure-related environment variables for the data science agent"
  value = {
    GOOGLE_CLOUD_PROJECT              = var.project_id
    GOOGLE_CLOUD_LOCATION            = var.region
    BQ_DATASET_ID                    = module.data_science_agent.dataset_id
    BQ_DATA_PROJECT_ID               = local.bq_data_project_id
    BQ_COMPUTE_PROJECT_ID            = local.bq_compute_project_id
    BQML_RAG_CORPUS_NAME            = module.data_science_agent.rag_corpus_name
    CODE_INTERPRETER_EXTENSION_NAME = module.data_science_agent.code_interpreter_resource_name
  }
  sensitive = false
}
