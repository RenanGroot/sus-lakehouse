output "bucket_name" {
  value       = google_storage_bucket.raw_data.name
  description = "Name of the raw data bucket"
}

output "dataset_id" {
  value       = google_bigquery_dataset.sih_raw.dataset_id
  description = "BigQuery dataset ID for raw data"
}

output "artifact_registry_url" {
  value       = "${google_artifact_registry_repository.sus_lakehouse.location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.sus_lakehouse.repository_id}"
  description = "URL for pushing Docker images"
}

output "streamlit_service_account" {
  value       = google_service_account.streamlit_runner.email
  description = "Service account email for Streamlit"
}