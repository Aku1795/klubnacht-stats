terraform {
 backend "gcs" {
   bucket  = "klubnacht-stats-terraform-backend-10101"
   prefix  = "terraform/state"
 }
}