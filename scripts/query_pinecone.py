import os
from pinecone import Pinecone
# Get API key from environment or enter it here
api_key = os.environ.get("PINECONE_API_KEY", "YOUR_API_KEY")
pc = Pinecone(api_key=api_key)
index = pc.Index("docqa-index")

# Query for recent threat vectors
results = index.query(
    vector=[0.1] * 1536,
    top_k=5,
    include_metadata=True
)

# Print results in a readable format
print("\nPinecone Query Results:")
print("======================")
for i, match in enumerate(results.get("matches", [])):
    print(f"\nMatch {i+1}:")
    print(f"  ID: {match.get('id')}")
    print(f"  Score: {match.get('score')}")
    print("  Metadata:")
    for k, v in match.get("metadata", {}).items():
        print(f"    {k}: {v}")
