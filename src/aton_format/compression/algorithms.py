"""
ATON Format - Compression Algorithms
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple
from collections import Counter


class CompressionAlgorithm(ABC):
    """Base class for compression algorithms"""
    
    @abstractmethod
    def compress(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Compress data and return compressed data + metadata"""
        pass
    
    @abstractmethod
    def estimate_savings(self, data: Dict[str, Any]) -> float:
        """Estimate compression savings (0.0 to 1.0)"""
        pass




class DictionaryCompression(CompressionAlgorithm):
    """Dictionary-based compression for repeated strings"""
    
    def __init__(self, min_length: int = 5, min_occurrences: int = 3):
        self.min_length = min_length
        self.min_occurrences = min_occurrences
        self.dictionary: Dict[str, str] = {}
        self.ref_counter = 0
    
    def compress(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Build dictionary and replace strings"""
        # Extract all strings
        strings = self._extract_strings(data)
        
        # Count occurrences
        string_counts = Counter(strings)
        
        # Build dictionary
        self.dictionary = {}
        for string, count in string_counts.items():
            if (len(string) >= self.min_length and 
                count >= self.min_occurrences and
                not string.startswith('#')):
                ref = f"#{self.ref_counter}"
                self.dictionary[ref] = string
                self.ref_counter += 1
        
        # Create reverse map
        reverse_dict = {v: k for k, v in self.dictionary.items()}
        
        # Replace strings in data
        compressed = self._replace_strings(data, reverse_dict)
        
        metadata = {'dictionary': self.dictionary}
        return compressed, metadata
    
    def estimate_savings(self, data: Dict[str, Any]) -> float:
        """Estimate potential savings"""
        strings = self._extract_strings(data)
        string_counts = Counter(strings)
        
        total_chars = sum(len(s) * count for s, count in string_counts.items())
        
        # Estimate compressed size
        saved_chars = 0
        for string, count in string_counts.items():
            if len(string) >= self.min_length and count >= self.min_occurrences:
                # Save (string_length - 3) * (count - 1) characters
                saved_chars += (len(string) - 3) * (count - 1)
        
        return saved_chars / total_chars if total_chars > 0 else 0.0
    
    def _extract_strings(self, obj: Any, strings: List[str] = None) -> List[str]:
        """Recursively extract strings"""
        if strings is None:
            strings = []
        
        if isinstance(obj, str):
            strings.append(obj)
        elif isinstance(obj, dict):
            for value in obj.values():
                self._extract_strings(value, strings)
        elif isinstance(obj, list):
            for item in obj:
                self._extract_strings(item, strings)
        
        return strings
    
    def _replace_strings(self, obj: Any, ref_map: Dict[str, str]) -> Any:
        """Replace strings with references"""
        if isinstance(obj, str) and obj in ref_map:
            return ref_map[obj]
        elif isinstance(obj, dict):
            return {k: self._replace_strings(v, ref_map) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._replace_strings(item, ref_map) for item in obj]
        else:
            return obj




class DeltaCompression(CompressionAlgorithm):
    """Delta encoding for numeric sequences"""
    
    def compress(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Apply delta encoding to numeric sequences"""
        compressed, delta_fields = self._apply_delta(data)
        metadata = {'delta_fields': delta_fields}
        return compressed, metadata
    
    def estimate_savings(self, data: Dict[str, Any]) -> float:
        """Estimate delta encoding savings"""
        numeric_sequences = self._find_numeric_sequences(data)
        
        if not numeric_sequences:
            return 0.0
        
        total_saved = 0
        total_values = 0
        
        for seq in numeric_sequences:
            if len(seq) > 1:
                deltas = [seq[i] - seq[i-1] for i in range(1, len(seq))]
                # Estimate: deltas are usually smaller
                avg_delta = sum(abs(d) for d in deltas) / len(deltas)
                avg_value = sum(abs(v) for v in seq) / len(seq)
                
                if avg_delta < avg_value * 0.5:
                    total_saved += len(seq) - 1
                    total_values += len(seq)
        
        return total_saved / total_values if total_values > 0 else 0.0
    
    def _apply_delta(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """Apply delta encoding where beneficial"""
        # Simplified for now - would need full implementation
        return data, []
    
    def _find_numeric_sequences(self, data: Dict[str, Any]) -> List[List[float]]:
        """Find numeric sequences in data"""
        sequences = []
        
        if isinstance(data, dict):
            for value in data.values():
                if isinstance(value, list) and all(isinstance(x, (int, float)) for x in value):
                    sequences.append(value)
                else:
                    sequences.extend(self._find_numeric_sequences(value))
        elif isinstance(data, list):
            for item in data:
                sequences.extend(self._find_numeric_sequences(item))
        
        return sequences




class PatternCompression(CompressionAlgorithm):
    """Pattern-based compression for structured data"""
    
    def compress(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Identify and compress patterns"""
        patterns = self._identify_patterns(data)
        compressed = self._apply_patterns(data, patterns)
        metadata = {'patterns': patterns}
        return compressed, metadata
    
    def estimate_savings(self, data: Dict[str, Any]) -> float:
        """Estimate pattern compression savings"""
        patterns = self._identify_patterns(data)
        return len(patterns) * 0.05  # Rough estimate
    
    def _identify_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify repeating patterns"""
        # Simplified - would implement full pattern detection
        return {}
    
    def _apply_patterns(self, data: Dict[str, Any], patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Apply identified patterns"""
        return data



