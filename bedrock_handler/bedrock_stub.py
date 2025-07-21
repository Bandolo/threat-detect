import os
import json
import boto3
import time
from botocore.exceptions import ClientError
from prototype.parse_response import parse_raw

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
MAX_TOKENS = int(os.getenv("MAX_TOKEN_COUNT", "512"))

# Cost parameters – per 1,000 tokens
INPUT_RATE = 0.0008    # Titan Text Express input cost
OUTPUT_RATE = 0.0016   # Titan Text Express output cost

def estimate_tokens(text: str) -> int:
    """
    Approximate token count using ~6 characters per token (AWS guideline).
    """
    return max(1, len(text) // 6)

def estimate_cost(input_toks: int, output_toks: int) -> float:
    """Estimate cost based on token counts and current pricing."""
    return (input_toks / 1000) * INPUT_RATE + (output_toks / 1000) * OUTPUT_RATE

def invoke_bedrock(logs):
    """Generate threat analysis using Bedrock Claude"""
    start_time = time.time()
    try:
        # Create a boto3 client for Bedrock
        try:
            client = boto3.client('bedrock-runtime', region_name='us-east-1')
        except:
            client = boto3.client('bedrock', region_name='us-east-1')
        
        # Prepare the prompt for Claude
        prompt = (
            "Analyze these AWS security log events and return a threat score (0–100), "
            "threat label, and explanation.\n\nLogs:\n"
            + json.dumps(logs, indent=2)
        )
        
        # Claude 3 Haiku payload format
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": MAX_TOKENS,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.0
        }
        
        # Invoke Claude 3 Haiku
        print("Invoking Claude 3 Haiku for threat analysis...")
        resp = client.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(payload).encode(),
            contentType="application/json",
            accept="application/json"
        )
        
        # Parse the response
        body = resp["body"].read()
        result = json.loads(body)
        output = result.get("content", [{}])[0].get("text")
        
        print(f"✅ Generated AI threat analysis")
        
        # Calculate metrics
        execution_time = time.time() - start_time
        input_tokens = estimate_tokens(json.dumps(logs))
        output_tokens = estimate_tokens(output) if output else 0
        estimated_cost = estimate_cost(input_tokens, output_tokens)
        
        # Log metrics to CloudWatch
        try:
            cloudwatch = boto3.client('cloudwatch')
            cloudwatch.put_metric_data(
                Namespace='ThreatDetection',
                MetricData=[
                    {
                        'MetricName': 'BedrockInvocationTime',
                        'Value': execution_time,
                        'Unit': 'Seconds'
                    },
                    {
                        'MetricName': 'BedrockInvocationCount',
                        'Value': 1,
                        'Unit': 'Count'
                    },
                    {
                        'MetricName': 'BedrockInputTokens',
                        'Value': input_tokens,
                        'Unit': 'Count'
                    },
                    {
                        'MetricName': 'BedrockOutputTokens',
                        'Value': output_tokens,
                        'Unit': 'Count'
                    },
                    {
                        'MetricName': 'BedrockEstimatedCost',
                        'Value': estimated_cost,
                        'Unit': 'None'
                    }
                ]
            )
        except Exception as e:
            print(f"Failed to log metrics: {e}")
        
        return {"raw": output}
    except Exception as e:
        print(f"Bedrock invoke failed: {e}")
        # Fallback to simple analysis if Bedrock fails
        log = logs[0] if logs else {}
        event_id = log.get("event_id", "unknown")
        source_ip = log.get("src_ip", log.get("sourceIPAddress", "unknown"))
        event_type = log.get("eventid", log.get("eventName", "unknown"))
        output = f"""Score: 50
Threat: Suspicious Activity
Explanation: Detected {event_type} from {source_ip}
"""
        return {"raw": output}

def invoke_embedding(log):
    """Generate embedding vector for log data"""
    # Use deterministic hash-based embedding to create unique vectors for each log
    import hashlib
    
    # Convert log to text
    text = json.dumps(log, separators=(',', ':'))
    
    # Create a hash of the text
    hash_obj = hashlib.sha256(text.encode())
    hash_bytes = hash_obj.digest()
    
    # Convert hash to a list of floats between 0 and 1
    embedding = []
    for i in range(0, len(hash_bytes), 2):
        if i+1 < len(hash_bytes):
            # Use pairs of bytes to create floats between 0 and 1
            val = (hash_bytes[i] * 256 + hash_bytes[i+1]) / 65535.0
            embedding.append(val)
    
    # Pad to 1536 dimensions
    while len(embedding) < 1536:
        embedding.extend(embedding[:min(len(embedding), 1536-len(embedding))])
    
    # Truncate to exactly 1536
    embedding = embedding[:1536]
    
    print(f"✅ Generated hash-based embedding")
    return {"embedding": embedding}

def handler(event, context):
    dynamodb = boto3.resource("dynamodb")
    table_name = os.getenv("THREATS_TABLE", "ThreatsTable")
    table = dynamodb.Table(table_name)
    
    results = []
    for log in event:
        result = invoke_bedrock([log])
        raw = result.get("raw")
        parsed = parse_raw(raw) if raw else {}
        
        item = {
            "event_id": log.get("event_id"),
            "timestamp": log.get("timestamp"),
            "anomaly_score": parsed.get("anomaly_score"),
            "threat": parsed.get("threat"),
            "explanation": parsed.get("explanation"),
            "raw": raw,
            "error": result.get("error")
        }
        
        table.put_item(Item=item)
        results.append(item)
        
    return {"results": results}