"""
ATON Format V2.0 - Adaptive Token-Oriented Notation
===================================================

Production-grade data serialization for LLMs.

Quick Start:
    >>> from aton_format import ATONEncoder, ATONDecoder, CompressionMode
    >>> 
    >>> encoder = ATONEncoder(compression=CompressionMode.BALANCED)
    >>> data = {"test": [{"id": 1, "value": "hello"}]}
    >>> aton = encoder.encode(data)
    >>> 
    >>> decoder = ATONDecoder()
    >>> original = decoder.decode(aton)
"""

__version__ = "2.0.0"
__author__ = "Stefano D'Agostino"

# Core
from .core.encoder import ATONEncoder
from .core.decoder import ATONDecoder
from .core.types import ATONType, SortOrder

# Compression
from .compression.modes import CompressionMode
from .compression.engine import ATONCompressionEngine

# Query
from .query.engine import ATONQueryEngine
from .query.operators import QueryOperator, LogicalOperator

# Streaming
from .streaming.encoder import ATONStreamEncoder

# Exceptions
from .exceptions import (
    ATONError,
    ATONEncodingError,
    ATONDecodingError,
    ATONQueryError,
    ATONCompressionError,
)

__all__ = [
    # Version
    "__version__",
    "__author__",
    
    # Core
    "ATONEncoder",
    "ATONDecoder",
    "ATONType",
    "SortOrder",
    
    # Compression
    "CompressionMode",
    "ATONCompressionEngine",
    
    # Query
    "ATONQueryEngine",
    "QueryOperator",
    "LogicalOperator",
    
    # Streaming
    "ATONStreamEncoder",
    
    # Exceptions
    "ATONError",
    "ATONEncodingError",
    "ATONDecodingError",
    "ATONQueryError",
    "ATONCompressionError",
]
