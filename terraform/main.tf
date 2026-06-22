# GCS bucket for raw data
resource "google_storage_bucket" "raw_data" {
  name          = var.bucket_name
  location      = var.region
  storage_class = "STANDARD"
  
  uniform_bucket_level_access = true
}

# BigQuery dataset
resource "google_bigquery_dataset" "sih_raw" {
  dataset_id = "sih_raw"
  location   = var.region
}

# Artifact Registry repository for Docker images
resource "google_artifact_registry_repository" "sus_lakehouse" {
  location      = var.region
  repository_id = "sus-lakehouse"
  description   = "Container images for SUS Lakehouse"
  format        = "DOCKER"
}

# Service account for Streamlit dashboard on Cloud Run
resource "google_service_account" "streamlit_runner" {
  account_id   = "streamlit-runner"
  display_name = "Streamlit Cloud Run service account"
}

# Grant BigQuery read permissions to streamlit-runner
resource "google_project_iam_member" "streamlit_bq_viewer" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:${google_service_account.streamlit_runner.email}"
}

resource "google_project_iam_member" "streamlit_bq_jobuser" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.streamlit_runner.email}"
}