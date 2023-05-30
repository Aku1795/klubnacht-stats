provider "google" {
    project = "klubnacht-stats"
}

resource "google_artifact_registry_repository" "my-repo" {
  location = "us-west1"
  repository_id = "klubnacht-scrapper"
  format = "docker"
}

resource "null_resource" "building_docker_image" {
  depends_on = [google_artifact_registry_repository.my-repo]
   triggers = {
    python_file       = md5(file("./main.py"))
    docker_file       = md5(file("./Dockerfile"))
    requirements_file = md5(file("./requirements.txt"))
    dockerignore = md5(file("./.dockerignore"))
  }

  provisioner "local-exec" {
    command = <<EOF
           docker build -t us-west1-docker.pkg.dev/klubnacht-stats/klubnacht-scrapper/scrapper-image .
           docker push us-west1-docker.pkg.dev/klubnacht-stats/klubnacht-scrapper/scrapper-image
       EOF
  }
}

resource "google_cloud_run_service" "default" {
  name     = "scrapper-service"
  location = "us-west1"

  template {
    spec {
      containers {
        image = "us-west1-docker.pkg.dev/klubnacht-stats/klubnacht-scrapper/scrapper-image"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}