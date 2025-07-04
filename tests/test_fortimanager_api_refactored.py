#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for refactored FortiManager API client
Tests compliance with official FortiManager JSON-RPC API documentation
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json

from src.api.clients.fortimanager_api_client import FortiManagerAPIClient
from src.utils.api_utils import JsonRpcMixin


class TestFortiManagerAPIRefactored(unittest.TestCase):
    """Test refactored FortiManager API client against official specs"""
    
    def setUp(self):
        """Set up test environment"""
        self.client = FortiManagerAPIClient(
            host='192.168.1.100',
            username='admin',
            password='password',
            verify_ssl=False
        )
        
    def test_json_rpc_request_format(self):
        """Test JSON-RPC request format follows official standard"""
        mixin = JsonRpcMixin()
        mixin.request_id = 1
        
        # Test basic request
        payload = mixin.build_json_rpc_request(
            method="get",
            url="/sys/status",
            session="test_session"
        )
        
        # Verify official format
        expected_structure = {
            "id": 1,
            "method": "get", 
            "params": [
                {
                    "url": "/sys/status"
                }
            ],
            "session": "test_session"
        }
        
        self.assertEqual(payload["id"], expected_structure["id"])
        self.assertEqual(payload["method"], expected_structure["method"])
        self.assertEqual(payload["session"], expected_structure["session"])
        self.assertIsInstance(payload["params"], list)
        self.assertEqual(len(payload["params"]), 1)
        self.assertEqual(payload["params"][0]["url"], "/sys/status")
        
    def test_json_rpc_request_with_data(self):
        """Test JSON-RPC request with data payload"""
        mixin = JsonRpcMixin()
        mixin.request_id = 1
        
        test_data = {
            "user": "admin",
            "passwd": "password"
        }
        
        payload = mixin.build_json_rpc_request(
            method="exec",
            url="/sys/login/user",
            data=test_data,
            verbose=1
        )
        
        # Verify structure
        self.assertEqual(payload["method"], "exec")
        self.assertIsInstance(payload["params"], list)
        self.assertEqual(len(payload["params"]), 1)
        
        params = payload["params"][0]
        self.assertEqual(params["url"], "/sys/login/user")
        self.assertEqual(params["data"], test_data)
        self.assertEqual(params["verbose"], 1)
        
    def test_json_rpc_response_parsing_success(self):
        """Test parsing successful JSON-RPC response"""
        mixin = JsonRpcMixin()
        
        # Mock successful response
        mock_response = {
            "id": 1,
            "result": [
                {
                    "status": {
                        "code": 0,
                        "message": "OK"
                    },
                    "url": "/sys/status",
                    "data": [
                        {
                            "version": "7.4.0",
                            "hostname": "FortiManager-VM"
                        }
                    ]
                }
            ]
        }
        
        success, result = mixin.parse_json_rpc_response(mock_response)
        
        self.assertTrue(success)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["version"], "7.4.0")
        
    def test_json_rpc_response_parsing_error(self):
        """Test parsing error JSON-RPC response"""
        mixin = JsonRpcMixin()
        
        # Mock error response
        mock_response = {
            "id": 1,
            "result": [
                {
                    "status": {
                        "code": -11,
                        "message": "No permission for the resource"
                    },
                    "url": "/sys/status"
                }
            ]
        }
        
        success, result = mixin.parse_json_rpc_response(mock_response)
        
        self.assertFalse(success)
        self.assertIn("No permission", result)
        self.assertIn("Code -11", result)
        
    def test_device_global_settings_url(self):
        """Test device global settings URL structure"""
        with patch.object(self.client, '_make_api_request') as mock_request:
            mock_request.return_value = (True, [{"name": "port1", "ip": "192.168.1.1"}])
            
            result = self.client.get_device_global_settings(
                device_name="FGT-001",
                cli_path="system/interface"
            )
            
            # Verify correct URL format: /pm/config/device/<device>/global/<cli>
            mock_request.assert_called_once_with(
                method="get",
                url="/pm/config/device/FGT-001/global/system/interface"
            )
            
    def test_device_vdom_settings_url(self):
        """Test device VDOM settings URL structure"""
        with patch.object(self.client, '_make_api_request') as mock_request:
            mock_request.return_value = (True, [{"policyid": 1, "action": "accept"}])
            
            result = self.client.get_device_vdom_settings(
                device_name="FGT-001",
                vdom="root",
                cli_path="firewall/policy"
            )
            
            # Verify correct URL format: /pm/config/device/<device>/vdom/<vdom>/<cli>
            mock_request.assert_called_once_with(
                method="get",
                url="/pm/config/device/FGT-001/vdom/root/firewall/policy"
            )
            
    def test_firewall_policies_url_corrected(self):
        """Test firewall policies use device-centric URL"""
        with patch.object(self.client, '_make_api_request') as mock_request:
            mock_request.return_value = (True, [{"policyid": 1}])
            
            result = self.client.get_firewall_policies(
                device_name="FGT-001",
                vdom="root"
            )
            
            # Should use device-centric URL, not package-centric
            mock_request.assert_called_once_with(
                method="get",
                url="/pm/config/device/FGT-001/vdom/root/firewall/policy"
            )
            
    def test_packet_path_analysis_integration(self):
        """Test packet path analysis with real FortiManager APIs"""
        with patch.object(self.client, 'get_routes') as mock_routes, \
             patch.object(self.client, 'get_interfaces') as mock_interfaces, \
             patch.object(self.client, 'get_firewall_policies') as mock_policies:
            
            # Mock API responses
            mock_interfaces.return_value = [
                {"name": "port1", "ip": "192.168.1.1", "netmask": "255.255.255.0"}
            ]
            mock_routes.return_value = [
                {"dst": "10.0.0.0", "netmask": "255.0.0.0", "device": "port2"}
            ]
            mock_policies.return_value = [
                {"policyid": 1, "action": "accept", "srcaddr": [{"name": "all"}], 
                 "dstaddr": [{"name": "all"}], "service": [{"name": "ALL"}]}
            ]
            
            result = self.client.analyze_packet_path(
                src_ip="192.168.1.100",
                dst_ip="10.0.0.50", 
                port=80,
                protocol="tcp",
                device_name="FGT-001"
            )
            
            # Verify analysis structure
            self.assertIn('analysis_result', result)
            self.assertIn('applied_policies', result['analysis_result'])
            self.assertIn('final_action', result['analysis_result'])
            self.assertEqual(result['analysis_result']['path_status'], 'completed')
            
    def test_policy_package_vs_device_settings(self):
        """Test distinction between policy package and device settings"""
        with patch.object(self.client, '_make_api_request') as mock_request:
            mock_request.return_value = (True, [{"policyid": 1}])
            
            # Test policy package URL (ADOM level)
            self.client.get_policy_package_settings("default", "firewall/policy")
            mock_request.assert_called_with(
                method="get",
                url="/pm/config/adom/root/pkg/default/firewall/policy"
            )
            
            mock_request.reset_mock()
            
            # Test device VDOM URL (Device level)
            self.client.get_device_vdom_settings("FGT-001", "root", "firewall/policy")
            mock_request.assert_called_with(
                method="get", 
                url="/pm/config/device/FGT-001/vdom/root/firewall/policy"
            )
            
    @patch('requests.Session')
    def test_authentication_flows(self, mock_session_class):
        """Test both session and token-based authentication"""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Test session-based authentication
        with patch.object(self.client, '_make_request') as mock_request:
            mock_request.return_value = (True, {
                "result": [{"status": {"code": 0}}],
                "session": "test_session_id"
            }, 200)
            
            success = self.client.login()
            
            self.assertTrue(success)
            self.assertEqual(self.client.session_id, "test_session_id")
            
            # Verify login request format
            call_args = mock_request.call_args
            payload = call_args[1]['data']
            self.assertEqual(payload['method'], 'exec')
            self.assertEqual(payload['params'][0]['url'], '/sys/login/user')
            
        # Test token-based authentication
        token_client = FortiManagerAPIClient(
            host='192.168.1.100',
            api_token='test_api_token'
        )
        
        with patch.object(token_client, '_make_request') as mock_request:
            mock_request.return_value = (True, {
                "result": [{"status": {"code": 0}}]
            }, 200)
            
            success = token_client.test_token_auth()
            
            # Verify Authorization header
            call_args = mock_request.call_args
            headers = call_args[1]['headers']
            self.assertIn('Authorization', headers)
            self.assertEqual(headers['Authorization'], 'Bearer test_api_token')
            
    def test_url_structure_compliance(self):
        """Test URL structures comply with official documentation"""
        test_cases = [
            # Device Global Settings
            {
                'method': 'get_device_global_settings',
                'args': ['FGT-001', 'system/interface'],
                'expected_url': '/pm/config/device/FGT-001/global/system/interface'
            },
            # Device VDOM Settings  
            {
                'method': 'get_device_vdom_settings',
                'args': ['FGT-001', 'root', 'firewall/policy'],
                'expected_url': '/pm/config/device/FGT-001/vdom/root/firewall/policy'
            },
            # Policy Package Settings
            {
                'method': 'get_policy_package_settings', 
                'args': ['default', 'firewall/address'],
                'expected_url': '/pm/config/adom/root/pkg/default/firewall/address'
            },
            # ADOM Management
            {
                'method': 'get_adom_list',
                'args': [],
                'expected_url': '/dvmdb/adom'
            }
        ]
        
        for case in test_cases:
            with patch.object(self.client, '_make_api_request') as mock_request:
                mock_request.return_value = (True, [])
                
                method = getattr(self.client, case['method'])
                method(*case['args'])
                
                mock_request.assert_called_once()
                call_args = mock_request.call_args[1]
                self.assertEqual(call_args['url'], case['expected_url'])


if __name__ == '__main__':
    unittest.main()