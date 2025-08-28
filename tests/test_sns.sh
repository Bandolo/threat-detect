#!/bin/bash

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