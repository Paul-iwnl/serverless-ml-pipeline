resource "aws_s3_bucket" "simple_storage_bucket" {
  bucket = var.bucket_name
  tags   = var.tags
}