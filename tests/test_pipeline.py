import json
import os
from src.handlers.bedrock_handler.bedrock_stub import invoke_bedrock, invoke_embedding
from src.utils.prototype.parse_response import parse_raw

print("Testing the full threat detection pipeline...")

# Load sample log
with open('scripts/payloads/sample_log.json', 'r') as f:
    log = json.load(f)

print("\n1. Sample log data:")
print(json.dumps(log, indent=2))

# Step 1: Invoke Bedrock for threat analysis
print("\n2. Generating threat analysis with Bedrock...")
bedrock_result = invoke_bedrock([log])
raw_analysis = bedrock_result.get("raw", "")
print(f"Raw analysis:\n{raw_analysis}")

# Step 2: Parse the analysis
print("\n3. Parsing the analysis...")
parsed = parse_raw(raw_analysis)
print(f"Parsed result:")
print(f"  Score: {parsed.get('anomaly_score')}")
print(f"  Threat: {parsed.get('threat')}")
print(f"  Explanation: {parsed.get('explanation')}")

# Step 3: Generate embedding
print("\n4. Generating embedding...")
embedding_result = invoke_embedding(log)
vector = embedding_result.get("embedding", [])
print(f"Embedding length: {len(vector)}")
print(f"First 5 values: {vector[:5]}")

print("\nFull pipeline test completed successfully!")
