"""Test round-trip encoding/decoding."""
import pytest
from aton import ATONEncoder, ATONDecoder


def test_roundtrip():
    encoder = ATONEncoder(optimize=True)
    decoder = ATONDecoder()
    
    original = {
        "users": [
            {"id": 1, "name": "John", "active": True},
            {"id": 2, "name": "Jane", "active": True}
        ]
    }
    
    aton = encoder.encode(original)
    decoded = decoder.decode(aton)
    
    assert decoded == original
