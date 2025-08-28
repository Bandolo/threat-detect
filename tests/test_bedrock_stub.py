"""
Tests for bedrock_handler/bedrock_stub.py
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the functions to test
from src.handlers.bedrock_handler.bedrock_stub import estimate_tokens, estimate_cost

def test_estimate_tokens_empty():
    """Test token estimation with empty text"""
    assert estimate_tokens("") == 1  # Function returns max(1, len(text) // 6)

def test_estimate_tokens_normal():
    """Test token estimation with normal text"""
    text = "This is a test string with exactly 10 words in it."
    expected_tokens = max(1, len(text) // 6)
    assert estimate_tokens(text) == expected_tokens

def test_estimate_cost_zero():
    """Test cost estimation with zero tokens"""
    assert estimate_cost(0, 0) == 0

def test_estimate_cost_normal():
    """Test cost estimation with normal token counts"""
    input_tokens = 1000
    output_tokens = 500
    expected_cost = (input_tokens / 1000) * 0.0008 + (output_tokens / 1000) * 0.0016
    assert estimate_cost(input_tokens, output_tokens) == expected_cost