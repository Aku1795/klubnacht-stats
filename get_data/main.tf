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
           docker build --tag ${var.docker_image_name} --build-arg BUCKET=${var.bucket} ./scraper/
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

resource "google_cloud_run_service_iam_member" "cloud_run_service_invoker" {
  project        = google_cloud_run_service.scraper.project
  location        = google_cloud_run_service.scraper.location
  service = google_cloud_run_service.scraper.name

  role   = "roles/run.invoker"
  member = "allUsers"
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

resource "google_cloudfunctions_function_iam_member" "cloud_func_invoker" {
  project        = google_cloudfunctions_function.date_generator.project
  region         = google_cloudfunctions_function.date_generator.region
  cloud_function = google_cloudfunctions_function.date_generator.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}


### Workflow

resource "google_project_service" "workflows" {
  service            = "workflows.googleapis.com"
  disable_on_destroy = false
}

resource "google_service_account" "workflows_service_account" {
  account_id   = "sample-workflows-sa"
  display_name = "Sample Workflows Service Account"
}

resource "google_workflows_workflow" "workflows_example" {
  name            = "scrapping_workflow"
  region          = var.location
  description     = "Workflow to be triggered once per month to get last months events"
  service_account = google_service_account.workflows_service_account.id
  source_contents = <<-EOF
  # This is a sample workflow, feel free to replace it with your source code
  #
  # This workflow does the following:
  # - reads current time and date information from an external API and stores
  #   the response in currentTime variable
  # - retrieves a list of Wikipedia articles related to the day of the week
  #   from currentTime
  # - returns the list of articles as an output of the workflow
  # FYI, In terraform you need to escape the $$ or it will cause errors.

  - getPreviousMonth:
      call: http.get
      args:
          url: ${google_cloudfunctions_function.date_generator.https_trigger_url}
      result: previousYearMonth
  - return_result:
      return: $${previousYearMonth.body}

EOF

  depends_on = [google_project_service.workflows]
}


#HTTP server responded with error code 500
#in step "scrapPreviousMonthEvents", routine "main", line: 17
#{
#  "body": "<!doctype html>\n<html lang=en>\n<title>500 Internal Server Error</title>\n<h1>Internal Server Error</h1>\n<p>The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.</p>\n",
#  "code": 500,
#  "headers": {
#    "Alt-Svc": "h3=\":443\"; ma=2592000,h3-29=\":443\"; ma=2592000",
#    "Content-Length": "265",
#    "Content-Type": "text/html; charset=utf-8",
#    "Date": "Thu, 01 Jun 2023 11:44:54 GMT",
#    "Server": "Google Frontend",
#    "X-Cloud-Trace-Context": "65a71344b4df2781b3d6da0b45a591a2;o=1"
#  },
#  "message": "HTTP server responded with error code 500",
#  "tags": [
#    "HttpError"
#  ]
#}