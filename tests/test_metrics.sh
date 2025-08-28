#!/bin/bash

# Check if CloudWatch metrics exist
echo "Checking CloudWatch metrics..."
aws cloudwatch list-metrics \
    --namespace ThreatDetection \
    --region us-east-1 \
    --output text

echo ""
echo "Getting statistics for Bedrock invocation count..."
aws cloudwatch get-metric-statistics \
    --namespace ThreatDetection \
    --metric-name BedrockInvocationCount \
    --statistics Sum \
    --period 3600 \
    --start-time "$(date -u -v-1d +"%Y-%m-%dT%H:%M:%SZ")" \
    --end-time "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
    --region us-east-1 \
    --output table

echo ""
echo "Getting statistics for Bedrock invocation time..."
aws cloudwatch get-metric-statistics \
    --namespace ThreatDetection \
    --metric-name BedrockInvocationTime \
    --statistics Average \
    --period 3600 \
    --start-time "$(date -u -v-1d +"%Y-%m-%dT%H:%M:%SZ")" \
    --end-time "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
    --region us-east-1 \
    --output table

echo ""
echo "Getting statistics for Bedrock estimated cost..."
aws cloudwatch get-metric-statistics \
    --namespace ThreatDetection \
    --metric-name BedrockEstimatedCost \
    --statistics Sum \
    --period 86400 \
    --start-time "$(date -u -v-1d +"%Y-%m-%dT%H:%M:%SZ")" \
    --end-time "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
    --region us-east-1 \
    --output table