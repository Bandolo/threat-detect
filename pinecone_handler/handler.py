import os
import json
import boto3
from datetime import datetime
from bedrock_handler.bedrock_stub import invoke_bedrock, invoke_embedding

def get_pinecone_client():
    """Get Pinecone client with API key from Secrets Manager"""
    import pinecone
    
    # Get API key from Secrets Manager
    secret_name = os.getenv("PINECONE_SECRET_NAME", "pinecone/credentials")
    region = os.getenv("AWS_REGION", "us-east-1")
    
    client = boto3.client('secretsmanager', region_name=region)
    response = client.get_secret_value(SecretId=secret_name)
    secret = json.loads(response['SecretString'])
    api_key = secret.get('apiKey')
    
    # Initialize Pinecone client
    pc = pinecone.Pinecone(api_key=api_key)
    return pc

def handler(event, context):
    """
    Lambda handler for processing S3 events.
    Analyzes logs with Bedrock and stores results in DynamoDB and Pinecone.
    """
    print(f"Processing event: {json.dumps(event)}")
    
    # Initialize AWS clients
    s3 = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb')
    table_name = os.getenv("THREATS_TABLE", "ThreatsTable")
    table = dynamodb.Table(table_name)
    
    # Process each record in the event
    results = []
    for record in event.get('Records', []):
        try:
            # Get the S3 object
            rec = record
            bucket = rec["s3"]["bucket"]["name"]
            key = rec["s3"]["object"]["key"]
            print(f"Processing S3 object: s3://{bucket}/{key}")
            
            # Read the log file
            body = s3.get_object(Bucket=rec["s3"]["bucket"]["name"], Key=rec["s3"]["object"]["key"])["Body"].read().decode()
            log = json.loads(body)
            
            # Generate threat analysis
            bedrock_result = invoke_bedrock([log])
            raw_analysis = bedrock_result.get("raw", "")
            
            # Generate embedding
            embedding_result = invoke_embedding(log)
            vector = embedding_result.get("embedding", [])
            
            # Parse the analysis
            from prototype.parse_response import parse_raw
            parsed = parse_raw(raw_analysis)
            
            # Create item for DynamoDB
            timestamp = log.get("timestamp", datetime.now().isoformat())
            event_id = log.get("event_id", f"event-{int(datetime.now().timestamp())}")
            
            item = {
                "event_id": event_id,
                "timestamp": timestamp,
                "src_ip": log.get("src_ip", "unknown"),
                "anomaly_score": parsed.get("anomaly_score"),
                "threat": parsed.get("threat"),
                "explanation": parsed.get("explanation"),
                "raw_analysis": raw_analysis
            }
            
            # Store in DynamoDB
            table.put_item(Item=item)
            
            # Store in Pinecone
            index_name = os.getenv("PINECONE_INDEX", "docqa-index")
            pc = get_pinecone_client()
            index = pc.Index(index_name)
            
            metadata = {
                "event_id": event_id,
                "timestamp": timestamp,
                "src_ip": log.get("src_ip", "unknown"),
                "anomaly_score": parsed.get("anomaly_score") or 0,
                "threat": parsed.get("threat", "Unknown"),
                "explanation": parsed.get("explanation", "")[:500]  # Limit length for metadata
            }
            
            index.upsert(
                vectors=[{
                    "id": event_id,
                    "values": vector,
                    "metadata": metadata
                }]
            )
            
            # Check if high severity and send notification
            severity_threshold = int(os.getenv("SEVERITY_THRESHOLD", "75"))
            if parsed.get("anomaly_score", 0) >= severity_threshold:
                # Send SNS notification for high severity threats
                sns_topic = os.getenv("SNS_TOPIC_ARN")
                if sns_topic:
                    sns = boto3.client('sns')
                    message = f"HIGH SEVERITY THREAT DETECTED!\n\n"
                    message += f"Score: {parsed.get('anomaly_score')}\n"
                    message += f"Threat: {parsed.get('threat')}\n"
                    message += f"Source IP: {log.get('src_ip', 'unknown')}\n"
                    message += f"Explanation: {parsed.get('explanation')}\n"
                    
                    sns.publish(
                        TopicArn=sns_topic,
                        Subject=f"High Severity Threat: {parsed.get('threat')}",
                        Message=message
                    )
                    print(f"Sent high severity notification to SNS topic: {sns_topic}")
            
            results.append({
                "event_id": event_id,
                "status": "processed",
                "anomaly_score": parsed.get("anomaly_score"),
                "threat": parsed.get("threat")
            })
            
        except Exception as e:
            print(f"Error processing record: {e}")
            results.append({
                "status": "error",
                "error": str(e)
            })
    
    return {
        "status": "ok",
        "results": results
    }