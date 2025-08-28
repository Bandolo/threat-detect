# Test Suite

Comprehensive test suite for the Threat Detection System.

## Running Tests

### All Tests
```bash
cd tests
./test_all.sh
```

### Individual Python Tests
```bash
# Unit tests
pytest test_bedrock_stub.py -v
pytest test_parse_response.py -v

# Integration tests  
python test_pipeline.py
python test_embedding.py
```

## Test Coverage

- **Unit Tests**: Core functionality (bedrock, parsing, embedding)
- **Integration Tests**: End-to-end pipeline testing
- **System Tests**: AWS services integration
- **Performance Tests**: Metrics and monitoring

## Prerequisites

- AWS CLI configured
- Python virtual environment activated
- Required AWS permissions for S3, Lambda, DynamoDB, SNS