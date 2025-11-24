"""ATON Format - Decoder"""

from typing import Any, Dict, List, Tuple
from ..exceptions import ATONDecodingError


class ATONDecoder:
    """Production-grade ATON decoder"""
    
    def __init__(self, validate: bool = True):
        self.validate = validate
        self.dictionary: Dict[str, str] = {}
    
    def decode(self, aton_string: str) -> Dict[str, List[Dict]]:
        """Decode ATON string"""
        try:
            lines = [l.rstrip() for l in aton_string.split('\n')]
            result = {}
            schema = []
            defaults = {}
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                if not line:
                    i += 1
                    continue
                
                if line.startswith('@dict'):
                    self.dictionary = self._parse_dict(line)
                elif line.startswith('@schema'):
                    schema = self._parse_schema(line)
                elif line.startswith('@defaults'):
                    defaults = self._parse_defaults(line)
                elif line.startswith('@'):
                    pass
                elif '(' in line and line.endswith('):'):
                    # Table header
                    table = line.split('(')[0]
                    count = int(line.split('(')[1].split(')')[0])
                    result[table] = []
                    
                    # Read count records
                    i += 1
                    for _ in range(count):
                        while i < len(lines):
                            data_line = lines[i].strip()
                            if data_line and not data_line.startswith('@') and not ('(' in data_line and data_line.endswith('):')):
                                record = self._parse_record(data_line, schema, defaults)
                                result[table].append(record)
                                i += 1
                                break
                            elif data_line.startswith('@') or not data_line:
                                i += 1
                            else:
                                break
                    continue
                
                i += 1
            
            return result
        except Exception as e:
            raise ATONDecodingError(f"Decode failed: {e}")
    
    def _parse_dict(self, line: str) -> Dict[str, str]:
        content = line[line.index('[')+1:line.rindex(']')]
        d = {}
        for item in self._split_smart(content, ','):
            if ':' in item:
                k, v = item.split(':', 1)
                v = v.strip().strip('"').replace('\\"', '"')
                d[k.strip()] = v
        return d
    
    def _parse_schema(self, line: str) -> List[Tuple[str, str]]:
        content = line[line.index('[')+1:line.rindex(']')]
        schema = []
        for item in self._split_smart(content, ','):
            if ':' in item:
                name, type_ = item.split(':', 1)
                schema.append((name.strip(), type_.strip()))
        return schema
    
    def _parse_defaults(self, line: str) -> Dict[str, Any]:
        content = line[line.index('[')+1:line.rindex(']')]
        defaults = {}
        for item in self._split_smart(content, ','):
            if ':' in item:
                k, v = item.split(':', 1)
                val = self._parse_val(v.strip())
                if isinstance(val, str) and val.startswith('#') and val in self.dictionary:
                    val = self.dictionary[val]
                defaults[k.strip()] = val
        return defaults
    
    def _parse_record(self, line: str, schema: List[Tuple], defaults: Dict) -> Dict:
        vals = self._split_smart(line, ',') if line else []
        rec = {name: defaults.get(name) for name, _ in schema if name in defaults}
        
        for idx, (name, _) in enumerate(schema):
            if idx < len(vals):
                val = self._parse_val(vals[idx].strip())
                if isinstance(val, str) and val.startswith('#') and val in self.dictionary:
                    val = self.dictionary[val]
                rec[name] = val
        return rec
    
    def _parse_val(self, v: str) -> Any:
        if v == 'null': return None
        if v == 'true': return True
        if v == 'false': return False
        if v.startswith('"') and v.endswith('"'):
            return v[1:-1].replace('\\"', '"')
        if v.startswith('#'): return v
        # Handle arrays like ['a', 'b', 'c']
        if v.startswith('[') and v.endswith(']'):
            return self._parse_array(v)
        try:
            return float(v) if '.' in v else int(v)
        except:
            return v

    def _parse_array(self, v: str) -> List[Any]:
        """Parse array notation like ['a', 'b'] or [1, 2, 3]"""
        content = v[1:-1].strip()
        if not content:
            return []
        items = self._split_smart(content, ',')
        return [self._parse_val(item.strip().strip("'")) for item in items]
    
    def _split_smart(self, text: str, delim: str) -> List[str]:
        parts = []
        curr = []
        in_q = False
        bracket_depth = 0
        i = 0
        while i < len(text):
            c = text[i]
            # Handle escaped quotes inside strings
            if c == '\\' and i + 1 < len(text) and text[i + 1] == '"':
                curr.append(c)
                curr.append(text[i + 1])
                i += 2
                continue
            if c == '"':
                in_q = not in_q
            elif c == '[' and not in_q:
                bracket_depth += 1
            elif c == ']' and not in_q:
                bracket_depth -= 1
            elif c == delim and not in_q and bracket_depth == 0:
                if curr: parts.append(''.join(curr).strip())
                curr = []
                i += 1
                continue
            curr.append(c)
            i += 1
        if curr: parts.append(''.join(curr).strip())
        return [p for p in parts if p]
