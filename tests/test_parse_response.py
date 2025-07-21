"""
Tests for prototype/parse_response.py
"""
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prototype.parse_response import parse_raw

# Load test payloads
with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'payloads', 'bedrock_responses.json')) as f:
    responses = json.load(f)

def test_parse_complete_response():
    """Test parsing a complete response with all fields"""
    sample_response = responses["standard_response"]
    
    result = parse_raw(sample_response)
    
    assert result["threat"] == "SSH Brute Force Attack"
    assert result["anomaly_score"] == 75
    assert result["explanation"] == "Multiple login attempts with different passwords from the same IP address."

def test_parse_partial_response():
    """Test parsing a response with missing fields"""
    sample_response = responses["partial_response"]
    
    result = parse_raw(sample_response)
    
    assert result["anomaly_score"] == 65
    assert result["explanation"] == "Suspicious activity detected but unable to classify specific threat type."
    assert result["threat"] is None

def test_parse_high_severity_response():
    """Test parsing a high severity response"""
    sample_response = responses["high_severity_response"]
    
    result = parse_raw(sample_response)
    
    assert result["anomaly_score"] == 90
    assert result["threat"] == "Malicious Command Execution"
    assert "malware" in result["explanation"].lower()

def test_parse_empty_response():
    """Test parsing an empty response"""
    sample_response = ""
    
    result = parse_raw(sample_response)
    
    assert result["anomaly_score"] is None
    assert result["threat"] is None
    assert result["explanation"] is None