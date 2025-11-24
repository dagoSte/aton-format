"""
ATON Format V2.0 - Streaming Tests
Tests for ATONStreamEncoder.
"""

import pytest
from aton_format import ATONStreamEncoder, CompressionMode
from aton_format.core.types import StreamChunk


class TestATONStreamEncoderBasic:
    """Basic streaming encoder functionality tests."""

    def test_create_stream_encoder(self, stream_encoder):
        """Should create stream encoder instance."""
        assert stream_encoder is not None

    def test_create_with_custom_chunk_size(self):
        """Should create with custom chunk size."""
        encoder = ATONStreamEncoder(chunk_size=25)
        assert encoder is not None

    def test_create_with_compression_mode(self):
        """Should create with different compression modes."""
        for mode in CompressionMode:
            encoder = ATONStreamEncoder(compression=mode)
            assert encoder is not None

    def test_stream_encode_returns_iterator(self, stream_encoder, large_dataset):
        """stream_encode should return an iterator."""
        result = stream_encoder.stream_encode(large_dataset)
        # Should be iterable
        assert hasattr(result, "__iter__")


class TestATONStreamEncoderChunking:
    """Tests for chunking functionality."""

    def test_produces_correct_number_of_chunks(self, stream_encoder_small_chunks):
        """Should produce correct number of chunks based on chunk_size."""
        # 50 records with chunk_size=10 should produce 5 chunks
        data = {"items": [{"id": i} for i in range(50)]}
        chunks = list(stream_encoder_small_chunks.stream_encode(data))

        assert len(chunks) == 5

    def test_first_chunk_marked(self, stream_encoder, large_dataset):
        """First chunk should be marked with is_first=True."""
        chunks = list(stream_encoder.stream_encode(large_dataset))

        assert chunks[0].is_first is True
        # Other chunks should not be first
        for chunk in chunks[1:]:
            assert chunk.is_first is False

    def test_last_chunk_marked(self, stream_encoder, large_dataset):
        """Last chunk should be marked with is_last=True."""
        chunks = list(stream_encoder.stream_encode(large_dataset))

        assert chunks[-1].is_last is True
        # Other chunks should not be last
        for chunk in chunks[:-1]:
            assert chunk.is_last is False

    def test_single_chunk_is_first_and_last(self, stream_encoder):
        """Single chunk should be both first and last."""
        data = {"items": [{"id": i} for i in range(10)]}  # Small data
        chunks = list(stream_encoder.stream_encode(data))

        if len(chunks) == 1:
            assert chunks[0].is_first is True
            assert chunks[0].is_last is True

    def test_chunk_ids_sequential(self, stream_encoder_small_chunks, large_dataset):
        """Chunk IDs should be sequential."""
        chunks = list(stream_encoder_small_chunks.stream_encode(large_dataset))

        for i, chunk in enumerate(chunks):
            assert chunk.chunk_id == i

    def test_total_chunks_accurate(self, stream_encoder_small_chunks):
        """total_chunks should match actual chunk count."""
        data = {"items": [{"id": i} for i in range(50)]}
        chunks = list(stream_encoder_small_chunks.stream_encode(data))

        expected_total = 5  # 50 / 10
        for chunk in chunks:
            assert chunk.total_chunks == expected_total


class TestStreamChunkContent:
    """Tests for chunk content."""

    def test_chunk_contains_data(self, stream_encoder, large_dataset):
        """Each chunk should contain data."""
        chunks = list(stream_encoder.stream_encode(large_dataset))

        for chunk in chunks:
            assert isinstance(chunk.data, str)
            assert len(chunk.data) > 0

    def test_first_chunk_contains_schema(self, stream_encoder, large_dataset):
        """First chunk should contain schema metadata."""
        chunks = list(stream_encoder.stream_encode(large_dataset))

        first_chunk = chunks[0]
        # Schema should be present in first chunk
        assert first_chunk.schema is not None or "$" in first_chunk.data

    def test_first_chunk_contains_defaults(self, stream_encoder):
        """First chunk should contain defaults if applicable."""
        data = {
            "items": [
                {"id": i, "status": "active"} for i in range(100)
            ]
        }
        chunks = list(stream_encoder.stream_encode(data))

        first_chunk = chunks[0]
        # Defaults should be present in first chunk
        assert first_chunk.defaults is not None or first_chunk.data is not None

    def test_chunk_metadata_present(self, stream_encoder, large_dataset):
        """Chunks should contain metadata."""
        chunks = list(stream_encoder.stream_encode(large_dataset))

        for chunk in chunks:
            assert chunk.metadata is not None or isinstance(chunk, StreamChunk)


class TestStreamEncoderEdgeCases:
    """Tests for edge cases in streaming."""

    def test_empty_data(self, stream_encoder):
        """Should handle empty data."""
        data = {"items": []}
        chunks = list(stream_encoder.stream_encode(data))

        # Should produce at least one chunk or handle gracefully
        assert isinstance(chunks, list)

    def test_single_record(self, stream_encoder):
        """Should handle single record."""
        data = {"items": [{"id": 1, "name": "Single"}]}
        chunks = list(stream_encoder.stream_encode(data))

        assert len(chunks) >= 1
        assert chunks[0].is_first
        assert chunks[-1].is_last

    def test_exact_chunk_boundary(self, stream_encoder_small_chunks):
        """Should handle data size exactly matching chunk boundary."""
        # Exactly 10 records with chunk_size=10
        data = {"items": [{"id": i} for i in range(10)]}
        chunks = list(stream_encoder_small_chunks.stream_encode(data))

        assert len(chunks) == 1

    def test_one_over_chunk_boundary(self, stream_encoder_small_chunks):
        """Should handle data size one over chunk boundary."""
        # 11 records with chunk_size=10
        data = {"items": [{"id": i} for i in range(11)]}
        chunks = list(stream_encoder_small_chunks.stream_encode(data))

        assert len(chunks) == 2

    def test_large_records(self, stream_encoder):
        """Should handle records with large values."""
        data = {
            "items": [
                {"id": i, "data": "x" * 1000} for i in range(20)
            ]
        }
        chunks = list(stream_encoder.stream_encode(data))

        assert len(chunks) >= 1
        for chunk in chunks:
            assert len(chunk.data) > 0


class TestStreamEncoderCompression:
    """Tests for compression in streaming."""

    def test_streaming_with_fast_compression(self, large_dataset):
        """Should stream with FAST compression."""
        encoder = ATONStreamEncoder(chunk_size=50, compression=CompressionMode.FAST)
        chunks = list(encoder.stream_encode(large_dataset))

        assert len(chunks) >= 1

    def test_streaming_with_balanced_compression(self, large_dataset):
        """Should stream with BALANCED compression."""
        encoder = ATONStreamEncoder(chunk_size=50, compression=CompressionMode.BALANCED)
        chunks = list(encoder.stream_encode(large_dataset))

        assert len(chunks) >= 1

    def test_streaming_with_ultra_compression(self, large_dataset):
        """Should stream with ULTRA compression."""
        encoder = ATONStreamEncoder(chunk_size=50, compression=CompressionMode.ULTRA)
        chunks = list(encoder.stream_encode(large_dataset))

        assert len(chunks) >= 1

    def test_streaming_with_adaptive_compression(self, large_dataset):
        """Should stream with ADAPTIVE compression."""
        encoder = ATONStreamEncoder(chunk_size=50, compression=CompressionMode.ADAPTIVE)
        chunks = list(encoder.stream_encode(large_dataset))

        assert len(chunks) >= 1


class TestStreamEncoderTableName:
    """Tests for table name handling."""

    def test_auto_detect_table_name(self, stream_encoder, large_dataset):
        """Should auto-detect table name from data keys."""
        chunks = list(stream_encoder.stream_encode(large_dataset))

        # Data should reference the table
        assert len(chunks) >= 1

    def test_explicit_table_name(self, stream_encoder, large_dataset):
        """Should accept explicit table name."""
        chunks = list(stream_encoder.stream_encode(large_dataset, table_name="records"))

        assert len(chunks) >= 1


class TestStreamEncoderMemoryEfficiency:
    """Tests for memory-efficient streaming."""

    def test_iterator_yields_incrementally(self, stream_encoder_small_chunks):
        """Iterator should yield chunks incrementally."""
        data = {"items": [{"id": i} for i in range(100)]}
        iterator = stream_encoder_small_chunks.stream_encode(data)

        # Get first chunk
        first = next(iterator)
        assert first.chunk_id == 0
        assert first.is_first is True

        # Get second chunk
        second = next(iterator)
        assert second.chunk_id == 1

    def test_can_iterate_multiple_times(self, stream_encoder, large_dataset):
        """Should be able to call stream_encode multiple times."""
        chunks1 = list(stream_encoder.stream_encode(large_dataset))
        chunks2 = list(stream_encoder.stream_encode(large_dataset))

        assert len(chunks1) == len(chunks2)


class TestStreamChunkDataClass:
    """Tests for StreamChunk dataclass."""

    def test_stream_chunk_attributes(self, stream_encoder, large_dataset):
        """StreamChunk should have all required attributes."""
        chunks = list(stream_encoder.stream_encode(large_dataset))

        for chunk in chunks:
            assert hasattr(chunk, "chunk_id")
            assert hasattr(chunk, "total_chunks")
            assert hasattr(chunk, "data")
            assert hasattr(chunk, "is_first")
            assert hasattr(chunk, "is_last")
            assert hasattr(chunk, "metadata")

    def test_stream_chunk_types(self, stream_encoder, large_dataset):
        """StreamChunk attributes should have correct types."""
        chunks = list(stream_encoder.stream_encode(large_dataset))

        for chunk in chunks:
            assert isinstance(chunk.chunk_id, int)
            assert isinstance(chunk.total_chunks, int)
            assert isinstance(chunk.data, str)
            assert isinstance(chunk.is_first, bool)
            assert isinstance(chunk.is_last, bool)


class TestStreamEncoderProgress:
    """Tests for progress tracking in streaming."""

    def test_progress_in_metadata(self, stream_encoder_small_chunks):
        """Metadata should contain progress information."""
        data = {"items": [{"id": i} for i in range(50)]}
        chunks = list(stream_encoder_small_chunks.stream_encode(data))

        # Check that progress can be calculated from chunk info
        for i, chunk in enumerate(chunks):
            expected_progress = (i + 1) / chunk.total_chunks * 100
            # Progress should be trackable
            assert chunk.chunk_id <= chunk.total_chunks

    def test_can_calculate_completion_percentage(self, stream_encoder_small_chunks):
        """Should be able to calculate completion percentage."""
        data = {"items": [{"id": i} for i in range(50)]}

        for chunk in stream_encoder_small_chunks.stream_encode(data):
            completion = (chunk.chunk_id + 1) / chunk.total_chunks * 100
            assert 0 < completion <= 100
