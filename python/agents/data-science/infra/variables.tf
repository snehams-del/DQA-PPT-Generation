variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "agent_name" {
  description = "Base name for resource naming (will be used with prefixes for consistent naming)"
  type        = string
  default     = "data-science"
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "us-central1"
}

variable "bq_data_project_id" {
  description = "GCP Project for BQ data storage (defaults to project_id if not specified)"
  type        = string
  default     = ""
}

variable "bq_compute_project_id" {
  description = "GCP Project for BQ compute (defaults to project_id if not specified)"
  type        = string
  default     = ""
}


variable "train_csv_path" {
  description = "Path to training CSV file"
  type        = string
  default     = "data_science/utils/data/train.csv"
}

variable "test_csv_path" {
  description = "Path to test CSV file"
  type        = string
  default     = "data_science/utils/data/test.csv"
}

variable "rag_data_sources" {
  description = "List of data sources for RAG corpus"
  type        = list(string)
  default     = ["gs://cloud-samples-data/adk-samples/data-science/bqml"]
}

variable "create_code_interpreter" {
  description = "Whether to create a new code interpreter extension"
  type        = bool
  default     = true
}

variable "create_staging_bucket" {
  description = "Whether to create staging bucket"
  type        = bool
  default     = true
}



