"""
ATON Format - Query Parser
"""

import re
from typing import Any, List, Optional, Tuple, Union
from ..query.operators import QueryOperator, LogicalOperator
from ..core.types import QueryExpression, ParsedQuery, SortOrder, QueryCondition
from ..exceptions import ATONQueryError


class QueryTokenizer:
    """Tokenize SQL-like query strings"""
    
    TOKEN_PATTERNS = [
        ('SELECT', r'\bSELECT\b'),
        ('FROM', r'\bFROM\b'),
        ('WHERE', r'\bWHERE\b'),
        ('ORDER', r'\bORDER\s+BY\b'),
        ('LIMIT', r'\bLIMIT\b'),
        ('OFFSET', r'\bOFFSET\b'),
        ('AND', r'\bAND\b'),
        ('OR', r'\bOR\b'),
        ('NOT', r'\bNOT\b'),
        ('IN', r'\bIN\b'),
        ('LIKE', r'\bLIKE\b'),
        ('BETWEEN', r'\bBETWEEN\b'),
        ('ASC', r'\bASC\b'),
        ('DESC', r'\bDESC\b'),
        ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('NUMBER', r'-?\d+\.?\d*'),
        ('STRING', r"'[^']*'|\"[^\"]*\""),
        ('OPERATOR', r'<=|>=|!=|<>|=|<|>'),
        ('COMMA', r','),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('WHITESPACE', r'\s+'),
    ]
    
    def __init__(self):
        self.patterns = [(name, re.compile(pattern, re.IGNORECASE)) 
                        for name, pattern in self.TOKEN_PATTERNS]
    
    def tokenize(self, query: str) -> List[Tuple[str, str]]:
        """Tokenize query string into tokens"""
        tokens = []
        pos = 0
        
        while pos < len(query):
            matched = False
            
            for token_name, pattern in self.patterns:
                match = pattern.match(query, pos)
                if match:
                    value = match.group(0)
                    if token_name != 'WHITESPACE':  # Skip whitespace
                        tokens.append((token_name, value))
                    pos = match.end()
                    matched = True
                    break
            
            if not matched:
                raise ATONQueryError(f"Invalid character at position {pos}: '{query[pos]}'")
        
        return tokens


class QueryParser:
    """Full AST parser for ATON query language"""
    
    def __init__(self):
        self.tokenizer = QueryTokenizer()
        self.tokens: List[Tuple[str, str]] = []
        self.pos = 0
    
    def parse(self, query_string: str) -> ParsedQuery:
        """Parse complete query into AST"""
        # Extract query from @query[...] if present
        query_match = re.search(r'@query\[(.*)\]', query_string, re.IGNORECASE | re.DOTALL)
        if query_match:
            query_string = query_match.group(1)
        
        # Tokenize
        self.tokens = self.tokenizer.tokenize(query_string)
        self.pos = 0
        
        # Parse components
        table = self._parse_table()
        select_fields = self._parse_select() if self._peek('SELECT') else None
        where_expr = self._parse_where() if self._peek('WHERE') else None
        order_by, order_dir = self._parse_order_by() if self._peek('ORDER') else (None, SortOrder.ASC)
        limit = self._parse_limit() if self._peek('LIMIT') else None
        offset = self._parse_offset() if self._peek('OFFSET') else 0
        
        return ParsedQuery(
            table=table,
            select_fields=select_fields,
            where_expression=where_expr,
            order_by=order_by,
            order_direction=order_dir,
            limit=limit,
            offset=offset
        )
    
    def _current(self) -> Optional[Tuple[str, str]]:
        """Get current token"""
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    
    def _peek(self, token_type: str) -> bool:
        """Check if current token matches type"""
        current = self._current()
        return current and current[0] == token_type
    
    def _consume(self, token_type: str) -> str:
        """Consume and return token of expected type"""
        current = self._current()
        if not current or current[0] != token_type:
            raise ATONQueryError(f"Expected {token_type}, got {current[0] if current else 'EOF'}")
        self.pos += 1
        return current[1]
    
    def _parse_table(self) -> str:
        """Parse table name"""
        return self._consume('IDENTIFIER')
    
    def _parse_select(self) -> List[str]:
        """Parse SELECT clause"""
        self._consume('SELECT')
        
        fields = []
        fields.append(self._consume('IDENTIFIER'))
        
        while self._peek('COMMA'):
            self._consume('COMMA')
            fields.append(self._consume('IDENTIFIER'))
        
        return fields
    
    def _parse_where(self) -> QueryExpression:
        """Parse WHERE clause into expression tree"""
        self._consume('WHERE')
        return self._parse_or_expression()
    
    def _parse_or_expression(self) -> QueryExpression:
        """Parse OR expressions"""
        left = self._parse_and_expression()
        
        if self._peek('OR'):
            conditions = [left]
            while self._peek('OR'):
                self._consume('OR')
                conditions.append(self._parse_and_expression())
            return QueryExpression(conditions=conditions, operator="OR")
        
        return left
    
    def _parse_and_expression(self) -> QueryExpression:
        """Parse AND expressions"""
        conditions = [self._parse_condition()]
        
        while self._peek('AND'):
            self._consume('AND')
            conditions.append(self._parse_condition())
        
        return QueryExpression(conditions=conditions, operator="AND")
    
    def _parse_condition(self) -> Union[QueryCondition, QueryExpression]:
        """Parse single condition"""
        # Handle parentheses
        if self._peek('LPAREN'):
            self._consume('LPAREN')
            expr = self._parse_or_expression()
            self._consume('RPAREN')
            return expr
        
        # Handle NOT
        if self._peek('NOT'):
            self._consume('NOT')
            inner = self._parse_condition()
            return QueryExpression(conditions=[inner], operator="NOT")
        
        # Parse field
        field = self._consume('IDENTIFIER')
        
        # Parse operator
        if self._peek('IN') or self._peek('LIKE') or self._peek('BETWEEN'):
            return self._parse_special_condition(field)
        
        # Standard operator
        op_str = self._consume('OPERATOR')
        operator = op_str
        
        # Parse value
        value = self._parse_value()
        
        return QueryCondition(field=field, operator=operator, value=value)
    
    def _parse_special_condition(self, field: str) -> QueryCondition:
        """Parse IN, LIKE, BETWEEN conditions"""
        if self._peek('IN'):
            self._consume('IN')
            self._consume('LPAREN')
            
            values = [self._parse_value()]
            while self._peek('COMMA'):
                self._consume('COMMA')
                values.append(self._parse_value())
            
            self._consume('RPAREN')
            return QueryCondition(field=field, operator="IN", value=values)
        
        elif self._peek('LIKE'):
            self._consume('LIKE')
            pattern = self._parse_value()
            return QueryCondition(field=field, operator="LIKE", value=pattern)
        
        elif self._peek('BETWEEN'):
            self._consume('BETWEEN')
            val1 = self._parse_value()
            self._consume('AND')
            val2 = self._parse_value()
            return QueryCondition(field=field, operator="BETWEEN", value=val1, value2=val2)
        
        raise ATONQueryError("Invalid special condition")
    
    def _parse_value(self) -> Any:
        """Parse value (string, number, identifier)"""
        if self._peek('STRING'):
            value = self._consume('STRING')
            return value[1:-1]  # Remove quotes
        elif self._peek('NUMBER'):
            value = self._consume('NUMBER')
            return float(value) if '.' in value else int(value)
        elif self._peek('IDENTIFIER'):
            # Could be boolean or null
            value = self._consume('IDENTIFIER')
            if value.upper() == 'TRUE':
                return True
            elif value.upper() == 'FALSE':
                return False
            elif value.upper() == 'NULL':
                return None
            return value
        else:
            raise ATONQueryError("Expected value")
    
    def _parse_order_by(self) -> Tuple[str, SortOrder]:
        """Parse ORDER BY clause"""
        self._consume('ORDER')
        field = self._consume('IDENTIFIER')
        
        direction = SortOrder.ASC
        if self._peek('ASC'):
            self._consume('ASC')
        elif self._peek('DESC'):
            self._consume('DESC')
            direction = SortOrder.DESC
        
        return field, direction
    
    def _parse_limit(self) -> int:
        """Parse LIMIT clause"""
        self._consume('LIMIT')
        value = self._consume('NUMBER')
        return int(value)
    
    def _parse_offset(self) -> int:
        """Parse OFFSET clause"""
        self._consume('OFFSET')
        value = self._consume('NUMBER')
        return int(value)
