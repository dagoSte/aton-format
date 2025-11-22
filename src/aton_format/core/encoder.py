"""ATON Format - Encoder"""

import time
from typing import Any, Dict, List, Tuple, Union
from collections import Counter, defaultdict

from ..compression.modes import CompressionMode
from ..compression.engine import ATONCompressionEngine
from ..query.engine import ATONQueryEngine
from ..exceptions import ATONEncodingError, ATONQueryError


class ATONEncoder:
    """Production-grade ATON Encoder v2.0"""
    
    def __init__(self,
                 optimize: bool = True,
                 compression: Union[str, CompressionMode] = CompressionMode.BALANCED,
                 queryable: bool = False,
                 validate: bool = True):
        """Initialize encoder"""
        self.optimize = optimize
        self.queryable = queryable
        self.validate = validate
        
        # Parse compression mode
        if isinstance(compression, str):
            try:
                self.compression_mode = CompressionMode(compression.lower())
            except ValueError:
                raise ValueError(f"Invalid compression mode: {compression}")
        else:
            self.compression_mode = compression
        
        # Initialize engines
        self.compression_engine = ATONCompressionEngine(self.compression_mode)
        self.query_engine = ATONQueryEngine()
    
    def encode(self, data: Dict[str, Any], compress: bool = True) -> str:
        """Encode data to ATON format"""
        try:
            # Validate input
            if self.validate:
                self._validate_data(data)
            
            # Apply compression
            if compress and self.compression_mode != CompressionMode.FAST:
                compressed_data, metadata = self.compression_engine.compress(data)
                dictionary = metadata.get('dictionary', {})
            else:
                compressed_data = data
                dictionary = {}
            
            # Build ATON string
            aton_parts = []
            
            # Add dictionary
            if dictionary:
                aton_parts.append(self._format_dictionary(dictionary))
                aton_parts.append("")
            
            # Encode tables
            for table_name, records in compressed_data.items():
                if not isinstance(records, list):
                    continue
                
                # Infer structure
                if records:
                    schema = self._infer_schema(records[0])
                    defaults = self._infer_defaults(records) if self.optimize else {}
                else:
                    schema = []
                    defaults = {}
                
                # Add schema
                aton_parts.append(self._format_schema(schema))
                
                # Add defaults
                if defaults:
                    aton_parts.append(self._format_defaults(defaults))
                
                # Add queryable marker
                if self.queryable:
                    aton_parts.append(f"@queryable[{table_name}]")
                
                # Add table header
                aton_parts.append(f"\n{table_name}({len(records)}):")
                
                # Add records
                for record in records:
                    row = self._format_record(record, schema, defaults)
                    aton_parts.append(f"  {row}")
            
            return "\n".join(aton_parts)
        
        except Exception as e:
            raise ATONEncodingError(f"Encoding failed: {str(e)}") from e
    
    def encode_with_query(self, data: Dict[str, Any], query_string: str) -> str:
        """Encode with query filtering"""
        try:
            query = self.query_engine.parse(f"@query[{query_string}]")
            filtered_records = self.query_engine.execute(data, query)
            filtered_data = {query.table: filtered_records}
            aton = self.encode(filtered_data)
            return f"@query[{query_string}]\n\n{aton}"
        except Exception as e:
            raise ATONQueryError(f"Query encoding failed: {str(e)}") from e
    
    def _validate_data(self, data: Dict[str, Any]):
        """Validate input data structure"""
        if not isinstance(data, dict):
            raise ATONEncodingError("Data must be a dictionary")
        
        for table_name, records in data.items():
            if not isinstance(table_name, str):
                raise ATONEncodingError("Table names must be strings")
            if not isinstance(records, list):
                raise ATONEncodingError(f"Table '{table_name}' must be a list of records")
            for i, record in enumerate(records):
                if not isinstance(record, dict):
                    raise ATONEncodingError(f"Record {i} in table '{table_name}' must be a dictionary")
    
    def _format_dictionary(self, dictionary: Dict[str, str]) -> str:
        """Format compression dictionary"""
        entries = []
        for key, value in sorted(dictionary.items()):
            escaped_value = value.replace('"', '\\"')
            entries.append(f'{key}:"{escaped_value}"')
        return f"@dict[{', '.join(entries)}]"
    
    def _format_schema(self, schema: List[Tuple[str, str]]) -> str:
        """Format schema line"""
        fields = [f"{name}:{type_}" for name, type_ in schema]
        return f"@schema[{', '.join(fields)}]"
    
    def _format_defaults(self, defaults: Dict[str, Any]) -> str:
        """Format defaults line"""
        entries = []
        for key, value in sorted(defaults.items()):
            if isinstance(value, str):
                escaped_value = value.replace('"', '\\"')
                entries.append(f'{key}:"{escaped_value}"')
            elif isinstance(value, bool):
                entries.append(f'{key}:{"true" if value else "false"}')
            elif value is None:
                entries.append(f'{key}:null')
            else:
                entries.append(f'{key}:{value}')
        return f"@defaults[{', '.join(entries)}]"
    
    def _format_record(self, record: Dict, schema: List[Tuple], defaults: Dict) -> str:
        """Format single record"""
        values = []
        for field_name, field_type in schema:
            value = record.get(field_name)
            if field_name in defaults and value == defaults[field_name]:
                continue
            
            if value is None:
                formatted = "null"
            elif isinstance(value, bool):
                formatted = "true" if value else "false"
            elif isinstance(value, str):
                if value.startswith('#'):
                    formatted = value
                else:
                    escaped = value.replace('"', '\\"')
                    formatted = f'"{escaped}"'
            else:
                formatted = str(value)
            values.append(formatted)
        return ", ".join(values)
    
    def _infer_schema(self, record: Dict) -> List[Tuple[str, str]]:
        """Infer schema from record"""
        schema = []
        for key, value in record.items():
            type_str = self._infer_type(value)
            schema.append((key, type_str))
        return schema
    
    def _infer_defaults(self, records: List[Dict]) -> Dict[str, Any]:
        """Infer default values"""
        defaults = {}
        if not records:
            return defaults
        
        sample_size = min(100, len(records))
        field_values: Dict[str, List[Any]] = defaultdict(list)
        
        for record in records[:sample_size]:
            for key, value in record.items():
                field_values[key].append(value)
        
        for field, values in field_values.items():
            if values:
                # Skip unhashable types (lists, dicts) for default detection
                try:
                    value_counts = Counter(values)
                    most_common, count = value_counts.most_common(1)[0]
                    if count / len(values) > 0.6:
                        defaults[field] = most_common
                except TypeError:
                    # Unhashable type, skip default detection for this field
                    pass
        return defaults
    
    def _infer_type(self, value: Any) -> str:
        """Infer ATON type from value"""
        if isinstance(value, bool):
            return "bool"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "str"
        elif value is None:
            return "null"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, dict):
            return "object"
        else:
            return "str"
