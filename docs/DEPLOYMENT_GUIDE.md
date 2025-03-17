# HealthData Gateway Deployment Guide

This guide explains how to deploy the HealthData Gateway application to AWS and set up the CI/CD pipeline using GitHub Actions.

## Prerequisites

- AWS Account with proper IAM permissions
- GitHub repository access with admin rights
- Docker and Docker Compose installed locally

## Setting Up AWS Resources

### 1. EC2 Instance Setup

1. Launch an EC2 instance with Ubuntu Server 22.04 LTS
2. Select an appropriate instance type (recommended: t3.medium or higher for production)
3. Configure security groups to allow:
   - SSH (port 22)
   - HTTP (port 80)
   - HTTPS (port 443)
   - Application port (8000)
4. Create and download the SSH key pair (.pem file)

### 2. Configure the EC2 Instance

SSH into your EC2 instance:

```bash
ssh -i /path/to/your-key.pem ubuntu@your-ec2-public-dns
```

Install Docker and Docker Compose:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose git
sudo usermod -aG docker ubuntu
```

Clone the repository:

```bash
git clone https://github.com/your-username/HealthDataGateway.git ~/HealthDataGateway
```

### 3. Set Up Amazon ECR

1. Go to AWS ECR console
2. Create a new repository named `healthdata-gateway`
3. Note the repository URI for later use

## Setting Up GitHub Actions Secrets

Add the following secrets to your GitHub repository:

1. `AWS_ACCESS_KEY_ID`: Your AWS access key ID with ECR and EC2 permissions
2. `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key
3. `EC2_HOST`: Your EC2 instance's public DNS or IP
4. `EC2_USERNAME`: `ubuntu` (or your custom username)
5. `EC2_SSH_KEY`: The contents of your EC2 SSH key (the private key)
6. For production, also add:
   - `PROD_EC2_HOST`
   - `PROD_EC2_USERNAME`
   - `PROD_EC2_SSH_KEY`

To add the SSH key as a secret:

1. Open the .pem file in a text editor
2. Copy the entire contents
3. Paste the contents into the GitHub secret value field

## Using the CI/CD Pipeline

### Automated Deployments

The pipeline will automatically deploy:
- To staging when pushing to the `main` branch
- To production when manually triggered with the "production" environment selected

### Manual Deployments

To manually trigger a deployment:

1. Go to the "Actions" tab in your GitHub repository
2. Select the "HealthData Gateway CI/CD Pipeline" workflow
3. Click "Run workflow"
4. Select the branch and environment
5. Click "Run workflow"

## Monitoring Deployments

- Check the GitHub Actions logs for deployment status
- SSH into the EC2 instance to view logs:
  ```bash
  ssh -i /path/to/your-key.pem ubuntu@your-ec2-public-dns
  cd ~/HealthDataGateway
  docker-compose logs -f
  ```

## Troubleshooting

### Common Issues

1. **Permission Denied**: Check that the SSH key secret is correct and properly formatted
2. **Docker Permissions**: Make sure the EC2 user is in the docker group
3. **Port Conflicts**: Ensure ports 8000 and 8001 are not in use by other applications
4. **AWS Credentials**: Verify the AWS credentials have the necessary permissions

### Health Checks

Access the health endpoint to verify the application is running:

```bash
curl http://your-ec2-public-dns:8000/health
```

## Security Considerations

- Keep your AWS credentials secure
- Regularly rotate AWS access keys
- Use proper IAM roles with least privileges
- Implement proper security monitoring
- Consider using AWS Secrets Manager for sensitive data
