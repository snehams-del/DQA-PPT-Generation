output "project_id" {
  description = "The ID of the created project."
  value       = data.google_project.project.project_id
}

output "project_number" {
  description = "The number of the created project."
  value       = data.google_project.project.number
}

output "bucket_name" {
  description = "The name of the Cloud Storage bucket."
  value       = google_storage_bucket.contracts_bucket.name
}

output "firestore_db_name" {
  description = "The name of the Firestore database."
  value       = google_firestore_database.database.name
}

output "vertex_search_datastore_id" {
  description = "The ID of the Vertex AI Search Data Store."
  value       = google_discovery_engine_data_store.contracts_search.data_store_id
}
