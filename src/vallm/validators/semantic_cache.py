"""Semantic validation cache to avoid redundant LLM calls."""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple

from vallm.scoring import ValidationResult


class SemanticCache:
    """Cache for semantic validation results to improve performance."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize semantic cache.
        
        Args:
            cache_dir: Directory for cache files. If None, uses temp directory.
        """
        if cache_dir is None:
            cache_dir = Path(tempfile.gettempdir()) / "vallm_semantic_cache"
        
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.memory_cache: Dict[str, ValidationResult] = {}
    
    def _get_cache_key(self, code: str, language: str, model: str) -> str:
        """Generate cache key for code validation.
        
        Args:
            code: Source code to validate
            language: Programming language
            model: LLM model name
            
        Returns:
            Cache key string
        """
        # Create hash of code + language + model
        content = f"{language}:{model}:{code}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get(self, code: str, language: str, model: str) -> Optional[ValidationResult]:
        """Get cached validation result.
        
        Args:
            code: Source code to validate
            language: Programming language  
            model: LLM model name
            
        Returns:
            Cached ValidationResult or None if not found
        """
        cache_key = self._get_cache_key(code, language, model)
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            return self.memory_cache[cache_key]
        
        # Check file cache
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                
                # Reconstruct ValidationResult
                result = ValidationResult(
                    validator=data['validator'],
                    score=data['score'],
                    weight=data['weight'],
                    issues=[
                        {
                            'message': issue['message'],
                            'severity': issue['severity'],
                            'line': issue.get('line'),
                            'rule': issue.get('rule'),
                            'column': issue.get('column'),
                        }
                        for issue in data['issues']
                    ],
                    details=data.get('details', {})
                )
                
                # Store in memory cache
                self.memory_cache[cache_key] = result
                return result
                
            except (json.JSONDecodeError, KeyError):
                # Invalid cache file, remove it
                cache_file.unlink()
        
        return None
    
    def set(self, code: str, language: str, model: str, result: ValidationResult) -> None:
        """Cache validation result.
        
        Args:
            code: Source code that was validated
            language: Programming language
            model: LLM model name
            result: ValidationResult to cache
        """
        cache_key = self._get_cache_key(code, language, model)
        
        # Store in memory cache
        self.memory_cache[cache_key] = result
        
        # Store in file cache
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        # Serialize ValidationResult
        data = {
            'validator': result.validator,
            'score': result.score,
            'weight': result.weight,
            'issues': [
                {
                    'message': issue.message,
                    'severity': issue.severity.value,
                    'line': issue.line,
                    'rule': issue.rule,
                    'column': getattr(issue, 'column', None),
                }
                for issue in result.issues
            ],
            'details': getattr(result, 'details', {})
        }
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except (OSError, json.JSONEncodeError):
            # Failed to write cache, ignore
            pass
    
    def clear(self) -> None:
        """Clear all cached results."""
        # Clear memory cache
        self.memory_cache.clear()
        
        # Clear file cache
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except OSError:
                pass
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        file_count = len(list(self.cache_dir.glob("*.json")))
        memory_count = len(self.memory_cache)
        
        return {
            'memory_entries': memory_count,
            'file_entries': file_count,
            'total_entries': max(memory_count, file_count)
        }


# Global cache instance
_global_cache: Optional[SemanticCache] = None


def get_semantic_cache() -> SemanticCache:
    """Get global semantic cache instance.
    
    Returns:
        SemanticCache instance
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = SemanticCache()
    return _global_cache


def clear_semantic_cache() -> None:
    """Clear global semantic cache."""
    global _global_cache
    if _global_cache is not None:
        _global_cache.clear()
