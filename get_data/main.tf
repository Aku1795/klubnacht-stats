provider "google" {
  project = "klubnacht-stats"
}

### Service enablers

resource "google_project_service" "run_api" {
  service            = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "iam_api" {
  service            = "iam.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "resource_manager_api" {
  service            = "cloudresourcemanager.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "scheduler_api" {
  service            = "cloudscheduler.googleapis.com"
  disable_on_destroy = false
}


### Scrapper
resource "google_artifact_registry_repository" "scraper_repo" {
  location      = var.location
  repository_id = "klubnacht-scraper"
  format        = "docker"
}

resource "null_resource" "building_docker_image" {
  depends_on = [google_artifact_registry_repository.scraper_repo]
  triggers = {
    python_file       = md5(file("./scraper/main.py"))
    docker_file       = md5(file("./scraper/Dockerfile"))
    requirements_file = md5(file("./scraper/requirements.txt"))
    dockerignore      = md5(file("./scraper/.dockerignore"))
  }

  provisioner "local-exec" {
    command = <<EOF
           docker build --tag ${var.docker_image_name} --build-arg BUCKET=${var.bucket} ./scraper/
           docker push ${var.docker_image_name}
       EOF
  }
}

resource "google_cloud_run_service" "scraper" {
  depends_on = [null_resource.building_docker_image]
  name       = "scraper-service"
  location   = var.location

  template {
    spec {
      containers {
        image = var.docker_image_name
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

### Scheduler
resource "google_service_account" "scheduler" {
  account_id   = "scheduler-sa"
  description  = "Cloud Scheduler service account; used to trigger scheduled Cloud Run jobs."
  display_name = "scheduler-sa"

  # Use an explicit depends_on clause to wait until API is enabled
  depends_on = [
    google_project_service.iam_api
  ]
}

resource "google_cloud_run_service_iam_member" "scheduler" {
  location = google_cloud_run_service.scraper.location
  service  = google_cloud_run_service.scraper.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.scheduler.email}"
}

resource "google_cloud_scheduler_job" "scrapper_scheduler" {
  name             = "scraper_scheduler"
  description      = "scraper_scheduler"
  schedule         = "0 5 2 * *"
  region           = var.location
  attempt_deadline = "320s"

  retry_config {
    retry_count = 1
  }

  http_target {
    http_method = "GET"
    uri         = "${google_cloud_run_service.scraper.status[0].url}/scrap_last_month"
    oidc_token {
      service_account_email = google_service_account.scheduler.email
    }
  }

  depends_on = [
    google_project_service.scheduler_api
  ]


}