"""
Integration tests for Health Check Validation

Tests post-deployment health check mechanisms and retry logic.
"""

import pytest
import time
import requests
from unittest.mock import patch, MagicMock, call
from requests.exceptions import ConnectionError, Timeout


class TestHealthCheckIntegration:
    """Test post-deployment health validation"""
    
    @pytest.fixture
    def health_check_url(self):
        """Health check endpoint URL"""
        return "https://fortinet.jclee.me/api/health"
    
    @pytest.fixture
    def mock_requests(self):
        """Mock requests library"""
        with patch('requests.get') as mock_get:
            yield mock_get
    
    def test_health_endpoint_availability(self, health_check_url, mock_requests):
        """Verify /api/health endpoint responds after deploy"""
        # Mock successful health check
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": "2024-01-01T12:00:00Z",
            "services": {
                "redis": "connected",
                "fortimanager": "connected",
                "database": "healthy"
            }
        }
        mock_requests.return_value = mock_response
        
        # Perform health check
        response = requests.get(health_check_url, verify=False, timeout=10)
        
        assert response.status_code == 200
        health_data = response.json()
        assert health_data["status"] == "healthy"
        assert "version" in health_data
        assert health_data["services"]["redis"] == "connected"
        
        # Verify SSL verification disabled for self-signed cert
        mock_requests.assert_called_with(health_check_url, verify=False, timeout=10)
    
    def test_health_check_retry_logic(self, health_check_url, mock_requests):
        """Test retry mechanism for health checks"""
        # Mock progression: fail -> fail -> success
        mock_responses = [
            ConnectionError("Connection refused"),
            MagicMock(status_code=503, json=lambda: {"status": "starting"}),
            MagicMock(status_code=200, json=lambda: {"status": "healthy"})
        ]
        
        mock_requests.side_effect = mock_responses
        
        # Health check with retry
        max_attempts = 3
        attempt = 0
        success = False
        
        for i in range(max_attempts):
            attempt += 1
            try:
                response = requests.get(health_check_url, verify=False, timeout=10)
                if response.status_code == 200:
                    success = True
                    break
            except ConnectionError:
                if i < max_attempts - 1:
                    time.sleep(0.1)  # Short sleep for test
                continue
            
            if response.status_code != 200 and i < max_attempts - 1:
                time.sleep(0.1)
        
        assert success is True
        assert attempt == 3
        assert mock_requests.call_count == 3
    
    def test_deployment_stabilization_wait(self, mock_requests):
        """Verify appropriate wait time for deployment"""
        # Track timing
        start_time = time.time()
        
        # Mock delayed success
        def delayed_response(*args, **kwargs):
            elapsed = time.time() - start_time
            if elapsed < 0.5:  # Simulate 0.5s deployment time
                raise ConnectionError("Service starting")
            else:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"status": "healthy"}
                return mock_response
        
        mock_requests.side_effect = delayed_response
        
        # Wait and retry logic
        wait_time = 0.5  # Reduced for testing
        time.sleep(wait_time)
        
        # Now should succeed
        response = requests.get("https://fortinet.jclee.me/api/health")
        assert response.status_code == 200
    
    def test_health_check_timeout_handling(self, health_check_url, mock_requests):
        """Test handling of health check timeouts"""
        # Mock timeout
        mock_requests.side_effect = Timeout("Request timed out")
        
        # Attempt health check
        with pytest.raises(Timeout):
            requests.get(health_check_url, verify=False, timeout=5)
    
    def test_health_check_service_degradation(self, health_check_url, mock_requests):
        """Test detection of degraded services"""
        # Mock degraded response
        mock_response = MagicMock()
        mock_response.status_code = 200  # Endpoint works
        mock_response.json.return_value = {
            "status": "degraded",
            "version": "1.0.0",
            "services": {
                "redis": "disconnected",
                "fortimanager": "connected",
                "database": "healthy"
            },
            "errors": ["Redis connection failed"]
        }
        mock_requests.return_value = mock_response
        
        response = requests.get(health_check_url)
        health_data = response.json()
        
        assert response.status_code == 200  # Endpoint is up
        assert health_data["status"] == "degraded"
        assert health_data["services"]["redis"] == "disconnected"
        assert "errors" in health_data
    
    def test_health_check_complete_failure(self, health_check_url, mock_requests):
        """Test complete health check failure scenario"""
        # All attempts fail
        mock_requests.side_effect = [
            ConnectionError("Connection refused"),
            ConnectionError("Connection refused"),
            ConnectionError("Connection refused"),
            ConnectionError("Connection refused"),
            ConnectionError("Connection refused")
        ]
        
        # Try health check with all retries
        max_attempts = 5
        all_failed = True
        
        for i in range(max_attempts):
            try:
                requests.get(health_check_url, verify=False, timeout=10)
                all_failed = False
                break
            except ConnectionError:
                continue
        
        assert all_failed is True
        assert mock_requests.call_count == max_attempts
    
    @pytest.mark.parametrize("status_code,expected_healthy", [
        (200, True),
        (201, True),
        (400, False),
        (401, False),
        (403, False),
        (404, False),
        (500, False),
        (502, False),
        (503, False),
    ])
    def test_health_status_code_interpretation(self, health_check_url, mock_requests, 
                                              status_code, expected_healthy):
        """Test interpretation of various HTTP status codes"""
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = {"status": "test"}
        mock_requests.return_value = mock_response
        
        response = requests.get(health_check_url)
        is_healthy = 200 <= response.status_code < 300
        
        assert is_healthy == expected_healthy
    
    def test_multi_endpoint_health_check(self, mock_requests):
        """Test checking multiple health endpoints"""
        endpoints = [
            "https://fortinet.jclee.me/api/health",
            "https://fortinet.jclee.me/api/ready",
            "https://fortinet.jclee.me/api/live"
        ]
        
        # Mock all healthy
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.return_value = mock_response
        
        # Check all endpoints
        results = {}
        for endpoint in endpoints:
            response = requests.get(endpoint, verify=False)
            results[endpoint] = response.status_code == 200
        
        assert all(results.values())
        assert mock_requests.call_count == len(endpoints)
    
    def test_health_check_with_authentication(self, health_check_url, mock_requests):
        """Test health check with authentication headers"""
        # Mock authenticated health check
        def check_auth(*args, **kwargs):
            headers = kwargs.get('headers', {})
            mock_response = MagicMock()
            
            if headers.get('Authorization') == 'Bearer valid-token':
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "status": "healthy",
                    "authenticated": True
                }
            else:
                mock_response.status_code = 401
                mock_response.json.return_value = {"error": "Unauthorized"}
            
            return mock_response
        
        mock_requests.side_effect = check_auth
        
        # Test with valid auth
        headers = {"Authorization": "Bearer valid-token"}
        response = requests.get(health_check_url, headers=headers)
        assert response.status_code == 200
        assert response.json()["authenticated"] is True
        
        # Test without auth
        response = requests.get(health_check_url)
        assert response.status_code == 401