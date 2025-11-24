"""
ATON Format V2.0 - Basic Tests
"""

from aton_format import ATONEncoder, ATONDecoder, CompressionMode


def test_basic_encoding():
    """Test basic encode/decode"""
    print("Testing basic encoding...")

    encoder = ATONEncoder(
        compression=CompressionMode.BALANCED,
        optimize=True
    )

    data = {
        "products": [
            {"id": 1, "name": "Laptop", "price": 999.90, "active": True},
            {"id": 2, "name": "Mouse", "price": 29.90, "active": True},
            {"id": 3, "name": "Keyboard", "price": 59.90, "active": False}
        ]
    }

    # Encode
    aton = encoder.encode(data)
    print("[OK] Encoded successfully")
    print(f"ATON output:\n{aton}\n")

    # Decode
    decoder = ATONDecoder()
    decoded = decoder.decode(aton)
    print("[OK] Decoded successfully")

    # Verify
    assert data == decoded, "Data mismatch!"
    print("[OK] Round-trip successful!\n")


def test_compression_modes():
    """Test different compression modes"""
    print("Testing compression modes...")

    data = {
        "employees": [
            {"id": i, "name": f"Employee {i}", "dept": "Engineering"}
            for i in range(10)
        ]
    }

    modes = [
        CompressionMode.FAST,
        CompressionMode.BALANCED,
        CompressionMode.ULTRA
    ]

    for mode in modes:
        encoder = ATONEncoder(compression=mode)
        aton = encoder.encode(data)

        decoder = ATONDecoder()
        decoded = decoder.decode(aton)

        assert data == decoded, f"Failed for mode: {mode.value}"
        print(f"[OK] {mode.value.upper()} mode: OK")

    print()


def test_query_language():
    """Test query functionality"""
    print("Testing query language...")

    encoder = ATONEncoder(compression=CompressionMode.BALANCED)

    data = {
        "products": [
            {"id": 1, "name": "Laptop", "price": 999, "stock": 5},
            {"id": 2, "name": "Mouse", "price": 29, "stock": 100},
            {"id": 3, "name": "Monitor", "price": 299, "stock": 20},
            {"id": 4, "name": "Keyboard", "price": 79, "stock": 50}
        ]
    }

    # Query with WHERE
    aton = encoder.encode_with_query(
        data,
        "products WHERE price > 50"
    )

    print("[OK] Query executed successfully")
    print(f"Filtered ATON:\n{aton}\n")


def test_streaming():
    """Test streaming encoder"""
    print("Testing streaming...")

    from aton_format import ATONStreamEncoder

    data = {
        "records": [
            {"id": i, "value": f"Record {i}"}
            for i in range(250)  # 250 records
        ]
    }

    stream_encoder = ATONStreamEncoder(
        chunk_size=100,
        compression=CompressionMode.FAST
    )

    chunks = list(stream_encoder.stream_encode(data))

    assert len(chunks) == 3, "Expected 3 chunks"
    assert chunks[0].is_first, "First chunk not marked"
    assert chunks[-1].is_last, "Last chunk not marked"

    print(f"[OK] Streaming: {len(chunks)} chunks created")
    print()


def main():
    """Run all tests"""
    print("=" * 60)
    print("ATON Format V2.0 - Test Suite")
    print("=" * 60)
    print()

    tests = [
        ("Basic Encoding", test_basic_encoding),
        ("Compression Modes", test_compression_modes),
        ("Query Language", test_query_language),
        ("Streaming", test_streaming),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {name} FAILED: {str(e)}\n")
            failed += 1

    print("=" * 60)
    print(f"Results: {passed}/{len(tests)} tests passed")
    if failed == 0:
        print("[OK] ALL TESTS PASSED!")
    else:
        print(f"[FAIL] {failed} test(s) failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
