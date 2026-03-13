# IAM Assume Role Policy (Trust Policy)
data "aws_iam_policy_document" "assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = [var.trusted_principal_arn]
    }
  }

  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["bedrock.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [var.account_id]
    }

    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = ["arn:aws:bedrock:${var.aws_region}:${var.account_id}:knowledge-base/*"]
    }
  }
}


# IAM Permission Policy
data "aws_iam_policy_document" "policy" {

  statement {
    sid     = "BedrockInvokeModelPermission"
    effect  = "Allow"
    actions = ["bedrock:InvokeModel"]
    resources = [
      "arn:aws:bedrock:${var.aws_region}::foundation-model/amazon.titan-embed-text-v2:0"
    ]
  }

  statement {
    sid    = "S3VectorsAccessPermission"
    effect = "Allow"
    actions = [
      "s3vectors:GetIndex",
      "s3vectors:QueryVectors",
      "s3vectors:PutVectors",
      "s3vectors:GetVectors",
      "s3vectors:DeleteVectors"
    ]
    resources = [
      "arn:aws:s3vectors:${var.aws_region}:${var.account_id}:bucket/${var.vector_bucket_name}/index/${var.vector_index_name}"
    ]
    condition {
      test     = "StringEquals"
      variable = "aws:ResourceAccount"
      values   = [var.account_id]
    }
  }

  statement {
    sid    = "CreateKB"
    effect = "Allow"
    actions = [
      "bedrock:CreateKnowledgeBase"
    ]
    resources = ["*"]
  }

  statement {
    sid    = "KBDataSourceManagement"
    effect = "Allow"
    actions = [
      "bedrock:GetKnowledgeBase",
      "bedrock:ListKnowledgeBases",
      "bedrock:UpdateKnowledgeBase",
      "bedrock:DeleteKnowledgeBase",
      "bedrock:StartIngestionJob",
      "bedrock:GetIngestionJob",
      "bedrock:ListIngestionJobs",
      "bedrock:StopIngestionJob",
      "bedrock:TagResource",
      "bedrock:UntagResource"
    ]
    resources = [
      "arn:aws:bedrock:${var.aws_region}:${var.account_id}:knowledge-base/*"
    ]
  }
}

# IAM Role
resource "aws_iam_role" "this" {
  name               = var.role_name
  assume_role_policy = data.aws_iam_policy_document.assume_role.json

  tags = {
    ManagedBy = "Terraform"
  }
}


# IAM Policy
resource "aws_iam_policy" "this" {
  name        = "${var.role_name}-policy"
  description = "Policy granting Bedrock, S3, and S3 Vectors access"
  policy      = data.aws_iam_policy_document.policy.json
}


# Attach Policy to Role
resource "aws_iam_role_policy_attachment" "this" {
  role       = aws_iam_role.this.name
  policy_arn = aws_iam_policy.this.arn
}
