# ATON Format V2.0 - Quick Start Guide

## Installation

```bash
pip install aton-format
```

## Basic Usage

```python
from aton_format import ATONEncoder, ATONDecoder, CompressionMode

# Create encoder
encoder = ATONEncoder(
    compression=CompressionMode.BALANCED,
    optimize=True
)

# Your data
data = {
    "employees": [
        {"id": 1, "name": "Alice", "salary": 95000},
        {"id": 2, "name": "Bob", "salary": 87000},
        {"id": 3, "name": "Carol", "salary": 92000}
    ]
}

# Encode (50-60% token reduction!)
aton_text = encoder.encode(data)
print(aton_text)

# Decode back
decoder = ATONDecoder()
original = decoder.decode(aton_text)

assert data == original  # Perfect round-trip!
```

## Output

```
@schema[id:int, name:str, salary:int]

employees(3):
  1, "Alice", 95000
  2, "Bob", 87000
  3, "Carol", 92000
```

## Key Features

- [OK] **50-60% Token Reduction** - Dramatic cost savings on LLM API calls
- [OK] **4 Compression Modes** - Fast, Balanced, Ultra, Adaptive
- [OK] **SQL-like Query Language** - Filter before encoding
- [OK] **Streaming Support** - Process millions of records
- [OK] **100% Data Integrity** - Perfect round-trip guaranteed
- [OK] **Production Ready** - Complete error handling

## Compression Modes

```python
# Fast mode - optimized for speed
encoder = ATONEncoder(compression=CompressionMode.FAST)

# Balanced mode - optimal mix (RECOMMENDED)
encoder = ATONEncoder(compression=CompressionMode.BALANCED)

# Ultra mode - maximum compression
encoder = ATONEncoder(compression=CompressionMode.ULTRA)

# Adaptive mode - AI-driven selection
encoder = ATONEncoder(compression=CompressionMode.ADAPTIVE)
```

## Query Language

```python
from aton_format import ATONQueryEngine

# Filter data BEFORE encoding
encoder.encode_with_query(
    data,
    "employees WHERE salary > 90000 ORDER BY salary DESC"
)
```

## Streaming

```python
from aton_format import ATONStreamEncoder

# Process large datasets with constant memory
stream_encoder = ATONStreamEncoder(chunk_size=1000)

for chunk in stream_encoder.stream_encode(huge_dataset):
    process_chunk(chunk['data'])
```

## Documentation

- **Full Documentation**: https://www.atonformat.com/documentation.html
- **GitHub**: https://github.com/dagoSte/aton-format
- **PyPI**: https://pypi.org/project/aton-format/

## Support

- **Issues**: https://github.com/dagoSte/aton-format/issues
- **Email**: dago.stefano@gmail.com

---

**Made with love by Stefano D'Agostino**
