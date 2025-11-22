# Changelog

All notable changes to ATON Format will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2025-11-20

### Major Release - Production-Grade Features

This is a **major release** with significant new features and architectural improvements. ATON V2 transforms from a proof-of-concept to a production-ready data serialization format for LLMs.

### Added

#### Advanced Compression System
- **4 Compression Modes**: Fast (~50K rec/sec), Balanced (~35K rec/sec), Ultra (~20K rec/sec), Adaptive (~30K rec/sec)
- **Dictionary Compression Algorithm**: Automatically identifies and compresses repeated strings
- **Delta Encoding**: Optimizes numeric sequences with differential encoding
- **Pattern Compression**: Detects and compresses structural patterns in data
- **Adaptive Mode**: AI-driven algorithm selection based on data characteristics
- **CompressionEngine**: Unified compression orchestration with mode-specific optimizations

#### SQL-like Query Language
- **Full AST-based Query Parser**: Complete lexical analysis and syntax parsing
- **WHERE Clause Support**: Multiple operators (=, !=, <, >, <=, >=, LIKE, IN, BETWEEN)
- **Logical Operators**: AND, OR, NOT with proper precedence
- **SELECT Projection**: Choose specific fields to encode
- **ORDER BY**: Sort results with ASC/DESC
- **LIMIT and OFFSET**: Pagination support
- **QueryEngine**: Efficient query execution on data before encoding
- **Error Handling**: Comprehensive query validation and error messages

#### Streaming Support
- **StreamEncoder**: Process datasets larger than memory
- **Chunked Processing**: Configurable chunk sizes for optimal performance
- **Schema Caching**: Reuse schema across chunks for efficiency
- **Memory Optimization**: Constant memory usage regardless of dataset size
- **Metadata Tracking**: Chunk information (first, last, total)
- **Progress Monitoring**: Track streaming progress in real-time

#### Production-Ready Infrastructure
- **Custom Exception Hierarchy**: ATONError, ATONEncodingError, ATONDecodingError, ATONQueryError, ATONCompressionError
- **Type Safety**: Complete type annotations with mypy compatibility
- **Input Validation**: Comprehensive validation at all API boundaries
- **Error Recovery**: Graceful error handling with detailed messages
- **Performance Metrics**: Built-in timing and compression statistics
- **Logging Support**: Integration with Python logging framework

#### Documentation & Developer Experience
- **Complete API Documentation**: Every class, method, and parameter documented
- **Usage Examples**: 15+ real-world examples for all features
- **Interactive Website**: Live converter with real-time token counting
- **Cost Calculator**: Estimate savings based on usage
- **Whitepaper**: Technical deep-dive into algorithms and design
- **Migration Guide**: Easy upgrade from V1 to V2

### Changed

#### Breaking Changes
- **Encoder API**: Now requires explicit compression mode selection
- **Schema Format**: Enhanced schema with more type information
- **Import Structure**: Reorganized into modular packages (core, compression, query, streaming)
- **Method Signatures**: Some parameter names changed for clarity

#### Improvements
- **Token Efficiency**: Improved from 45% to 50-60% reduction vs JSON
- **Encoding Speed**: 30% faster with optimized algorithms
- **Memory Usage**: 40% reduction in peak memory with streaming
- **Error Messages**: More descriptive and actionable
- **Type System**: Expanded type support (datetime, nested objects, arrays)

### Fixed
- **Schema Inference**: Handles edge cases with mixed-type arrays
- **Default Detection**: More accurate identification of common values
- **Relationship Parsing**: Correctly resolves circular references
- **Unicode Handling**: Proper encoding/decoding of all Unicode characters
- **Numeric Precision**: Maintains float precision across encode/decode cycles
- **Empty Arrays**: Correct handling of empty collections

### Dependencies
- **Zero Runtime Dependencies**: Pure Python implementation
- **Development Dependencies**: Updated to latest versions
  - pytest 7.4.0
  - black 23.7.0
  - mypy 1.5.0
  - flake8 6.1.0

### Performance

#### Benchmarks (vs V1)
```
Metric                  V1          V2          Improvement
---------------------------------------------------------------
Token Reduction        45%         56%         +24%
Encoding Speed         27K/sec     35K/sec     +30%
Memory Usage           100MB       60MB        -40%
Query Support          [X]         [OK]        New!
Streaming              [X]         [OK]        New!
Compression Modes      1           4           New!
```

#### Real-World Impact
- **API Cost Savings**: 50-60% reduction in LLM token costs
- **Context Window**: 2x more data in same context
- **Response Time**: 30% faster due to smaller payloads
- **Scalability**: Process 10x larger datasets with streaming

### Security
- **Input Sanitization**: Protection against malformed data
- **Injection Prevention**: Query parser prevents injection attacks
- **Safe Eval**: No use of eval() or exec()
- **Memory Safety**: Bounds checking on all operations

### Compatibility
- **Python Versions**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Operating Systems**: Linux, macOS, Windows
- **Architectures**: x86_64, ARM64, Apple Silicon
- **Backward Compatible**: Can decode V1 ATON format

### Documentation Updates
- **New Sections**: Query Language, Streaming, Compression Modes
- **API Reference**: Complete API documentation with examples
- **Migration Guide**: Step-by-step V1 to V2 upgrade
- **Best Practices**: Performance optimization guide
- **FAQ**: Common questions and solutions

---

## [1.0.2] - 2025-11-01

### Fixed
- Fixed schema inference for nested objects
- Corrected default value detection in sparse arrays
- Improved error messages for malformed ATON

### Changed
- Updated documentation with more examples
- Improved README with clearer quick start guide

---

## [1.0.1] - 2025-10-25

### Fixed
- Fixed encoding of special characters in strings
- Corrected handling of null values in arrays
- Fixed decoder for edge case with empty entities

### Added
- Added validation for schema field names
- Added support for datetime type inference

---

## [1.0.0] - 2025-10-15

### Initial Release

First stable release of ATON Format!

### Added
- **Core Encoding/Decoding**: Convert between JSON and ATON
- **Schema Inference**: Automatic type detection
- **Default Values**: Optimize repeated values
- **Type System**: Support for int, float, str, bool, array, object, null
- **Relationships**: Reference syntax with -> and <-
- **Optimization**: Configurable optimization levels
- **Documentation**: Complete API docs and examples

### Features
- 40-45% token reduction vs JSON
- Zero dependencies
- Pure Python implementation
- Full round-trip data integrity
- Human-readable format

---

## [0.9.0] - 2025-10-01

### Beta Release

Pre-release for testing and feedback.

### Added
- Basic encoder and decoder
- Simple schema system
- Default value detection
- Initial documentation

### Known Issues
- Limited error handling
- No query support
- No streaming
- Single compression strategy

---

## Version History Summary

| Version | Date | Status | Key Feature |
|---------|------|--------|-------------|
| 2.0.0 | 2025-11-20 | [OK] Stable | Production-grade with compression, queries, streaming |
| 1.0.2 | 2025-11-01 | [OK] Stable | Bug fixes and improvements |
| 1.0.1 | 2025-10-25 | [OK] Stable | Minor fixes |
| 1.0.0 | 2025-10-15 | [OK] Stable | Initial stable release |
| 0.9.0 | 2025-10-01 | [!] Beta | Pre-release |

---

## Upgrade Guides

### Upgrading from V1 to V2

#### Breaking Changes

**1. Encoder Initialization**
```python
# V1
encoder = ATONEncoder(optimize=True)

# V2
from aton_format import CompressionMode
encoder = ATONEncoder(
    compression=CompressionMode.BALANCED,
    optimize=True
)
```

**2. Import Structure**
```python
# V1
from aton_format import ATONEncoder, ATONDecoder

# V2 (same - backward compatible!)
from aton_format import ATONEncoder, ATONDecoder

# V2 (new features)
from aton_format import (
    CompressionMode,
    ATONQueryEngine,
    ATONStreamEncoder
)
```

**3. Error Handling**
```python
# V1
try:
    aton = encoder.encode(data)
except Exception as e:
    print(f"Error: {e}")

# V2 (more specific)
from aton_format import ATONEncodingError
try:
    aton = encoder.encode(data)
except ATONEncodingError as e:
    print(f"Encoding failed: {e}")
```

#### New Features to Adopt

**1. Use Compression Modes**
```python
# For real-time applications
encoder = ATONEncoder(compression=CompressionMode.FAST)

# For general purpose (recommended)
encoder = ATONEncoder(compression=CompressionMode.BALANCED)

# For maximum compression
encoder = ATONEncoder(compression=CompressionMode.ULTRA)
```

**2. Filter with Queries**
```python
from aton_format import ATONQueryEngine

query_engine = ATONQueryEngine()
filtered = query_engine.query(
    data,
    "employees WHERE salary > 100000"
)
aton = encoder.encode(filtered)
```

**3. Stream Large Datasets**
```python
from aton_format import ATONStreamEncoder

stream_encoder = ATONStreamEncoder(chunk_size=1000)
for chunk in stream_encoder.stream_encode(huge_dataset):
    process(chunk)
```

---

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Reporting Issues
- **Bugs**: [GitHub Issues](https://github.com/dagoSte/aton-format/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/dagoSte/aton-format/discussions)

### Development
```bash
git clone https://github.com/dagoSte/aton-format.git
cd aton-format
pip install -e ".[dev]"
pytest tests/
```

---

## Credits

**Author**: Stefano D'Agostino ([@dagoSte](https://github.com/dagoSte))

**Contributors**: See [CONTRIBUTORS.md](CONTRIBUTORS.md)

**License**: MIT

---

**[Website](https://www.atonformat.com)** | **[Documentation](https://www.atonformat.com/documentation.html)** | **[GitHub](https://github.com/dagoSte/aton-format)** | **[PyPI](https://pypi.org/project/aton-format/)**

Made with love for the LLM community
