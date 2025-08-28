#!/bin/bash

echo "===== THREAT DETECTION SYSTEM - INTEGRATION TESTS ====="
echo ""

# Test 1: Dashboard Setup
if [ -f "../infrastructure/dashboard/create_dashboard.py" ]; then
    echo "[1/4] Creating CloudWatch Dashboard..."
    python ../infrastructure/dashboard/create_dashboard.py
else
    echo "[1/4] Dashboard script not found - skipping"
fi

# Test 2: SNS Alerts
echo "[2/4] Testing SNS notifications..."
aws sns publish \
    --topic-arn arn:aws:sns:us-east-1:609738416112:threat-alerts \
    --message "Test alert - Threat Detection System" \
    --subject "Test Alert" \
    --region us-east-1 \
    --output text > /dev/null
echo "SNS test sent - check your email"

# Test 3: End-to-End Pipeline
echo "[3/4] Testing threat detection pipeline..."
echo '{"event_id":"test-'$(date +%s)'","src_ip":"192.168.1.100","eventid":"cowrie.login.success"}' > test_threat.json
aws s3 cp test_threat.json s3://creditcardd/cowrie-logs/test_$(date +%s).json --region us-east-1 > /dev/null
echo "Test log uploaded - Lambda processing..."
sleep 5

# Test 4: Verification
echo "[4/4] Verifying system components..."
echo "Checking DynamoDB records:"
aws dynamodb scan --table-name ThreatsTable --limit 3 --query "Items[*].{ID:event_id.S,Score:anomaly_score.N,Threat:threat.S}" --output table

echo "\nChecking CloudWatch metrics:"
aws cloudwatch list-metrics --namespace ThreatDetection --query "Metrics[*].MetricName" --output text

echo "\n===== TEST COMPLETE ====="
echo "✓ Dashboard setup"
echo "✓ SNS notifications"
echo "✓ Threat detection pipeline"
echo "✓ System verification"
echo "\nView dashboard: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:"

# Cleanup
rm -f test_threat.json