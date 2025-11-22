"""
ATON Format V2.0 - Core Types Tests
Tests for type definitions, enums, and data classes.
"""

import pytest
from aton_format.core.types import (
    ATONType,
    SortOrder,
    CompressionStats,
    QueryCondition,
    QueryExpression,
    ParsedQuery,
    StreamChunk,
)


class TestATONTypeEnum:
    """Tests for ATONType enumeration."""

    def test_all_types_defined(self):
        """All ATON types should be defined."""
        expected_types = ["INT", "FLOAT", "STR", "BOOL", "ARRAY", "OBJECT", "NULL", "DATETIME"]
        for type_name in expected_types:
            assert hasattr(ATONType, type_name)

    def test_type_values(self):
        """Type values should be lowercase strings."""
        assert ATONType.INT.value == "int"
        assert ATONType.FLOAT.value == "float"
        assert ATONType.STR.value == "str"
        assert ATONType.BOOL.value == "bool"
        assert ATONType.ARRAY.value == "array"
        assert ATONType.OBJECT.value == "object"
        assert ATONType.NULL.value == "null"
        assert ATONType.DATETIME.value == "datetime"


class TestSortOrderEnum:
    """Tests for SortOrder enumeration."""

    def test_sort_orders_defined(self):
        """ASC and DESC should be defined."""
        assert SortOrder.ASC.value == "ASC"
        assert SortOrder.DESC.value == "DESC"


class TestCompressionStats:
    """Tests for CompressionStats dataclass."""

    def test_create_compression_stats(self):
        """Should create CompressionStats with all fields."""
        stats = CompressionStats(
            original_size=1000,
            compressed_size=500,
            compression_ratio=0.5,
            tokens_saved=100,
            encoding_time_ms=10.5,
            mode="balanced",
            dictionary_size=20,
            metadata={"test": True},
        )

        assert stats.original_size == 1000
        assert stats.compressed_size == 500
        assert stats.compression_ratio == 0.5
        assert stats.tokens_saved == 100
        assert stats.encoding_time_ms == 10.5
        assert stats.mode == "balanced"
        assert stats.dictionary_size == 20
        assert stats.metadata == {"test": True}

    def test_compression_stats_defaults(self):
        """CompressionStats should have sensible defaults where applicable."""
        stats = CompressionStats(
            original_size=100,
            compressed_size=50,
            compression_ratio=0.5,
            tokens_saved=10,
            encoding_time_ms=1.0,
            mode="fast",
        )
        # dictionary_size and metadata may have defaults
        assert stats.original_size == 100


class TestQueryCondition:
    """Tests for QueryCondition dataclass and evaluation."""

    def test_create_query_condition(self):
        """Should create QueryCondition with field, operator, value."""
        condition = QueryCondition(
            field="price",
            operator=">",
            value=100,
        )
        assert condition.field == "price"
        assert condition.operator == ">"
        assert condition.value == 100

    def test_evaluate_equality(self):
        """Should evaluate equality conditions."""
        condition = QueryCondition(field="name", operator="=", value="test")
        assert condition.evaluate({"name": "test"}) is True
        assert condition.evaluate({"name": "other"}) is False

    def test_evaluate_not_equal(self):
        """Should evaluate not-equal conditions."""
        condition = QueryCondition(field="status", operator="!=", value="inactive")
        assert condition.evaluate({"status": "active"}) is True
        assert condition.evaluate({"status": "inactive"}) is False

    def test_evaluate_less_than(self):
        """Should evaluate less-than conditions."""
        condition = QueryCondition(field="price", operator="<", value=100)
        assert condition.evaluate({"price": 50}) is True
        assert condition.evaluate({"price": 100}) is False
        assert condition.evaluate({"price": 150}) is False

    def test_evaluate_greater_than(self):
        """Should evaluate greater-than conditions."""
        condition = QueryCondition(field="stock", operator=">", value=10)
        assert condition.evaluate({"stock": 20}) is True
        assert condition.evaluate({"stock": 10}) is False
        assert condition.evaluate({"stock": 5}) is False

    def test_evaluate_less_than_or_equal(self):
        """Should evaluate less-than-or-equal conditions."""
        condition = QueryCondition(field="qty", operator="<=", value=100)
        assert condition.evaluate({"qty": 50}) is True
        assert condition.evaluate({"qty": 100}) is True
        assert condition.evaluate({"qty": 101}) is False

    def test_evaluate_greater_than_or_equal(self):
        """Should evaluate greater-than-or-equal conditions."""
        condition = QueryCondition(field="qty", operator=">=", value=100)
        assert condition.evaluate({"qty": 150}) is True
        assert condition.evaluate({"qty": 100}) is True
        assert condition.evaluate({"qty": 99}) is False

    def test_evaluate_like_pattern(self):
        """Should evaluate LIKE pattern matching."""
        # LIKE with % wildcard
        condition = QueryCondition(field="name", operator="LIKE", value="%Laptop%")
        assert condition.evaluate({"name": "Laptop Pro"}) is True
        assert condition.evaluate({"name": "My Laptop"}) is True
        assert condition.evaluate({"name": "Mouse"}) is False

    def test_evaluate_in_list(self):
        """Should evaluate IN conditions."""
        condition = QueryCondition(
            field="category", operator="IN", value=["Electronics", "Furniture"]
        )
        assert condition.evaluate({"category": "Electronics"}) is True
        assert condition.evaluate({"category": "Furniture"}) is True
        assert condition.evaluate({"category": "Office"}) is False

    def test_evaluate_not_in_list(self):
        """Should evaluate NOT IN conditions."""
        condition = QueryCondition(
            field="status", operator="NOT IN", value=["deleted", "archived"]
        )
        assert condition.evaluate({"status": "active"}) is True
        assert condition.evaluate({"status": "deleted"}) is False

    def test_evaluate_between(self):
        """Should evaluate BETWEEN conditions."""
        condition = QueryCondition(
            field="price", operator="BETWEEN", value=50, value2=100
        )
        assert condition.evaluate({"price": 75}) is True
        assert condition.evaluate({"price": 50}) is True
        assert condition.evaluate({"price": 100}) is True
        assert condition.evaluate({"price": 49}) is False
        assert condition.evaluate({"price": 101}) is False

    def test_evaluate_missing_field(self):
        """Should handle missing fields gracefully."""
        condition = QueryCondition(field="nonexistent", operator="=", value="test")
        # Depending on implementation, may return False or raise
        result = condition.evaluate({"other_field": "value"})
        assert result is False  # Missing field should not match


class TestQueryExpression:
    """Tests for QueryExpression (complex query AST)."""

    def test_create_and_expression(self):
        """Should create AND expression with conditions."""
        cond1 = QueryCondition(field="price", operator=">", value=50)
        cond2 = QueryCondition(field="stock", operator=">", value=0)

        expr = QueryExpression(
            operator="AND",
            conditions=[cond1, cond2],
        )

        assert expr.operator == "AND"
        assert len(expr.conditions) == 2

    def test_evaluate_and_expression(self):
        """Should evaluate AND expression correctly."""
        cond1 = QueryCondition(field="price", operator=">", value=50)
        cond2 = QueryCondition(field="active", operator="=", value=True)

        expr = QueryExpression(operator="AND", conditions=[cond1, cond2])

        # Both true
        assert expr.evaluate({"price": 100, "active": True}) is True
        # One false
        assert expr.evaluate({"price": 100, "active": False}) is False
        assert expr.evaluate({"price": 30, "active": True}) is False
        # Both false
        assert expr.evaluate({"price": 30, "active": False}) is False

    def test_evaluate_or_expression(self):
        """Should evaluate OR expression correctly."""
        cond1 = QueryCondition(field="category", operator="=", value="Electronics")
        cond2 = QueryCondition(field="category", operator="=", value="Furniture")

        expr = QueryExpression(operator="OR", conditions=[cond1, cond2])

        assert expr.evaluate({"category": "Electronics"}) is True
        assert expr.evaluate({"category": "Furniture"}) is True
        assert expr.evaluate({"category": "Office"}) is False

    def test_evaluate_not_expression(self):
        """Should evaluate NOT expression correctly."""
        cond = QueryCondition(field="deleted", operator="=", value=True)
        expr = QueryExpression(operator="NOT", conditions=[cond])

        assert expr.evaluate({"deleted": False}) is True
        assert expr.evaluate({"deleted": True}) is False

    def test_nested_expressions(self):
        """Should handle nested expressions."""
        # (price > 50 AND active = True) OR category = "Featured"
        inner_and = QueryExpression(
            operator="AND",
            conditions=[
                QueryCondition(field="price", operator=">", value=50),
                QueryCondition(field="active", operator="=", value=True),
            ],
        )
        featured_cond = QueryCondition(
            field="category", operator="=", value="Featured"
        )
        outer_or = QueryExpression(
            operator="OR",
            conditions=[inner_and, featured_cond],
        )

        # Matches inner AND
        assert outer_or.evaluate({"price": 100, "active": True, "category": "Normal"}) is True
        # Matches featured
        assert outer_or.evaluate({"price": 10, "active": False, "category": "Featured"}) is True
        # Matches neither
        assert outer_or.evaluate({"price": 10, "active": False, "category": "Normal"}) is False


class TestParsedQuery:
    """Tests for ParsedQuery dataclass."""

    def test_create_parsed_query(self):
        """Should create ParsedQuery with all components."""
        where_expr = QueryExpression(
            operator="AND",
            conditions=[QueryCondition(field="price", operator=">", value=0)],
        )

        query = ParsedQuery(
            table="products",
            select_fields=["id", "name", "price"],
            where_expression=where_expr,
            order_by="price",
            order_direction=SortOrder.DESC,
            limit=10,
            offset=5,
        )

        assert query.table == "products"
        assert query.select_fields == ["id", "name", "price"]
        assert query.where_expression == where_expr
        assert query.order_by == "price"
        assert query.order_direction == SortOrder.DESC
        assert query.limit == 10
        assert query.offset == 5

    def test_parsed_query_optional_fields(self):
        """ParsedQuery should handle optional fields."""
        query = ParsedQuery(table="orders")
        assert query.table == "orders"
        assert query.select_fields is None or query.select_fields == []
        assert query.where_expression is None
        assert query.limit is None


class TestStreamChunk:
    """Tests for StreamChunk dataclass."""

    def test_create_stream_chunk(self):
        """Should create StreamChunk with all fields."""
        chunk = StreamChunk(
            chunk_id=1,
            total_chunks=5,
            data="@products|...",
            is_first=True,
            is_last=False,
            metadata={"progress": 20},
            schema=[("id", "int"), ("name", "str")],
            defaults={"active": True},
        )

        assert chunk.chunk_id == 1
        assert chunk.total_chunks == 5
        assert chunk.data == "@products|..."
        assert chunk.is_first is True
        assert chunk.is_last is False
        assert chunk.metadata == {"progress": 20}
        assert chunk.schema == [("id", "int"), ("name", "str")]
        assert chunk.defaults == {"active": True}

    def test_stream_chunk_first_last_markers(self):
        """StreamChunk should correctly identify first and last chunks."""
        first = StreamChunk(
            chunk_id=0, total_chunks=3, data="...", is_first=True, is_last=False, metadata={}
        )
        middle = StreamChunk(
            chunk_id=1, total_chunks=3, data="...", is_first=False, is_last=False, metadata={}
        )
        last = StreamChunk(
            chunk_id=2, total_chunks=3, data="...", is_first=False, is_last=True, metadata={}
        )

        assert first.is_first and not first.is_last
        assert not middle.is_first and not middle.is_last
        assert not last.is_first and last.is_last
