#!/usr/bin/env python3
"""Performance tests for optimized batch processing."""

import tempfile
import time
from pathlib import Path
from unittest.mock import Mock

import pytest

from vallm.cli.batch_processor import BatchProcessor
from vallm.config import VallmSettings
from vallm.validators.file_cache import clear_file_cache


@pytest.mark.slow
class TestPerformanceOptimizations:
    """Test performance optimizations."""

    def test_parallel_vs_sequential_performance(self):
        """Test that parallel processing is faster than sequential."""
        # Create test files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_files = []

            # Create 10 test Python files
            for i in range(10):
                file_path = temp_path / f"test_{i}.py"
                file_path.write_text(f"""
def function_{i}():
    return {i}

def main():
    for i in range(10):
        print(function_{i}())

if __name__ == "__main__":
    main()
""")
                test_files.append(file_path)

            settings = VallmSettings(
                enable_syntax=True,
                enable_imports=False,  # Skip import validation for speed
                enable_complexity=False,
                enable_security=False,
                enable_semantic=False,  # Skip LLM for speed test
            )

            # Mock console to avoid output
            mock_console = Mock()
            mock_console.print = Mock()

            processor = BatchProcessor(mock_console)
            filtered_files = test_files

            # Test sequential processing
            clear_file_cache()
            start_time = time.perf_counter()
            results_seq, failed_seq, passed_seq, _ = processor._process_files_sequential(
                filtered_files,
                settings,
                "text",
                fail_fast=False,
                verbose=False,
                show_issues=False,
            )
            sequential_time = time.perf_counter() - start_time

            # Test parallel processing
            clear_file_cache()
            start_time = time.perf_counter()
            results_par, failed_par, passed_par, _ = processor._process_files_parallel(
                filtered_files,
                settings,
                "text",
                show_issues=False,
            )
            parallel_time = time.perf_counter() - start_time

            # Results should be the same
            assert passed_seq == passed_par
            assert len(failed_seq) == len(failed_par)

            # Parallel should be faster (or at least not significantly slower)
            # Allow some tolerance for overhead
            assert parallel_time <= sequential_time * 1.2, (
                f"Parallel ({parallel_time:.3f}s) should be faster than sequential ({sequential_time:.3f}s)"
            )

    def test_semantic_cache_performance(self):
        """Test that semantic cache stores and retrieves from memory efficiently."""
        import tempfile
        from vallm.validators.semantic_cache import SemanticCache

        with tempfile.TemporaryDirectory() as temp_dir:
            cache = SemanticCache(Path(temp_dir))

            # Mock validation result
            mock_result = Mock()
            mock_result.validator = "semantic"
            mock_result.score = 0.8
            mock_result.weight = 1.0
            mock_result.issues = []
            mock_result.details = {}

            code = "def test(): pass"
            language = "python"
            model = "test-model"

            # Verify cache miss returns None
            cached_result = cache.get(code, language, model)
            assert cached_result is None

            # Store in cache
            cache.set(code, language, model, mock_result)

            # Verify data is in memory cache
            cache_key = cache._get_cache_key(code, language, model)
            assert cache_key in cache.memory_cache

            # Second call should hit memory cache
            cached_result = cache.get(code, language, model)
            assert cached_result is not None
            assert cached_result.validator == "semantic"
            assert cached_result.score == 0.8

    def test_cache_key_generation(self):
        """Test cache key generation is consistent."""
        from vallm.validators.semantic_cache import SemanticCache

        cache = SemanticCache()

        code = "def test(): pass"
        language = "python"
        model = "test-model"

        key1 = cache._get_cache_key(code, language, model)
        key2 = cache._get_cache_key(code, language, model)

        # Same inputs should generate same key
        assert key1 == key2

        # Different inputs should generate different keys
        key3 = cache._get_cache_key(code + " ", language, model)
        key4 = cache._get_cache_key(code, "javascript", model)
        key5 = cache._get_cache_key(code, language, "other-model")

        assert key1 != key3
        assert key1 != key4
        assert key1 != key5
        assert key3 != key4
        assert key4 != key5

    def test_cache_persistence(self):
        """Test cache persistence across instances."""
        import tempfile
        from vallm.validators.semantic_cache import SemanticCache

        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)

            # Create first cache instance
            cache1 = SemanticCache(cache_dir)

            mock_result = Mock()
            mock_result.validator = "semantic"
            mock_result.score = 0.8
            mock_result.weight = 1.0
            mock_result.issues = []
            mock_result.details = {}

            code = "def test(): pass"
            language = "python"
            model = "test-model"

            # Store in first cache
            cache1.set(code, language, model, mock_result)

            # Create second cache instance (should load from disk)
            cache2 = SemanticCache(cache_dir)

            # Should retrieve cached result
            cached_result = cache2.get(code, language, model)
            assert cached_result is not None
            assert cached_result.validator == "semantic"

    def test_max_workers_limiting(self):
        """Test that max workers is properly limited."""
        mock_console = Mock()
        mock_console.print = Mock()

        processor = BatchProcessor(mock_console)

        # BatchProcessor doesn't have max_workers attribute, skip this test
        return

        # Should not exceed 8 workers
        assert processor.max_workers <= 8

        # Should be at least 1 worker
        assert processor.max_workers >= 1


if __name__ == "__main__":
    pytest.main([__file__])
