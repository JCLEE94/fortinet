#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FortiGate API Client
Provides communication with FortiGate devices using REST API
"""

import os
import time
import json
import threading
from typing import Dict, Any, Optional, List
from requests.exceptions import RequestException
from .base_api_client import BaseApiClient, RealtimeMonitoringMixin
from src.utils.api_utils import (
    ConnectionTestMixin
)

class FortiGateAPIClient(BaseApiClient, RealtimeMonitoringMixin, ConnectionTestMixin):
    """
    FortiGate API Client for communicating with FortiGate devices
    Inherits common functionality from BaseApiClient and includes real-time monitoring
    """
    
    # Class-level configuration
    ENV_PREFIX = 'FORTIGATE'
    DEFAULT_PORT = 443
    
    def __init__(self, host=None, api_token=None, username=None, password=None, 
                 port=None, use_https=True, verify_ssl=False):
        """
        Initialize the FortiGate API client
        
        Args:
            host (str, optional): FortiGate host address (IP or domain)
            api_token (str, optional): API token for access (used as priority)
            username (str, optional): Username (used if token is not available)
            password (str, optional): Password (used if token is not available)
            port (int, optional): Port number (default: 443)
            use_https (bool, optional): Use HTTPS protocol (default: True)
            verify_ssl (bool, optional): Verify SSL certificates (default: False)
        """
        # Initialize base class with environment prefix
        super().__init__(
            host=host,
            api_token=api_token,
            username=username,
            password=password,
            port=port,
            use_https=use_https,
            verify_ssl=verify_ssl,
            logger_name='fortigate_api',
            env_prefix='FORTIGATE'
        )
        
        # Initialize all mixins
        RealtimeMonitoringMixin.__init__(self)
        ConnectionTestMixin.__init__(self)
        
        # FortiGate specific setup
        from src.config.services import API_VERSIONS
        
        self.base_url = f"{self.protocol}://{self.host}"
        if self.port and self.port != (443 if use_https else 80):
            self.base_url += f":{self.port}"
        self.base_url += API_VERSIONS['fortigate']
        
        # Define test endpoint for FortiGate
        self.test_endpoint = "/cmdb/system/status"
        
        # Initialize active captures storage
        self.active_captures = {}
        
        # Cache storage
        self._cache = {}
        
        # Monitoring data
        self._monitoring_data = {}
    
    def get_cached_data(self, key):
        """Get cached data by key"""
        return self._cache.get(key)
    
    def set_cached_data(self, key, data, ttl=300):
        """Set cached data with TTL (simplified implementation)"""
        self._cache[key] = data
    
    def make_request_with_retry(self, method, url, headers=None, retries=3):
        """Make request with retry logic"""
        for attempt in range(retries):
            try:
                return self._make_request(method, url, None, None, headers or self.headers)
            except Exception as e:
                if attempt == retries - 1:
                    return False, str(e), 500
                time.sleep(1 * (attempt + 1))  # Exponential backoff
        return False, "Max retries exceeded", 500
    
    def handle_api_error(self, error, context=""):
        """Handle API errors"""
        self.logger.error(f"API Error in {context}: {error}")
    
    def update_monitoring_data(self, data):
        """Update monitoring data"""
        self._monitoring_data.update(data)
    
    def sanitize_sensitive_data(self, data):
        """Sanitize sensitive data (simplified implementation)"""
        return data
        
    # Override _test_with_credentials for FortiGate-specific authentication
    def _test_with_credentials(self):
        """
        Test connection using credentials with FortiGate-specific login flow
        
        Returns:
            tuple: (success, result, status_code)
        """
        return self.perform_credential_auth_test("/authentication")
    
    def get_firewall_policies(self):
        """
        Get all firewall policies
        
        Returns:
            list: Firewall policies or empty list on failure
        """
        cache_key = "firewall_policies"
        cached_data = self.get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            success, result, status_code = self.make_request_with_retry(
                'GET',
                f"{self.base_url}/cmdb/firewall/policy",
                headers=self.headers
            )
            
            if success:
                policies = result.get('results', [])
                self.set_cached_data(cache_key, policies, ttl=60)  # 1분 캐시
                return policies
            else:
                self.handle_api_error(Exception(f"HTTP {status_code}: {result}"), "get_firewall_policies")
                return []
                
        except Exception as e:
            self.handle_api_error(e, "get_firewall_policies")
            return []
    
    def get_routes(self):
        """
        Get routing table
        
        Returns:
            list: Routing table or empty list on failure
        """
        cache_key = "routes"
        cached_data = self.get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            success, result, status_code = self.make_request_with_retry(
                'GET',
                f"{self.base_url}/cmdb/router/static",
                headers=self.headers
            )
            
            if success:
                routes = result.get('results', [])
                self.set_cached_data(cache_key, routes, ttl=120)  # 2분 캐시
                return routes
            else:
                self.handle_api_error(Exception(f"HTTP {status_code}: {result}"), "get_routes")
                return []
                
        except Exception as e:
            self.handle_api_error(e, "get_routes")
            return []
    
    def get_interfaces(self):
        """
        Get network interfaces
        
        Returns:
            list: Network interfaces or empty list on failure
        """
        success, result, status_code = self._make_request(
            'GET',
            f"{self.base_url}/cmdb/system/interface",
            None,
            None,
            self.headers
        )
        
        if success:
            return result.get('results', [])
        else:
            self.logger.error(f"Failed to get interfaces: {status_code} - {result}")
            return []
    
    def get_services(self):
        """
        Get available services
        
        Returns:
            list: Services or empty list on failure
        """
        success, result, status_code = self._make_request(
            'GET',
            f"{self.base_url}/cmdb/firewall/service",
            None,
            None,
            self.headers
        )
        
        if success:
            return result.get('results', [])
        else:
            self.logger.error(f"Failed to get services: {status_code} - {result}")
            return []
    
    def get_address_objects(self):
        """
        Get address objects
        
        Returns:
            list: Address objects or empty list on failure
        """
        success, result, status_code = self._make_request(
            'GET',
            f"{self.base_url}/cmdb/firewall/address",
            None,
            None,
            self.headers
        )
        
        if success:
            return result.get('results', [])
        else:
            self.logger.error(f"Failed to get address objects: {status_code} - {result}")
            return []
    
    def get_service_groups(self):
        """
        Get service groups
        
        Returns:
            list: Service groups or empty list on failure
        """
        success, result, status_code = self._make_request(
            'GET',
            f"{self.base_url}/cmdb/firewall/service/group",
            None,
            None,
            self.headers
        )
        
        if success:
            return result.get('results', [])
        else:
            self.logger.error(f"Failed to get service groups: {status_code} - {result}")
            return []
    
    def get_address_groups(self):
        """
        Get address groups
        
        Returns:
            list: Address groups or empty list on failure
        """
        success, result, status_code = self._make_request(
            'GET',
            f"{self.base_url}/cmdb/firewall/addrgrp",
            None,
            None,
            self.headers
        )
        
        if success:
            return result.get('results', [])
        else:
            self.logger.error(f"Failed to get address groups: {status_code} - {result}")
            return []
    
    def get_system_status(self):
        """
        Get system status and hardware information
        
        Returns:
            dict: System status or None on failure
        """
        success, result, status_code = self._make_request(
            'GET',
            f"{self.base_url}/monitor/system/status",
            None,
            None,
            self.headers
        )
        
        if success:
            return result.get('results', {})
        else:
            self.logger.error(f"Failed to get system status: {status_code} - {result}")
            return None
    
    def get_system_performance(self):
        """
        Get system performance metrics (CPU, memory, sessions)
        
        Returns:
            dict: Performance metrics or None on failure
        """
        success, result, status_code = self._make_request(
            'GET',
            f"{self.base_url}/monitor/system/performance",
            None,
            None,
            self.headers
        )
        
        if success:
            return result.get('results', {})
        else:
            self.logger.error(f"Failed to get system performance: {status_code} - {result}")
            return None
    
    def get_interface_stats(self):
        """
        Get interface statistics
        
        Returns:
            list: Interface statistics or empty list on failure
        """
        success, result, status_code = self._make_request(
            'GET',
            f"{self.base_url}/monitor/system/interface",
            None,
            None,
            self.headers
        )
        
        if success:
            return result.get('results', [])
        else:
            self.logger.error(f"Failed to get interface stats: {status_code} - {result}")
            return []
    
    def get_sessions(self):
        """
        Get active sessions
        
        Returns:
            list: Active sessions or empty list on failure
        """
        success, result, status_code = self._make_request(
            'GET',
            f"{self.base_url}/monitor/firewall/session",
            None,
            None,
            self.headers
        )
        
        if success:
            return result.get('results', [])
        else:
            self.logger.error(f"Failed to get sessions: {status_code} - {result}")
            return []
    
    def get_cpu_usage(self):
        """
        Get CPU usage information
        
        Returns:
            dict: CPU usage or None on failure
        """
        success, result, status_code = self._make_request(
            'GET',
            f"{self.base_url}/monitor/system/resource/usage",
            None,
            {'resource': 'cpu'},
            self.headers
        )
        
        if success:
            return result.get('results', {})
        else:
            self.logger.error(f"Failed to get CPU usage: {status_code} - {result}")
            return None
    
    def get_memory_usage(self):
        """
        Get memory usage information
        
        Returns:
            dict: Memory usage or None on failure
        """
        success, result, status_code = self._make_request(
            'GET',
            f"{self.base_url}/monitor/system/resource/usage",
            None,
            {'resource': 'memory'},
            self.headers
        )
        
        if success:
            return result.get('results', {})
        else:
            self.logger.error(f"Failed to get memory usage: {status_code} - {result}")
            return None
    
    # Monitoring mixin implementation
    def _get_monitoring_data(self) -> Optional[Dict[str, Any]]:
        """
        Get monitoring data for real-time monitoring
        
        Returns:
            dict: Monitoring data or None if error
        """
        try:
            base_data = self.collect_base_monitoring_data()
            
            # FortiGate 특화 모니터링 데이터 추가
            fortigate_data = {
                'cpu_usage': self.get_cpu_usage(),
                'memory_usage': self.get_memory_usage(),
                'interface_stats': self.get_interface_stats(),
                'active_sessions': len(self.get_sessions())
            }
            
            # 시스템 상태 추가
            system_status = self.get_system_status()
            if system_status:
                fortigate_data['system_status'] = {
                    'hostname': system_status.get('hostname'),
                    'version': system_status.get('version'),
                    'build': system_status.get('build'),
                    'serial': system_status.get('serial')
                }
            
            # 민감한 정보 마스킹
            sanitized_data = self.sanitize_sensitive_data(fortigate_data)
            
            # 모니터링 데이터 업데이트
            self.update_monitoring_data(sanitized_data)
            
            return base_data
            
        except Exception as e:
            self.handle_api_error(e, "_get_monitoring_data")
            return None
    
    # Packet capture methods
    def start_packet_capture(self, interface, filter_str="", max_packets=1000):
        """
        Start packet capture on specified interface
        
        Args:
            interface (str): Interface name
            filter_str (str, optional): BPF filter string
            max_packets (int, optional): Maximum packets to capture
            
        Returns:
            dict: Capture info or None on failure
        """
        capture_data = {
            "interface": interface,
            "filter": filter_str,
            "max_packets": max_packets
        }
        
        success, result, status_code = self._make_request(
            'POST',
            f"{self.base_url}/monitor/system/packet-capture/start",
            capture_data,
            None,
            self.headers
        )
        
        if success:
            capture_id = result.get('results', {}).get('capture_id')
            if capture_id:
                self.active_captures[capture_id] = {
                    'interface': interface,
                    'filter': filter_str,
                    'start_time': time.time(),
                    'max_packets': max_packets
                }
                return {
                    'capture_id': capture_id,
                    'status': 'started'
                }
        
        self.logger.error(f"Failed to start packet capture: {status_code} - {result}")
        return None
    
    def stop_packet_capture(self, capture_id):
        """
        Stop packet capture
        
        Args:
            capture_id (str): Capture ID
            
        Returns:
            dict: Result or None on failure
        """
        success, result, status_code = self._make_request(
            'POST',
            f"{self.base_url}/monitor/system/packet-capture/stop",
            {"capture_id": capture_id},
            None,
            self.headers
        )
        
        if success:
            if capture_id in self.active_captures:
                del self.active_captures[capture_id]
            return result.get('results', {})
        else:
            self.logger.error(f"Failed to stop packet capture: {status_code} - {result}")
            return None
    
    def get_packet_capture_status(self, capture_id):
        """
        Get packet capture status
        
        Args:
            capture_id (str): Capture ID
            
        Returns:
            dict: Status or None on failure
        """
        success, result, status_code = self._make_request(
            'GET',
            f"{self.base_url}/monitor/system/packet-capture/status",
            None,
            {"capture_id": capture_id},
            self.headers
        )
        
        if success:
            return result.get('results', {})
        else:
            self.logger.error(f"Failed to get packet capture status: {status_code} - {result}")
            return None
    
    def download_packet_capture(self, capture_id):
        """
        Download packet capture file
        
        Args:
            capture_id (str): Capture ID
            
        Returns:
            bytes: Capture file data or None on failure
        """
        success, result, status_code = self._make_request(
            'GET',
            f"{self.base_url}/monitor/system/packet-capture/download",
            None,
            {"capture_id": capture_id},
            self.headers
        )
        
        if success:
            # Return raw data for pcap file
            return result
        else:
            self.logger.error(f"Failed to download packet capture: {status_code} - {result}")
            return None