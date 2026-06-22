variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "southamerica-east1"
}

variable "bucket_name" {
  description = "GCS bucket name for raw data"
  type        = string
}