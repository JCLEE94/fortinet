#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mock FortiGate 방화벽 시스템
정책 변경 시 실시간 분석이 가능한 가상 FortiGate 시스템
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import ipaddress
import threading
import queue
import uuid

class MockFortiGatePolicy:
    """Mock FortiGate 정책 클래스"""
    
    def __init__(self, policy_id: int, name: str, srcintf: str, dstintf: str, 
                 srcaddr: List[str], dstaddr: List[str], service: List[str], 
                 action: str = "accept", status: str = "enable", **kwargs):
        self.policy_id = policy_id
        self.name = name
        self.srcintf = srcintf
        self.dstintf = dstintf
        self.srcaddr = srcaddr if isinstance(srcaddr, list) else [srcaddr]
        self.dstaddr = dstaddr if isinstance(dstaddr, list) else [dstaddr]
        self.service = service if isinstance(service, list) else [service]
        self.action = action
        self.status = status
        self.created_time = datetime.now().isoformat()
        self.modified_time = datetime.now().isoformat()
        self.hit_count = kwargs.get('hit_count', 0)
        self.last_hit = kwargs.get('last_hit', None)
        self.uuid = kwargs.get('uuid', str(uuid.uuid4()))
        
    def to_dict(self) -> Dict[str, Any]:
        """정책을 딕셔너리로 변환"""
        return {
            'policyid': self.policy_id,
            'name': self.name,
            'srcintf': self.srcintf,
            'dstintf': self.dstintf,
            'srcaddr': self.srcaddr,
            'dstaddr': self.dstaddr,
            'service': self.service,
            'action': self.action,
            'status': self.status,
            'created_time': self.created_time,
            'modified_time': self.modified_time,
            'hit_count': self.hit_count,
            'last_hit': self.last_hit,
            'uuid': self.uuid
        }
    
    def update(self, **kwargs):
        """정책 업데이트"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.modified_time = datetime.now().isoformat()

class MockFortiGateAddressObject:
    """Mock FortiGate 주소 객체"""
    
    def __init__(self, name: str, type: str, subnet: str = None, 
                 start_ip: str = None, end_ip: str = None, **kwargs):
        self.name = name
        self.type = type  # ipmask, iprange, fqdn, geography
        self.subnet = subnet
        self.start_ip = start_ip
        self.end_ip = end_ip
        self.created_time = datetime.now().isoformat()
        self.uuid = kwargs.get('uuid', str(uuid.uuid4()))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'type': self.type,
            'subnet': self.subnet,
            'start-ip': self.start_ip,
            'end-ip': self.end_ip,
            'created_time': self.created_time,
            'uuid': self.uuid
        }

class MockFortiGateService:
    """Mock FortiGate 서비스 객체"""
    
    def __init__(self, name: str, protocol: str, port_range: str = None, **kwargs):
        self.name = name
        self.protocol = protocol  # TCP, UDP, ICMP
        self.port_range = port_range
        self.created_time = datetime.now().isoformat()
        self.uuid = kwargs.get('uuid', str(uuid.uuid4()))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'protocol': self.protocol,
            'tcp-portrange': self.port_range if self.protocol == 'TCP' else None,
            'udp-portrange': self.port_range if self.protocol == 'UDP' else None,
            'created_time': self.created_time,
            'uuid': self.uuid
        }

class MockFortiGate:
    """Mock FortiGate 방화벽 시스템"""
    
    def __init__(self, hostname: str = "FortiGate-Mock", version: str = "7.4.0"):
        self.hostname = hostname
        self.version = version
        self.serial_number = f"FGT-MOCK-{int(time.time())}"
        self.policies: Dict[int, MockFortiGatePolicy] = {}
        self.address_objects: Dict[str, MockFortiGateAddressObject] = {}
        self.service_objects: Dict[str, MockFortiGateService] = {}
        self.interfaces = {
            'port1': {'name': 'port1', 'alias': 'internal', 'ip': '192.168.1.1/24', 'status': 'up'},
            'port2': {'name': 'port2', 'alias': 'external', 'ip': '203.0.113.1/24', 'status': 'up'},
            'port3': {'name': 'port3', 'alias': 'dmz', 'ip': '172.16.1.1/24', 'status': 'up'},
            'port4': {'name': 'port4', 'alias': 'guest', 'ip': '10.10.1.1/24', 'status': 'up'}
        }
        self.policy_change_listeners = []
        self.analysis_cache = {}
        self._init_default_objects()
        self._init_default_policies()
    
    def _init_default_objects(self):
        """기본 주소 객체 및 서비스 생성"""
        # 기본 주소 객체
        default_addresses = [
            ('all', 'ipmask', '0.0.0.0/0'),
            ('internal_network', 'ipmask', '192.168.0.0/16'),
            ('dmz_network', 'ipmask', '172.16.0.0/16'),
            ('guest_network', 'ipmask', '10.10.0.0/16'),
            ('web_server', 'ipmask', '172.16.10.100/32'),
            ('db_server', 'ipmask', '172.16.20.50/32'),
            ('mail_server', 'ipmask', '172.16.30.10/32')
        ]
        
        for name, addr_type, subnet in default_addresses:
            self.address_objects[name] = MockFortiGateAddressObject(
                name=name, type=addr_type, subnet=subnet
            )
        
        # 기본 서비스 객체
        default_services = [
            ('ALL', 'ALL', None),
            ('HTTP', 'TCP', '80'),
            ('HTTPS', 'TCP', '443'),
            ('SSH', 'TCP', '22'),
            ('FTP', 'TCP', '21'),
            ('SMTP', 'TCP', '25'),
            ('DNS', 'UDP', '53'),
            ('DHCP', 'UDP', '67-68'),
            ('MySQL', 'TCP', '3306'),
            ('PostgreSQL', 'TCP', '5432'),
            ('PING', 'ICMP', None)
        ]
        
        for name, protocol, port_range in default_services:
            self.service_objects[name] = MockFortiGateService(
                name=name, protocol=protocol, port_range=port_range
            )
    
    def _init_default_policies(self):
        """기본 정책 생성"""
        default_policies = [
            {
                'policy_id': 1,
                'name': 'Internal_to_DMZ_Web',
                'srcintf': 'internal',
                'dstintf': 'dmz',
                'srcaddr': ['internal_network'],
                'dstaddr': ['web_server'],
                'service': ['HTTP', 'HTTPS'],
                'action': 'accept',
                'status': 'enable'
            },
            {
                'policy_id': 2,
                'name': 'DMZ_to_Internet',
                'srcintf': 'dmz',
                'dstintf': 'external',
                'srcaddr': ['dmz_network'],
                'dstaddr': ['all'],
                'service': ['HTTP', 'HTTPS', 'DNS'],
                'action': 'accept',
                'status': 'enable'
            },
            {
                'policy_id': 3,
                'name': 'Internal_to_Internet',
                'srcintf': 'internal',
                'dstintf': 'external',
                'srcaddr': ['internal_network'],
                'dstaddr': ['all'],
                'service': ['HTTP', 'HTTPS', 'DNS'],
                'action': 'accept',
                'status': 'enable'
            },
            {
                'policy_id': 4,
                'name': 'Guest_Isolation',
                'srcintf': 'guest',
                'dstintf': 'internal',
                'srcaddr': ['guest_network'],
                'dstaddr': ['internal_network'],
                'service': ['ALL'],
                'action': 'deny',
                'status': 'enable'
            },
            {
                'policy_id': 5,
                'name': 'SSH_Management',
                'srcintf': 'internal',
                'dstintf': 'dmz',
                'srcaddr': ['192.168.1.100/32'],
                'dstaddr': ['dmz_network'],
                'service': ['SSH'],
                'action': 'accept',
                'status': 'enable'
            }
        ]
        
        for policy_data in default_policies:
            policy = MockFortiGatePolicy(**policy_data)
            self.policies[policy.policy_id] = policy
    
    def add_policy_change_listener(self, callback):
        """정책 변경 리스너 추가"""
        self.policy_change_listeners.append(callback)
    
    def _notify_policy_change(self, action: str, policy: MockFortiGatePolicy):
        """정책 변경 알림"""
        for callback in self.policy_change_listeners:
            try:
                callback(action, policy.to_dict())
            except Exception as e:
                print(f"Policy change notification error: {e}")
    
    def get_policies(self, policy_id: Optional[int] = None) -> Dict[str, Any]:
        """정책 목록 조회"""
        if policy_id:
            policy = self.policies.get(policy_id)
            if policy:
                return {
                    'status': 'success',
                    'policy': policy.to_dict()
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Policy {policy_id} not found'
                }
        
        policies_list = [policy.to_dict() for policy in self.policies.values()]
        return {
            'status': 'success',
            'policies': policies_list,
            'total': len(policies_list)
        }
    
    def create_policy(self, policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """새 정책 생성"""
        try:
            # 새 정책 ID 생성
            new_id = max(self.policies.keys()) + 1 if self.policies else 1
            policy_data['policy_id'] = new_id
            
            # 정책 객체 생성
            policy = MockFortiGatePolicy(**policy_data)
            self.policies[new_id] = policy
            
            # 분석 캐시 무효화
            self.analysis_cache.clear()
            
            # 변경 알림
            self._notify_policy_change('create', policy)
            
            return {
                'status': 'success',
                'message': 'Policy created successfully',
                'policy_id': new_id,
                'policy': policy.to_dict()
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to create policy: {str(e)}'
            }
    
    def update_policy(self, policy_id: int, policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """정책 업데이트"""
        try:
            if policy_id not in self.policies:
                return {
                    'status': 'error',
                    'message': f'Policy {policy_id} not found'
                }
            
            policy = self.policies[policy_id]
            policy.update(**policy_data)
            
            # 분석 캐시 무효화
            self.analysis_cache.clear()
            
            # 변경 알림
            self._notify_policy_change('update', policy)
            
            return {
                'status': 'success',
                'message': 'Policy updated successfully',
                'policy': policy.to_dict()
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to update policy: {str(e)}'
            }
    
    def delete_policy(self, policy_id: int) -> Dict[str, Any]:
        """정책 삭제"""
        try:
            if policy_id not in self.policies:
                return {
                    'status': 'error',
                    'message': f'Policy {policy_id} not found'
                }
            
            policy = self.policies.pop(policy_id)
            
            # 분석 캐시 무효화
            self.analysis_cache.clear()
            
            # 변경 알림
            self._notify_policy_change('delete', policy)
            
            return {
                'status': 'success',
                'message': 'Policy deleted successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to delete policy: {str(e)}'
            }
    
    def analyze_packet_path(self, src_ip: str, dst_ip: str, 
                          port: int = 80, protocol: str = 'tcp') -> Dict[str, Any]:
        """패킷 경로 분석 (정책 기반)"""
        cache_key = f"{src_ip}:{dst_ip}:{port}:{protocol}"
        
        # 캐시된 결과 확인
        if cache_key in self.analysis_cache:
            cached_result = self.analysis_cache[cache_key]
            cached_result['cached'] = True
            cached_result['cache_time'] = cached_result.get('analysis_time')
            cached_result['analysis_time'] = datetime.now().isoformat()
            return cached_result
        
        try:
            # 실제 분석 수행
            matching_policies = self._find_matching_policies(src_ip, dst_ip, port, protocol)
            
            if not matching_policies:
                result = {
                    'status': 'blocked',
                    'reason': 'No matching policy found',
                    'src_ip': src_ip,
                    'dst_ip': dst_ip,
                    'port': port,
                    'protocol': protocol,
                    'matched_policies': [],
                    'analysis_time': datetime.now().isoformat(),
                    'fortigate_info': {
                        'hostname': self.hostname,
                        'version': self.version,
                        'serial': self.serial_number
                    }
                }
            else:
                # 첫 번째 매칭 정책으로 결정
                primary_policy = matching_policies[0]
                
                result = {
                    'status': 'allowed' if primary_policy['action'] == 'accept' else 'blocked',
                    'reason': f"Matched policy: {primary_policy['name']}",
                    'src_ip': src_ip,
                    'dst_ip': dst_ip,
                    'port': port,
                    'protocol': protocol,
                    'matched_policies': matching_policies,
                    'primary_policy': primary_policy,
                    'path_analysis': self._generate_path_analysis(src_ip, dst_ip, primary_policy),
                    'analysis_time': datetime.now().isoformat(),
                    'fortigate_info': {
                        'hostname': self.hostname,
                        'version': self.version,
                        'serial': self.serial_number
                    }
                }
            
            # 결과 캐시
            self.analysis_cache[cache_key] = result.copy()
            
            return result
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Analysis failed: {str(e)}',
                'src_ip': src_ip,
                'dst_ip': dst_ip,
                'port': port,
                'protocol': protocol,
                'analysis_time': datetime.now().isoformat()
            }
    
    def _find_matching_policies(self, src_ip: str, dst_ip: str, 
                              port: int, protocol: str) -> List[Dict[str, Any]]:
        """매칭되는 정책 찾기"""
        matching_policies = []
        
        for policy in self.policies.values():
            if policy.status != 'enable':
                continue
                
            # 주소 매칭 확인
            if (self._ip_matches_addresses(src_ip, policy.srcaddr) and 
                self._ip_matches_addresses(dst_ip, policy.dstaddr) and
                self._port_matches_services(port, protocol, policy.service)):
                
                matching_policies.append(policy.to_dict())
        
        # 정책 ID 순서로 정렬 (FortiGate는 위에서부터 처리)
        matching_policies.sort(key=lambda p: p['policyid'])
        
        return matching_policies
    
    def _ip_matches_addresses(self, ip: str, addresses: List[str]) -> bool:
        """IP가 주소 목록과 매칭되는지 확인"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            for addr_name in addresses:
                # 주소 객체에서 찾기
                if addr_name in self.address_objects:
                    addr_obj = self.address_objects[addr_name]
                    if addr_obj.subnet:
                        if ip_obj in ipaddress.ip_network(addr_obj.subnet, strict=False):
                            return True
                
                # 직접 IP/네트워크 매칭
                try:
                    if '/' in addr_name:
                        if ip_obj in ipaddress.ip_network(addr_name, strict=False):
                            return True
                    else:
                        if str(ip_obj) == addr_name:
                            return True
                except:
                    continue
                    
                # 'all' 주소
                if addr_name == 'all':
                    return True
            
            return False
        except:
            return False
    
    def _port_matches_services(self, port: int, protocol: str, services: List[str]) -> bool:
        """포트가 서비스 목록과 매칭되는지 확인"""
        for service_name in services:
            if service_name == 'ALL':
                return True
                
            if service_name in self.service_objects:
                service_obj = self.service_objects[service_name]
                
                # 프로토콜 확인
                if service_obj.protocol != 'ALL' and service_obj.protocol.upper() != protocol.upper():
                    continue
                
                # 포트 범위 확인
                if service_obj.port_range:
                    port_ranges = service_obj.port_range.split(',')
                    for port_range in port_ranges:
                        port_range = port_range.strip()
                        if '-' in port_range:
                            start_port, end_port = map(int, port_range.split('-'))
                            if start_port <= port <= end_port:
                                return True
                        else:
                            if int(port_range) == port:
                                return True
                else:
                    # 포트 범위가 없으면 모든 포트 허용
                    return True
        
        return False
    
    def _generate_path_analysis(self, src_ip: str, dst_ip: str, 
                              policy: Dict[str, Any]) -> Dict[str, Any]:
        """경로 분석 생성"""
        return {
            'source_interface': policy['srcintf'],
            'destination_interface': policy['dstintf'],
            'routing_decision': f"{policy['srcintf']} -> {policy['dstintf']}",
            'policy_action': policy['action'],
            'traffic_flow': f"{src_ip} ({policy['srcintf']}) -> {dst_ip} ({policy['dstintf']})",
            'security_processing': [
                'Interface-based routing',
                f"Policy {policy['policyid']} evaluation",
                f"Action: {policy['action']}"
            ]
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        return {
            'hostname': self.hostname,
            'version': self.version,
            'serial_number': self.serial_number,
            'uptime': '15 days, 3 hours, 22 minutes',
            'cpu_usage': '12%',
            'memory_usage': '34%',
            'session_count': 1847,
            'policy_count': len(self.policies),
            'interface_count': len(self.interfaces),
            'status': 'online'
        }
    
    def get_interfaces(self) -> Dict[str, Any]:
        """인터페이스 정보 조회"""
        return {
            'status': 'success',
            'interfaces': list(self.interfaces.values())
        }

# 글로벌 Mock FortiGate 인스턴스
mock_fortigate = MockFortiGate()