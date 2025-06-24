#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FortiManager API Client
Provides communication with FortiManager devices using JSON-RPC API
"""

import os
import json
import time
import threading
from typing import Dict, Any, Optional, List, Tuple
from requests.exceptions import RequestException
from .base_api_client import BaseApiClient, RealtimeMonitoringMixin
from src.utils.api_common import (
    JsonRpcMixin, ConnectionTestMixin, MonitoringMixin, 
    ErrorHandlingMixin, RequestRetryMixin, CacheMixin, sanitize_sensitive_data
)

class FortiManagerAPIClient(BaseApiClient, RealtimeMonitoringMixin, JsonRpcMixin, 
                            ConnectionTestMixin, MonitoringMixin, ErrorHandlingMixin, 
                            RequestRetryMixin, CacheMixin):
    """
    FortiManager API Client for central management of FortiGate devices
    Inherits common functionality from BaseApiClient and uses common mixins
    """
    
    def __init__(self, host=None, api_token=None, username=None, password=None, port=443, verify_ssl=False):
        """
        Initialize the FortiManager API client
        
        Args:
            host (str, optional): FortiManager host address (IP or domain)
            api_token (str, optional): API token for access (used as priority)
            username (str, optional): Username (used if token is not available)
            password (str, optional): Password (used if token is not available)
            port (int, optional): FortiManager API port (default: 443)
            verify_ssl (bool, optional): Verify SSL certificates (default: False)
        """
        # Initialize base class with environment prefix
        super().__init__(
            host=host,
            api_token=api_token,
            username=username,
            password=password,
            port=port,
            verify_ssl=verify_ssl,
            logger_name='fortimanager_api',
            env_prefix='FORTIMANAGER'
        )
        
        # Initialize all mixins
        RealtimeMonitoringMixin.__init__(self)
        JsonRpcMixin.__init__(self)
        ConnectionTestMixin.__init__(self)
        MonitoringMixin.__init__(self)
        ErrorHandlingMixin.__init__(self)
        RequestRetryMixin.__init__(self)
        CacheMixin.__init__(self)
        
        # FortiManager specific setup
        self.protocol = 'https' if self.port in [443, 3791] else 'http'
        self.base_url = f"{self.protocol}://{self.host}:{self.port}/jsonrpc"
        
        # Define test endpoint for FortiManager (not used since it's JSON-RPC)
        self.test_endpoint = "/sys/status"
    
    def login(self):
        """
        Login to FortiManager API with username/password
        
        Returns:
            bool: Success or failure
        """
        # Skip login if using API token
        if self.api_token:
            self.logger.info("Using API token authentication")
            return self.test_token_auth()
        
        # Require credentials if no token
        if not self.username or not self.password:
            self.logger.error("API token or user credentials are required")
            return False
        
        # Prepare login payload using common mixin
        payload = self.build_json_rpc_request(
            method="exec",
            url="/sys/login/user",
            data={
                "user": self.username,
                "passwd": self.password
            }
        )
        
        # Make login request
        success, result, status_code = self._make_request(
            'POST',
            self.base_url,
            payload,
            None,
            self.headers
        )
        
        if success:
            # Parse response using common mixin
            parsed_success, parsed_data = self.parse_json_rpc_response(result)
            if parsed_success:
                self.session_id = result.get('session')
                self.auth_method = 'session'
                self.logger.info("FortiManager API login successful")
                return True
            else:
                self.logger.error(f"FortiManager API login failed: {parsed_data}")
                return False
        else:
            self.logger.error(f"FortiManager API login failed: {status_code} - {result}")
            return False
    
    def test_token_auth(self):
        """
        Test API token authentication
        
        Returns:
            bool: Success or failure
        """
        if not self.api_token:
            return False
        
        # Simple request to test token using common mixin
        payload = self.build_json_rpc_request(
            method="get",
            url="/sys/status"
        )
        
        # Add token to headers
        headers = self.headers.copy()
        headers['Authorization'] = f'Bearer {self.api_token}'
        
        success, result, status_code = self._make_request(
            'POST',
            self.base_url,
            payload,
            None,
            headers
        )
        
        if success:
            parsed_success, _ = self.parse_json_rpc_response(result)
            return parsed_success
        else:
            return False
    
    # Override test_connection for FortiManager-specific JSON-RPC flow
    def test_connection(self):
        """
        Test connection to FortiManager API using JSON-RPC
        
        Returns:
            tuple: (success, message)
        """
        # Use the common connection test mixin
        return self.perform_token_auth_test(self.test_endpoint)
    
    # Override _test_with_credentials for FortiManager-specific authentication
    def _test_with_credentials(self):
        """
        Test connection using credentials with FortiManager-specific login flow
        
        Returns:
            tuple: (success, result, status_code)
        """
        if self.login():
            return True, "Credential authentication successful", 200
        else:
            return False, "Authentication failed", 401
    
    def _make_api_request(self, method: str, url: str, data: Optional[Dict] = None, verbose: int = 0) -> Tuple[bool, Any]:
        """
        Make FortiManager API request with automatic authentication retry
        
        Args:
            method: JSON-RPC method (get, set, exec, etc.)
            url: API endpoint URL
            data: Optional request data
            verbose: Verbose level
            
        Returns:
            tuple: (success, result)
        """
        # Build payload using common mixin
        payload = self.build_json_rpc_request(
            method=method,
            url=url,
            data=data,
            session=self.session_id if self.auth_method == 'session' else None,
            verbose=verbose
        )
        
        # Add token to headers if using token auth
        headers = self.headers.copy()
        if self.auth_method == 'token' and self.api_token:
            headers['Authorization'] = f'Bearer {self.api_token}'
        
        # Make request
        success, result, status_code = self._make_request(
            'POST',
            self.base_url,
            payload,
            None,
            headers
        )
        
        if success:
            parsed_success, parsed_data = self.parse_json_rpc_response(result)
            if parsed_success:
                return True, parsed_data
            else:
                # Check if authentication error
                if "No permission" in str(parsed_data) or "Invalid session" in str(parsed_data):
                    self.logger.warning("Authentication error, attempting to re-login")
                    if self.login():
                        # Retry request with new session
                        payload = self.build_json_rpc_request(
                            method=method,
                            url=url,
                            data=data,
                            session=self.session_id,
                            verbose=verbose
                        )
                        retry_success, retry_result, _ = self._make_request(
                            'POST',
                            self.base_url,
                            payload,
                            None,
                            self.headers
                        )
                        if retry_success:
                            parsed_success, parsed_data = self.parse_json_rpc_response(retry_result)
                            return parsed_success, parsed_data
                
                return False, parsed_data
        else:
            return False, result
    
    # Device management methods
    def get_adom_list(self):
        """
        Get list of ADOMs (Administrative Domains)
        
        Returns:
            list: ADOMs or empty list on failure
        """
        success, result = self._make_api_request(
            method="get",
            url="/dvmdb/adom"
        )
        
        if success:
            return result if isinstance(result, list) else []
        else:
            self.logger.error(f"Failed to get ADOM list: {result}")
            return []
    
    def get_devices(self, adom="root"):
        """
        Get managed devices (alias for get_managed_devices)
        
        Args:
            adom (str): ADOM name (default: root)
            
        Returns:
            list: Managed devices or empty list on failure
        """
        return self.get_managed_devices(adom)
    
    def get_managed_devices(self, adom="root"):
        """
        Get managed devices in an ADOM
        
        Args:
            adom (str): ADOM name (default: root)
            
        Returns:
            list: Managed devices or empty list on failure
        """
        success, result = self._make_api_request(
            method="get",
            url=f"/dvmdb/adom/{adom}/device"
        )
        
        if success:
            return result if isinstance(result, list) else []
        else:
            self.logger.error(f"Failed to get managed devices: {result}")
            return []
    
    def get_device_status(self, device_name, adom="root"):
        """
        Get device status information
        
        Args:
            device_name (str): Device name
            adom (str): ADOM name (default: root)
            
        Returns:
            dict: Device status or None on failure
        """
        success, result = self._make_api_request(
            method="get",
            url=f"/dvmdb/adom/{adom}/device/{device_name}"
        )
        
        if success:
            return result
        else:
            self.logger.error(f"Failed to get device status: {result}")
            return None
    
    def get_firewall_policies(self, device_name, vdom="root", adom="root"):
        """
        Get firewall policies for a device
        
        Args:
            device_name (str): Device name
            vdom (str): VDOM name (default: root)
            adom (str): ADOM name (default: root)
            
        Returns:
            list: Firewall policies or empty list on failure
        """
        success, result = self._make_api_request(
            method="get",
            url=f"/pm/config/adom/{adom}/pkg/default/{device_name}/firewall/policy"
        )
        
        if success:
            return result if isinstance(result, list) else []
        else:
            self.logger.error(f"Failed to get firewall policies: {result}")
            return []
    
    def get_device_interfaces(self, device_name, vdom="root", adom="root"):
        """
        Get device interfaces (alias for get_interfaces)
        
        Args:
            device_name (str): Device name
            vdom (str): VDOM name (default: root)
            adom (str): ADOM name (default: root)
            
        Returns:
            list: Interfaces or empty list on failure
        """
        return self.get_interfaces(device_name, vdom, adom)
    
    def get_interfaces(self, device_name, vdom="root", adom="root"):
        """
        Get device interfaces
        
        Args:
            device_name (str): Device name
            vdom (str): VDOM name (default: root)
            adom (str): ADOM name (default: root)
            
        Returns:
            list: Interfaces or empty list on failure
        """
        success, result = self._make_api_request(
            method="get",
            url=f"/pm/config/device/{device_name}/global/system/interface"
        )
        
        if success:
            return result if isinstance(result, list) else []
        else:
            self.logger.error(f"Failed to get interfaces: {result}")
            return []
    
    def get_routes(self, device_name, vdom="root", adom="root"):
        """
        Get routing table for a device
        
        Args:
            device_name (str): Device name
            vdom (str): VDOM name (default: root)
            adom (str): ADOM name (default: root)
            
        Returns:
            list: Routes or empty list on failure
        """
        success, result = self._make_api_request(
            method="get",
            url=f"/pm/config/device/{device_name}/vdom/{vdom}/router/static"
        )
        
        if success:
            return result if isinstance(result, list) else []
        else:
            self.logger.error(f"Failed to get routes: {result}")
            return []
    
    def get_system_status(self):
        """
        Get FortiManager system status
        
        Returns:
            dict: System status or None on failure
        """
        success, result = self._make_api_request(
            method="get",
            url="/sys/status"
        )
        
        if success:
            return result
        else:
            self.logger.error(f"Failed to get system status: {result}")
            return None
    
    def get_task_status(self, task_id):
        """
        Get task status
        
        Args:
            task_id (int): Task ID
            
        Returns:
            dict: Task status or None on failure
        """
        success, result = self._make_api_request(
            method="get",
            url=f"/task/task/{task_id}"
        )
        
        if success:
            return result
        else:
            self.logger.error(f"Failed to get task status: {result}")
            return None
    
    def install_policy_package(self, package_name, device_name, adom="root"):
        """
        Install policy package to device
        
        Args:
            package_name (str): Policy package name
            device_name (str): Device name
            adom (str): ADOM name (default: root)
            
        Returns:
            dict: Task info or None on failure
        """
        success, result = self._make_api_request(
            method="exec",
            url=f"/securityconsole/install/package",
            data={
                "adom": adom,
                "pkg": package_name,
                "scope": [
                    {
                        "name": device_name,
                        "vdom": "root"
                    }
                ]
            }
        )
        
        if success:
            return result
        else:
            self.logger.error(f"Failed to install policy package: {result}")
            return None
    
    def get_security_events(self, limit=100, adom="root"):
        """
        Get security events from FortiManager
        
        Args:
            limit (int): Maximum number of events to retrieve
            adom (str): ADOM name
            
        Returns:
            list: Security events or empty list on failure
        """
        try:
            success, result = self._make_api_request(
                method="get",
                url=f"/logview/adom/{adom}/logsearch",
                data={
                    "time_range": {
                        "start": int(time.time() - 86400),  # Last 24 hours
                        "end": int(time.time())
                    },
                    "filter": "",
                    "limit": limit
                }
            )
            
            if success and result:
                return result.get('data', [])
            else:
                self.logger.warning(f"No security events found or failed to retrieve")
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting security events: {e}")
            return []
    
    def get_threat_statistics(self, adom="root"):
        """
        Get threat statistics from FortiManager
        
        Args:
            adom (str): ADOM name
            
        Returns:
            dict: Threat statistics or empty dict on failure
        """
        try:
            success, result = self._make_api_request(
                method="get",
                url=f"/report/adom/{adom}/chart/generic",
                data={
                    "time_range": {
                        "start": int(time.time() - 86400),  # Last 24 hours
                        "end": int(time.time())
                    },
                    "chart_type": "threat_summary"
                }
            )
            
            if success and result:
                # Transform data to expected format
                stats = result.get('data', {})
                return {
                    'today': stats.get('threats_today', 0),
                    'week': stats.get('threats_week', 0),
                    'month': stats.get('threats_month', 0),
                    'by_type': stats.get('threat_types', {}),
                    'blocked_percentage': stats.get('blocked_percent', 95),
                    'quarantined_percentage': stats.get('quarantined_percent', 3)
                }
            else:
                self.logger.warning(f"No threat statistics found")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error getting threat statistics: {e}")
            return {}
    
    
    def get_device_performance(self, device_name, adom="root"):
        """
        Get device performance metrics
        
        Args:
            device_name (str): Device name
            adom (str): ADOM name
            
        Returns:
            dict: Performance metrics or None on failure
        """
        try:
            success, result = self._make_api_request(
                method="get",
                url=f"/monitor/adom/{adom}/device/{device_name}/system/performance"
            )
            
            if success and result:
                perf_data = result.get('data', {})
                return {
                    'cpu_usage': perf_data.get('cpu', 0),
                    'memory_usage': perf_data.get('memory', 0),
                    'session_count': perf_data.get('sessions', 0),
                    'bandwidth_in': perf_data.get('bandwidth_rx', 0),
                    'bandwidth_out': perf_data.get('bandwidth_tx', 0)
                }
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting device performance for {device_name}: {e}")
            return None
    
    def get_policies(self, device_name=None, adom="root", package="default"):
        """
        Get firewall policies
        
        Args:
            device_name (str, optional): Device name (if None, get package policies)
            adom (str): ADOM name
            package (str): Policy package name
            
        Returns:
            list: Policies or empty list on failure
        """
        try:
            if device_name:
                url = f"/pm/config/device/{device_name}/vdom/root/firewall/policy"
            else:
                url = f"/pm/config/adom/{adom}/pkg/{package}/firewall/policy"
            
            success, result = self._make_api_request(
                method="get",
                url=url
            )
            
            if success and result:
                return result.get('data', [])
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting policies: {e}")
            return []
    
    # Monitoring mixin implementation
    def _get_monitoring_data(self) -> Optional[Dict[str, Any]]:
        """
        Get monitoring data for real-time monitoring
        
        Returns:
            dict: Monitoring data or None if error
        """
        try:
            monitoring_data = {
                'timestamp': time.time(),
                'system_status': self.get_system_status(),
                'adoms': len(self.get_adom_list()),
                'managed_devices': []
            }
            
            # Get device summary for each ADOM
            for adom in self.get_adom_list():
                adom_name = adom.get('name', 'unknown')
                devices = self.get_managed_devices(adom_name)
                monitoring_data['managed_devices'].extend([{
                    'name': dev.get('name'),
                    'adom': adom_name,
                    'status': dev.get('conn_status'),
                    'ip': dev.get('ip')
                } for dev in devices])
            
            return monitoring_data
            
        except Exception as e:
            self.logger.error(f"Error getting monitoring data: {e}")
            return None
    
    # Policy management methods
    def create_firewall_policy(self, device_name, policy_data, vdom="root", adom="root"):
        """
        Create a new firewall policy
        
        Args:
            device_name (str): Device name
            policy_data (dict): Policy configuration
            vdom (str): VDOM name (default: root)
            adom (str): ADOM name (default: root)
            
        Returns:
            dict: Result or None on failure
        """
        success, result = self._make_api_request(
            method="add",
            url=f"/pm/config/adom/{adom}/pkg/default/{device_name}/firewall/policy",
            data=policy_data
        )
        
        if success:
            return result
        else:
            self.logger.error(f"Failed to create firewall policy: {result}")
            return None
    
    def update_firewall_policy(self, device_name, policy_id, policy_data, vdom="root", adom="root"):
        """
        Update an existing firewall policy
        
        Args:
            device_name (str): Device name
            policy_id (int): Policy ID
            policy_data (dict): Policy configuration
            vdom (str): VDOM name (default: root)
            adom (str): ADOM name (default: root)
            
        Returns:
            dict: Result or None on failure
        """
        success, result = self._make_api_request(
            method="set",
            url=f"/pm/config/adom/{adom}/pkg/default/{device_name}/firewall/policy/{policy_id}",
            data=policy_data
        )
        
        if success:
            return result
        else:
            self.logger.error(f"Failed to update firewall policy: {result}")
            return None
    
    def delete_firewall_policy(self, device_name, policy_id, vdom="root", adom="root"):
        """
        Delete a firewall policy
        
        Args:
            device_name (str): Device name
            policy_id (int): Policy ID
            vdom (str): VDOM name (default: root)
            adom (str): ADOM name (default: root)
            
        Returns:
            dict: Result or None on failure
        """
        success, result = self._make_api_request(
            method="delete",
            url=f"/pm/config/adom/{adom}/pkg/default/{device_name}/firewall/policy/{policy_id}"
        )
        
        if success:
            return result
        else:
            self.logger.error(f"Failed to delete firewall policy: {result}")
            return None
    
    # Object management methods
    def get_address_objects(self, adom="root"):
        """
        Get address objects
        
        Args:
            adom (str): ADOM name (default: root)
            
        Returns:
            list: Address objects or empty list on failure
        """
        success, result = self._make_api_request(
            method="get",
            url=f"/pm/config/adom/{adom}/obj/firewall/address"
        )
        
        if success:
            return result if isinstance(result, list) else []
        else:
            self.logger.error(f"Failed to get address objects: {result}")
            return []
    
    def get_service_objects(self, adom="root"):
        """
        Get service objects
        
        Args:
            adom (str): ADOM name (default: root)
            
        Returns:
            list: Service objects or empty list on failure
        """
        success, result = self._make_api_request(
            method="get",
            url=f"/pm/config/adom/{adom}/obj/firewall/service/custom"
        )
        
        if success:
            return result if isinstance(result, list) else []
        else:
            self.logger.error(f"Failed to get service objects: {result}")
            return []
    
    def logout(self):
        """
        Logout from FortiManager API
        
        Returns:
            bool: Success or failure
        """
        if self.auth_method == 'token':
            # No logout needed for token auth
            return True
        
        if not self.session_id:
            # Already logged out
            return True
        
        payload = self.build_json_rpc_request(
            method="exec",
            url="/sys/logout",
            session=self.session_id
        )
        
        success, result, _ = self._make_request(
            'POST',
            self.base_url,
            payload,
            None,
            self.headers
        )
        
        if success:
            self.session_id = None
            self.logger.info("FortiManager API logout successful")
            return True
        else:
            self.logger.warning("FortiManager API logout failed, but clearing session")
            self.session_id = None
            return True