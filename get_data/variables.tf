variable "location" {
  type = string
  default = "us-west1"
}

variable "bucket" {
  type = string
  default = "klubnacht-stats-raw-10101"
}

variable "docker_image_name" {
  type = string
  default = "us-west1-docker.pkg.dev/klubnacht-stats/klubnacht-scraper/scraper-image:latest"
}