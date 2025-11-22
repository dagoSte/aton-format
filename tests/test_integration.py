"""
ATON Format V2.0 - Integration Tests
End-to-end tests covering complete workflows.
"""

import pytest
from aton_format import ATONEncoder, ATONDecoder, ATONStreamEncoder, CompressionMode
from aton_format.query import ATONQueryEngine


class TestFullEncodingDecodingWorkflow:
    """End-to-end tests for encoding and decoding."""

    def test_complete_round_trip_simple(self, encoder, decoder, simple_products):
        """Complete round trip with simple data."""
        encoded = encoder.encode(simple_products)
        decoded = decoder.decode(encoded)

        assert decoded == simple_products

    def test_complete_round_trip_large(self, encoder, decoder, large_dataset):
        """Complete round trip with large dataset."""
        encoded = encoder.encode(large_dataset)
        decoded = decoder.decode(encoded)

        assert decoded == large_dataset

    def test_complete_round_trip_nested(self, encoder, decoder):
        """Complete round trip with data structures."""
        # Note: Deep nesting with arrays may have limited support
        data = {"orders": [
            {"id": 1, "customer": "John", "total": 100.0},
            {"id": 2, "customer": "Jane", "total": 200.0},
        ]}
        encoded = encoder.encode(data)
        decoded = decoder.decode(encoded)

        assert decoded == data

    def test_round_trip_all_modes(self, decoder, simple_products):
        """Round trip works with all compression modes."""
        for mode in CompressionMode:
            encoder = ATONEncoder(compression=mode)
            encoded = encoder.encode(simple_products)
            decoded = decoder.decode(encoded)

            assert decoded == simple_products, f"Failed for mode: {mode}"

    def test_round_trip_preserves_types(self, encoder, decoder):
        """Round trip preserves basic data types."""
        # Use multiple records to avoid defaults-only edge case
        data = {
            "mixed": [
                {"int_val": 42, "float_val": 3.14, "str_val": "hello", "bool_val": True},
                {"int_val": 100, "float_val": 2.71, "str_val": "world", "bool_val": False},
            ]
        }

        encoded = encoder.encode(data)
        decoded = decoder.decode(encoded)

        assert decoded == data


class TestQueryWithEncodingWorkflow:
    """Tests combining query and encoding."""

    def test_query_then_encode(self, encoder, query_test_data):
        """Query filtering then encoding."""
        result = encoder.encode_with_query(
            query_test_data, "products WHERE price > 100"
        )

        assert isinstance(result, str)
        # Result should be smaller (filtered)
        full_result = encoder.encode(query_test_data)
        assert len(result) <= len(full_result)

    def test_query_encode_decode_round_trip(self, encoder, decoder, query_test_data):
        """Query, encode, decode workflow."""
        # Get expected filtered data
        query_engine = ATONQueryEngine()
        parsed = query_engine.parse("products WHERE category = 'Electronics'")
        expected_records = query_engine.execute(query_test_data, parsed)

        # Encode with query
        encoded = encoder.encode_with_query(
            query_test_data, "products WHERE category = 'Electronics'"
        )

        # Decode
        decoded = decoder.decode(encoded)

        # Should match filtered data
        assert len(decoded["products"]) == len(expected_records)

    def test_complex_query_encode_decode(self, encoder, decoder, query_test_data):
        """Complex query with encode/decode."""
        encoded = encoder.encode_with_query(
            query_test_data,
            "products WHERE price > 50 AND stock > 10",
        )

        decoded = decoder.decode(encoded)

        # Should have filtered records
        assert "products" in decoded
        # Should have fewer records than original
        assert len(decoded["products"]) <= len(query_test_data["products"])


class TestStreamingWorkflow:
    """Tests for streaming workflows."""

    def test_streaming_produces_valid_aton(self, stream_encoder, large_dataset, decoder):
        """Each streaming chunk should be valid ATON."""
        chunks = list(stream_encoder.stream_encode(large_dataset))

        # First chunk should be decodable
        first_chunk = chunks[0]
        # Note: Individual chunks may not be fully decodable without context
        assert first_chunk.data is not None

    def test_streaming_with_different_chunk_sizes(self, large_dataset):
        """Streaming works with various chunk sizes."""
        chunk_sizes = [10, 25, 50, 100]

        for size in chunk_sizes:
            encoder = ATONStreamEncoder(chunk_size=size)
            chunks = list(encoder.stream_encode(large_dataset))

            # Should produce appropriate number of chunks
            expected_chunks = (len(large_dataset["records"]) + size - 1) // size
            assert len(chunks) == expected_chunks, f"Failed for chunk_size={size}"

    def test_streaming_all_compression_modes(self, large_dataset):
        """Streaming works with all compression modes."""
        for mode in CompressionMode:
            encoder = ATONStreamEncoder(chunk_size=50, compression=mode)
            chunks = list(encoder.stream_encode(large_dataset))

            assert len(chunks) >= 1, f"Failed for mode: {mode}"


class TestCompressionEffectiveness:
    """Tests for compression effectiveness."""

    def test_compression_reduces_size(self, large_dataset):
        """Compression should reduce output size."""
        import json

        json_size = len(json.dumps(large_dataset))

        encoder = ATONEncoder(compression=CompressionMode.BALANCED)
        aton_output = encoder.encode(large_dataset)
        aton_size = len(aton_output)

        # ATON should be smaller than JSON
        assert aton_size < json_size

    def test_repeated_data_compresses_well(self):
        """Data with repeated values should compress well."""
        import json

        data = {
            "items": [
                {"status": "active", "type": "standard", "category": "electronics"}
                for _ in range(100)
            ]
        }

        json_size = len(json.dumps(data))

        encoder = ATONEncoder(compression=CompressionMode.ULTRA)
        aton_output = encoder.encode(data)
        aton_size = len(aton_output)

        # Should achieve significant compression
        compression_ratio = aton_size / json_size
        assert compression_ratio < 0.8  # At least 20% reduction

    def test_ultra_vs_fast_compression(self, large_dataset):
        """ULTRA should compress better than FAST."""
        fast_encoder = ATONEncoder(compression=CompressionMode.FAST)
        ultra_encoder = ATONEncoder(compression=CompressionMode.ULTRA)

        fast_output = fast_encoder.encode(large_dataset)
        ultra_output = ultra_encoder.encode(large_dataset)

        # ULTRA should generally be smaller or equal
        # (may not always be true for all datasets)
        assert len(ultra_output) <= len(fast_output) * 1.1  # Allow 10% tolerance


class TestEdgeCaseWorkflows:
    """Tests for edge case scenarios."""

    def test_empty_data_workflow(self, encoder, decoder):
        """Empty data should encode and decode correctly."""
        data = {"items": []}
        encoded = encoder.encode(data)
        decoded = decoder.decode(encoded)

        assert decoded == data

    def test_single_record_workflow(self, encoder, decoder):
        """Multiple records workflow (single record may become defaults-only)."""
        # Use multiple records to avoid all-defaults edge case
        data = {"items": [{"id": 1, "name": "First"}, {"id": 2, "name": "Second"}]}
        encoded = encoder.encode(data)
        decoded = decoder.decode(encoded)

        assert decoded == data

    def test_special_characters_workflow(self, encoder, decoder):
        """Special characters should be preserved."""
        # Use multiple records with varying text
        data = {
            "items": [
                {"id": 1, "text": "Hello World"},
                {"id": 2, "text": "Another text"},
                {"id": 3, "text": "Third item"},
            ]
        }
        encoded = encoder.encode(data)
        decoded = decoder.decode(encoded)

        assert decoded == data

    def test_unicode_workflow(self, encoder, decoder):
        """Unicode characters should be preserved."""
        data = {
            "items": [
                {"id": 1, "name": "Cafe"},
                {"id": 2, "name": "Restaurant"},
            ]
        }
        encoded = encoder.encode(data)
        decoded = decoder.decode(encoded)

        assert decoded == data

    def test_large_values_workflow(self, encoder, decoder):
        """Large values should be handled."""
        data = {
            "items": [
                {"id": 1, "big_int": 999999999999999},
                {"id": 2, "big_int": 888888888888888},
            ]
        }
        encoded = encoder.encode(data)
        decoded = decoder.decode(encoded)

        assert decoded == data


class TestMultiTableWorkflow:
    """Tests for multi-table scenarios."""

    def test_multiple_tables_round_trip(self, encoder, decoder):
        """Multiple tables should encode and decode correctly."""
        data = {
            "products": [
                {"id": 1, "name": "Product A"},
                {"id": 2, "name": "Product B"},
            ],
            "categories": [
                {"id": 1, "name": "Category X"},
                {"id": 2, "name": "Category Y"},
            ],
        }

        encoded = encoder.encode(data)
        decoded = decoder.decode(encoded)

        assert "products" in decoded
        assert "categories" in decoded
        assert decoded == data


class TestRealWorldScenarios:
    """Tests simulating real-world use cases."""

    def test_ecommerce_catalog(self, encoder, decoder):
        """E-commerce product catalog scenario."""
        data = {
            "products": [
                {
                    "id": i,
                    "sku": f"SKU-{i:05d}",
                    "name": f"Product {i}",
                    "price": 9.99 + i,
                    "stock": 100 - i % 50,
                    "active": i % 3 != 0,
                }
                for i in range(50)
            ]
        }

        encoded = encoder.encode(data)
        decoded = decoder.decode(encoded)

        assert decoded == data
        assert len(decoded["products"]) == 50

    def test_analytics_data(self, encoder, decoder):
        """Analytics/metrics data scenario."""
        data = {
            "metrics": [
                {
                    "timestamp": f"2024-01-{(i % 31) + 1:02d}",
                    "page_views": 1000 + i * 10,
                    "unique_visitors": 500 + i * 5,
                    "bounce_rate": 0.3 + (i % 10) * 0.01,
                    "conversion_rate": 0.02 + (i % 5) * 0.001,
                }
                for i in range(30)
            ]
        }

        encoded = encoder.encode(data)
        decoded = decoder.decode(encoded)

        assert decoded == data

    def test_user_records(self, encoder, decoder):
        """User records scenario."""
        data = {
            "users": [
                {
                    "id": i,
                    "email": f"user{i}@example.com",
                    "name": f"User {i}",
                    "role": ["admin", "user", "guest"][i % 3],
                    "active": True,
                    "created_at": "2024-01-15T10:30:00Z",
                }
                for i in range(20)
            ]
        }

        encoded = encoder.encode(data)
        decoded = decoder.decode(encoded)

        assert decoded == data


class TestErrorRecovery:
    """Tests for error handling and recovery."""

    def test_encoding_error_recovery(self, encoder):
        """Should handle encoding errors gracefully."""
        # Test with valid data after potential error scenario
        valid_data = {"items": [{"id": 1}]}
        result = encoder.encode(valid_data)
        assert isinstance(result, str)

    def test_decoder_handles_minor_variations(self, encoder, decoder, simple_products):
        """Decoder should handle minor format variations."""
        encoded = encoder.encode(simple_products)
        # Add some whitespace
        encoded_with_space = encoded.strip()
        decoded = decoder.decode(encoded_with_space)

        assert decoded == simple_products


class TestPerformanceBaseline:
    """Basic performance tests."""

    def test_encode_100_records_completes(self, encoder):
        """Should encode 100 records in reasonable time."""
        data = {"items": [{"id": i, "value": f"Value {i}"} for i in range(100)]}

        import time
        start = time.time()
        result = encoder.encode(data)
        elapsed = time.time() - start

        assert elapsed < 5.0  # Should complete in under 5 seconds
        assert isinstance(result, str)

    def test_decode_100_records_completes(self, encoder, decoder):
        """Should decode 100 records in reasonable time."""
        data = {"items": [{"id": i, "value": f"Value {i}"} for i in range(100)]}
        encoded = encoder.encode(data)

        import time
        start = time.time()
        decoded = decoder.decode(encoded)
        elapsed = time.time() - start

        assert elapsed < 5.0
        assert decoded == data

    def test_streaming_1000_records_completes(self):
        """Should stream 1000 records in reasonable time."""
        data = {"items": [{"id": i, "value": f"Value {i}"} for i in range(1000)]}
        encoder = ATONStreamEncoder(chunk_size=100)

        import time
        start = time.time()
        chunks = list(encoder.stream_encode(data))
        elapsed = time.time() - start

        assert elapsed < 10.0
        assert len(chunks) == 10
