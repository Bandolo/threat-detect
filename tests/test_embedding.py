import json
from bedrock_handler.bedrock_stub import invoke_embedding

# Load test data
with open('payloads/sample_log.json', 'r') as f:
    log = json.load(f)

# Test embedding generation
print("Testing invoke_embedding function...")
result = invoke_embedding(log)
embedding = result.get("embedding", [])

print(f"Embedding length: {len(embedding)}")
print(f"First 5 values: {embedding[:5]}")
print(f"Last 5 values: {embedding[-5:]}")

# Verify embedding properties
assert len(embedding) == 1536, "Embedding should be 1536 dimensions"
assert all(0 <= x <= 1 for x in embedding), "All values should be between 0 and 1"

print("\nEmbedding test passed!")
