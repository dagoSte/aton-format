"""
ATON Format V2.0 - Exception Tests
Tests for the custom exception hierarchy.
"""

import pytest
from aton_format.exceptions import (
    ATONError,
    ATONEncodingError,
    ATONDecodingError,
    ATONQueryError,
    ATONCompressionError,
)


class TestATONErrorHierarchy:
    """Tests for exception inheritance hierarchy."""

    def test_aton_error_is_base_exception(self):
        """ATONError should be the base for all custom exceptions."""
        error = ATONError("base error")
        assert isinstance(error, Exception)
        assert str(error) == "base error"

    def test_encoding_error_inherits_from_aton_error(self):
        """ATONEncodingError should inherit from ATONError."""
        error = ATONEncodingError("encoding failed")
        assert isinstance(error, ATONError)
        assert isinstance(error, Exception)
        assert str(error) == "encoding failed"

    def test_decoding_error_inherits_from_aton_error(self):
        """ATONDecodingError should inherit from ATONError."""
        error = ATONDecodingError("decoding failed")
        assert isinstance(error, ATONError)
        assert isinstance(error, Exception)
        assert str(error) == "decoding failed"

    def test_query_error_inherits_from_aton_error(self):
        """ATONQueryError should inherit from ATONError."""
        error = ATONQueryError("query failed")
        assert isinstance(error, ATONError)
        assert isinstance(error, Exception)
        assert str(error) == "query failed"

    def test_compression_error_inherits_from_aton_error(self):
        """ATONCompressionError should inherit from ATONError."""
        error = ATONCompressionError("compression failed")
        assert isinstance(error, ATONError)
        assert isinstance(error, Exception)
        assert str(error) == "compression failed"


class TestExceptionUsage:
    """Tests for practical exception usage."""

    def test_can_catch_specific_exception(self):
        """Should be able to catch specific exception types."""
        with pytest.raises(ATONEncodingError):
            raise ATONEncodingError("test")

    def test_can_catch_with_base_class(self):
        """All ATON exceptions should be catchable with ATONError."""
        exceptions = [
            ATONEncodingError("encoding"),
            ATONDecodingError("decoding"),
            ATONQueryError("query"),
            ATONCompressionError("compression"),
        ]

        for exc in exceptions:
            with pytest.raises(ATONError):
                raise exc

    def test_exception_message_preserved(self):
        """Exception messages should be preserved."""
        message = "Detailed error message with context"
        error = ATONEncodingError(message)
        assert str(error) == message
        assert message in repr(error)

    def test_exception_can_wrap_original(self):
        """Exceptions should support wrapping original errors."""
        original = ValueError("original error")
        try:
            raise ATONDecodingError("wrapped error") from original
        except ATONDecodingError as e:
            assert e.__cause__ is original

    def test_exception_differentiation(self):
        """Different exception types should be distinguishable."""
        errors = {
            "encoding": ATONEncodingError("enc"),
            "decoding": ATONDecodingError("dec"),
            "query": ATONQueryError("qry"),
            "compression": ATONCompressionError("cmp"),
        }

        for name, error in errors.items():
            assert type(error).__name__ == f"ATON{name.capitalize()}Error"


class TestExceptionInContext:
    """Tests for exceptions in realistic usage contexts."""

    def test_encoding_error_in_try_except(self):
        """Test handling encoding errors in try-except blocks."""
        handled = False
        try:
            raise ATONEncodingError("Invalid data structure")
        except ATONEncodingError as e:
            handled = True
            assert "Invalid" in str(e)
        assert handled

    def test_multiple_exception_handling(self):
        """Test handling multiple ATON exception types."""
        results = []

        for error_class, message in [
            (ATONEncodingError, "enc"),
            (ATONDecodingError, "dec"),
            (ATONQueryError, "qry"),
        ]:
            try:
                raise error_class(message)
            except ATONEncodingError:
                results.append("encoding")
            except ATONDecodingError:
                results.append("decoding")
            except ATONQueryError:
                results.append("query")

        assert results == ["encoding", "decoding", "query"]
