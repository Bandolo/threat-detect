import json
from prototype.parse_response import parse_raw

# Load test data
with open('payloads/bedrock_responses.json', 'r') as f:
    responses = json.load(f)

# Test parsing
print("Testing parse_raw function...")
for key, response in responses.items():
    print(f"\nTesting {key}:")
    result = parse_raw(response)
    print(f"  Score: {result['anomaly_score']}")
    print(f"  Threat: {result['threat']}")
    print(f"  Explanation: {result['explanation']}")

print("\nAll tests completed!")
