# HealthData Gateway - AWS Deployment Guide

This document provides instructions for deploying the HealthData Gateway application to AWS.

## Prerequisites

Before deployment, ensure you have the following:

1. **AWS Account** with necessary permissions
2. **AWS CLI** installed and configured
3. **Python 3.8+** installed
4. **Git** for version control

## Required Dependencies

Install all required dependencies:

```bash
pip install -r requirements.txt
```

The requirements.txt file includes:
- fastapi
- uvicorn
- web3
- python-dotenv
- pyjwt
- fhir.resources
- boto3 (for AWS integration)

## Environment Configuration

Create a `.env` file based on the `.env.example` template with all required environment variables:

```
# API Configuration
API_PORT=8000
API_HOST=0.0.0.0
DEBUG_MODE=False

# Blockchain Configuration
BLOCKCHAIN_PROVIDER="https://your-blockchain-provider.com"
CONTRACT_ADDRESS_CONSENT="0xYourConsentContractAddress"
CONTRACT_ADDRESS_REWARDS="0xYourRewardsContractAddress"
PRIVATE_KEY="YourPrivateKeyHere"

# AWS Configuration
AWS_REGION="us-east-1"
AWS_ACCESS_KEY_ID="YourAccessKeyID"
AWS_SECRET_ACCESS_KEY="YourSecretAccessKey"

# Security Configuration
JWT_SECRET_KEY="YourJWTSecretKey"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_MINUTES=60

# Integration Keys
HEALTHDATA_REWARDS_API_KEY="YourHealthDataRewardsAPIKey"
OAUTH2_CLIENT_ID="YourOAuth2ClientID"
OAUTH2_CLIENT_SECRET="YourOAuth2ClientSecret"
```

**IMPORTANT**: Never commit the actual `.env` file to version control. Only use `.env.example` with placeholder values.

## AWS Deployment Steps

### 1. Set Up AWS Resources

#### Create an EC2 Instance

1. Launch a new EC2 instance (recommended: t2.medium or larger)
2. Choose Amazon Linux 2023 or Ubuntu Server 22.04 LTS
3. Configure security groups to allow:
   - SSH (port 22)
   - HTTP (port 80)
   - HTTPS (port 443)
   - Application port (default: 8000)

#### Set Up RDS (Optional for Database)

If using a managed database:

1. Create an RDS instance (PostgreSQL recommended)
2. Configure security group to allow access from your EC2 instance
3. Update your environment variables with database connection details

### 2. Deploy Application

#### Clone Repository

```bash
git clone https://github.com/your-repo/HealthDataGateway.git
cd HealthDataGateway
```

#### Set Up Environment

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your production values
```

#### Configure Nginx (Optional)

For production, it's recommended to use Nginx as a reverse proxy:

```bash
sudo apt-get install nginx
```

Create an Nginx configuration file:

```
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

#### Set Up SSL with Let's Encrypt (Recommended)

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. Run the Application

#### Using systemd for Production

Create a systemd service file:

```
[Unit]
Description=HealthData Gateway
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/path/to/HealthDataGateway
ExecStart=/path/to/HealthDataGateway/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always
Environment="PATH=/path/to/HealthDataGateway/venv/bin"
EnvironmentFile=/path/to/HealthDataGateway/.env

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable healthdata-gateway
sudo systemctl start healthdata-gateway
```

### 4. Integration with HealthData Rewards

Follow these steps to integrate with HealthData Rewards:

1. Obtain OAuth2 credentials from HealthData Rewards platform
2. Update your `.env` file with the OAuth2 client ID and secret
3. Configure the callback URL in the HealthData Rewards admin portal
4. Verify integration by running integration tests:

```bash
python test_core_functions.py
```

### 5. Monitoring and Maintenance

#### Set Up CloudWatch (Recommended)

1. Install CloudWatch agent:
   ```bash
   sudo amazon-linux-extras install collectd
   sudo amazon-linux-extras install aws-cli
   sudo yum install amazon-cloudwatch-agent
   ```

2. Configure CloudWatch agent to monitor:
   - System metrics (CPU, memory, disk)
   - Application logs
   - Custom metrics

#### Regular Maintenance

1. Create a backup strategy for your data
2. Set up alerts for system anomalies
3. Implement a log rotation policy
4. Plan for regular security updates

## Security Considerations

1. **Enable AWS WAF** to protect against common web exploits
2. **Use IAM roles** with least privilege principle
3. **Regularly update** all system packages
4. **Monitor security groups** and network access
5. **Implement API rate limiting** to prevent abuse
6. **Enable multi-factor authentication** for AWS accounts

## Troubleshooting

Common issues and solutions:

1. **Application won't start**: Check logs in `/var/log/healthdata-gateway.log`
2. **Connectivity issues**: Verify security groups and network settings
3. **Database connection failures**: Check RDS status and connection strings
4. **Blockchain integration errors**: Verify contract addresses and private keys

For more assistance, refer to the project documentation or contact the development team.
