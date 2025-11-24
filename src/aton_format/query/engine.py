"""
ATON Format - Query Engine
"""

from typing import Any, Dict, List
from .parser import QueryParser
from ..core.types import SortOrder, ParsedQuery
from ..exceptions import ATONQueryError


class ATONQueryEngine:
    """Execute parsed queries on data"""
    
    def __init__(self):
        self.parser = QueryParser()
    
    def parse(self, query_string: str) -> ParsedQuery:
        """Parse query string"""
        return self.parser.parse(query_string)
    
    def execute(self, data: Dict[str, List[Dict]], query: ParsedQuery) -> List[Dict]:
        """Execute parsed query on data"""
        # Get table
        if query.table not in data:
            raise ATONQueryError(f"Table '{query.table}' not found")
        
        records = data[query.table]
        
        # WHERE filtering
        if query.where_expression:
            records = [r for r in records if query.where_expression.evaluate(r)]
        
        # SELECT projection
        if query.select_fields:
            records = [
                {field: record.get(field) for field in query.select_fields}
                for record in records
            ]
        
        # ORDER BY
        if query.order_by:
            reverse = query.order_direction == SortOrder.DESC
            records = sorted(records, 
                           key=lambda x: x.get(query.order_by, 0), 
                           reverse=reverse)
        
        # OFFSET
        if query.offset:
            records = records[query.offset:]
        
        # LIMIT
        if query.limit:
            records = records[:query.limit]
        
        return records
