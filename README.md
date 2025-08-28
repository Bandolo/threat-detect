# AI-Powered Threat Detection System

Real-time threat detection using AWS Bedrock AI, Pinecone vector search, and honeypot data.

## 🎥 Live Demo

[![AI Threat Detection Demo](https://img.youtube.com/vi/ZTbJbibylAc/maxresdefault.jpg)](https://youtu.be/ZTbJbibylAc)

**[▶️ Watch 5-Minute Demo](https://youtu.be/ZTbJbibylAc)**

## Architecture

![Architecture](assets/Cowrie.jpg)

```
Honeypot → S3 → Lambda → Bedrock (Claude) → Pinecone + DynamoDB + SNS
```

**Key Features:**
- Real-time AI threat analysis with Claude
- Vector similarity search for attack patterns
- Automated alerts for high-severity threats
- Production monitoring with CloudWatch

## Quick Start

```bash
# Setup
git clone https://github.com/yourusername/threat-detect.git
cd threat-detect
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Deploy
aws s3 mb s3://your-bucket
aws secretsmanager create-secret --name pinecone/credentials --secret-string '{"apiKey":"YOUR_KEY"}'
serverless deploy

# Test
cd tests && ./test_all.sh
```

## Tech Stack

- **AI**: AWS Bedrock (Claude)
- **Vector DB**: Pinecone
- **Storage**: S3, DynamoDB
- **Compute**: Lambda
- **Monitoring**: CloudWatch, SNS
- **Infrastructure**: Serverless Framework

## Project Structure

```
src/
├── handlers/           # Lambda functions
├── utils/             # Shared utilities
tests/                 # Test suite
infrastructure/        # IaC and setup scripts
scripts/              # Utilities and test data
```

## Results

- **Threat Detection**: 90/100 score for malware execution
- **Response Time**: <3 seconds end-to-end
- **Accuracy**: High-confidence threat classification
- **Scalability**: Serverless auto-scaling architecture