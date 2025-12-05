variable "project_id" {
  description = "Add the ID of the project where you want to deploy the bridge"
  type        = string
}

variable "region" {
  description = "Add the region where you want to deploy the bridge"
  type        = string
  default     = "us-central1"
}

variable "bucket_name" {
  description = "Add the name of the bucket where you want to store the raw data"
  type        = string
}

variable "bq_dataset_id" {
  description = "Add the name of the BigQuery dataset where you want to store the analytics data"
  type        = string
}
