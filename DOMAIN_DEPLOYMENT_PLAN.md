# hokm.ai Domain Configuration - Deployment Plan

## 🎯 Overview
Configure root domain `hokm.ai` with AWS infrastructure using Route 53, ACM certificates, and CloudFront distributions.

## ✅ Completed Changes

### 1. Terraform Infrastructure Updates
- ✅ Added us-east-1 AWS provider for CloudFront certificates
- ✅ Created Route 53 hosted zone for hokm.ai
- ✅ Added ACM certificate with DNS validation for hokm.ai and *.hokm.ai
- ✅ Updated CloudFront distributions with custom domain aliases:
  - Frontend: hokm.ai, www.hokm.ai
  - Backend: api.hokm.ai
- ✅ Added Route 53 ALIAS records pointing to CloudFront distributions
- ✅ Updated CORS configuration for new domains

### 2. Frontend API Configuration
- ✅ Updated API base URL to use `https://api.hokm.ai` for production

## 🚀 Deployment Steps

### Phase 1: Infrastructure Deployment
```bash
cd infrastructure
terraform plan -out=domain-plan.tfplan
terraform apply domain-plan.tfplan
```

**Expected Resources:**
- Route 53 hosted zone
- ACM certificate (auto-validated via DNS)
- Updated CloudFront distributions
- DNS records (A records with ALIAS)

### Phase 2: Domain Registrar Configuration
**CRITICAL**: Update nameservers at your domain registrar with the Route 53 nameservers:
```bash
terraform output nameservers
```

### Phase 3: Frontend Deployment
```bash
cd frontend
npm run build
aws s3 sync dist/ s3://your-frontend-bucket/ --delete
aws cloudfront create-invalidation --distribution-id YOUR_FRONTEND_DIST_ID --paths "/*"
```

### Phase 4: Backend Deployment
```bash
cd backend
# Build and push new image with updated CORS
docker build -t hokm-ai-backend .
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin YOUR_ECR_URI
docker tag hokm-ai-backend:latest YOUR_ECR_URI:latest
docker push YOUR_ECR_URI:latest

# Update ECS service
aws ecs update-service --cluster hokm-ai-cluster --service hokm-ai-backend-service --force-new-deployment
```

## 🔍 Validation Checklist

### DNS Propagation (24-48 hours)
- [ ] `dig hokm.ai` returns CloudFront IP
- [ ] `dig www.hokm.ai` returns CloudFront IP  
- [ ] `dig api.hokm.ai` returns CloudFront IP

### SSL Certificate
- [ ] `https://hokm.ai` shows valid SSL certificate
- [ ] `https://www.hokm.ai` shows valid SSL certificate
- [ ] `https://api.hokm.ai` shows valid SSL certificate

### Application Functionality
- [ ] Frontend loads at `https://hokm.ai`
- [ ] API endpoints work at `https://api.hokm.ai`
- [ ] CORS allows requests from hokm.ai domains
- [ ] Authentication flows work correctly

### Performance & Caching
- [ ] CloudFront caching working for static assets
- [ ] API responses not cached (TTL=0)
- [ ] Gzip compression enabled

## 🛠 Troubleshooting

### Certificate Issues
```bash
# Check certificate status
aws acm describe-certificate --certificate-arn YOUR_CERT_ARN

# Force certificate renewal if needed
aws acm resend-validation-email --certificate-arn YOUR_CERT_ARN
```

### DNS Issues
```bash
# Check Route 53 records
aws route53 list-resource-record-sets --hosted-zone-id YOUR_ZONE_ID

# Test DNS propagation
dig @8.8.8.8 hokm.ai
nslookup hokm.ai
```

### CloudFront Issues
```bash
# Check distribution status
aws cloudfront get-distribution --id YOUR_DIST_ID

# Create invalidation
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

## 📊 Post-Deployment Monitoring

### Metrics to Watch
- CloudFront cache hit ratio
- SSL certificate expiry (auto-renewed)
- Route 53 health checks
- ECS service health

### Cost Impact
- **Route 53**: ~$0.50/month per hosted zone
- **ACM Certificate**: FREE
- **CloudFront**: Pay-per-use (minimal for typical traffic)
- **No additional compute costs**

## 🔒 Security Considerations

### SSL/TLS
- TLS 1.2+ enforced
- HSTS headers recommended
- Secure cookie settings

### CORS
- Restricted to hokm.ai domains only
- No wildcard origins in production

### DNS Security
- DNSSEC can be enabled post-deployment
- Regular certificate monitoring

---

**Next Steps After Deployment:**
1. Update any hardcoded URLs in documentation
2. Update monitoring/alerting for new domains
3. Consider setting up www.hokm.ai → hokm.ai redirect if preferred
4. Update Google Analytics/search console for new domain