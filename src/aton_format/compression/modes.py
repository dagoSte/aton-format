"""
ATON Format - Compression Modes
"""

from enum import Enum

class CompressionMode(Enum):
    """Compression strategies for ATON encoding"""
    FAST = "fast"           # Minimal processing, maximum speed
    BALANCED = "balanced"   # Optimal balance of speed and compression
    ULTRA = "ultra"         # Maximum compression, all algorithms
    ADAPTIVE = "adaptive"   # Intelligent mode selection

    @property
    def description(self) -> str:
        descriptions = {
            "fast": "Dictionary compression only",
            "balanced": "Dictionary + selective algorithms",
            "ultra": "All compression algorithms",
            "adaptive": "AI-driven mode selection"
        }
        return descriptions.get(self.value, "")


