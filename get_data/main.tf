provider "google" {
    project = "klubnacht-stats"
}

### Service enablements

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
  location = var.location
  repository_id = "klubnacht-scraper"
  format = "docker"
}

resource "null_resource" "building_docker_image" {
  depends_on = [google_artifact_registry_repository.scraper_repo]
   triggers = {
    python_file       = md5(file("./scraper/main.py"))
    docker_file       = md5(file("./scraper/Dockerfile"))
    requirements_file = md5(file("./scraper/requirements.txt"))
    dockerignore = md5(file("./scraper/.dockerignore"))
  }

  provisioner "local-exec" {
    command = <<EOF
           docker build -t ${var.docker_image_name} ./scraper/
           docker push ${var.docker_image_name}
       EOF
  }
}

resource "google_cloud_run_service" "scraper" {
  depends_on = [null_resource.building_docker_image]
  name     = "scraper-service"
  location = var.location

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

### Date generator
data "archive_file" "date_generator" {
    type        = "zip"
    source_dir  = "./date_generator/"
    output_path = "./date_generator/date_generator.zip"
}

resource "google_storage_bucket_object" "zip" {
    source       = data.archive_file.date_generator.output_path
    content_type = "application/zip"

    # Append to the MD5 checksum of the files's content
    # to force the zip to be updated as soon as a change occurs
    name         = "functions/${data.archive_file.date_generator.output_md5}.zip"
    bucket       = var.bucket

    # Dependencies are automatically inferred so these lines can be deleted
    depends_on   = [
        data.archive_file.date_generator
    ]
}

resource "google_cloudfunctions_function" "date_generator" {
  name        = "date_generator"
  description = "Gives the current year and month"
  runtime     = "python310"
  region = var.location

  available_memory_mb   = 128
  source_archive_bucket = var.bucket
  source_archive_object = google_storage_bucket_object.zip.name
  trigger_http          = true
  entry_point           = "current_date"
}

resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = google_cloudfunctions_function.date_generator.project
  region         = google_cloudfunctions_function.date_generator.region
  cloud_function = google_cloudfunctions_function.date_generator.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}