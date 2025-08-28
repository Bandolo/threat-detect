import boto3
import json

# Initialize CloudWatch client
cloudwatch = boto3.client('cloudwatch')

# Create dashboard
dashboard_name = 'ThreatDetectionDashboard'
dashboard_body = {
    "widgets": [
        {
            "type": "text",
            "x": 0,
            "y": 0,
            "width": 24,
            "height": 1,
            "properties": {
                "markdown": "# Threat Detection System Dashboard"
            }
        },
        {
            "type": "metric",
            "x": 0,
            "y": 1,
            "width": 12,
            "height": 6,
            "properties": {
                "metrics": [
                    [ "AWS/Lambda", "Invocations", "FunctionName", "threat-detect-bedrock-dev-threatAnalyzer" ],
                    [ ".", "Errors", ".", "." ],
                    [ ".", "Duration", ".", "." ]
                ],
                "view": "timeSeries",
                "stacked": False,
                "region": "us-east-1",
                "title": "Lambda Function Metrics",
                "period": 300
            }
        },
        {
            "type": "metric",
            "x": 12,
            "y": 1,
            "width": 12,
            "height": 6,
            "properties": {
                "metrics": [
                    [ "ThreatDetection", "BedrockInvocationCount", { "stat": "Sum" } ],
                    [ ".", "BedrockInvocationTime", { "stat": "Average" } ]
                ],
                "view": "timeSeries",
                "stacked": False,
                "region": "us-east-1",
                "title": "Bedrock API Usage",
                "period": 300
            }
        },
        {
            "type": "log",
            "x": 0,
            "y": 7,
            "width": 24,
            "height": 6,
            "properties": {
                "query": "SOURCE '/aws/lambda/threat-detect-bedrock-dev-threatAnalyzer' | fields @timestamp, @message\n| filter @message like /threat/\n| sort @timestamp desc\n| limit 20",
                "region": "us-east-1",
                "title": "Recent Threat Detections",
                "view": "table"
            }
        },
        {
            "type": "metric",
            "x": 0,
            "y": 13,
            "width": 12,
            "height": 6,
            "properties": {
                "metrics": [
                    [ "ThreatDetection", "BedrockEstimatedCost", { "stat": "Sum", "period": 86400 } ]
                ],
                "view": "timeSeries",
                "stacked": False,
                "region": "us-east-1",
                "title": "Daily Bedrock Cost Estimate",
                "period": 86400
            }
        },
        {
            "type": "metric",
            "x": 12,
            "y": 13,
            "width": 12,
            "height": 6,
            "properties": {
                "metrics": [
                    [ "AWS/S3", "NumberOfObjects", "BucketName", "creditcardd", "StorageType", "AllStorageTypes" ]
                ],
                "view": "timeSeries",
                "stacked": False,
                "region": "us-east-1",
                "title": "S3 Object Count",
                "period": 86400
            }
        }
    ]
}

# Create or update the dashboard
try:
    response = cloudwatch.put_dashboard(
        DashboardName=dashboard_name,
        DashboardBody=json.dumps(dashboard_body)
    )
    print(f"Dashboard '{dashboard_name}' created successfully!")
    print(f"Access it at: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name={dashboard_name}")
except Exception as e:
    print(f"Error creating dashboard: {e}")