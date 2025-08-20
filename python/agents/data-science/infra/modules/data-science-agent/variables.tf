variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "project_name" {
  description = "Base name for resource naming (agent name)"
  type        = string
  default     = "data-science"
}

variable "region" {
  description = "The GCP region"
  type        = string
}


variable "bq_data_project_id" {
  description = "GCP Project for BQ data storage"
  type        = string
}

variable "bq_compute_project_id" {
  description = "GCP Project for BQ compute"
  type        = string
}

variable "train_csv_path" {
  description = "Path to training CSV file"
  type        = string
}

variable "test_csv_path" {
  description = "Path to test CSV file"
  type        = string
}

variable "rag_data_sources" {
  description = "List of data sources for RAG corpus"
  type        = list(string)
}

variable "create_code_interpreter" {
  description = "Whether to create a new code interpreter extension"
  type        = bool
}

variable "create_staging_bucket" {
  description = "Whether to create staging bucket"
  type        = bool
}

