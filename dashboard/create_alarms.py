import boto3
import json
import os

# Initialize CloudWatch client
cloudwatch = boto3.client('cloudwatch')

# Get AWS account ID
sts = boto3.client('sts')
account_id = sts.get_caller_identity()['Account']

# SNS topic ARN
sns_topic_arn = f"arn:aws:sns:us-east-1:{account_id}:threat-alerts"

# Create alarms
alarms = [
    {
        "name": "HighBedrockCost",
        "description": "Alarm when Bedrock cost exceeds threshold",
        "namespace": "ThreatDetection",
        "metric_name": "BedrockEstimatedCost",
        "statistic": "Sum",
        "period": 86400,  # 1 day
        "threshold": 5.0,
        "comparison": "GreaterThanThreshold",
        "evaluation_periods": 1
    },
    {
        "name": "LambdaErrors",
        "description": "Alarm when Lambda has errors",
        "namespace": "AWS/Lambda",
        "metric_name": "Errors",
        "dimensions": [
            {
                "Name": "FunctionName",
                "Value": "threat-detect-bedrock-dev-threatAnalyzer"
            }
        ],
        "statistic": "Sum",
        "period": 300,  # 5 minutes
        "threshold": 1.0,
        "comparison": "GreaterThanOrEqualToThreshold",
        "evaluation_periods": 1
    },
    {
        "name": "HighSeverityThreats",
        "description": "Alarm when high severity threats are detected",
        "namespace": "ThreatDetection",
        "metric_name": "HighSeverityThreatCount",
        "statistic": "Sum",
        "period": 300,  # 5 minutes
        "threshold": 1.0,
        "comparison": "GreaterThanOrEqualToThreshold",
        "evaluation_periods": 1
    }
]

# Create each alarm
for alarm in alarms:
    try:
        params = {
            "AlarmName": alarm["name"],
            "AlarmDescription": alarm["description"],
            "MetricName": alarm["metric_name"],
            "Namespace": alarm["namespace"],
            "Statistic": alarm["statistic"],
            "Period": alarm["period"],
            "Threshold": alarm["threshold"],
            "ComparisonOperator": alarm["comparison"],
            "EvaluationPeriods": alarm["evaluation_periods"],
            "AlarmActions": [sns_topic_arn]
        }
        
        # Add dimensions if present
        if "dimensions" in alarm:
            params["Dimensions"] = alarm["dimensions"]
            
        cloudwatch.put_metric_alarm(**params)
        print(f"Created alarm: {alarm['name']}")
    except Exception as e:
        print(f"Error creating alarm {alarm['name']}: {e}")

print("\nAlarms setup complete!")
print(f"Notifications will be sent to SNS topic: {sns_topic_arn}")
print("You can view alarms in the CloudWatch console: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#alarmsV2:?")