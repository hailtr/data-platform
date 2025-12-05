variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "bucket_name" {
  description = "GCS Bucket Name"
  type        = string
}

variable "bq_dataset_id" {
  description = "BigQuery Dataset ID"
  type        = string
  default     = "analytics_raw"
}
