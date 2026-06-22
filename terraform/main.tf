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
# Ingestion service account
resource "google_service_account" "ingestion_runner" {
  account_id   = "ingestion-runner"
  display_name = "Ingestion Cloud Run Job service account"
}

resource "google_project_iam_member" "ingestion_gcs_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.ingestion_runner.email}"
}

resource "google_project_iam_member" "ingestion_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.ingestion_runner.email}"
}

# Cloud Run Job for ingestion
resource "google_cloud_run_v2_job" "ingestion" {
  name     = "sus-lakehouse-ingestion"
  location = var.region
  
  template {
    template {
      service_account = google_service_account.ingestion_runner.email
      timeout         = "3600s"
      
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/sus-lakehouse/ingestion:latest"
        
        resources {
          limits = {
            cpu    = "1"
            memory = "2Gi"
          }
        }
        
        env {
          name  = "BUCKET_NAME"
          value = var.bucket_name
        }
      }
    }
  }
}

# Cloud Scheduler — triggers ingestion monthly
resource "google_cloud_scheduler_job" "ingestion_monthly" {
  name        = "sus-lakehouse-ingestion-monthly"
  region      = var.region
  schedule    = "0 10 1 * *"
  description = "Run ingestion on the 1st of every month at 6 AM"
  
  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.ingestion.name}:run"
    
    oauth_token {
      service_account_email = google_service_account.ingestion_runner.email
    }
  }
}

# Cloud Run Service for Streamlit dashboard
resource "google_cloud_run_v2_service" "streamlit" {
  name     = "sus-lakehouse-dashboard"
  location = var.region
  
  template {
    service_account = google_service_account.streamlit_runner.email
    
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/sus-lakehouse/streamlit:latest"
      
      ports {
        container_port = 8080
      }
      
      resources {
        limits = {
          cpu    = "1"
          memory = "1Gi"
        }
      }
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "streamlit_public" {
  name     = google_cloud_run_v2_service.streamlit.name
  location = google_cloud_run_v2_service.streamlit.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}