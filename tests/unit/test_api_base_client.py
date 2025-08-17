#!/usr/bin/env python3
"""
Unit tests for Base API Client
Tests for api/clients/base_api_client.py
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
import sys
import os
from requests.exceptions import ConnectionError, Timeout, RequestException

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from api.clients.base_api_client import (
    BaseAPIClient,
    RealtimeMonitoringMixin,
    APIConnectionPool,
    SessionManager
)


class TestBaseAPIClient:
    """Test cases for BaseAPIClient class"""
    
    def test_initialization_minimal(self):
        """Test BaseAPIClient initialization with minimal parameters"""
        client = BaseAPIClient()
        
        assert client.session is not None
        assert isinstance(client.session, requests.Session)
        assert client.base_url is None
        assert client.api_key is None
        assert client.timeout == 30
        assert client.retry_attempts == 3
        assert not client.verify_ssl
        assert client.offline_mode is False
    
    def test_initialization_with_parameters(self):
        """Test BaseAPIClient initialization with custom parameters"""
        client = BaseAPIClient(
            base_url="https://api.example.com",
            api_key="test_key_123",
            timeout=60,
            retry_attempts=5,
            verify_ssl=True
        )
        
        assert client.base_url == "https://api.example.com"
        assert client.api_key == "test_key_123"
        assert client.timeout == 60
        assert client.retry_attempts == 5
        assert client.verify_ssl is True
    
    @patch.dict(os.environ, {
        'OFFLINE_MODE': 'true',
        'NO_INTERNET': 'true',
        'DISABLE_EXTERNAL_CALLS': 'true'
    })
    def test_offline_mode_detection(self):
        """Test offline mode detection from environment variables"""
        client = BaseAPIClient()
        assert client.offline_mode is True
    
    def test_headers_setup(self):
        """Test default headers setup"""
        client = BaseAPIClient(api_key="test_key")
        
        expected_headers = {
            'User-Agent': 'FortiGate-Analyzer/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test_key'
        }
        
        for key, value in expected_headers.items():
            assert client.session.headers.get(key) == value
    
    def test_headers_no_api_key(self):
        """Test headers when no API key is provided"""
        client = BaseAPIClient()
        
        assert 'Authorization' not in client.session.headers
        assert client.session.headers.get('User-Agent') == 'FortiGate-Analyzer/1.0'
    
    @patch('requests.Session.request')
    def test_make_request_success(self, mock_request):
        """Test successful API request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response
        
        client = BaseAPIClient(base_url="https://api.example.com")
        
        result = client._make_request("GET", "/test")
        
        assert result["result"] == "success"
        mock_request.assert_called_once_with(
            "GET",
            "https://api.example.com/test",
            timeout=30,
            verify=False,
            json=None,
            params=None
        )
    
    @patch('requests.Session.request')
    def test_make_request_with_data(self, mock_request):
        """Test API request with data"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 123}
        mock_request.return_value = mock_response
        
        client = BaseAPIClient(base_url="https://api.example.com")
        
        data = {"name": "test", "value": 42}
        result = client._make_request("POST", "/create", data=data)
        
        assert result["id"] == 123
        mock_request.assert_called_once_with(
            "POST",
            "https://api.example.com/create",
            timeout=30,
            verify=False,
            json=data,
            params=None
        )
    
    @patch('requests.Session.request')
    def test_make_request_with_params(self, mock_request):
        """Test API request with query parameters"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_request.return_value = mock_response
        
        client = BaseAPIClient(base_url="https://api.example.com")
        
        params = {"page": 1, "limit": 10}
        result = client._make_request("GET", "/list", params=params)
        
        assert "data" in result
        mock_request.assert_called_once_with(
            "GET",
            "https://api.example.com/list",
            timeout=30,
            verify=False,
            json=None,
            params=params
        )
    
    def test_make_request_offline_mode(self):
        """Test request in offline mode"""
        with patch.dict(os.environ, {'OFFLINE_MODE': 'true'}):
            client = BaseAPIClient(base_url="https://api.example.com")
            
            result = client._make_request("GET", "/test")
            
            assert result["status"] == "offline_mode"
            assert result["message"] == "Request blocked - offline mode enabled"
    
    @patch('requests.Session.request')
    def test_make_request_http_error(self, mock_request):
        """Test API request with HTTP error"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Not found"}
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Error")
        mock_request.return_value = mock_response
        
        client = BaseAPIClient(base_url="https://api.example.com")
        
        with pytest.raises(requests.HTTPError):
            client._make_request("GET", "/nonexistent")
    
    @patch('requests.Session.request')
    def test_make_request_connection_error(self, mock_request):
        """Test API request with connection error"""
        mock_request.side_effect = ConnectionError("Connection failed")
        
        client = BaseAPIClient(base_url="https://api.example.com")
        
        with pytest.raises(ConnectionError):
            client._make_request("GET", "/test")
    
    @patch('requests.Session.request')
    def test_make_request_timeout(self, mock_request):
        """Test API request timeout"""
        mock_request.side_effect = Timeout("Request timed out")
        
        client = BaseAPIClient(base_url="https://api.example.com")
        
        with pytest.raises(Timeout):
            client._make_request("GET", "/test")
    
    @patch('requests.Session.request')
    def test_make_request_retry_mechanism(self, mock_request):
        """Test request retry mechanism"""
        # First two calls fail, third succeeds
        mock_request.side_effect = [
            ConnectionError("Connection failed"),
            ConnectionError("Connection failed"),
            Mock(status_code=200, json=lambda: {"result": "success"})
        ]
        
        client = BaseAPIClient(base_url="https://api.example.com", retry_attempts=3)
        
        with patch('time.sleep'):  # Speed up test
            result = client._make_request("GET", "/test")
            
        assert result["result"] == "success"
        assert mock_request.call_count == 3
    
    @patch('requests.Session.request')
    def test_make_request_max_retries_exceeded(self, mock_request):
        """Test when max retries are exceeded"""
        mock_request.side_effect = ConnectionError("Connection failed")
        
        client = BaseAPIClient(base_url="https://api.example.com", retry_attempts=2)
        
        with patch('time.sleep'):  # Speed up test
            with pytest.raises(ConnectionError):
                client._make_request("GET", "/test")
        
        assert mock_request.call_count == 3  # Initial + 2 retries
    
    def test_get_method(self):
        """Test GET convenience method"""
        client = BaseAPIClient()
        
        with patch.object(client, '_make_request') as mock_make_request:
            mock_make_request.return_value = {"data": "test"}
            
            result = client.get("/test", params={"key": "value"})
            
            assert result["data"] == "test"
            mock_make_request.assert_called_once_with("GET", "/test", params={"key": "value"})
    
    def test_post_method(self):
        """Test POST convenience method"""
        client = BaseAPIClient()
        
        with patch.object(client, '_make_request') as mock_make_request:
            mock_make_request.return_value = {"id": 123}
            
            data = {"name": "test"}
            result = client.post("/create", data=data)
            
            assert result["id"] == 123
            mock_make_request.assert_called_once_with("POST", "/create", data=data)
    
    def test_put_method(self):
        """Test PUT convenience method"""
        client = BaseAPIClient()
        
        with patch.object(client, '_make_request') as mock_make_request:
            mock_make_request.return_value = {"updated": True}
            
            data = {"name": "updated"}
            result = client.put("/update/123", data=data)
            
            assert result["updated"] is True
            mock_make_request.assert_called_once_with("PUT", "/update/123", data=data)
    
    def test_delete_method(self):
        """Test DELETE convenience method"""
        client = BaseAPIClient()
        
        with patch.object(client, '_make_request') as mock_make_request:
            mock_make_request.return_value = {"deleted": True}
            
            result = client.delete("/delete/123")
            
            assert result["deleted"] is True
            mock_make_request.assert_called_once_with("DELETE", "/delete/123")
    
    def test_connection_test_success(self):
        """Test successful connection test"""
        client = BaseAPIClient()
        
        with patch.object(client, 'get') as mock_get:
            mock_get.return_value = {"status": "ok"}
            
            result = client.test_connection()
            
            assert result is True
    
    def test_connection_test_failure(self):
        """Test failed connection test"""
        client = BaseAPIClient()
        
        with patch.object(client, 'get') as mock_get:
            mock_get.side_effect = ConnectionError("Connection failed")
            
            result = client.test_connection()
            
            assert result is False
    
    def test_health_check(self):
        """Test health check endpoint"""
        client = BaseAPIClient()
        
        with patch.object(client, 'get') as mock_get:
            mock_get.return_value = {"status": "healthy", "timestamp": "2024-01-01T12:00:00Z"}
            
            result = client.health_check()
            
            assert result["status"] == "healthy"
            mock_get.assert_called_once_with("/health")
    
    def test_close_session(self):
        """Test session closing"""
        client = BaseAPIClient()
        
        with patch.object(client.session, 'close') as mock_close:
            client.close()
            mock_close.assert_called_once()
    
    def test_context_manager(self):
        """Test using client as context manager"""
        with patch('api.clients.base_api_client.BaseAPIClient.close') as mock_close:
            with BaseAPIClient() as client:
                assert isinstance(client, BaseAPIClient)
            
            mock_close.assert_called_once()


class TestRealtimeMonitoringMixin:
    """Test cases for RealtimeMonitoringMixin"""
    
    def test_mixin_initialization(self):
        """Test mixin initialization"""
        
        class TestClient(BaseAPIClient, RealtimeMonitoringMixin):
            pass
        
        client = TestClient()
        
        assert not client.monitoring_active
        assert client.monitoring_interval == 30
        assert client.monitoring_callbacks == []
        assert client.monitoring_thread is None
    
    def test_start_monitoring(self):
        """Test starting monitoring"""
        
        class TestClient(BaseAPIClient, RealtimeMonitoringMixin):
            pass
        
        client = TestClient()
        
        with patch('threading.Thread') as mock_thread:
            mock_thread_instance = Mock()
            mock_thread.return_value = mock_thread_instance
            
            client.start_monitoring(interval=60)
            
            assert client.monitoring_active is True
            assert client.monitoring_interval == 60
            mock_thread.assert_called_once()
            mock_thread_instance.start.assert_called_once()
    
    def test_stop_monitoring(self):
        """Test stopping monitoring"""
        
        class TestClient(BaseAPIClient, RealtimeMonitoringMixin):
            pass
        
        client = TestClient()
        client.monitoring_active = True
        client.monitoring_thread = Mock()
        
        client.stop_monitoring()
        
        assert client.monitoring_active is False
    
    def test_add_monitoring_callback(self):
        """Test adding monitoring callback"""
        
        class TestClient(BaseAPIClient, RealtimeMonitoringMixin):
            pass
        
        client = TestClient()
        callback = Mock()
        
        client.add_monitoring_callback(callback)
        
        assert callback in client.monitoring_callbacks
    
    def test_remove_monitoring_callback(self):
        """Test removing monitoring callback"""
        
        class TestClient(BaseAPIClient, RealtimeMonitoringMixin):
            pass
        
        client = TestClient()
        callback = Mock()
        
        client.add_monitoring_callback(callback)
        client.remove_monitoring_callback(callback)
        
        assert callback not in client.monitoring_callbacks
    
    def test_monitoring_loop(self):
        """Test monitoring loop execution"""
        
        class TestClient(BaseAPIClient, RealtimeMonitoringMixin):
            def get_monitoring_data(self):
                return {"status": "active", "data": [1, 2, 3]}
        
        client = TestClient()
        callback = Mock()
        client.add_monitoring_callback(callback)
        
        # Run one iteration of the monitoring loop
        client.monitoring_active = True
        
        with patch('time.sleep') as mock_sleep:
            # Mock sleep to exit after one iteration
            mock_sleep.side_effect = lambda x: setattr(client, 'monitoring_active', False)
            
            client._monitoring_loop()
            
            callback.assert_called_once_with({"status": "active", "data": [1, 2, 3]})
    
    def test_monitoring_loop_exception_handling(self):
        """Test monitoring loop handles exceptions"""
        
        class TestClient(BaseAPIClient, RealtimeMonitoringMixin):
            def get_monitoring_data(self):
                raise Exception("Test error")
        
        client = TestClient()
        callback = Mock()
        client.add_monitoring_callback(callback)
        
        client.monitoring_active = True
        
        with patch('time.sleep') as mock_sleep, \
             patch('api.clients.base_api_client.logger') as mock_logger:
            
            # Mock sleep to exit after one iteration
            mock_sleep.side_effect = lambda x: setattr(client, 'monitoring_active', False)
            
            client._monitoring_loop()
            
            # Callback should not be called due to exception
            callback.assert_not_called()
            mock_logger.error.assert_called()


class TestSessionManager:
    """Test cases for SessionManager class"""
    
    def test_session_manager_initialization(self):
        """Test SessionManager initialization"""
        manager = SessionManager()
        
        assert isinstance(manager.session, requests.Session)
        assert manager.session.mount.call_count >= 1  # HTTPAdapter should be mounted
    
    def test_session_configuration(self):
        """Test session configuration with custom parameters"""
        manager = SessionManager(
            max_retries=5,
            backoff_factor=0.5,
            status_forcelist=[502, 503, 504]
        )
        
        assert isinstance(manager.session, requests.Session)
    
    def test_session_headers_setup(self):
        """Test session headers setup"""
        headers = {"Custom-Header": "test_value"}
        manager = SessionManager(headers=headers)
        
        assert manager.session.headers.get("Custom-Header") == "test_value"
    
    def test_get_session(self):
        """Test getting session instance"""
        manager = SessionManager()
        session = manager.get_session()
        
        assert session is manager.session
        assert isinstance(session, requests.Session)
    
    def test_close_session(self):
        """Test closing session"""
        manager = SessionManager()
        
        with patch.object(manager.session, 'close') as mock_close:
            manager.close()
            mock_close.assert_called_once()


class TestAPIConnectionPool:
    """Test cases for APIConnectionPool class"""
    
    def test_connection_pool_initialization(self):
        """Test APIConnectionPool initialization"""
        pool = APIConnectionPool(max_size=10)
        
        assert pool.max_size == 10
        assert len(pool.connections) == 0
        assert pool.current_size == 0
    
    def test_get_connection_new(self):
        """Test getting new connection"""
        pool = APIConnectionPool(max_size=5)
        
        connection = pool.get_connection("https://api.example.com")
        
        assert connection is not None
        assert isinstance(connection, requests.Session)
        assert pool.current_size == 1
    
    def test_get_connection_reuse(self):
        """Test reusing existing connection"""
        pool = APIConnectionPool(max_size=5)
        
        # Get connection twice for same URL
        connection1 = pool.get_connection("https://api.example.com")
        connection2 = pool.get_connection("https://api.example.com")
        
        assert connection1 is connection2
        assert pool.current_size == 1
    
    def test_get_connection_max_size_limit(self):
        """Test connection pool size limit"""
        pool = APIConnectionPool(max_size=2)
        
        # Create connections up to limit
        connection1 = pool.get_connection("https://api1.example.com")
        connection2 = pool.get_connection("https://api2.example.com")
        
        # Third connection should reuse oldest
        connection3 = pool.get_connection("https://api3.example.com")
        
        assert pool.current_size <= 2
        assert connection3 is not None
    
    def test_release_connection(self):
        """Test releasing connection"""
        pool = APIConnectionPool(max_size=5)
        
        connection = pool.get_connection("https://api.example.com")
        pool.release_connection("https://api.example.com")
        
        # Connection should still exist but be available for reuse
        assert "https://api.example.com" in pool.connections
    
    def test_clear_connections(self):
        """Test clearing all connections"""
        pool = APIConnectionPool(max_size=5)
        
        pool.get_connection("https://api1.example.com")
        pool.get_connection("https://api2.example.com")
        
        pool.clear()
        
        assert len(pool.connections) == 0
        assert pool.current_size == 0
    
    def test_connection_pool_thread_safety(self):
        """Test connection pool thread safety"""
        pool = APIConnectionPool(max_size=10)
        
        import threading
        results = []
        
        def get_connection_worker():
            connection = pool.get_connection("https://api.example.com")
            results.append(connection)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=get_connection_worker)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All threads should get the same connection
        assert len(set(id(conn) for conn in results)) == 1
    
    def test_connection_pool_health_check(self):
        """Test connection pool health check"""
        pool = APIConnectionPool(max_size=5)
        
        pool.get_connection("https://api1.example.com")
        pool.get_connection("https://api2.example.com")
        
        health = pool.health_check()
        
        assert health['active_connections'] == 2
        assert health['max_size'] == 5
        assert health['utilization'] == 0.4  # 2/5


@pytest.mark.integration
class TestBaseAPIClientIntegration:
    """Integration tests for BaseAPIClient"""
    
    def test_full_client_workflow(self):
        """Test complete client workflow"""
        client = BaseAPIClient(
            base_url="https://httpbin.org",
            timeout=10,
            retry_attempts=2
        )
        
        try:
            # Test connection
            connection_ok = client.test_connection()
            
            if connection_ok:
                # Test GET request
                response = client.get("/get", params={"test": "value"})
                assert "args" in response
                
                # Test POST request
                data = {"key": "value", "number": 42}
                response = client.post("/post", data=data)
                assert "json" in response
            
        except (ConnectionError, Timeout):
            # Skip if no internet connection
            pytest.skip("No internet connection available")
        
        finally:
            client.close()
    
    def test_client_with_monitoring(self):
        """Test client with monitoring capabilities"""
        
        class MonitoringClient(BaseAPIClient, RealtimeMonitoringMixin):
            def get_monitoring_data(self):
                return {"timestamp": "2024-01-01T12:00:00Z", "status": "active"}
        
        client = MonitoringClient()
        
        # Test monitoring setup
        callback_results = []
        
        def test_callback(data):
            callback_results.append(data)
        
        client.add_monitoring_callback(test_callback)
        
        # Start monitoring briefly
        client.start_monitoring(interval=0.1)
        
        import time
        time.sleep(0.2)  # Let it run briefly
        
        client.stop_monitoring()
        
        # Should have received at least one callback
        assert len(callback_results) > 0
        assert callback_results[0]["status"] == "active"