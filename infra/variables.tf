variable "aws_region" {
  description = "AWS region where resources are deployed"
  type        = string
}

variable "account_id" {
  description = "AWS account ID"
  type        = string
}

variable "vector_bucket_name" {
  description = "Name of the S3 vectors bucket"
  type        = string
}

variable "vector_index_name" {
  description = "Name of the S3 vectors index"
  type        = string
}

variable "role_name" {
  description = "Name of the IAM role to create"
  type        = string
  default     = "bedrock-s3-vectors-role"
}

variable "trusted_principal_arn" {
  description = "AWS service principal allowed to assume this role"
  type        = string
  default     = "lambda.amazonaws.com"
}