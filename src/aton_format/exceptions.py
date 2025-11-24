"""
ATON Format - Custom Exceptions
================================

Custom exception hierarchy for ATON Format operations.
"""


class ATONError(Exception):
    """Base exception for all ATON-related errors."""
    pass


class ATONEncodingError(ATONError):
    """Exception raised during ATON encoding operations."""
    pass


class ATONDecodingError(ATONError):
    """Exception raised during ATON decoding operations."""
    pass


class ATONQueryError(ATONError):
    """Exception raised during query parsing or execution."""
    pass


class ATONCompressionError(ATONError):
    """Exception raised during compression operations."""
    pass
