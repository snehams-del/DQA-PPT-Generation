variable "project_id" {
  description = "The ID of the project to deploy resources to."
  type        = string
}

variable "billing_project_id" {
  description = "The ID of the project to use for billing/quota."
  type        = string
}

variable "gcp_region" {
  description = "The GCP region to deploy resources to."
  type        = string
  default     = "us-central1"
}

variable "docker_image" {
  description = "The container image to deploy to Cloud Run jobs."
  type        = string
  default     = "us-docker.pkg.dev/cloudrun/container/hello"
}

variable "drive_folder_id" {
  description = "The ID of the Google Drive folder to poll for contracts."
  type        = string
}
