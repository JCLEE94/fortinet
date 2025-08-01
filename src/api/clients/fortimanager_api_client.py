#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FortiManager API Client
Provides communication with FortiManager devices using JSON-RPC API
"""

import os
import time
from typing import Any, Dict, Optional, Tuple

import requests

from utils.api_utils import ConnectionTestMixin
from utils.unified_logger import get_logger

from .base_api_client import BaseApiClient, RealtimeMonitoringMixin


class FortiManagerAPIClient(BaseApiClient, RealtimeMonitoringMixin, ConnectionTestMixin):
    """
    FortiManager API Client for central management of FortiGate devices
    Inherits common functionality from BaseApiClient and uses common mixins
    """

    def __init__(
        self,
        host=None,
        api_token=None,
        username=None,
        password=None,
        port=None,
        verify_ssl=False,
    ):
        """
        Initialize the FortiManager API client

        Args:
            host (str, optional): FortiManager host address (IP or domain)
            api_token (str, optional): API token for access (used as priority)
            username (str, optional): Username (used if token is not available)
            password (str, optional): Password (used if token is not available)
            port (int, optional): Port number (defaults to config value)
            verify_ssl (bool): Whether to verify SSL certificates
        """
        from config.services import FORTINET_PRODUCTS

        # Use default port from config if not specified
        if port is None:
            port = FORTINET_PRODUCTS["fortimanager"]["default_port"]

        super().__init__()
        self.logger = get_logger(__name__)
        self.host = host
        self.port = port
        self.api_token = api_token
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.session_id = None
        self.transaction_id = None
        self.request_id = 1  # JSON-RPC request ID counter
        self.adom = os.getenv("FORTIMANAGER_DEFAULT_ADOM", "root")  # Default administrative domain
        self.auth_headers = {}  # Store successful auth headers

        # Configuration for API endpoints
        self.protocol = "https" if verify_ssl else "https"
        self.base_url = f"{self.protocol}://{self.host}:{self.port}/jsonrpc"

        # Request session for connection pooling
        self.session = requests.Session()
        self.session.verify = self.verify_ssl
        if not self.verify_ssl:
            # Suppress SSL warnings when verification is disabled
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # API client extensions
        self._extensions = {}

    def build_json_rpc_request(self, method: str, url: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Build JSON-RPC request payload for FortiManager API

        Args:
            method (str): RPC method (exec, get, set, etc.)
            url (str): API URL path
            data (dict): Request data payload

        Returns:
            dict: JSON-RPC request payload
        """
        payload = {"id": int(time.time()), "method": method, "params": [{"url": url}]}

        # Add session if available
        if hasattr(self, "session_id") and self.session_id:
            payload["session"] = self.session_id

        # Add data payload if provided
        if data:
            payload["params"][0]["data"] = data

        return payload

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
            data={"user": self.username, "passwd": self.password},
        )

        # Make login request
        success, result, status_code = self._make_request("POST", self.base_url, payload, None, self.headers)

        if success:
            # Parse response using common mixin
            parsed_success, parsed_data = self.parse_json_rpc_response(result)
            if parsed_success:
                self.session_id = result.get("session")
                self.auth_method = "session"
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
        Test API token authentication with multiple methods

        Returns:
            bool: Success or failure
        """
        if not self.api_token:
            return False

        # Try multiple authentication methods
        auth_methods = [
            {"Authorization": f"Bearer {self.api_token}"},
            {"Authorization": f"Token {self.api_token}", "X-API-Key": self.api_token},
            {"X-API-Key": self.api_token},
            {"X-Auth-Token": self.api_token},
        ]

        payload = self.build_json_rpc_request(method="get", url="/sys/status")

        for i, auth_headers in enumerate(auth_methods):
            headers = self.headers.copy()
            headers.update(auth_headers)

            try:
                success, result, status_code = self._make_request("POST", self.base_url, payload, None, headers)

                if success and result:
                    parsed_success, parsed_data = self.parse_json_rpc_response(result)

                    # Check if we got actual data or just permission error
                    if parsed_success or (
                        isinstance(parsed_data, dict) and parsed_data.get("status", {}).get("code") != -11
                    ):
                        self.auth_method = "token"
                        self.auth_headers = auth_headers
                        self.logger.info(f"Token authentication successful with method {i+1}")
                        return True
                    elif parsed_data.get("status", {}).get("code") == -11:
                        self.logger.warning(
                            f"Token method {i+1}: No permission error. API user may need rpc-permit=read-write"
                        )
                        # 권한 문제 시 세션 인증으로 자동 전환 시도
                        if self.username and self.password:
                            self.logger.info("Attempting session authentication due to API permission error")
                            return False  # login() 메서드가 호출되도록 함
                        continue

            except Exception as e:
                self.logger.debug(f"Token auth method {i+1} failed: {e}")
                continue

        return False

    # Override test_connection for FortiManager-specific JSON-RPC flow
    def test_connection(self):
        """
        Test connection to FortiManager API using JSON-RPC

        Returns:
            tuple: (success, message)
        """
        try:
            # Try API token first if available
            if self.api_token and self.test_token_auth():
                return True, "API token authentication successful"

            # Try username/password login
            if self.username and self.password and self.login():
                return True, "Username/password authentication successful"

            return False, "Authentication failed - no valid credentials"

        except Exception as e:
            return False, f"Connection test failed: {str(e)}"

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

    def _make_api_request(
        self,
        method: str,
        url: str,
        data: Optional[Dict] = None,
        verbose: int = 0,
        timeout: Optional[int] = None,
    ) -> Tuple[bool, Any]:
        """
        Make FortiManager API request with automatic authentication retry

        Args:
            method: JSON-RPC method (get, set, exec, etc.)
            url: API endpoint URL
            data: Optional request data
            verbose: Verbose level
            timeout: Request timeout in seconds

        Returns:
            tuple: (success, result)
        """
        # Build payload using common mixin
        payload = self.build_json_rpc_request(
            method=method,
            url=url,
            data=data,
            session=self.session_id if self.auth_method == "session" else None,
            verbose=verbose,
        )

        # Add token to headers if using token auth
        headers = self.headers.copy()
        if self.auth_method == "token" and self.api_token and hasattr(self, "auth_headers"):
            headers.update(self.auth_headers)
        elif self.auth_method == "token" and self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"

        # Make request
        success, result, status_code = self._make_request(
            "POST", self.base_url, payload, None, headers, timeout=timeout
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
                            verbose=verbose,
                        )
                        retry_success, retry_result, _ = self._make_request(
                            "POST", self.base_url, payload, None, self.headers
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
        Get list of ADOMs (Administrative Domains) with caching

        Returns:
            list: ADOMs or empty list on failure
        """
        # Check if we have cached ADOM list
        cache_key = "adom_list"
        if hasattr(self, "_cache") and cache_key in self._cache:
            cache_time, cached_data = self._cache[cache_key]
            if time.time() - cache_time < 300:  # 5 minutes cache
                self.logger.debug("Returning cached ADOM list")
                return cached_data

        success, result = self._make_api_request(method="get", url="/dvmdb/adom", timeout=10)  # 10 second timeout

        if success:
            # Cache the result
            if not hasattr(self, "_cache"):
                self._cache = {}
            self._cache[cache_key] = (time.time(), result)
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
        success, result = self._make_api_request(method="get", url=f"/dvmdb/adom/{adom}/device")

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
        success, result = self._make_api_request(method="get", url=f"/dvmdb/adom/{adom}/device/{device_name}")

        if success:
            return result
        else:
            self.logger.error(f"Failed to get device status: {result}")
            return None

    def get_firewall_policies(self, device_name, vdom="root", adom="root"):
        """
        Get firewall policies for a device (공식 API 구조 준수)

        Args:
            device_name (str): Device name
            vdom (str): VDOM name (default: root)
            adom (str): ADOM name (default: root)

        Returns:
            list: Firewall policies or empty list on failure
        """
        # 공식 FortiManager API 구조 사용: /pm/config/device/{device}/vdom/{vdom}/firewall/policy
        success, result = self._make_api_request(
            method="get",
            url=f"/pm/config/device/{device_name}/vdom/{vdom}/firewall/policy",
        )

        if success:
            return result if isinstance(result, list) else []
        else:
            self.logger.error(f"Failed to get firewall policies: {result}")
            return []

    def get_package_policies(self, package_name="default", adom="root"):
        """
        Get policies from a policy package (Policy Package 관리)

        Args:
            package_name (str): Policy package name (default: default)
            adom (str): ADOM name (default: root)

        Returns:
            list: Package policies or empty list on failure
        """
        success, result = self._make_api_request(
            method="get",
            url=f"/pm/config/adom/{adom}/pkg/{package_name}/firewall/policy",
        )

        if success:
            return result if isinstance(result, list) else []
        else:
            self.logger.error(f"Failed to get package policies: {result}")
            return []

    def analyze_packet_path(
        self,
        src_ip: str,
        dst_ip: str,
        port: int,
        protocol: str = "tcp",
        device_name: str = None,
        vdom: str = "root",
    ) -> Dict[str, Any]:
        """
        Analyze packet path through FortiGate using FortiManager APIs

        Args:
            src_ip (str): Source IP address
            dst_ip (str): Destination IP address
            port (int): Destination port
            protocol (str): Protocol (tcp/udp/icmp)
            device_name (str): Target device name
            vdom (str): VDOM name (default: root)

        Returns:
            dict: Path analysis result with multi-firewall support
        """
        try:
            # If no device specified, analyze across all devices
            devices_to_analyze = []
            if device_name:
                devices_to_analyze = [device_name]
            else:
                # Get all managed devices
                all_devices = self.get_managed_devices()
                if not all_devices:
                    # Fallback - try to get from first ADOM
                    adom_list = self.get_adom_list()
                    if adom_list:
                        for adom in adom_list:
                            devices = self.get_devices(adom.get("name", "root"))
                            if devices:
                                all_devices = devices
                                break

                devices_to_analyze = [dev.get("name") for dev in all_devices if dev.get("name")] if all_devices else []

                # If still no devices, return error
                if not devices_to_analyze:
                    return {
                        "source_ip": src_ip,
                        "destination_ip": dst_ip,
                        "port": port,
                        "protocol": protocol,
                        "error": "No managed devices found",
                        "path_status": "error",
                    }

            # Path analysis result structure
            path_analysis = {
                "source_ip": src_ip,
                "destination_ip": dst_ip,
                "port": port,
                "protocol": protocol,
                "analysis_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "devices_analyzed": [],
                "packet_path": [],
                "final_action": "unknown",
                "path_status": "analyzing",
            }

            # Analyze each device
            for device in devices_to_analyze:
                try:
                    # Get device info
                    device_info = self.get_device_info(device)
                    hostname = device_info.get("hostname", device) if device_info else device

                    # Get routing information
                    routes = self.get_routes(device, vdom)

                    # Get interfaces
                    interfaces = self.get_interfaces(device, vdom)

                    # Get firewall policies
                    policies = self.get_firewall_policies(device, vdom)

                    # Device-specific analysis
                    device_analysis = {
                        "device_name": device,
                        "hostname": hostname,
                        "vdom": vdom,
                        "ingress_interface": None,
                        "egress_interface": None,
                        "matching_route": None,
                        "applied_policies": [],
                        "action": "unknown",
                    }

                    # Find ingress interface
                    for interface in interfaces:
                        if self._ip_in_subnet(
                            src_ip,
                            interface.get("ip", ""),
                            interface.get("netmask", ""),
                        ):
                            device_analysis["ingress_interface"] = interface.get("name")
                            break

                    # Find matching route for destination
                    for route in routes:
                        if self._ip_in_subnet(dst_ip, route.get("dst", ""), route.get("netmask", "")):
                            device_analysis["matching_route"] = route
                            device_analysis["egress_interface"] = route.get("device", route.get("interface"))
                            break

                    # Find ALL applicable policies (not just first match)
                    matching_policies = []
                    for policy in policies:
                        if self._policy_matches_traffic(policy, src_ip, dst_ip, port, protocol):
                            # Add device hostname to policy info
                            policy_info = policy.copy()
                            policy_info["device_hostname"] = hostname
                            policy_info["device_name"] = device
                            # 정책 매칭 상세 정보 추가
                            policy_info["match_details"] = {
                                "policy_id": policy.get("policyid"),
                                "policy_name": policy.get("name", "Unnamed"),
                                "action": policy.get("action", "unknown"),
                                "sequence": policy.get("policyid"),  # 정책 순서
                                "srcintf": policy.get("srcintf"),
                                "dstintf": policy.get("dstintf"),
                                "srcaddr": policy.get("srcaddr"),
                                "dstaddr": policy.get("dstaddr"),
                                "service": policy.get("service"),
                            }
                            matching_policies.append(policy_info)

                    device_analysis["applied_policies"] = matching_policies

                    # Determine action based on policies
                    if matching_policies:
                        # Check all matching policies - if any denies, traffic is denied
                        actions = [p.get("action", "unknown") for p in matching_policies]
                        if "deny" in actions:
                            device_analysis["action"] = "deny"
                        elif "accept" in actions:
                            device_analysis["action"] = "accept"
                        else:
                            device_analysis["action"] = actions[0] if actions else "unknown"
                    else:
                        # No matching policy - implicit deny
                        device_analysis["action"] = "deny"

                    # Add to devices analyzed
                    path_analysis["devices_analyzed"].append(device_analysis)

                    # Build packet path
                    if device_analysis["ingress_interface"] or device_analysis["egress_interface"]:
                        path_hop = {
                            "device": device,
                            "hostname": hostname,
                            "ingress": device_analysis["ingress_interface"],
                            "egress": device_analysis["egress_interface"],
                            "action": device_analysis["action"],
                            "policies_matched": len(device_analysis["applied_policies"]),
                        }
                        path_analysis["packet_path"].append(path_hop)

                except Exception as e:
                    self.logger.error(f"Error analyzing device {device}: {e}")
                    continue

            # Determine final action based on all devices
            all_actions = [d["action"] for d in path_analysis["devices_analyzed"]]
            if "deny" in all_actions:
                path_analysis["final_action"] = "deny"
            elif all_actions and all(a == "accept" for a in all_actions):
                path_analysis["final_action"] = "accept"
            else:
                path_analysis["final_action"] = "unknown"

            path_analysis["path_status"] = "completed"

            return path_analysis

        except Exception as e:
            self.logger.error(f"Failed to analyze packet path: {e}")
            return {
                "source_ip": src_ip,
                "destination_ip": dst_ip,
                "port": port,
                "protocol": protocol,
                "error": str(e),
                "analysis_result": {"path_status": "error"},
            }

    # Device Settings vs Security Settings Management
    def get_device_global_settings(self, device_name: str, cli_path: str, adom: str = "root") -> Dict[str, Any]:
        """
        Get device global settings (Device Settings 관리)
        URL 형식: /pm/config/device/<device>/global/<cli>

        Args:
            device_name (str): Device name
            cli_path (str): CLI path (e.g., 'system/interface', 'system/dns')
            adom (str): ADOM name

        Returns:
            dict: Global settings result
        """
        success, result = self._make_api_request(method="get", url=f"/pm/config/device/{device_name}/global/{cli_path}")

        if success:
            return result if isinstance(result, (dict, list)) else {}
        else:
            self.logger.error(f"Failed to get device global settings: {result}")
            return {}

    def set_device_global_settings(
        self, device_name: str, cli_path: str, data: Dict[str, Any], adom: str = "root"
    ) -> bool:
        """
        Set device global settings (Device Settings 관리)
        URL 형식: /pm/config/device/<device>/global/<cli>

        Args:
            device_name (str): Device name
            cli_path (str): CLI path
            data (dict): Configuration data
            adom (str): ADOM name

        Returns:
            bool: Success status
        """
        success, result = self._make_api_request(
            method="set",
            url=f"/pm/config/device/{device_name}/global/{cli_path}",
            data=data,
        )

        if success:
            return True
        else:
            self.logger.error(f"Failed to set device global settings: {result}")
            return False

    def get_device_vdom_settings(
        self, device_name: str, vdom: str, cli_path: str, adom: str = "root"
    ) -> Dict[str, Any]:
        """
        Get device VDOM settings (Security Settings 관리)
        URL 형식: /pm/config/device/<device>/vdom/<vdom>/<cli>

        Args:
            device_name (str): Device name
            vdom (str): VDOM name
            cli_path (str): CLI path (e.g., 'firewall/policy', 'router/static')
            adom (str): ADOM name

        Returns:
            dict: VDOM settings result
        """
        success, result = self._make_api_request(
            method="get", url=f"/pm/config/device/{device_name}/vdom/{vdom}/{cli_path}"
        )

        if success:
            return result if isinstance(result, (dict, list)) else {}
        else:
            self.logger.error(f"Failed to get device VDOM settings: {result}")
            return {}

    def set_device_vdom_settings(
        self,
        device_name: str,
        vdom: str,
        cli_path: str,
        data: Dict[str, Any],
        adom: str = "root",
    ) -> bool:
        """
        Set device VDOM settings (Security Settings 관리)
        URL 형식: /pm/config/device/<device>/vdom/<vdom>/<cli>

        Args:
            device_name (str): Device name
            vdom (str): VDOM name
            cli_path (str): CLI path
            data (dict): Configuration data
            adom (str): ADOM name

        Returns:
            bool: Success status
        """
        success, result = self._make_api_request(
            method="set",
            url=f"/pm/config/device/{device_name}/vdom/{vdom}/{cli_path}",
            data=data,
        )

        if success:
            return True
        else:
            self.logger.error(f"Failed to set device VDOM settings: {result}")
            return False

    # Policy Package Management (ADOM 레벨)
    def get_policy_package_settings(self, package_name: str, cli_path: str, adom: str = "root") -> Dict[str, Any]:
        """
        Get policy package settings (ADOM 레벨 정책 관리)
        URL 형식: /pm/config/adom/<adom>/pkg/<package>/<cli>

        Args:
            package_name (str): Policy package name
            cli_path (str): CLI path (e.g., 'firewall/policy', 'firewall/address')
            adom (str): ADOM name

        Returns:
            dict: Package settings result
        """
        success, result = self._make_api_request(
            method="get", url=f"/pm/config/adom/{adom}/pkg/{package_name}/{cli_path}"
        )

        if success:
            return result if isinstance(result, (dict, list)) else {}
        else:
            self.logger.error(f"Failed to get policy package settings: {result}")
            return {}

    def _ip_in_subnet(self, ip: str, network: str, netmask: str) -> bool:
        """
        Check if IP is in subnet (간단한 구현)
        """
        try:
            import ipaddress

            network_obj = ipaddress.IPv4Network(f"{network}/{netmask}", strict=False)
            ip_obj = ipaddress.IPv4Address(ip)
            return ip_obj in network_obj
        except (ValueError, ipaddress.AddressValueError):
            return False

    def _policy_matches_traffic(self, policy: Dict, src_ip: str, dst_ip: str, port: int, protocol: str) -> bool:
        """
        Check if policy matches the given traffic
        """
        try:
            # 단순화된 매칭 로직 - 실제 구현에서는 더 복잡한 로직 필요
            src_addrs = policy.get("srcaddr", [])
            dst_addrs = policy.get("dstaddr", [])
            services = policy.get("service", [])

            # Source address check
            src_match = False
            if not src_addrs or "all" in [addr.get("name", "") for addr in src_addrs]:
                src_match = True
            # 추가 로직 필요

            # Destination address check
            dst_match = False
            if not dst_addrs or "all" in [addr.get("name", "") for addr in dst_addrs]:
                dst_match = True
            # 추가 로직 필요

            # Service check
            service_match = False
            if not services or "ALL" in [svc.get("name", "") for svc in services]:
                service_match = True
            # 추가 로직 필요

            return src_match and dst_match and service_match

        except Exception:
            return False

    # Duplicate function removed - using the original definition at line 368

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
            method="get", url=f"/pm/config/device/{device_name}/global/system/interface"
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
            url=f"/pm/config/device/{device_name}/vdom/{vdom}/router/static",
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
        success, result = self._make_api_request(method="get", url="/sys/status")

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
        success, result = self._make_api_request(method="get", url=f"/task/task/{task_id}")

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
            url="/securityconsole/install/package",
            data={
                "adom": adom,
                "pkg": package_name,
                "scope": [{"name": device_name, "vdom": "root"}],
            },
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
                        "start": int(time.time() - 86400),
                        "end": int(time.time()),
                    },  # Last 24 hours
                    "filter": "",
                    "limit": limit,
                },
            )

            if success and result:
                return result.get("data", [])
            else:
                self.logger.warning("No security events found or failed to retrieve")
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
                        "start": int(time.time() - 86400),
                        "end": int(time.time()),
                    },  # Last 24 hours
                    "chart_type": "threat_summary",
                },
            )

            if success and result:
                # Transform data to expected format
                stats = result.get("data", {})
                return {
                    "today": stats.get("threats_today", 0),
                    "week": stats.get("threats_week", 0),
                    "month": stats.get("threats_month", 0),
                    "by_type": stats.get("threat_types", {}),
                    "blocked_percentage": stats.get("blocked_percent", 95),
                    "quarantined_percentage": stats.get("quarantined_percent", 3),
                }
            else:
                self.logger.warning("No threat statistics found")
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
                url=f"/monitor/adom/{adom}/device/{device_name}/system/performance",
            )

            if success and result:
                perf_data = result.get("data", {})
                return {
                    "cpu_usage": perf_data.get("cpu", 0),
                    "memory_usage": perf_data.get("memory", 0),
                    "session_count": perf_data.get("sessions", 0),
                    "bandwidth_in": perf_data.get("bandwidth_rx", 0),
                    "bandwidth_out": perf_data.get("bandwidth_tx", 0),
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

            success, result = self._make_api_request(method="get", url=url)

            if success and result:
                return result.get("data", [])
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
                "timestamp": time.time(),
                "system_status": self.get_system_status(),
                "adoms": len(self.get_adom_list()),
                "managed_devices": [],
            }

            # Get device summary for each ADOM
            for adom in self.get_adom_list():
                adom_name = adom.get("name", "unknown")
                devices = self.get_managed_devices(adom_name)
                monitoring_data["managed_devices"].extend(
                    [
                        {
                            "name": dev.get("name"),
                            "adom": adom_name,
                            "status": dev.get("conn_status"),
                            "ip": dev.get("ip"),
                        }
                        for dev in devices
                    ]
                )

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
            url=f"/pm/config/device/{device_name}/vdom/{vdom}/firewall/policy",
            data=policy_data,
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
            url=f"/pm/config/device/{device_name}/vdom/{vdom}/firewall/policy/{policy_id}",
            data=policy_data,
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
            url=f"/pm/config/device/{device_name}/vdom/{vdom}/firewall/policy/{policy_id}",
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
        success, result = self._make_api_request(method="get", url=f"/pm/config/adom/{adom}/obj/firewall/address")

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
            method="get", url=f"/pm/config/adom/{adom}/obj/firewall/service/custom"
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
        if self.auth_method == "token":
            # No logout needed for token auth
            return True

        if not self.session_id:
            # Already logged out
            return True

        payload = self.build_json_rpc_request(method="exec", url="/sys/logout", session=self.session_id)

        success, result, _ = self._make_request("POST", self.base_url, payload, None, self.headers)

        if success:
            self.session_id = None
            self.logger.info("FortiManager API logout successful")
            return True
        else:
            self.logger.warning("FortiManager API logout failed, but clearing session")
            self.session_id = None
            return True
