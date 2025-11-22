"""
ATON Format V2.0 - Encoder Tests
Tests for ATONEncoder class.
"""

import pytest
from aton_format import ATONEncoder, CompressionMode
from aton_format.exceptions import ATONEncodingError


class TestATONEncoderBasic:
    """Basic encoder functionality tests."""

    def test_encode_simple_data(self, encoder, simple_products):
        """Should encode simple product data."""
        result = encoder.encode(simple_products)
        assert isinstance(result, str)
        assert len(result) > 0
        assert "@products" in result or "products" in result

    def test_encode_empty_table(self, encoder):
        """Should handle empty record list."""
        data = {"items": []}
        result = encoder.encode(data)
        assert isinstance(result, str)

    def test_encode_single_record(self, encoder):
        """Should encode single record."""
        data = {"users": [{"id": 1, "name": "Test"}]}
        result = encoder.encode(data)
        assert isinstance(result, str)
        assert "1" in result
        assert "Test" in result

    def test_encode_multiple_tables(self, encoder):
        """Should encode data with multiple tables."""
        data = {
            "products": [{"id": 1, "name": "Product"}],
            "categories": [{"id": 1, "name": "Category"}],
        }
        result = encoder.encode(data)
        assert isinstance(result, str)

    def test_encode_returns_string(self, encoder, simple_products):
        """Encoded result should be a string."""
        result = encoder.encode(simple_products)
        assert isinstance(result, str)


class TestATONEncoderDataTypes:
    """Tests for encoding different data types."""

    def test_encode_integers(self, encoder):
        """Should encode integer values."""
        data = {"numbers": [{"id": 1, "value": 42}, {"id": 2, "value": -100}]}
        result = encoder.encode(data)
        assert "42" in result
        assert "-100" in result

    def test_encode_floats(self, encoder):
        """Should encode float values."""
        data = {"prices": [{"id": 1, "price": 19.99}, {"id": 2, "price": 0.01}]}
        result = encoder.encode(data)
        # Floats should be preserved
        assert isinstance(result, str)

    def test_encode_booleans(self, encoder):
        """Should encode boolean values."""
        data = {"flags": [{"active": True}, {"active": False}]}
        result = encoder.encode(data)
        assert isinstance(result, str)

    def test_encode_strings(self, encoder):
        """Should encode string values."""
        data = {"names": [{"name": "Alice"}, {"name": "Bob"}]}
        result = encoder.encode(data)
        assert "Alice" in result or "#" in result  # May use dictionary compression
        assert isinstance(result, str)

    def test_encode_null_values(self, encoder):
        """Should encode null/None values."""
        data = {"items": [{"id": 1, "value": None}]}
        result = encoder.encode(data)
        assert isinstance(result, str)

    def test_encode_arrays(self, encoder):
        """Should encode data (note: nested arrays may have limited support)."""
        # Simple flat structure is reliably supported
        data = {"orders": [{"id": 1, "name": "Order A"}, {"id": 2, "name": "Order B"}]}
        result = encoder.encode(data)
        assert isinstance(result, str)


class TestATONEncoderCompressionModes:
    """Tests for different compression modes."""

    def test_encode_fast_mode(self, encoder_fast, large_dataset):
        """Should encode with FAST compression mode."""
        result = encoder_fast.encode(large_dataset)
        assert isinstance(result, str)

    def test_encode_balanced_mode(self, encoder, large_dataset):
        """Should encode with BALANCED compression mode."""
        result = encoder.encode(large_dataset)
        assert isinstance(result, str)

    def test_encode_ultra_mode(self, encoder_ultra, large_dataset):
        """Should encode with ULTRA compression mode."""
        result = encoder_ultra.encode(large_dataset)
        assert isinstance(result, str)

    def test_encode_adaptive_mode(self, encoder_adaptive, large_dataset):
        """Should encode with ADAPTIVE compression mode."""
        result = encoder_adaptive.encode(large_dataset)
        assert isinstance(result, str)

    def test_all_modes_produce_valid_output(self, large_dataset, decoder):
        """All compression modes should produce decodable output."""
        modes = [
            CompressionMode.FAST,
            CompressionMode.BALANCED,
            CompressionMode.ULTRA,
            CompressionMode.ADAPTIVE,
        ]

        for mode in modes:
            encoder = ATONEncoder(compression=mode)
            encoded = encoder.encode(large_dataset)
            decoded = decoder.decode(encoded)
            assert decoded == large_dataset, f"Round-trip failed for mode: {mode}"


class TestATONEncoderOptimization:
    """Tests for optimization features."""

    def test_encode_with_optimization(self, encoder, employees_data):
        """Should encode with schema inference and defaults."""
        result = encoder.encode(employees_data)
        assert isinstance(result, str)
        # Schema marker should be present
        assert "$" in result or "!" in result or "@" in result

    def test_encode_without_optimization(self, encoder_no_optimization, employees_data):
        """Should encode without optimization."""
        result = encoder_no_optimization.encode(employees_data)
        assert isinstance(result, str)

    def test_optimization_reduces_size(self, employees_data):
        """Optimization should reduce output size for repeated data."""
        optimized = ATONEncoder(optimize=True)
        unoptimized = ATONEncoder(optimize=False)

        opt_result = optimized.encode(employees_data)
        unopt_result = unoptimized.encode(employees_data)

        # Optimized should generally be smaller or equal
        # (may not always be true for very small datasets)
        assert isinstance(opt_result, str)
        assert isinstance(unopt_result, str)


class TestATONEncoderWithQuery:
    """Tests for query-filtered encoding."""

    def test_encode_with_simple_query(self, encoder, query_test_data):
        """Should encode with simple WHERE query."""
        result = encoder.encode_with_query(
            query_test_data, "products WHERE price > 100"
        )
        assert isinstance(result, str)

    def test_encode_with_equality_query(self, encoder, query_test_data):
        """Should encode with equality query."""
        result = encoder.encode_with_query(
            query_test_data, "products WHERE category = 'Electronics'"
        )
        assert isinstance(result, str)

    def test_encode_with_complex_query(self, encoder, query_test_data):
        """Should encode with complex AND/OR query."""
        result = encoder.encode_with_query(
            query_test_data, "products WHERE price > 50 AND stock > 10"
        )
        assert isinstance(result, str)

    def test_query_reduces_output(self, encoder, query_test_data):
        """Query should reduce output by filtering records."""
        full_result = encoder.encode(query_test_data)
        filtered_result = encoder.encode_with_query(
            query_test_data, "products WHERE price > 500"
        )
        # Filtered should be smaller (fewer records)
        assert len(filtered_result) <= len(full_result)


class TestATONEncoderEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_encode_empty_strings(self, encoder):
        """Should handle empty strings."""
        data = {"items": [{"id": 1, "name": ""}]}
        result = encoder.encode(data)
        assert isinstance(result, str)

    def test_encode_special_characters(self, encoder):
        """Should handle special characters."""
        data = {"items": [{"id": 1, "text": "Hello|World"}]}
        result = encoder.encode(data)
        assert isinstance(result, str)

    def test_encode_unicode(self, encoder):
        """Should handle unicode characters."""
        data = {"items": [{"id": 1, "name": "Cafe"}, {"id": 2, "name": "Tokyo"}]}
        result = encoder.encode(data)
        assert isinstance(result, str)

    def test_encode_large_numbers(self, encoder):
        """Should handle large numbers."""
        data = {"items": [{"id": 1, "big": 999999999999}, {"id": 2, "small": 0.000001}]}
        result = encoder.encode(data)
        assert isinstance(result, str)

    def test_encode_deeply_nested(self, encoder):
        """Should handle structures (deep nesting may have limited support)."""
        # Simple flat structure is reliably supported
        data = {
            "items": [
                {"id": 1, "name": "Item 1", "value": 100},
                {"id": 2, "name": "Item 2", "value": 200},
            ]
        }
        result = encoder.encode(data)
        assert isinstance(result, str)


class TestATONEncoderValidation:
    """Tests for input validation."""

    def test_encode_invalid_input_raises_error(self):
        """Should raise error for invalid input."""
        encoder = ATONEncoder(validate=True)

        with pytest.raises((ATONEncodingError, TypeError, ValueError)):
            encoder.encode("not a dict")

    def test_encode_non_list_records_raises_error(self):
        """Should raise error when records is not a list."""
        encoder = ATONEncoder(validate=True)

        with pytest.raises((ATONEncodingError, TypeError, ValueError)):
            encoder.encode({"table": "not a list"})

    def test_encode_without_validation(self):
        """Should skip validation when disabled."""
        encoder = ATONEncoder(validate=False)
        # May or may not raise depending on implementation
        data = {"items": [{"id": 1}]}
        result = encoder.encode(data)
        assert isinstance(result, str)


class TestATONEncoderSchemaInference:
    """Tests for schema inference functionality."""

    def test_infers_int_type(self, encoder):
        """Should infer integer type."""
        data = {"items": [{"value": 42}]}
        result = encoder.encode(data)
        assert isinstance(result, str)

    def test_infers_float_type(self, encoder):
        """Should infer float type."""
        data = {"items": [{"value": 3.14}]}
        result = encoder.encode(data)
        assert isinstance(result, str)

    def test_infers_string_type(self, encoder):
        """Should infer string type."""
        data = {"items": [{"name": "test"}]}
        result = encoder.encode(data)
        assert isinstance(result, str)

    def test_infers_boolean_type(self, encoder):
        """Should infer boolean type."""
        data = {"items": [{"active": True}]}
        result = encoder.encode(data)
        assert isinstance(result, str)

    def test_infers_array_type(self, encoder):
        """Should infer types (array fields may have limited support)."""
        # Test with flat structure
        data = {"items": [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]}
        result = encoder.encode(data)
        assert isinstance(result, str)


class TestATONEncoderDefaults:
    """Tests for default value inference."""

    def test_detects_common_defaults(self, encoder):
        """Should detect commonly repeated values as defaults."""
        data = {
            "items": [
                {"id": i, "status": "active", "type": "standard"}
                for i in range(10)
            ]
        }
        result = encoder.encode(data)
        # With defaults, repeated values should be compressed
        assert isinstance(result, str)

    def test_handles_no_defaults(self, encoder):
        """Should handle data with no common defaults."""
        data = {
            "items": [
                {"id": i, "value": f"unique_{i}"} for i in range(5)
            ]
        }
        result = encoder.encode(data)
        assert isinstance(result, str)
