variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "moaen-ai"
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

variable "deepseek_api_key" {
  description = "DeepSeek API key"
  type        = string
  default     = "sk-9e4b48ede22f41e1b548b771ca1cc4ea"
  sensitive   = true
}

variable "secret_key" {
  description = "JWT secret key"
  type        = string
  default     = "yLYyqgJE5sayLwdljIRJa9M73EcQHZYIdS70HFwNZcKo"
  sensitive   = true
}
