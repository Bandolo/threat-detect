# Threat Detection System with AWS Bedrock and Pinecone

Automated threat detection system using a honeypot, AWS Bedrock for AI analysis, and Pinecone for vector storage.

## Architecture

```
Honeypot → S3 → Lambda → Bedrock (Claude) → Pinecone + DynamoDB
```

1. **Honeypot (Cowrie)** captures attack data
2. **S3 uploads** trigger Lambda processing
3. **Claude AI** analyzes threat severity and type
4. **Pinecone** stores vectors for similarity search
5. **DynamoDB** stores detailed threat analysis

## Prerequisites

- AWS Account with Lambda, S3, DynamoDB, Bedrock, IAM, EC2 access
- Pinecone account with an index named `docqa-index`
- AWS CLI configured
- Node.js and npm (for Serverless Framework)
- Python 3.11

## Quick Start

### 1. Setup Infrastructure

```bash
# Create S3 bucket
aws s3 mb s3://creditcardd --region us-east-1
aws s3api put-bucket-versioning --bucket creditcardd --versioning-configuration Status=Enabled

# Create DynamoDB table
aws dynamodb create-table --table-name ThreatsTable \
    --attribute-definitions AttributeName=event_id,AttributeType=S \
    --key-schema AttributeName=event_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST

# Store Pinecone API key
aws secretsmanager create-secret --name pinecone/credentials \
    --secret-string '{"apiKey":"YOUR_PINECONE_API_KEY"}'
```

### 2. Deploy Lambda Function

```bash
# Install dependencies
npm install -g serverless
npm install --save-dev serverless-python-requirements

# Deploy
npx sls deploy
```

### 3. Launch Honeypot

```bash
# Launch EC2 instance with Cowrie
aws ec2 run-instances \
    --image-id ami-0c7217cdde317cfec \
    --instance-type t2.micro \
    --key-name YOUR_KEY_PAIR \
    --security-group-ids sg-XXXXXXXXXX \
    --user-data file://cowrie-simple-setup.sh \
    --iam-instance-profile Name=HoneypotS3Profile
```

## Testing

```bash
# Verify honeypot setup
ssh -i ~/.ssh/keys/YOUR_KEY_PAIR.pem ubuntu@YOUR_EC2_IP
sudo -u cowrie /home/cowrie/cowrie/bin/cowrie status

# Simulate an attack
ssh -p 2222 root@YOUR_EC2_IP  # Try various passwords

# Check results
aws s3 ls s3://creditcardd/cowrie-logs/
aws dynamodb scan --table-name ThreatsTable --limit 5 --output text

# Run unit tests
pytest
```

## Enhanced Features

### Alerting & Visualization

- **SNS Alerts** for high-severity threats (threshold: 75)
  ```bash
  aws sns create-topic --name threat-alerts
  aws sns subscribe --topic-arn arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:threat-alerts \
      --protocol email --notification-endpoint your-email@example.com
  ```

- **CloudWatch Dashboard** for metrics visualization
  ```bash
  python dashboard/create_dashboard.py
  ```

### Metrics & Monitoring

- **Custom Metrics**: Invocation time, token usage, cost estimates
- **CloudWatch Alarms**: Cost thresholds, Lambda errors, high-severity threats
  ```bash
  python dashboard/create_alarms.py
  ```

### Testing Scripts

- `test_all.sh` - Comprehensive system test
- `test_high_severity.sh` - Tests threat detection
- `test_sns.sh` - Tests notifications
- `test-honeypot.sh` - Verifies honeypot setup

## Project Structure

- `bedrock_handler/` - AI analysis code
- `pinecone_handler/` - Vector storage code
- `prototype/` - Utility code
- `payloads/` - Test data
- `tests/` - Unit tests
- `dashboard/` - CloudWatch resources
- `serverless.yml` - Deployment config

## Cleanup

```bash
npx sls remove
aws ec2 terminate-instances --instance-ids YOUR_INSTANCE_ID
aws dynamodb delete-table --table-name ThreatsTable
aws s3 rm s3://creditcardd --recursive
aws s3api delete-bucket --bucket creditcardd
```

## Troubleshooting

- **S3 Access Denied**: Check IAM permissions for both `s3:GetObject` and `s3:ListBucket`
- **SNS Issues**: Check spam folder, verify subscription confirmation
- **Missing Metrics**: Ensure Lambda has `cloudwatch:PutMetricData` permission

For detailed documentation, see the `docs/` directory.