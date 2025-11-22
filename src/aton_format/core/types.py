"""
ATON Format - Type Definitions
===============================

Core type definitions, enums, and data classes.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import re


class ATONType(Enum):
    """ATON data types."""
    INT = "int"
    FLOAT = "float"
    STR = "str"
    BOOL = "bool"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"
    DATETIME = "datetime"


class SortOrder(Enum):
    """Sort direction for query results."""
    ASC = "ASC"
    DESC = "DESC"


@dataclass
class CompressionStats:
    """Statistics from compression operation."""
    original_size: int
    compressed_size: int
    compression_ratio: float
    tokens_saved: int
    encoding_time_ms: float
    mode: str
    dictionary_size: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryCondition:
    """Single query condition."""
    field: str
    operator: str
    value: Any
    value2: Optional[Any] = None  # For BETWEEN
    
    def evaluate(self, record: Dict[str, Any]) -> bool:
        """Evaluate condition against record."""
        if self.field not in record:
            return False
        
        record_value = record[self.field]
        
        if self.operator == "=":
            return record_value == self.value
        elif self.operator == "!=":
            return record_value != self.value
        elif self.operator == "<":
            return record_value < self.value if record_value is not None else False
        elif self.operator == ">":
            return record_value > self.value if record_value is not None else False
        elif self.operator == "<=":
            return record_value <= self.value if record_value is not None else False
        elif self.operator == ">=":
            return record_value >= self.value if record_value is not None else False
        elif self.operator == "LIKE":
            if not isinstance(record_value, str):
                return False
            pattern = str(self.value).replace("%", ".*").replace("_", ".")
            return bool(re.search(pattern, record_value, re.IGNORECASE))
        elif self.operator == "IN":
            return record_value in self.value if self.value else False
        elif self.operator == "NOT IN":
            return record_value not in self.value if self.value else True
        elif self.operator == "BETWEEN":
            low, high = self.value, self.value2
            return low <= record_value <= high if record_value is not None else False
        return False


@dataclass
class QueryExpression:
    """AST node for query expressions."""
    conditions: List[Any]  # List[Union[QueryCondition, QueryExpression]]
    operator: str
    
    def evaluate(self, record: Dict[str, Any]) -> bool:
        """Recursively evaluate expression against record."""
        if self.operator == "AND":
            return all(self._eval_condition(cond, record) for cond in self.conditions)
        elif self.operator == "OR":
            return any(self._eval_condition(cond, record) for cond in self.conditions)
        elif self.operator == "NOT":
            return not self._eval_condition(self.conditions[0], record)
        else:
            # Single condition
            return self._eval_condition(self.conditions[0], record)
    
    def _eval_condition(self, condition: Any, record: Dict[str, Any]) -> bool:
        """Evaluate a single condition."""
        if isinstance(condition, QueryExpression):
            return condition.evaluate(record)
        elif isinstance(condition, QueryCondition):
            return condition.evaluate(record)
        return False


@dataclass
class ParsedQuery:
    """Parsed query structure."""
    table: str
    select_fields: Optional[List[str]] = None
    where_expression: Optional[QueryExpression] = None
    order_by: Optional[str] = None
    order_direction: SortOrder = SortOrder.ASC
    limit: Optional[int] = None
    offset: int = 0


@dataclass
class StreamChunk:
    """Single chunk in streaming mode."""
    chunk_id: int
    total_chunks: int
    data: str
    is_first: bool
    is_last: bool
    metadata: Dict[str, Any]
    schema: Optional[List[Tuple[str, str]]] = None
    defaults: Optional[Dict[str, Any]] = None
