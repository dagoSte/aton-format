"""ATON Format - Stream Encoder"""

from typing import Any, Dict, Iterator, List, Tuple, Optional
from collections import Counter, defaultdict
from ..compression.modes import CompressionMode
from ..core.types import StreamChunk
from ..exceptions import ATONEncodingError


class ATONStreamEncoder:
    """Production-ready streaming encoder"""
    
    def __init__(self, 
                 chunk_size: int = 100,
                 compression: CompressionMode = CompressionMode.BALANCED):
        """Initialize streaming encoder"""
        if chunk_size < 1:
            raise ValueError("chunk_size must be >= 1")
        
        self.chunk_size = chunk_size
        self.compression_mode = compression
    
    def stream_encode(self, 
                     data: Dict[str, List[Dict]], 
                     table_name: Optional[str] = None) -> Iterator[StreamChunk]:
        """Stream encode large dataset"""
        if not data:
            raise ATONEncodingError("Empty data provided")
        
        if table_name is None:
            if len(data) != 1:
                raise ATONEncodingError("Multiple tables found, specify table_name")
            table_name = list(data.keys())[0]
        
        if table_name not in data:
            raise ATONEncodingError(f"Table '{table_name}' not found")
        
        records = data[table_name]
        
        if not isinstance(records, list):
            raise ATONEncodingError(f"Table '{table_name}' must be a list")
        
        total_records = len(records)
        total_chunks = (total_records + self.chunk_size - 1) // self.chunk_size
        
        if records:
            schema = self._infer_schema(records[0])
            defaults = self._infer_defaults(records)
        else:
            schema = []
            defaults = {}
        
        for chunk_id in range(total_chunks):
            start_idx = chunk_id * self.chunk_size
            end_idx = min(start_idx + self.chunk_size, total_records)
            chunk_records = records[start_idx:end_idx]
            
            if chunk_id == 0:
                aton_chunk = self._encode_full_chunk(chunk_records, schema, defaults, table_name)
            else:
                aton_chunk = self._encode_rows_only(chunk_records, schema, defaults, table_name)
            
            yield StreamChunk(
                chunk_id=chunk_id,
                total_chunks=total_chunks,
                data=aton_chunk,
                is_first=(chunk_id == 0),
                is_last=(chunk_id == total_chunks - 1),
                metadata={
                    'table': table_name,
                    'records_in_chunk': len(chunk_records),
                    'start_idx': start_idx,
                    'end_idx': end_idx,
                    'total_records': total_records,
                    'progress': (chunk_id + 1) / total_chunks
                },
                schema=schema if chunk_id == 0 else None,
                defaults=defaults if chunk_id == 0 else None
            )
    
    def _encode_full_chunk(self, records: List[Dict], schema: List[Tuple[str, str]], 
                          defaults: Dict[str, Any], table_name: str) -> str:
        """Encode first chunk with schema and defaults"""
        lines = []
        lines.append(self._format_schema(schema))
        if defaults:
            lines.append(self._format_defaults(defaults))
        lines.append(f"\n{table_name}({len(records)}):")
        for record in records:
            row = self._format_record(record, schema, defaults)
            lines.append(f"  {row}")
        return "\n".join(lines)
    
    def _encode_rows_only(self, records: List[Dict], schema: List[Tuple[str, str]], 
                          defaults: Dict[str, Any], table_name: str) -> str:
        """Encode data rows only"""
        lines = [f"\n{table_name}+({len(records)}):"]
        for record in records:
            row = self._format_record(record, schema, defaults)
            if row:
                lines.append(f"  {row}")
        return "\n".join(lines)
    
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
            values.append(self._format_value(value, field_type))
        return ", ".join(values)
    
    def _format_value(self, value: Any, type_hint: str) -> str:
        """Format value for ATON"""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, str):
            if '"' in value:
                value = value.replace('"', '\\"')
            return f'"{value}"'
        else:
            return str(value)
    
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
                value_counts = Counter(values)
                most_common, count = value_counts.most_common(1)[0]
                if count / len(values) > 0.6:
                    defaults[field] = most_common
        return defaults
    
    def _infer_type(self, value: Any) -> str:
        """Infer ATON type"""
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
