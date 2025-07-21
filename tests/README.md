# Tests for Threat Detection System

This directory contains tests for the core functionality of the threat detection system.

## Running Tests

To run all tests with pytest:

```bash
cd /path/to/threat-detect
pytest
```

To run a specific test file:

```bash
pytest tests/test_parse_response.py
```

To run a specific test function:

```bash
pytest tests/test_parse_response.py::test_parse_complete_response
```

## Test Coverage

The tests cover the following components:

### 1. Response Parser (`test_parse_response.py`)
- `parse_raw`: Tests parsing of raw AI responses into structured data
- Tests complete responses with all fields
- Tests partial responses with missing fields
- Tests high severity threat detection
- Tests empty response handling

### 2. Bedrock Handler (`test_bedrock_stub.py`)
- `estimate_tokens`: Tests token estimation for cost calculation
- `estimate_cost`: Tests cost calculation based on token usage

## Adding New Tests

When adding new functionality, create corresponding tests following these guidelines:

1. Use descriptive test method names that explain what's being tested
2. Mock external dependencies to isolate the unit being tested
3. Test both success cases and error handling
4. Include assertions that verify the expected behavior

## Continuous Integration

These tests can be integrated into a CI/CD pipeline to ensure code quality before deployment.