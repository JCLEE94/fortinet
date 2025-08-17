#!/usr/bin/env python3
"""
Unit tests for Unified Cache Manager
Tests for utils/unified_cache_manager.py
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time
import json
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from utils.unified_cache_manager import (
    UnifiedCacheManager,
    CacheConfig,
    CacheStats,
    cache_key_generator,
    TTLCache
)


class TestCacheConfig:
    """Test cases for CacheConfig class"""
    
    def test_cache_config_defaults(self):
        """Test CacheConfig with default values"""
        config = CacheConfig()
        
        assert config.redis_enabled is True
        assert config.memory_enabled is True
        assert config.default_ttl == 3600
        assert config.max_memory_items == 1000
        assert config.redis_host == "localhost"
        assert config.redis_port == 6379
        assert config.redis_db == 0
    
    def test_cache_config_custom_values(self):
        """Test CacheConfig with custom values"""
        config = CacheConfig(
            redis_enabled=False,
            memory_enabled=True,
            default_ttl=7200,
            max_memory_items=2000,
            redis_host="remote.redis.com",
            redis_port=6380,
            redis_db=1
        )
        
        assert config.redis_enabled is False
        assert config.memory_enabled is True
        assert config.default_ttl == 7200
        assert config.max_memory_items == 2000
        assert config.redis_host == "remote.redis.com"
        assert config.redis_port == 6380
        assert config.redis_db == 1
    
    def test_cache_config_from_env(self):
        """Test CacheConfig from environment variables"""
        env_vars = {
            'REDIS_HOST': 'env.redis.com',
            'REDIS_PORT': '6381',
            'REDIS_DB': '2',
            'CACHE_TTL': '3600',
            'MAX_CACHE_ITEMS': '5000'
        }
        
        with patch.dict(os.environ, env_vars):
            config = CacheConfig.from_environment()
            
            assert config.redis_host == "env.redis.com"
            assert config.redis_port == 6381
            assert config.redis_db == 2
            assert config.default_ttl == 3600
            assert config.max_memory_items == 5000


class TestCacheStats:
    """Test cases for CacheStats class"""
    
    def test_cache_stats_initialization(self):
        """Test CacheStats initialization"""
        stats = CacheStats()
        
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.total_requests == 0
        assert stats.hit_rate == 0.0
    
    def test_cache_stats_record_hit(self):
        """Test recording cache hits"""
        stats = CacheStats()
        
        stats.record_hit()
        assert stats.hits == 1
        assert stats.total_requests == 1
        assert stats.hit_rate == 1.0
        
        stats.record_hit()
        assert stats.hits == 2
        assert stats.total_requests == 2
        assert stats.hit_rate == 1.0
    
    def test_cache_stats_record_miss(self):
        """Test recording cache misses"""
        stats = CacheStats()
        
        stats.record_miss()
        assert stats.misses == 1
        assert stats.total_requests == 1
        assert stats.hit_rate == 0.0
        
        stats.record_miss()
        assert stats.misses == 2
        assert stats.total_requests == 2
        assert stats.hit_rate == 0.0
    
    def test_cache_stats_hit_rate_calculation(self):
        """Test hit rate calculation"""
        stats = CacheStats()
        
        # Record some hits and misses
        stats.record_hit()
        stats.record_hit()
        stats.record_miss()
        stats.record_hit()
        
        assert stats.hits == 3
        assert stats.misses == 1
        assert stats.total_requests == 4
        assert stats.hit_rate == 0.75
    
    def test_cache_stats_reset(self):
        """Test resetting cache stats"""
        stats = CacheStats()
        
        stats.record_hit()
        stats.record_miss()
        
        stats.reset()
        
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.total_requests == 0
        assert stats.hit_rate == 0.0
    
    def test_cache_stats_to_dict(self):
        """Test converting stats to dictionary"""
        stats = CacheStats()
        
        stats.record_hit()
        stats.record_miss()
        
        stats_dict = stats.to_dict()
        
        expected = {
            'hits': 1,
            'misses': 1,
            'total_requests': 2,
            'hit_rate': 0.5
        }
        
        assert stats_dict == expected


class TestTTLCache:
    """Test cases for TTLCache class"""
    
    def test_ttl_cache_initialization(self):
        """Test TTLCache initialization"""
        cache = TTLCache(max_size=100)
        
        assert cache.max_size == 100
        assert len(cache.data) == 0
        assert len(cache.timestamps) == 0
    
    def test_ttl_cache_set_get(self):
        """Test basic set and get operations"""
        cache = TTLCache(max_size=100)
        
        cache.set("key1", "value1", ttl=60)
        assert cache.get("key1") == "value1"
        
        cache.set("key2", {"data": "test"}, ttl=60)
        assert cache.get("key2") == {"data": "test"}
    
    def test_ttl_cache_expiration(self):
        """Test cache expiration"""
        cache = TTLCache(max_size=100)
        
        with patch('time.time', return_value=1000):
            cache.set("key1", "value1", ttl=60)
        
        # Item should exist
        with patch('time.time', return_value=1030):
            assert cache.get("key1") == "value1"
        
        # Item should be expired
        with patch('time.time', return_value=1070):
            assert cache.get("key1") is None
    
    def test_ttl_cache_size_limit(self):
        """Test cache size limitation"""
        cache = TTLCache(max_size=2)
        
        cache.set("key1", "value1", ttl=60)
        cache.set("key2", "value2", ttl=60)
        cache.set("key3", "value3", ttl=60)  # Should evict oldest
        
        assert cache.get("key1") is None  # Evicted
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
    
    def test_ttl_cache_delete(self):
        """Test cache deletion"""
        cache = TTLCache(max_size=100)
        
        cache.set("key1", "value1", ttl=60)
        assert cache.get("key1") == "value1"
        
        cache.delete("key1")
        assert cache.get("key1") is None
    
    def test_ttl_cache_exists(self):
        """Test cache key existence check"""
        cache = TTLCache(max_size=100)
        
        assert not cache.exists("key1")
        
        cache.set("key1", "value1", ttl=60)
        assert cache.exists("key1")
        
        cache.delete("key1")
        assert not cache.exists("key1")
    
    def test_ttl_cache_clear(self):
        """Test cache clearing"""
        cache = TTLCache(max_size=100)
        
        cache.set("key1", "value1", ttl=60)
        cache.set("key2", "value2", ttl=60)
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert len(cache.data) == 0
        assert len(cache.timestamps) == 0


class TestCacheKeyGenerator:
    """Test cases for cache_key_generator function"""
    
    def test_basic_key_generation(self):
        """Test basic cache key generation"""
        key = cache_key_generator("users", user_id=123)
        assert key.startswith("users:")
        assert "user_id=123" in key
    
    def test_key_generation_with_multiple_params(self):
        """Test key generation with multiple parameters"""
        key = cache_key_generator("data", user=123, category="test", active=True)
        
        assert key.startswith("data:")
        assert "user=123" in key
        assert "category=test" in key
        assert "active=True" in key
    
    def test_key_generation_deterministic(self):
        """Test that key generation is deterministic"""
        key1 = cache_key_generator("test", a=1, b=2, c=3)
        key2 = cache_key_generator("test", c=3, b=2, a=1)  # Different order
        
        assert key1 == key2
    
    def test_key_generation_with_complex_values(self):
        """Test key generation with complex values"""
        key = cache_key_generator("complex", 
                                data={"nested": "value"}, 
                                list_param=[1, 2, 3])
        
        assert key.startswith("complex:")
        assert "data=" in key
        assert "list_param=" in key


class TestUnifiedCacheManager:
    """Test cases for UnifiedCacheManager class"""
    
    @pytest.fixture
    def cache_manager(self):
        """Create a cache manager with memory-only configuration"""
        config = CacheConfig(redis_enabled=False, memory_enabled=True)
        return UnifiedCacheManager(config)
    
    def test_cache_manager_initialization(self):
        """Test cache manager initialization"""
        config = CacheConfig()
        manager = UnifiedCacheManager(config)
        
        assert manager.config == config
        assert isinstance(manager.stats, CacheStats)
        assert manager.memory_cache is not None
    
    @patch('redis.Redis')
    def test_cache_manager_with_redis(self, mock_redis):
        """Test cache manager with Redis enabled"""
        mock_redis_instance = Mock()
        mock_redis.return_value = mock_redis_instance
        
        config = CacheConfig(redis_enabled=True)
        manager = UnifiedCacheManager(config)
        
        assert manager.redis_client is not None
        mock_redis.assert_called_once()
    
    def test_cache_set_get_memory_only(self, cache_manager):
        """Test cache set/get with memory cache only"""
        cache_manager.set("test_key", "test_value", ttl=60)
        result = cache_manager.get("test_key")
        
        assert result == "test_value"
        assert cache_manager.stats.hits == 1
        assert cache_manager.stats.total_requests == 1
    
    def test_cache_get_miss(self, cache_manager):
        """Test cache miss"""
        result = cache_manager.get("nonexistent_key")
        
        assert result is None
        assert cache_manager.stats.misses == 1
        assert cache_manager.stats.total_requests == 1
    
    def test_cache_delete(self, cache_manager):
        """Test cache deletion"""
        cache_manager.set("test_key", "test_value", ttl=60)
        assert cache_manager.get("test_key") == "test_value"
        
        cache_manager.delete("test_key")
        assert cache_manager.get("test_key") is None
    
    def test_cache_exists(self, cache_manager):
        """Test cache key existence"""
        assert not cache_manager.exists("test_key")
        
        cache_manager.set("test_key", "test_value", ttl=60)
        assert cache_manager.exists("test_key")
    
    def test_cache_clear(self, cache_manager):
        """Test cache clearing"""
        cache_manager.set("key1", "value1", ttl=60)
        cache_manager.set("key2", "value2", ttl=60)
        
        cache_manager.clear()
        
        assert cache_manager.get("key1") is None
        assert cache_manager.get("key2") is None
    
    def test_cache_with_default_ttl(self, cache_manager):
        """Test cache with default TTL"""
        cache_manager.set("test_key", "test_value")  # No TTL specified
        result = cache_manager.get("test_key")
        
        assert result == "test_value"
    
    def test_cache_json_serialization(self, cache_manager):
        """Test caching complex objects"""
        test_data = {
            "users": [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}],
            "metadata": {"count": 2, "active": True}
        }
        
        cache_manager.set("complex_data", test_data, ttl=60)
        result = cache_manager.get("complex_data")
        
        assert result == test_data
    
    @patch('redis.Redis')
    def test_cache_redis_fallback_to_memory(self, mock_redis):
        """Test fallback to memory cache when Redis fails"""
        mock_redis_instance = Mock()
        mock_redis_instance.set.side_effect = Exception("Redis connection failed")
        mock_redis_instance.get.side_effect = Exception("Redis connection failed")
        mock_redis.return_value = mock_redis_instance
        
        config = CacheConfig(redis_enabled=True, memory_enabled=True)
        manager = UnifiedCacheManager(config)
        
        # Should fallback to memory cache
        manager.set("test_key", "test_value", ttl=60)
        result = manager.get("test_key")
        
        assert result == "test_value"
    
    def test_cache_stats_tracking(self, cache_manager):
        """Test cache statistics tracking"""
        # Generate some cache activity
        cache_manager.set("key1", "value1", ttl=60)
        cache_manager.get("key1")  # Hit
        cache_manager.get("key2")  # Miss
        cache_manager.get("key1")  # Hit
        
        stats = cache_manager.get_stats()
        
        assert stats['hits'] == 2
        assert stats['misses'] == 1
        assert stats['total_requests'] == 3
        assert stats['hit_rate'] == 2/3
    
    def test_cache_stats_reset(self, cache_manager):
        """Test cache statistics reset"""
        cache_manager.set("key1", "value1", ttl=60)
        cache_manager.get("key1")  # Hit
        cache_manager.get("key2")  # Miss
        
        cache_manager.reset_stats()
        
        stats = cache_manager.get_stats()
        assert stats['hits'] == 0
        assert stats['misses'] == 0
        assert stats['total_requests'] == 0
        assert stats['hit_rate'] == 0.0
    
    def test_cache_health_check(self, cache_manager):
        """Test cache health check"""
        health = cache_manager.health_check()
        
        assert 'memory_cache' in health
        assert health['memory_cache']['status'] == 'healthy'
        
        if cache_manager.config.redis_enabled:
            assert 'redis_cache' in health
    
    @patch('redis.Redis')
    def test_cache_redis_health_check_failure(self, mock_redis):
        """Test Redis health check failure"""
        mock_redis_instance = Mock()
        mock_redis_instance.ping.side_effect = Exception("Connection failed")
        mock_redis.return_value = mock_redis_instance
        
        config = CacheConfig(redis_enabled=True)
        manager = UnifiedCacheManager(config)
        
        health = cache_manager.health_check()
        
        if 'redis_cache' in health:
            assert health['redis_cache']['status'] == 'unhealthy'


@pytest.mark.integration
class TestUnifiedCacheManagerIntegration:
    """Integration tests for UnifiedCacheManager"""
    
    def test_cache_manager_end_to_end(self):
        """Test complete cache workflow"""
        config = CacheConfig(redis_enabled=False, memory_enabled=True, max_memory_items=10)
        manager = UnifiedCacheManager(config)
        
        # Test various data types
        test_data = [
            ("string_key", "string_value"),
            ("int_key", 42),
            ("list_key", [1, 2, 3, 4, 5]),
            ("dict_key", {"nested": {"data": "test"}}),
            ("bool_key", True),
            ("float_key", 3.14159)
        ]
        
        # Set all data
        for key, value in test_data:
            manager.set(key, value, ttl=60)
        
        # Verify all data
        for key, expected_value in test_data:
            actual_value = manager.get(key)
            assert actual_value == expected_value
        
        # Test cache operations
        assert manager.exists("string_key")
        assert not manager.exists("nonexistent_key")
        
        manager.delete("string_key")
        assert not manager.exists("string_key")
        assert manager.get("string_key") is None
        
        # Check stats
        stats = manager.get_stats()
        assert stats['hits'] > 0
        assert stats['total_requests'] > 0
    
    def test_cache_expiration_workflow(self):
        """Test cache expiration in realistic scenario"""
        config = CacheConfig(redis_enabled=False, memory_enabled=True)
        manager = UnifiedCacheManager(config)
        
        with patch('time.time') as mock_time:
            # Set initial time
            mock_time.return_value = 1000
            
            # Cache item with 60 second TTL
            manager.set("expiring_key", "expiring_value", ttl=60)
            
            # Item should exist within TTL
            mock_time.return_value = 1030
            assert manager.get("expiring_key") == "expiring_value"
            
            # Item should be expired after TTL
            mock_time.return_value = 1070
            assert manager.get("expiring_key") is None
    
    def test_cache_performance_under_load(self):
        """Test cache performance with many operations"""
        config = CacheConfig(redis_enabled=False, memory_enabled=True, max_memory_items=1000)
        manager = UnifiedCacheManager(config)
        
        # Simulate load
        for i in range(100):
            key = f"load_test_key_{i}"
            value = f"load_test_value_{i}"
            manager.set(key, value, ttl=60)
        
        # Verify all items
        for i in range(100):
            key = f"load_test_key_{i}"
            expected_value = f"load_test_value_{i}"
            assert manager.get(key) == expected_value
        
        # Check final stats
        stats = manager.get_stats()
        assert stats['total_requests'] >= 100
        assert stats['hit_rate'] > 0