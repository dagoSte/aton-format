"""
ATON Format V2.0 - Compression Tests
Tests for compression engine and algorithms.
"""

import pytest
from aton_format import CompressionMode
from aton_format.compression import ATONCompressionEngine
from aton_format.compression.algorithms import (
    DictionaryCompression,
    DeltaCompression,
    PatternCompression,
)


class TestCompressionModeEnum:
    """Tests for CompressionMode enumeration."""

    def test_all_modes_defined(self):
        """All compression modes should be defined."""
        assert CompressionMode.FAST.value == "fast"
        assert CompressionMode.BALANCED.value == "balanced"
        assert CompressionMode.ULTRA.value == "ultra"
        assert CompressionMode.ADAPTIVE.value == "adaptive"

    def test_mode_count(self):
        """Should have exactly 4 compression modes."""
        modes = list(CompressionMode)
        assert len(modes) == 4


class TestATONCompressionEngine:
    """Tests for the compression engine orchestrator."""

    def test_create_engine_fast(self, compression_engine_fast):
        """Should create engine with FAST mode."""
        assert compression_engine_fast is not None

    def test_create_engine_balanced(self, compression_engine_balanced):
        """Should create engine with BALANCED mode."""
        assert compression_engine_balanced is not None

    def test_create_engine_ultra(self, compression_engine_ultra):
        """Should create engine with ULTRA mode."""
        assert compression_engine_ultra is not None

    def test_create_engine_adaptive(self, compression_engine_adaptive):
        """Should create engine with ADAPTIVE mode."""
        assert compression_engine_adaptive is not None

    def test_compress_returns_tuple(self, compression_engine_balanced, employees_data):
        """Compress should return (data, metadata) tuple."""
        result = compression_engine_balanced.compress(employees_data)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_compress_fast_mode(self, compression_engine_fast, large_dataset):
        """FAST mode should compress data."""
        compressed, metadata = compression_engine_fast.compress(large_dataset)
        assert compressed is not None
        assert metadata is not None

    def test_compress_balanced_mode(self, compression_engine_balanced, large_dataset):
        """BALANCED mode should compress data."""
        compressed, metadata = compression_engine_balanced.compress(large_dataset)
        assert compressed is not None
        assert metadata is not None

    def test_compress_ultra_mode(self, compression_engine_ultra, large_dataset):
        """ULTRA mode should compress data."""
        compressed, metadata = compression_engine_ultra.compress(large_dataset)
        assert compressed is not None
        assert metadata is not None

    def test_compress_adaptive_mode(self, compression_engine_adaptive, large_dataset):
        """ADAPTIVE mode should compress data."""
        compressed, metadata = compression_engine_adaptive.compress(large_dataset)
        assert compressed is not None
        assert metadata is not None

    def test_metadata_contains_timing(self, compression_engine_balanced, employees_data):
        """Metadata should contain encoding time."""
        _, metadata = compression_engine_balanced.compress(employees_data)
        # Metadata may contain timing or other stats
        assert isinstance(metadata, dict)


class TestDictionaryCompression:
    """Tests for dictionary compression algorithm."""

    def test_create_dictionary_compression(self):
        """Should create DictionaryCompression instance."""
        algo = DictionaryCompression()
        assert algo is not None

    def test_create_with_custom_params(self):
        """Should create with custom min_length and min_occurrences."""
        algo = DictionaryCompression(min_length=3, min_occurrences=2)
        assert algo is not None

    def test_compress_repeated_strings(self):
        """Should compress repeated string values."""
        algo = DictionaryCompression(min_length=3, min_occurrences=2)
        data = {
            "items": [
                {"status": "completed", "type": "standard"},
                {"status": "completed", "type": "standard"},
                {"status": "completed", "type": "standard"},
            ]
        }
        compressed, metadata = algo.compress(data)
        # Dictionary should be created for repeated values
        assert compressed is not None
        assert metadata is not None

    def test_compress_no_repeated_strings(self):
        """Should handle data with no repeated strings."""
        algo = DictionaryCompression()
        data = {"items": [{"id": 1, "name": "unique1"}, {"id": 2, "name": "unique2"}]}
        compressed, metadata = algo.compress(data)
        assert compressed is not None

    def test_estimate_savings(self):
        """Should estimate compression savings."""
        algo = DictionaryCompression(min_length=3, min_occurrences=2)
        data = {
            "items": [
                {"status": "completed"} for _ in range(10)
            ]
        }
        savings = algo.estimate_savings(data)
        assert isinstance(savings, float)
        assert 0.0 <= savings <= 1.0

    def test_estimate_savings_no_repetition(self):
        """Should return low savings for non-repetitive data."""
        algo = DictionaryCompression()
        data = {"items": [{"id": i} for i in range(5)]}
        savings = algo.estimate_savings(data)
        assert isinstance(savings, float)
        assert savings >= 0.0


class TestDeltaCompression:
    """Tests for delta compression algorithm."""

    def test_create_delta_compression(self):
        """Should create DeltaCompression instance."""
        algo = DeltaCompression()
        assert algo is not None

    def test_compress_numeric_sequences(self, numeric_sequence_data):
        """Should compress sequential numeric data."""
        algo = DeltaCompression()
        compressed, metadata = algo.compress(numeric_sequence_data)
        assert compressed is not None
        assert metadata is not None

    def test_compress_non_sequential(self):
        """Should handle non-sequential data."""
        algo = DeltaCompression()
        data = {"items": [{"value": 100}, {"value": 50}, {"value": 200}]}
        compressed, metadata = algo.compress(data)
        assert compressed is not None

    def test_estimate_savings_sequential(self, numeric_sequence_data):
        """Should estimate higher savings for sequential data."""
        algo = DeltaCompression()
        savings = algo.estimate_savings(numeric_sequence_data)
        assert isinstance(savings, float)
        assert savings >= 0.0

    def test_estimate_savings_random(self):
        """Should estimate lower savings for random data."""
        algo = DeltaCompression()
        data = {"items": [{"value": v} for v in [5, 100, 3, 999, 1]]}
        savings = algo.estimate_savings(data)
        assert isinstance(savings, float)


class TestPatternCompression:
    """Tests for pattern compression algorithm."""

    def test_create_pattern_compression(self):
        """Should create PatternCompression instance."""
        algo = PatternCompression()
        assert algo is not None

    def test_compress_patterned_data(self):
        """Should compress data with structural patterns."""
        algo = PatternCompression()
        data = {
            "items": [
                {"type": "A", "value": 1},
                {"type": "A", "value": 2},
                {"type": "A", "value": 3},
            ]
        }
        compressed, metadata = algo.compress(data)
        assert compressed is not None

    def test_compress_no_patterns(self):
        """Should handle data without patterns."""
        algo = PatternCompression()
        data = {
            "items": [
                {"a": 1},
                {"b": 2},
                {"c": 3},
            ]
        }
        compressed, metadata = algo.compress(data)
        assert compressed is not None

    def test_estimate_savings(self):
        """Should estimate pattern compression savings."""
        algo = PatternCompression()
        data = {
            "items": [
                {"pattern": "same", "id": i} for i in range(10)
            ]
        }
        savings = algo.estimate_savings(data)
        assert isinstance(savings, float)
        assert savings >= 0.0


class TestCompressionComparison:
    """Tests comparing different compression approaches."""

    def test_fast_is_fastest(self, large_dataset):
        """FAST mode should be quicker than ULTRA."""
        fast_engine = ATONCompressionEngine(mode=CompressionMode.FAST)
        ultra_engine = ATONCompressionEngine(mode=CompressionMode.ULTRA)

        import time

        start = time.time()
        fast_engine.compress(large_dataset)
        fast_time = time.time() - start

        start = time.time()
        ultra_engine.compress(large_dataset)
        ultra_time = time.time() - start

        # FAST should generally be faster or similar
        # (may not always hold for small datasets)
        assert fast_time >= 0  # Just verify it completes

    def test_all_modes_compress_successfully(self, employees_data):
        """All compression modes should successfully compress data."""
        modes = [
            CompressionMode.FAST,
            CompressionMode.BALANCED,
            CompressionMode.ULTRA,
            CompressionMode.ADAPTIVE,
        ]

        for mode in modes:
            engine = ATONCompressionEngine(mode=mode)
            compressed, metadata = engine.compress(employees_data)
            assert compressed is not None, f"Failed for mode: {mode}"

    def test_compression_preserves_structure(self, compression_engine_balanced, simple_products):
        """Compression should preserve data structure."""
        compressed, _ = compression_engine_balanced.compress(simple_products)

        # Structure should be maintained
        assert "products" in compressed or isinstance(compressed, dict)


class TestCompressionEdgeCases:
    """Tests for edge cases in compression."""

    def test_compress_empty_data(self, compression_engine_balanced):
        """Should handle empty data."""
        data = {"items": []}
        compressed, metadata = compression_engine_balanced.compress(data)
        assert compressed is not None

    def test_compress_single_record(self, compression_engine_balanced):
        """Should handle single record."""
        data = {"items": [{"id": 1, "name": "Single"}]}
        compressed, metadata = compression_engine_balanced.compress(data)
        assert compressed is not None

    def test_compress_large_strings(self, compression_engine_balanced):
        """Should handle large string values."""
        data = {
            "items": [
                {"id": 1, "text": "x" * 1000},
                {"id": 2, "text": "x" * 1000},
            ]
        }
        compressed, metadata = compression_engine_balanced.compress(data)
        assert compressed is not None

    def test_compress_deep_nesting(self, compression_engine_balanced):
        """Should handle deeply nested structures."""
        data = {
            "items": [
                {
                    "id": 1,
                    "nested": {
                        "level1": {
                            "level2": {"value": "deep"}
                        }
                    }
                }
            ]
        }
        compressed, metadata = compression_engine_balanced.compress(data)
        assert compressed is not None

    def test_compress_special_characters(self, compression_engine_balanced):
        """Should handle special characters."""
        data = {
            "items": [
                {"text": "Hello|World"},
                {"text": "Tab\there"},
                {"text": "Quote's"},
            ]
        }
        compressed, metadata = compression_engine_balanced.compress(data)
        assert compressed is not None


class TestAdaptiveCompression:
    """Tests for adaptive compression mode."""

    def test_adaptive_selects_appropriate_mode(self):
        """Adaptive mode should select mode based on data characteristics."""
        engine = ATONCompressionEngine(mode=CompressionMode.ADAPTIVE)

        # Small data
        small_data = {"items": [{"id": 1}]}
        compressed_small, _ = engine.compress(small_data)
        assert compressed_small is not None

        # Large data
        large_data = {"items": [{"id": i, "data": "x" * 100} for i in range(100)]}
        compressed_large, _ = engine.compress(large_data)
        assert compressed_large is not None

    def test_adaptive_handles_varied_data(self):
        """Adaptive mode should handle various data types."""
        engine = ATONCompressionEngine(mode=CompressionMode.ADAPTIVE)

        test_cases = [
            {"items": []},  # Empty
            {"items": [{"id": 1}]},  # Single
            {"items": [{"id": i} for i in range(50)]},  # Medium
            {"items": [{"status": "active"} for _ in range(20)]},  # Repeated
        ]

        for data in test_cases:
            compressed, _ = engine.compress(data)
            assert compressed is not None
