output "dataset_id" {
  description = "The BigQuery dataset ID"
  value       = google_bigquery_dataset.dataset.dataset_id
}

output "dataset_location" {
  description = "The BigQuery dataset location"
  value       = google_bigquery_dataset.dataset.location
}

output "table_ids" {
  description = "The BigQuery table IDs created"
  value = {
    train = google_bigquery_table.train.table_id
    test  = google_bigquery_table.test.table_id
  }
}

output "table_row_counts" {
  description = "Row counts for the BigQuery tables"
  value = {
    train_rows = data.external.bigquery_row_counts.result.train_rows
    test_rows  = data.external.bigquery_row_counts.result.test_rows
    total_rows = data.external.bigquery_row_counts.result.total_rows
  }
}

output "rag_corpus_name" {
  description = "The RAG corpus name"
  value       = data.external.rag_corpus_info.result.name
}

output "rag_corpus_location" {
  description = "The RAG corpus location"
  value       = data.external.rag_corpus_info.result.location
}

output "staging_bucket_name" {
  description = "The staging bucket name"
  value       = var.create_staging_bucket ? google_storage_bucket.staging[0].name : ""
}

output "staging_bucket_url" {
  description = "The staging bucket URL"
  value       = var.create_staging_bucket ? google_storage_bucket.staging[0].url : ""
}

output "code_interpreter_name" {
  description = "The code interpreter extension display name"
  value       = var.create_code_interpreter ? data.external.code_interpreter_info[0].result.name : ""
}

output "code_interpreter_resource_name" {
  description = "The code interpreter extension resource name"
  value       = var.create_code_interpreter ? data.external.code_interpreter_info[0].result.resource_name : ""
}

output "code_interpreter_created" {
  description = "Whether the code interpreter was created successfully"
  value       = var.create_code_interpreter ? data.external.code_interpreter_info[0].result.created : "false"
}

output "project_number" {
  description = "The GCP project number"
  value       = data.google_project.project.number
}

# Additional data resources
data "google_project" "project" {
  project_id = var.project_id
}