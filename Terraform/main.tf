module "s3_bucket" {
  source      = "./modules/s3"
  bucket_name = "serverless-ml-raw-data-bucket"
  tags = {
    Environment = "dev"
    Owner       = "paul"
  }
}