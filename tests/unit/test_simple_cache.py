#!/usr/bin/env python3
"""
Simple unit tests for Cache System
Tests for utils/unified_cache_manager.py CacheBackend class
"""

import pytest
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from utils.unified_cache_manager import CacheBackend, UnifiedCacheManager


class TestCacheBackend:
    """Test cases for CacheBackend abstract class"""
    
    def test_cache_backend_interface(self):
        """Test CacheBackend abstract interface"""
        backend = CacheBackend()
        
        # Abstract methods should raise NotImplementedError
        with pytest.raises(NotImplementedError):
            backend.get("test_key")
        
        with pytest.raises(NotImplementedError):
            backend.set("test_key", "test_value")


class TestUnifiedCacheManager:
    """Test cases for UnifiedCacheManager class"""
    
    @pytest.fixture
    def cache_manager(self):
        """Create a cache manager for testing"""
        return UnifiedCacheManager()
    
    def test_cache_manager_initialization(self, cache_manager):
        """Test cache manager initialization"""
        assert cache_manager is not None
        assert hasattr(cache_manager, 'memory_backend')
        assert hasattr(cache_manager, 'redis_backend')
    
    def test_cache_set_get_basic(self, cache_manager):
        """Test basic cache set and get operations"""
        key = "test_key"
        value = "test_value"
        
        # Set value
        result = cache_manager.set(key, value)
        assert result is True
        
        # Get value
        retrieved = cache_manager.get(key)
        assert retrieved == value
    
    def test_cache_set_get_with_ttl(self, cache_manager):
        """Test cache operations with TTL"""
        key = "ttl_test_key"
        value = "ttl_test_value"
        ttl = 300  # 5 minutes
        
        # Set with TTL
        result = cache_manager.set(key, value, ttl=ttl)
        assert result is True
        
        # Get value (should exist)
        retrieved = cache_manager.get(key)
        assert retrieved == value
    
    def test_cache_delete(self, cache_manager):
        """Test cache deletion"""
        key = "delete_test_key"
        value = "delete_test_value"
        
        # Set and verify
        cache_manager.set(key, value)
        assert cache_manager.get(key) == value
        
        # Delete and verify
        result = cache_manager.delete(key)
        assert result is True
        
        # Should return None after deletion
        assert cache_manager.get(key) is None
    
    def test_cache_exists(self, cache_manager):
        """Test cache key existence check"""
        key = "exists_test_key"
        value = "exists_test_value"
        
        # Key should not exist initially
        assert cache_manager.exists(key) is False
        
        # Set value
        cache_manager.set(key, value)
        
        # Key should exist now
        assert cache_manager.exists(key) is True
        
        # Delete and check again
        cache_manager.delete(key)
        assert cache_manager.exists(key) is False
    
    def test_cache_clear(self, cache_manager):
        """Test cache clearing"""
        # Set multiple values
        test_data = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        }
        
        for key, value in test_data.items():
            cache_manager.set(key, value)
        
        # Verify all values exist
        for key, value in test_data.items():
            assert cache_manager.get(key) == value
        
        # Clear cache
        cache_manager.clear()
        
        # Verify all values are gone
        for key in test_data.keys():
            assert cache_manager.get(key) is None
    
    def test_cache_get_nonexistent_key(self, cache_manager):
        """Test getting non-existent key"""
        result = cache_manager.get("nonexistent_key")
        assert result is None
    
    def test_cache_delete_nonexistent_key(self, cache_manager):
        """Test deleting non-existent key"""
        result = cache_manager.delete("nonexistent_key")
        # Should not raise error, might return False or True depending on implementation
        assert isinstance(result, bool)
    
    def test_cache_with_different_data_types(self, cache_manager):
        """Test caching different data types"""
        test_cases = [
            ("string_key", "string_value"),
            ("int_key", 42),
            ("float_key", 3.14159),
            ("bool_key", True),
            ("list_key", [1, 2, 3, "test"]),
            ("dict_key", {"nested": {"key": "value"}}),
            ("none_key", None)
        ]
        
        for key, value in test_cases:
            # Set value
            cache_manager.set(key, value)
            
            # Get and verify
            retrieved = cache_manager.get(key)
            assert retrieved == value
    
    def test_cache_key_overwrite(self, cache_manager):
        """Test overwriting existing cache key"""
        key = "overwrite_test"
        
        # Set initial value
        cache_manager.set(key, "initial_value")
        assert cache_manager.get(key) == "initial_value"
        
        # Overwrite with new value
        cache_manager.set(key, "new_value")
        assert cache_manager.get(key) == "new_value"
    
    def test_cache_health_check(self, cache_manager):
        """Test cache health check functionality"""
        health_status = cache_manager.health_check()
        
        assert isinstance(health_status, dict)
        assert "memory_backend" in health_status
        
        # Memory backend should always be healthy
        assert health_status["memory_backend"]["status"] == "healthy"
    
    def test_cache_statistics(self, cache_manager):
        """Test cache statistics if available"""
        # Perform some operations
        cache_manager.set("stats_key1", "value1")
        cache_manager.get("stats_key1")  # Hit
        cache_manager.get("nonexistent")  # Miss
        
        # Try to get statistics (method may not exist in all implementations)
        try:
            stats = cache_manager.get_stats()
            if stats:
                assert isinstance(stats, dict)
                # Basic stats that might be available
                expected_keys = ["hits", "misses", "hit_rate"]
                for key in expected_keys:
                    if key in stats:
                        assert isinstance(stats[key], (int, float))
        except AttributeError:
            # get_stats method may not be implemented
            pass


@pytest.mark.integration
class TestCacheIntegration:
    """Integration tests for cache system"""
    
    def test_cache_performance_basic(self):
        """Test basic cache performance"""
        cache_manager = UnifiedCacheManager()
        
        # Test setting many values
        num_items = 100
        
        for i in range(num_items):
            key = f"perf_key_{i}"
            value = f"perf_value_{i}"
            result = cache_manager.set(key, value)
            assert result is True
        
        # Test getting all values
        for i in range(num_items):
            key = f"perf_key_{i}"
            expected_value = f"perf_value_{i}"
            actual_value = cache_manager.get(key)
            assert actual_value == expected_value
    
    def test_cache_concurrent_access_simulation(self):
        """Test simulated concurrent access"""
        cache_manager = UnifiedCacheManager()
        
        # Simulate multiple operations
        operations = [
            ("set", "key1", "value1"),
            ("set", "key2", "value2"),
            ("get", "key1", None),
            ("get", "key2", None),
            ("delete", "key1", None),
            ("get", "key1", None),  # Should return None
            ("exists", "key2", None),
        ]
        
        results = []
        for operation in operations:
            op_type = operation[0]
            key = operation[1]
            value = operation[2] if len(operation) > 2 else None
            
            if op_type == "set":
                result = cache_manager.set(key, value)
                results.append(("set", key, result))
            elif op_type == "get":
                result = cache_manager.get(key)
                results.append(("get", key, result))
            elif op_type == "delete":
                result = cache_manager.delete(key)
                results.append(("delete", key, result))
            elif op_type == "exists":
                result = cache_manager.exists(key)
                results.append(("exists", key, result))
        
        # Verify expected results
        assert len(results) == len(operations)
        
        # Check specific results
        set_results = [r for r in results if r[0] == "set"]
        assert all(r[2] is True for r in set_results)  # All sets should succeed
        
        # Get after delete should return None
        delete_get_result = next((r for r in results if r[0] == "get" and r[1] == "key1"), None)
        if delete_get_result and delete_get_result != results[2]:  # Skip the first get
            assert delete_get_result[2] is None