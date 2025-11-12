variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "hokm-ai"
}

variable "environment" {
  description = "Environment (production, staging)"
  type        = string
  default     = "production"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-central-1"
}

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  default     = "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"
  sensitive   = true
}


variable "secret_key" {
  description = "JWT secret key"
  type        = string
  default     = "yLYyqgJE5sayLwdljIRJa9M73EcQHZYIdS70HFwNZcKo"
  sensitive   = true
}
