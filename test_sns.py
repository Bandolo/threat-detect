import json
import os
import boto3
from unittest.mock import MagicMock, patch

# Set environment variables for testing
os.environ["SNS_TOPIC_ARN"] = "arn:aws:sns:us-east-1:123456789012:test-topic"
os.environ["SEVERITY_THRESHOLD"] = "75"

# Import the handler after setting environment variables
from pinecone_handler.handler import handler

# Create a mock event
with open('payloads/s3_event.json', 'r') as f:
    event = json.load(f)

# Create a mock log
with open('payloads/high_severity_log.json', 'r') as f:
    high_severity_log = json.load(f)

# Mock the S3 get_object response
s3_response = {
    "Body": MagicMock(read=lambda: json.dumps(high_severity_log).encode())
}

# Test the SNS notification functionality
@patch('boto3.client')
@patch('boto3.resource')
def test_sns_notification(mock_resource, mock_client):
    # Mock S3 client
    mock_s3 = MagicMock()
    mock_s3.get_object.return_value = s3_response
    
    # Mock SNS client
    mock_sns = MagicMock()
    
    # Mock DynamoDB resource and table
    mock_table = MagicMock()
    mock_dynamodb = MagicMock()
    mock_dynamodb.Table.return_value = mock_table
    
    # Mock Pinecone client
    mock_pinecone = MagicMock()
    mock_index = MagicMock()
    mock_pinecone.Index.return_value = mock_index
    
    # Set up the mock clients
    def get_client(service, **kwargs):
        if service == 's3':
            return mock_s3
        elif service == 'sns':
            return mock_sns
        elif service == 'secretsmanager':
            mock_secrets = MagicMock()
            mock_secrets.get_secret_value.return_value = {
                'SecretString': '{"apiKey":"test-api-key"}'
            }
            return mock_secrets
        return MagicMock()
    
    mock_client.side_effect = get_client
    mock_resource.return_value = mock_dynamodb
    
    # Mock the Pinecone client
    with patch('pinecone.Pinecone', return_value=mock_pinecone):
        # Call the handler
        print("Testing SNS notification for high severity threat...")
        result = handler(event, None)
        
        # Check if SNS publish was called
        if mock_sns.publish.called:
            print("Successful: SNS notification was sent")
            call_args = mock_sns.publish.call_args
            print(f"Topic ARN: {call_args[1]['TopicArn']}")
            print(f"Subject: {call_args[1]['Subject']}")
            print(f"Message: {call_args[1]['Message'][:100]}...")
        else:
            print("Failed: SNS notification was NOT sent")
        
        print("\nTest completed!")
        return result

# Run the test
if __name__ == "__main__":
    test_sns_notification()
