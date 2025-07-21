"""
Pytest configuration file
"""
import sys
import os
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock external dependencies for all tests
import types

# Mock boto3
boto3_mock = MagicMock()
sys.modules['boto3'] = boto3_mock

# Mock botocore and its exceptions
botocore_mock = MagicMock()
botocore_exceptions = types.ModuleType('botocore.exceptions')
botocore_exceptions.ClientError = type('ClientError', (Exception,), {})

sys.modules['botocore'] = botocore_mock
sys.modules['botocore.exceptions'] = botocore_exceptions

# Mock pinecone
sys.modules['pinecone'] = MagicMock()