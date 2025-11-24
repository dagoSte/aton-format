"""
ATON Format - Compression Engine
"""

import json
import time
from typing import Any, Dict, Tuple
from aton_format.compression.modes import CompressionMode
from aton_format.compression.algorithms import DictionaryCompression, DeltaCompression, PatternCompression

class ATONCompressionEngine:
    """Production-grade compression orchestrator"""
    
    def __init__(self, mode: CompressionMode = CompressionMode.BALANCED):
        self.mode = mode
        self.algorithms: List[CompressionAlgorithm] = [
            DictionaryCompression(min_length=5, min_occurrences=3),
            DeltaCompression(),
            PatternCompression()
        ]
    
    def compress(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Apply compression based on mode"""
        start_time = time.time()
        
        if self.mode == CompressionMode.FAST:
            compressed, metadata = self._compress_fast(data)
        elif self.mode == CompressionMode.BALANCED:
            compressed, metadata = self._compress_balanced(data)
        elif self.mode == CompressionMode.ULTRA:
            compressed, metadata = self._compress_ultra(data)
        else:  # ADAPTIVE
            compressed, metadata = self._compress_adaptive(data)
        
        encoding_time = (time.time() - start_time) * 1000
        metadata['encoding_time_ms'] = encoding_time
        
        return compressed, metadata
    
    def _compress_fast(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Fast compression - dictionary only"""
        algo = self.algorithms[0]  # Dictionary
        return algo.compress(data)
    
    def _compress_balanced(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Balanced compression - dictionary + selective others"""
        compressed = data
        combined_metadata = {}
        
        # Apply dictionary
        compressed, meta = self.algorithms[0].compress(compressed)
        combined_metadata.update(meta)
        
        return compressed, combined_metadata
    
    def _compress_ultra(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Ultra compression - all algorithms"""
        compressed = data
        combined_metadata = {}
        
        for algo in self.algorithms:
            compressed, meta = algo.compress(compressed)
            combined_metadata.update(meta)
        
        return compressed, combined_metadata
    
    def _compress_adaptive(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Adaptive compression - choose best strategy"""
        data_str = json.dumps(data)
        
        # Analyze data characteristics
        size = len(data_str)
        
        if size < 1000:
            return self._compress_fast(data)
        elif size < 10000:
            return self._compress_balanced(data)
        else:
            # Estimate each algorithm
            best_algo = max(self.algorithms, key=lambda a: a.estimate_savings(data))
            return best_algo.compress(data)


