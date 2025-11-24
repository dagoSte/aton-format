"""
ATON Format V2.0 - Pytest Configuration and Shared Fixtures
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from aton_format import ATONEncoder, ATONDecoder, CompressionMode, ATONStreamEncoder
from aton_format.query import ATONQueryEngine, QueryParser
from aton_format.compression import ATONCompressionEngine


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def simple_products():
    """Simple product data for basic tests."""
    return {
        "products": [
            {"id": 1, "name": "Laptop", "price": 999.99, "active": True},
            {"id": 2, "name": "Mouse", "price": 29.99, "active": True},
            {"id": 3, "name": "Keyboard", "price": 59.99, "active": False},
        ]
    }


@pytest.fixture
def large_dataset():
    """Large dataset for performance and compression tests."""
    return {
        "records": [
            {
                "id": i,
                "name": f"Record {i}",
                "category": f"Category {i % 5}",
                "value": i * 10.5,
                "active": i % 2 == 0,
            }
            for i in range(100)
        ]
    }


@pytest.fixture
def employees_data():
    """Employee data with repeated values for compression tests."""
    return {
        "employees": [
            {"id": 1, "name": "Alice", "dept": "Engineering", "salary": 80000},
            {"id": 2, "name": "Bob", "dept": "Engineering", "salary": 75000},
            {"id": 3, "name": "Charlie", "dept": "Marketing", "salary": 65000},
            {"id": 4, "name": "Diana", "dept": "Engineering", "salary": 90000},
            {"id": 5, "name": "Eve", "dept": "Marketing", "salary": 70000},
        ]
    }


@pytest.fixture
def nested_data():
    """Data with nested structures."""
    return {
        "orders": [
            {
                "id": 1,
                "customer": "John",
                "items": ["laptop", "mouse"],
                "total": 1029.98,
            },
            {
                "id": 2,
                "customer": "Jane",
                "items": ["keyboard"],
                "total": 59.99,
            },
        ]
    }


@pytest.fixture
def edge_case_data():
    """Data with edge cases: nulls, empty strings, special characters."""
    return {
        "items": [
            {"id": 1, "name": "", "value": None, "active": True},
            {"id": 2, "name": "Test|Pipe", "value": 0, "active": False},
            {"id": 3, "name": "Quote's", "value": -1, "active": True},
            {"id": 4, "name": "Tab\there", "value": 0.0, "active": None},
        ]
    }


@pytest.fixture
def numeric_sequence_data():
    """Data with numeric sequences for delta compression tests."""
    return {
        "readings": [
            {"id": i, "timestamp": 1000 + i, "value": 100 + i * 2}
            for i in range(20)
        ]
    }


@pytest.fixture
def query_test_data():
    """Data for query testing with various filterable values."""
    return {
        "products": [
            {"id": 1, "name": "Laptop Pro", "price": 1299, "stock": 5, "category": "Electronics"},
            {"id": 2, "name": "Wireless Mouse", "price": 49, "stock": 100, "category": "Electronics"},
            {"id": 3, "name": "Monitor 27\"", "price": 399, "stock": 20, "category": "Electronics"},
            {"id": 4, "name": "USB Keyboard", "price": 79, "stock": 50, "category": "Electronics"},
            {"id": 5, "name": "Desk Chair", "price": 299, "stock": 10, "category": "Furniture"},
            {"id": 6, "name": "Standing Desk", "price": 599, "stock": 8, "category": "Furniture"},
            {"id": 7, "name": "Notebook", "price": 5, "stock": 500, "category": "Office"},
            {"id": 8, "name": "Pen Set", "price": 12, "stock": 200, "category": "Office"},
        ]
    }


# ============================================================================
# Encoder/Decoder Fixtures
# ============================================================================

@pytest.fixture
def encoder():
    """Default ATONEncoder instance."""
    return ATONEncoder(compression=CompressionMode.BALANCED, optimize=True)


@pytest.fixture
def encoder_fast():
    """Fast compression encoder."""
    return ATONEncoder(compression=CompressionMode.FAST, optimize=True)


@pytest.fixture
def encoder_ultra():
    """Ultra compression encoder."""
    return ATONEncoder(compression=CompressionMode.ULTRA, optimize=True)


@pytest.fixture
def encoder_adaptive():
    """Adaptive compression encoder."""
    return ATONEncoder(compression=CompressionMode.ADAPTIVE, optimize=True)


@pytest.fixture
def encoder_no_optimization():
    """Encoder without optimization."""
    return ATONEncoder(compression=CompressionMode.BALANCED, optimize=False)


@pytest.fixture
def decoder():
    """Default ATONDecoder instance."""
    return ATONDecoder()


@pytest.fixture
def decoder_no_validation():
    """Decoder without validation."""
    return ATONDecoder(validate=False)


# ============================================================================
# Compression Fixtures
# ============================================================================

@pytest.fixture
def compression_engine_fast():
    """Fast compression engine."""
    return ATONCompressionEngine(mode=CompressionMode.FAST)


@pytest.fixture
def compression_engine_balanced():
    """Balanced compression engine."""
    return ATONCompressionEngine(mode=CompressionMode.BALANCED)


@pytest.fixture
def compression_engine_ultra():
    """Ultra compression engine."""
    return ATONCompressionEngine(mode=CompressionMode.ULTRA)


@pytest.fixture
def compression_engine_adaptive():
    """Adaptive compression engine."""
    return ATONCompressionEngine(mode=CompressionMode.ADAPTIVE)


# ============================================================================
# Query Fixtures
# ============================================================================

@pytest.fixture
def query_engine():
    """Query engine instance."""
    return ATONQueryEngine()


@pytest.fixture
def query_parser():
    """Query parser instance."""
    return QueryParser()


# ============================================================================
# Streaming Fixtures
# ============================================================================

@pytest.fixture
def stream_encoder():
    """Default stream encoder with chunk_size=50."""
    return ATONStreamEncoder(chunk_size=50, compression=CompressionMode.FAST)


@pytest.fixture
def stream_encoder_small_chunks():
    """Stream encoder with small chunks for testing."""
    return ATONStreamEncoder(chunk_size=10, compression=CompressionMode.FAST)


# ============================================================================
# Helper Functions
# ============================================================================

def assert_round_trip(encoder, decoder, data):
    """Helper to verify encode/decode round trip."""
    encoded = encoder.encode(data)
    decoded = decoder.decode(encoded)
    assert data == decoded, f"Round-trip failed: {data} != {decoded}"
    return encoded
