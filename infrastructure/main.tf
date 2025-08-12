terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }

}

provider "aws" {
  region = var.aws_region
  profile = "newaccount"  # Add this line
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

provider "aws" {
  alias   = "us_east_1"
  region  = "us-east-1"
  profile = "newaccount"  # (both providers)
  
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}


data "aws_availability_zones" "available" {
  state = "available"
}

resource "random_password" "database_password" {
  length  = 32
  special = false
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "${var.project_name}-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = {
    Name = "${var.project_name}-igw"
  }
}

# Public Subnets
resource "aws_subnet" "public" {
  count = 2
  
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  
  tags = {
    Name = "${var.project_name}-public-subnet-${count.index + 1}"
  }
}

# Private Subnets
resource "aws_subnet" "private" {
  count = 2
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name = "${var.project_name}-private-subnet-${count.index + 1}"
  }
}

# Database Subnets
resource "aws_subnet" "database" {
  count = 2
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 20}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name = "${var.project_name}-database-subnet-${count.index + 1}"
  }
}

# Route Tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.project_name}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count = 2

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Security Groups
resource "aws_security_group" "rds" {
  name_prefix = "${var.project_name}-rds"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  tags = {
    Name = "${var.project_name}-rds-sg"
  }
}

# Database Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = aws_subnet.database[*].id
  
  tags = {
    Name = "${var.project_name}-db-subnet-group"
  }
}

# PostgreSQL Database
resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-database"
  
  engine         = "postgres"
  engine_version = "15.8"
  instance_class = "db.t4g.micro"
  
  db_name  = "arabic_legal_db"
  username = "postgres"
  password = random_password.database_password.result
  
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp3"
  storage_encrypted     = true
  
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  deletion_protection = false
  skip_final_snapshot = true
  
  tags = {
    Name = "${var.project_name}-database"
  }
}

# Secrets Manager
resource "aws_secretsmanager_secret" "database" {
  name = "${var.project_name}/database"
  
  tags = {
    Name = "${var.project_name}-database-secret"
  }
}

resource "aws_secretsmanager_secret_version" "database" {
  secret_id = aws_secretsmanager_secret.database.id
  secret_string = jsonencode({
    username = aws_db_instance.main.username
    password = random_password.database_password.result
    host     = aws_db_instance.main.endpoint
    port     = aws_db_instance.main.port
    dbname   = aws_db_instance.main.db_name
  })
}

resource "aws_secretsmanager_secret" "app_secrets" {
  name = "${var.project_name}/app"
  
  tags = {
    Name = "${var.project_name}-app-secrets"
  }
}

resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    secret_key     = var.secret_key
    openai_api_key = var.openai_api_key
  })
}

# S3 Frontend Bucket
resource "aws_s3_bucket" "frontend" {
  bucket = "${var.project_name}-frontend-${random_id.bucket_suffix.hex}"
}

# Keep website configuration but it won't be used directly
resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  index_document {
    suffix = "index.html"
  }
  error_document {
    key = "index.html"
  }
}

# Block public access to S3 (security best practice)
resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  block_public_acls       = true
  block_public_policy     = true  
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Origin Access Identity for CloudFront
resource "aws_cloudfront_origin_access_identity" "frontend" {
  comment = "Frontend CloudFront OAI for ${var.project_name}"
}

# CloudFront Distribution with FREE SSL
resource "aws_cloudfront_distribution" "frontend" {
  origin {
    domain_name = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.frontend.bucket}"
    
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.frontend.cloudfront_access_identity_path
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  aliases = ["hokm.ai", "www.hokm.ai"]

  default_cache_behavior {
    target_origin_id       = "S3-${aws_s3_bucket.frontend.bucket}"
    viewer_protocol_policy = "redirect-to-https"  # Forces HTTPS!
    
    allowed_methods = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods  = ["GET", "HEAD"]
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
    
    min_ttl     = 0
    default_ttl = 86400
    max_ttl     = 31536000
  }

  viewer_certificate {
  acm_certificate_arn      = aws_acm_certificate_validation.frontend_cert.certificate_arn
  ssl_support_method       = "sni-only"
  minimum_protocol_version = "TLSv1.2_2021"
}

  # Handle React Router (SPA) - redirect 404s to index.html
  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }

  

  # No geographic restrictions
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  tags = {
    Name        = "${var.project_name}-frontend-cdn"
    Environment = var.environment
  }

 depends_on = [aws_acm_certificate_validation.frontend_cert]

}

# S3 bucket policy - only allow CloudFront access
resource "aws_s3_bucket_policy" "frontend_policy" {
  bucket = aws_s3_bucket.frontend.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowCloudFrontAccess"
        Effect = "Allow"
        Principal = {
          AWS = aws_cloudfront_origin_access_identity.frontend.iam_arn
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.frontend.arn}/*"
      }
    ]
  })
}

# Add this to your main.tf after the existing CloudFront distribution

# CloudFront Distribution for Backend API (HTTPS)
resource "aws_cloudfront_distribution" "backend" {
  origin {
    domain_name = aws_lb.main.dns_name
    origin_id   = "ALB-${var.project_name}-backend"
    
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  enabled = true
  is_ipv6_enabled = true

  # Cache behavior for API endpoints
  default_cache_behavior {
    target_origin_id       = "ALB-${var.project_name}-backend"
    viewer_protocol_policy = "redirect-to-https"  # Force HTTPS
    
    allowed_methods = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods  = ["GET", "HEAD", "OPTIONS"]
    
    forwarded_values {
      query_string = true  # Forward query parameters
      headers      = ["*"] # Forward all headers for API
      cookies {
        forward = "all"    # Forward cookies for authentication
      }
    }
    
    # No caching for API responses (always fresh)
    min_ttl     = 0
    default_ttl = 0
    max_ttl     = 0
  }

  # Specific cache behavior for health check (can be cached)
  ordered_cache_behavior {
    path_pattern     = "/"
    target_origin_id = "ALB-${var.project_name}-backend"
    viewer_protocol_policy = "redirect-to-https"
    
    allowed_methods = ["GET", "HEAD"]
    cached_methods  = ["GET", "HEAD"]
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
    
    min_ttl     = 300    # Cache health check for 5 minutes
    default_ttl = 300
    max_ttl     = 3600
  }

  # Use CloudFront's free SSL certificate
  viewer_certificate {
  cloudfront_default_certificate = true
}

  # No geographic restrictions
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  tags = {
    Name        = "${var.project_name}-backend-cdn"
    Environment = var.environment
  }
  
}

# Output the backend CloudFront domain
output "backend_cloudfront_url" {
  description = "HTTPS URL for backend API"
  value       = "https://${aws_cloudfront_distribution.backend.domain_name}"
}






# Security Groups for Load Balancer
resource "aws_security_group" "alb" {
  name_prefix = "${var.project_name}-alb"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-alb-sg"
  }
}

# Security Group for ECS
resource "aws_security_group" "ecs" {
  name_prefix = "${var.project_name}-ecs"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-ecs-sg"
  }
}

# ECR Repository
resource "aws_ecr_repository" "backend" {
  name                 = "${var.project_name}/backend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "${var.project_name}-backend-ecr"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name = "${var.project_name}-cluster"
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = false

  tags = {
    Name = "${var.project_name}-alb"
  }
}

# Target Group
resource "aws_lb_target_group" "backend" {
  name        = "${var.project_name}-backend-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = {
    Name = "${var.project_name}-backend-tg"
  }
}

# Load Balancer Listener
resource "aws_lb_listener" "backend" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }
}

# IAM Roles for ECS
resource "aws_iam_role" "ecs_task_execution" {
  name = "${var.project_name}-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "ecs_secrets" {
  name = "${var.project_name}-ecs-secrets-policy"
  role = aws_iam_role.ecs_task_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          aws_secretsmanager_secret.database.arn,
          aws_secretsmanager_secret.app_secrets.arn
        ]
      }
    ]
  })
}

# ECS Task Role
resource "aws_iam_role" "ecs_task" {
  name = "${var.project_name}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/${var.project_name}/backend"
  retention_in_days = 30

  tags = {
    Name = "${var.project_name}-backend-logs"
  }
}

output "cloudfront_url" {
  description = "HTTPS URL for mobile access - USE THIS INSTEAD OF S3"
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}





# ECS Task Definition
resource "aws_ecs_task_definition" "backend" {
  family                   = "${var.project_name}-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn           = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name  = "backend-container"
      image = "${aws_ecr_repository.backend.repository_url}:latest"
      
      essential = true
      
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]
      
      environment = [
        {
          name  = "ENVIRONMENT"
          value = "production"
        },
        {
          name  = "AI_PROVIDER"
          value = "openai"
        },
        {
          name  = "CORS_ORIGINS"
          value = "https://hokm.ai,https://www.hokm.ai,https://${aws_cloudfront_distribution.frontend.domain_name},https://${aws_cloudfront_distribution.backend.domain_name},http://localhost:3000"
        }
      ]
      
      secrets = [
        {
          name      = "DB_PASSWORD"
          valueFrom = "${aws_secretsmanager_secret.database.arn}:password::"
        },
        {
          name      = "SECRET_KEY"
          valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:secret_key::"
        },
        {
          name      = "OPENAI_API_KEY"
          valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:openai_api_key::"
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.backend.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "backend"
        }
      }
    }
  ])
}

# ECS Service
resource "aws_ecs_service" "backend" {
  name            = "${var.project_name}-backend-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

 network_configuration {
  subnets          = aws_subnet.public[*].id
  security_groups  = [aws_security_group.ecs.id]
  assign_public_ip = true
}

  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "backend-container"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.backend]
}




resource "aws_route53_zone" "main" {
  name = "hokm.ai"
  
  tags = {
    Name = "${var.project_name}-hosted-zone"
  }
}


output "name_servers" {
  description = "Configure these at Spaceship NOW"
  value       = aws_route53_zone.main.name_servers
}

# SSL Certificate for hokm.ai
resource "aws_acm_certificate" "frontend_cert" {
  provider          = aws.us_east_1
  domain_name       = "hokm.ai"
  subject_alternative_names = ["www.hokm.ai"]
  validation_method = "DNS"
  
  lifecycle {
    create_before_destroy = true
  }
  
  tags = {
    Name = "${var.project_name}-frontend-cert"
  }
}

# Certificate validation records
resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.frontend_cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }
  
  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = aws_route53_zone.main.zone_id
}

# Certificate validation
resource "aws_acm_certificate_validation" "frontend_cert" {
  provider                = aws.us_east_1
  certificate_arn         = aws_acm_certificate.frontend_cert.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
}

# DNS Records for hokm.ai
resource "aws_route53_record" "frontend_a" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "hokm.ai"
  type    = "A"
  
  alias {
    name                   = aws_cloudfront_distribution.frontend.domain_name
    zone_id                = aws_cloudfront_distribution.frontend.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "frontend_www" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "www.hokm.ai"
  type    = "A"
  
  alias {
    name                   = aws_cloudfront_distribution.frontend.domain_name
    zone_id                = aws_cloudfront_distribution.frontend.hosted_zone_id
    evaluate_target_health = false
  }
}





