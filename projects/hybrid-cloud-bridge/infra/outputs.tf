output "service_account_key" {
  value     = google_service_account_key.bridge_sa_key.private_key
  sensitive = true
}

output "bucket_name" {
  value = google_storage_bucket.data_lake.name
}
