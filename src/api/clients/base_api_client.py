#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base API Client Module
Provides a common base class for all API clients with shared functionality
"""

import os
import sys
import json
import time
import threading
import requests
from requests.exceptions import RequestException
from typing import Dict, Any, Optional, Tuple, List, Callable
from abc import ABC, abstractmethod

from src.utils.unified_logger import get_logger
from src.core.connection_pool import connection_pool_manager

# 오프라인 모드 감지 - 클래스 속성으로 이동
class BaseApiClient(ABC):
    """
    Base API Client that provides common functionality for all API clients
    """
    
    # Class attribute for offline mode detection
    OFFLINE_MODE = (
        os.getenv('OFFLINE_MODE', 'false').lower() == 'true' or
        os.getenv('NO_INTERNET', 'false').lower() == 'true' or
        os.getenv('DISABLE_EXTERNAL_CALLS', 'false').lower() == 'true'
    )
    
    def __init__(self, host=None, api_token=None, username=None, password=None, 
                 port=None, use_https=True, verify_ssl=None, logger_name=None,
                 env_prefix=None):
        """
        Initialize the base API client with common parameters
        
        Args:
            host (str, optional): API host address (IP or domain)
            api_token (str, optional): API token for authorization (priority)
            username (str, optional): Username for basic auth (fallback)
            password (str, optional): Password for basic auth (fallback)
            port (int, optional): Port number for the API endpoint
            use_https (bool, optional): Use HTTPS protocol (default: True)
            verify_ssl (bool, optional): Verify SSL certificates (default: from env or False)
            logger_name (str, optional): Logger name (default: derived from class name)
            env_prefix (str, optional): Prefix for environment variables (e.g., 'FORTIGATE')
        """
        # Load configuration from environment if prefix is provided
        if env_prefix:
            env_config = self._get_env_config(env_prefix)
            host = host or env_config.get('host')
            api_token = api_token or env_config.get('api_token')
            username = username or env_config.get('username')
            password = password or env_config.get('password')
            port = port or env_config.get('port')
            if verify_ssl is None:
                verify_ssl = env_config.get('verify_ssl')
        
        # Common client properties
        self.host = host
        self.api_token = api_token
        self.username = username
        self.password = password
        self.port = port
        self.session_id = None
        
        # Set auth method based on provided credentials
        self.auth_method = 'token' if self.api_token else 'credentials'
        
        # SSL verification (from environment or default to False)
        if verify_ssl is None:
            self.verify_ssl = os.environ.get('VERIFY_SSL', 'false').lower() == 'true'
        else:
            self.verify_ssl = verify_ssl
            
        # Timeout settings
        self.timeout = int(os.environ.get('API_TIMEOUT', '30'))
        
        # Set up logger name attribute for session initialization
        self.logger_name = logger_name or self.__class__.__name__.lower()
        
        # Set up logger
        try:
            self.logger = get_logger(self.logger_name, 'advanced')
        except Exception:
            # Fallback to basic logging if advanced logger fails
            import logging
            self.logger = logging.getLogger(self.logger_name)
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
                self.logger.setLevel(logging.INFO)
        
        # Set up protocol and base URL
        self.protocol = "https" if use_https else "http"
        if self.port:
            self.base_url = f"{self.protocol}://{self.host}:{self.port}"
        else:
            self.base_url = f"{self.protocol}://{self.host}"
        
        # Initialize session
        self._init_session()
        
        # Set default headers
        self._setup_headers()
    
    def _init_session(self):
        """Initialize requests session using connection pool manager"""
        # Use connection pool manager for better performance
        session_id = f"{self.logger_name or self.__class__.__name__}_{self.host}"
        self.session = connection_pool_manager.get_session(
            identifier=session_id,
            pool_connections=20,
            pool_maxsize=50,
            max_retries=3
        )
        self.session.verify = self.verify_ssl
        
        # Disable SSL warnings if not verifying
        if not self.verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def _get_env_config(self, prefix: str) -> Dict[str, Any]:
        """
        Load configuration from environment variables with prefix
        
        Args:
            prefix: Environment variable prefix (e.g., 'FORTIGATE', 'FORTIMANAGER')
            
        Returns:
            dict: Configuration loaded from environment
        """
        return {
            'host': os.environ.get(f'{prefix}_HOST'),
            'api_token': os.environ.get(f'{prefix}_API_TOKEN'),
            'username': os.environ.get(f'{prefix}_USERNAME'),
            'password': os.environ.get(f'{prefix}_PASSWORD'),
            'port': os.environ.get(f'{prefix}_PORT'),
            'verify_ssl': os.environ.get(f'{prefix}_VERIFY_SSL', 'false').lower() == 'true'
        }
    
    def _setup_headers(self):
        """Setup default headers based on authentication method"""
        if self.api_token:
            self.headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
        else:
            self.headers = {
                'Content-Type': 'application/json'
            }
    
    def _make_request(self, method, url, data=None, params=None, headers=None, timeout=None):
        """
        Make an HTTP request with error handling and logging
        
        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE)
            url (str): URL for the request
            data (dict, optional): Request data/payload
            params (dict, optional): URL parameters
            headers (dict, optional): Custom headers to override defaults
            timeout (int, optional): Request timeout in seconds
            
        Returns:
            tuple: (success, response_data, status_code)
        """
        # 오프라인 모드에서는 외부 연결 차단 (동적 체크)
        offline_mode = (
            os.getenv('OFFLINE_MODE', 'false').lower() == 'true' or
            os.getenv('NO_INTERNET', 'false').lower() == 'true' or
            os.getenv('DISABLE_EXTERNAL_CALLS', 'false').lower() == 'true' or
            self.OFFLINE_MODE
        )
        if offline_mode:
            self.logger.warning("🔒 외부 API 호출이 오프라인 모드에 의해 차단됨")
            return False, {"error": "Offline mode - external connections disabled"}, 503
        
        # Use default timeout if not specified
        if timeout is None:
            timeout = self.timeout
            
        # Use default headers if not specified
        if headers is None:
            headers = self.headers
        
        # Log the request (sanitizing sensitive information)
        sanitized_data = self._sanitize_data(data) if data else None
        sanitized_headers = self._sanitize_headers(headers) if headers else None
        self.logger.debug(f"API Request: {method} {url}")
        if sanitized_data:
            self.logger.debug(f"Request Data: {sanitized_data}")
        if sanitized_headers:
            self.logger.debug(f"Request Headers: {sanitized_headers}")
        
        try:
            # Make the request using session
            response = self.session.request(
                method=method,
                url=url,
                json=data if data else None,
                params=params,
                headers=headers,
                timeout=timeout
            )
            
            # Log the response
            if response.ok:
                self.logger.debug(f"API Response: {response.status_code} OK")
            else:
                self.logger.warning(f"API Response: {response.status_code} {response.reason}")
            
            # Return success flag, response data, and status code
            if response.ok:
                return True, self._parse_response(response), response.status_code
            else:
                return False, response.text, response.status_code
                
        except RequestException as e:
            # Log and handle request exceptions
            self.logger.error(f"Request error: {str(e)}")
            return False, str(e), 0
    
    def _parse_response(self, response):
        """
        Parse the response based on content type
        
        Args:
            response: Response object
            
        Returns:
            dict or str: Parsed response data
        """
        content_type = response.headers.get('Content-Type', '')
        
        if 'application/json' in content_type:
            try:
                return response.json()
            except ValueError:
                return response.text
        else:
            return response.text
    
    def _sanitize_data(self, data):
        """
        Sanitize sensitive information in request data
        
        Args:
            data (dict): Request data
            
        Returns:
            dict: Sanitized data with sensitive fields masked
        """
        if not data or not isinstance(data, dict):
            return data
            
        sanitized = data.copy()
        sensitive_keys = ['password', 'passwd', 'secret', 'key', 'token']
        
        def _sanitize_dict(d):
            if not isinstance(d, dict):
                return d
                
            result = {}
            for key, value in d.items():
                if isinstance(value, dict):
                    result[key] = _sanitize_dict(value)
                elif isinstance(value, list):
                    result[key] = [_sanitize_dict(item) if isinstance(item, dict) else item for item in value]
                elif any(sk in key.lower() for sk in sensitive_keys):
                    result[key] = '********'
                else:
                    result[key] = value
            return result
            
        return _sanitize_dict(sanitized)
    
    def _sanitize_headers(self, headers):
        """
        Sanitize sensitive information in headers
        
        Args:
            headers (dict): Request headers
            
        Returns:
            dict: Sanitized headers with sensitive fields masked
        """
        if not headers:
            return {}
        
        sanitized = headers.copy()
        sensitive_keys = ['Authorization', 'api-key', 'token', 'password', 'secret']
        
        for key in sanitized:
            for sensitive_key in sensitive_keys:
                if sensitive_key.lower() in key.lower():
                    sanitized[key] = '********'
        
        return sanitized
    
    def test_connection(self):
        """
        Test API connection with automatic fallback from token to credentials
        
        Returns:
            tuple: (success, message)
        """
        # Check if we're in offline mode
        if self.OFFLINE_MODE:
            self.logger.warning("🔒 Test connection blocked in offline mode")
            return False, "Offline mode - external connections disabled"
        
        # Try token authentication first if available
        if self.auth_method == 'token':
            self.logger.info(f"Testing {self.__class__.__name__} API connection with token")
            
            # Get the test endpoint for this client type
            test_endpoint = getattr(self, 'test_endpoint', '/monitor/system/status')
            test_url = f"{self.base_url}/{test_endpoint.lstrip('/')}"
            
            success, result, status_code = self._make_request(
                'GET',
                test_url,
                None,
                None,
                self.headers
            )
            
            if success:
                self.logger.info(f"{self.__class__.__name__} API token authentication successful")
                return True, result
            else:
                self.logger.warning(f"{self.__class__.__name__} API token authentication failed: {status_code} - {result}")
                
                # Fall back to credential authentication if available
                if self.username and self.password:
                    return self._test_with_credentials()
                else:
                    return False, f"Token authentication failed and no credentials available"
        else:
            # Direct credential authentication
            return self._test_with_credentials()
    
    def _test_with_credentials(self):
        """
        Test connection using credentials (to be overridden by subclasses if needed)
        
        Returns:
            tuple: (success, message)
        """
        # This is a basic implementation that can be overridden by subclasses
        if hasattr(self, 'login'):
            return self.login()
        else:
            # Fallback: try basic auth
            self.logger.info(f"Testing {self.__class__.__name__} API connection with credentials")
            
            # Set up basic auth headers
            import base64
            credentials = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
            headers = self.headers.copy()
            headers['Authorization'] = f'Basic {credentials}'
            
            # Get the test endpoint
            test_endpoint = getattr(self, 'test_endpoint', '/monitor/system/status')
            test_url = f"{self.base_url}/{test_endpoint.lstrip('/')}"
            
            success, result, status_code = self._make_request(
                'GET',
                test_url,
                None,
                None,
                headers
            )
            
            if success:
                self.logger.info(f"{self.__class__.__name__} credential authentication successful")
                return True, "Credential authentication successful"
            else:
                self.logger.error(f"{self.__class__.__name__} credential authentication failed: {status_code}")
                return False, f"Credential authentication failed: {result}"


class RealtimeMonitoringMixin:
    """Mixin for real-time monitoring functionality"""
    
    def __init__(self):
        """Initialize monitoring attributes"""
        self.monitoring_active = False
        self.monitoring_thread = None
        self.monitoring_callbacks = []
        
        # Connection status tracking
        self.is_connected = False
        self.last_heartbeat = None
        self.connection_error_count = 0
        self.max_connection_errors = 5
        
        # Initialize logger if not already present
        if not hasattr(self, 'logger'):
            self.logger = get_logger(self.__class__.__name__)
    
    def start_realtime_monitoring(self, callback: Callable, interval: int = 5):
        """
        Start real-time monitoring
        
        Args:
            callback: Function to call with monitoring data
            interval: Monitoring interval in seconds
        """
        if self.monitoring_active:
            self.logger.warning("Real-time monitoring is already active")
            return
        
        self.monitoring_callbacks.append(callback)
        self.monitoring_active = True
        self.connection_error_count = 0
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitoring_thread.start()
        self.logger.info(f"Real-time monitoring started with {interval}s interval")
    
    def stop_realtime_monitoring(self):
        """Stop real-time monitoring"""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        self.monitoring_callbacks.clear()
        
        # Wait for thread to finish
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        self.logger.info("Real-time monitoring stopped")
    
    def _monitoring_loop(self, interval: int):
        """
        Main monitoring loop
        
        Args:
            interval: Monitoring interval in seconds
        """
        while self.monitoring_active:
            try:
                # Get monitoring data (to be implemented by the class using this mixin)
                data = self._get_monitoring_data()
                
                if data:
                    # Update connection status
                    self.is_connected = True
                    self.last_heartbeat = time.time()
                    self.connection_error_count = 0
                    
                    # Call all registered callbacks
                    for callback in self.monitoring_callbacks:
                        try:
                            callback(data)
                        except Exception as e:
                            self.logger.error(f"Error in monitoring callback: {e}")
                else:
                    # Handle connection error
                    self.connection_error_count += 1
                    if self.connection_error_count >= self.max_connection_errors:
                        self.is_connected = False
                        self.logger.error("Max connection errors reached, marking as disconnected")
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                self.connection_error_count += 1
            
            # Sleep for the interval
            time.sleep(interval)
    
    def _get_monitoring_data(self) -> Optional[Dict[str, Any]]:
        """
        Get monitoring data (to be implemented by the class using this mixin)
        
        Returns:
            dict: Monitoring data or None if error
        """
        raise NotImplementedError("Classes using RealtimeMonitoringMixin must implement _get_monitoring_data")




# API Error Classes
class APIError(Exception):
    """Base API exception"""
    pass


class AuthenticationError(APIError):
    """Authentication specific errors"""
    pass


class ConnectionError(APIError):
    """Connection specific errors"""
    pass


class ConfigurationError(APIError):
    """Configuration specific errors"""
    pass