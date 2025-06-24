#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
더미 데이터 생성기 모듈
테스트 모드에서 사용할 가짜 데이터를 생성합니다.
"""

import random
import secrets
import time
from datetime import datetime, timedelta
import ipaddress

class DummyDataGenerator:
    """테스트용 더미 데이터 생성기"""
    
    def __init__(self):
        self.device_types = ['firewall', 'router', 'switch', 'server', 'workstation']
        self.protocols = ['TCP', 'UDP', 'ICMP', 'HTTP', 'HTTPS', 'SSH', 'DNS', 'FTP']
        self.actions = ['allow', 'deny', 'monitor']
        self.zones = ['internal', 'external', 'dmz', 'guest', 'management']
        
    def generate_ip(self):
        """랜덤 IP 주소 생성"""
        return f"{secrets.randbelow(254) + 1}.{secrets.randbelow(256)}.{secrets.randbelow(256)}.{secrets.randbelow(254) + 1}"
    
    def generate_mac(self):
        """랜덤 MAC 주소 생성"""
        return ':'.join([f'{secrets.randbelow(256):02x}' for _ in range(6)])
    
    def generate_devices(self, count=20):
        """더미 장치 목록 생성"""
        devices = []
        for i in range(count):
            device_type = secrets.choice(self.device_types)
            zone = secrets.choice(self.zones)
            
            device = {
                'id': f'device_{i+1}',
                'name': f'{device_type.upper()}-{i+1:02d}',
                'type': device_type,
                'ip_address': self.generate_ip(),
                'mac_address': self.generate_mac(),
                'zone': zone,
                'status': secrets.choice(['online', 'online', 'online', 'offline']),  # 75% online
                'cpu_usage': secrets.randbelow(80) + 10,  # 10-90%
                'memory_usage': secrets.randbelow(75) + 20,  # 20-95%
                'session_count': secrets.randbelow(4900) + 100,  # 100-5000
                'bandwidth_in': secrets.randbelow(990) + 10,  # 10-1000 Mbps
                'bandwidth_out': secrets.randbelow(990) + 10,  # 10-1000 Mbps
                'uptime': secrets.randbelow(8636400) + 3600,  # 1 hour to 100 days in seconds
                'last_seen': datetime.now() - timedelta(seconds=secrets.randbelow(3600)),
                'firmware_version': f'v{secrets.randbelow(2) + 6}.{secrets.randbelow(5)}.{secrets.randbelow(9) + 1}',
                'serial_number': f'FG{secrets.randbelow(900) + 100}{chr(65 + secrets.randbelow(26))}{secrets.randbelow(90000) + 10000}'
            }
            
            # 장치 타입별 추가 정보
            if device_type == 'firewall':
                device['policy_count'] = secrets.randbelow(450) + 50
                device['threat_level'] = secrets.choice(['low', 'medium', 'high'])
            elif device_type == 'switch':
                device['port_count'] = secrets.choice([24, 48])
                device['vlan_count'] = secrets.randbelow(19) + 1
            
            devices.append(device)
        
        return devices
    
    def generate_interfaces(self, device_id, count=4):
        """장치의 인터페이스 목록 생성"""
        interfaces = []
        for i in range(count):
            interface = {
                'id': f'{device_id}_if_{i+1}',
                'name': f'port{i+1}',
                'status': secrets.choice(['up', 'up', 'up', 'down']),  # 75% up
                'ip_address': self.generate_ip(),
                'netmask': '255.255.255.0',
                'speed': secrets.choice([100, 1000, 10000]),  # Mbps
                'duplex': secrets.choice(['full', 'half']),
                'mtu': 1500,
                'tx_packets': secrets.randbelow(9000000) + 1000000,
                'rx_packets': secrets.randbelow(9000000) + 1000000,
                'tx_errors': secrets.randbelow(100),
                'rx_errors': secrets.randbelow(100)
            }
            interfaces.append(interface)
        return interfaces
    
    def generate_policies(self, count=50):
        """방화벽 정책 목록 생성"""
        policies = []
        for i in range(count):
            policy = {
                'id': i + 1,
                'name': f'Policy_{i+1:03d}',
                'source_zone': secrets.choice(self.zones),
                'destination_zone': secrets.choice(self.zones),
                'source_address': self.generate_ip() + '/24',
                'destination_address': self.generate_ip() + '/24',
                'service': secrets.choice(['HTTP', 'HTTPS', 'SSH', 'Any', 'Custom']),
                'action': secrets.choice(self.actions),
                'status': secrets.choice(['enabled', 'enabled', 'disabled']),  # 66% enabled
                'hit_count': secrets.randbelow(1000000),
                'bytes_processed': secrets.randbelow(10000000000),
                'created_date': datetime.now() - timedelta(days=secrets.randbelow(364) + 1),
                'last_used': datetime.now() - timedelta(hours=secrets.randbelow(720))
            }
            policies.append(policy)
        return policies
    
    def generate_path_analysis(self, src_ip=None, dst_ip=None, port=None, protocol=None):
        """경로 분석 결과 생성 - 고정된 방화벽 4대 기준"""
        # 더미 방화벽 4대 정의
        firewalls = {
            'FW-01': {
                'name': 'FortiGate-HQ-01',
                'location': '본사',
                'zone': 'internal',
                'ip': '192.168.1.1',
                'policies': self._get_fw01_policies()
            },
            'FW-02': {
                'name': 'FortiGate-DMZ-01', 
                'location': 'DMZ',
                'zone': 'dmz',
                'ip': '172.16.1.1',
                'policies': self._get_fw02_policies()
            },
            'FW-03': {
                'name': 'FortiGate-Edge-01',
                'location': '인터넷 엣지',
                'zone': 'external', 
                'ip': '203.0.113.1',
                'policies': self._get_fw03_policies()
            },
            'FW-04': {
                'name': 'FortiGate-Branch-01',
                'location': '지사',
                'zone': 'branch',
                'ip': '10.10.1.1',
                'policies': self._get_fw04_policies()
            }
        }
        
        # 입력 파라미터가 제공된 경우 사용, 아니면 테스트 시나리오 사용
        if src_ip and dst_ip:
            # 사용자 입력 기반 시나리오 생성
            scenario = self._create_scenario_from_input(src_ip, dst_ip, port or 80, protocol or 'TCP')
        else:
            # 테스트 시나리오 정의 (일관된 기준)
            scenarios = [
                # 시나리오 1: 내부 -> DMZ 웹서버 (허용)
                {
                    'source': '192.168.10.100',
                    'destination': '172.16.10.80',
                    'port': 443,
                    'protocol': 'HTTPS',
                    'path': ['FW-01', 'FW-02'],
                    'expected': 'allow'
                },
                # 시나리오 2: 외부 -> DMZ 웹서버 (허용)
                {
                    'source': '8.8.8.8',
                    'destination': '172.16.10.80',
                    'port': 443,
                    'protocol': 'HTTPS',
                    'path': ['FW-03', 'FW-02'],
                    'expected': 'allow'
                },
                # 시나리오 3: 내부 -> 인터넷 (허용)
                {
                    'source': '192.168.20.50',
                    'destination': '1.1.1.1',
                    'port': 80,
                    'protocol': 'HTTP',
                    'path': ['FW-01', 'FW-03'],
                    'expected': 'allow'
                },
                # 시나리오 4: DMZ -> 내부 DB (차단)
                {
                    'source': '172.16.10.80',
                    'destination': '192.168.30.100',
                    'port': 3306,
                    'protocol': 'MySQL',
                    'path': ['FW-02', 'FW-01'],
                    'expected': 'deny'
                },
                # 시나리오 5: 지사 -> 본사 (허용)
                {
                    'source': '10.10.20.100',
                    'destination': '192.168.10.50',
                    'port': 22,
                    'protocol': 'SSH',
                    'path': ['FW-04', 'FW-01'],
                    'expected': 'allow'
                }
            ]
            
            # 랜덤하게 시나리오 선택
            scenario = secrets.choice(scenarios)
        
        # 경로 생성
        path = []
        current_src = scenario['source']  # 시작 IP
        
        for i, fw_id in enumerate(scenario['path']):
            fw = firewalls[fw_id]
            
            # 해당 방화벽의 정책 중 매칭되는 것 찾기
            matching_policy = self._find_matching_policy(
                fw['policies'], 
                current_src,  # 현재 소스 IP 사용
                scenario['destination'],
                scenario['port'],
                scenario['protocol']
            )
            
            if not matching_policy:
                # 기본 정책 (암시적 거부)
                matching_policy = {
                    'id': 999,
                    'name': 'Implicit_Deny',
                    'action': 'deny'
                }
            
            # 정책 정보 생성
            policy_id = matching_policy['id']
            action = matching_policy['action']
            
            # 다음 홉의 목적지 IP 결정
            if i == len(scenario['path']) - 1:
                # 마지막 홉은 최종 목적지
                next_dst = scenario['destination']
            else:
                # 중간 홉은 다음 방화벽의 IP
                next_fw = firewalls[scenario['path'][i + 1]]
                next_dst = next_fw['ip']
            
            # 상세 정책 정보 (실제 매칭된 정책 정보 사용)
            policy = {
                'id': policy_id,
                'name': matching_policy.get('name', f'Policy_{policy_id:03d}'),
                'hostname': matching_policy.get('hostname', fw['name']),
                'action': action,
                'status': 'enable',
                'srcintf': [{'name': matching_policy.get('srcintf', 'any')}],
                'dstintf': [{'name': matching_policy.get('dstintf', 'any')}],
                'srcaddr': [{'name': self._get_address_object_name(matching_policy.get('source', 'any'))}],
                'dstaddr': [{'name': self._get_address_object_name(matching_policy.get('destination', 'any'))}],
                'service': [{'name': matching_policy.get('service', scenario['protocol'])}],
                'schedule': 'always',
                'nat': matching_policy.get('nat', 'disable'),
                'logtraffic': matching_policy.get('logtraffic', 'all'),
                'ips-sensor': 'default' if action == 'allow' else None,
                'comments': matching_policy.get('comments', matching_policy.get('description', ''))
            }
            
            hop = {
                'firewall_id': fw_id,
                'firewall_name': fw['name'],
                'firewall_location': fw['location'],
                'src_ip': current_src,
                'dst_ip': next_dst,
                'policy_id': policy_id,
                'policy': policy,
                'action': action,
                'interface_in': f'port{secrets.randbelow(3) + 1}',
                'interface_out': f'port{secrets.randbelow(3) + 1}',
                'latency': random.uniform(0.1, 5.0)
            }
            path.append(hop)
            
            # 차단된 경우 더 이상 진행하지 않음
            if action == 'deny':
                break
            
            # 다음 홉의 소스 IP 설정
            current_src = next_dst
        
        # 최종 허용 여부 결정
        denied_hop = None
        allowed = True
        for hop in path:
            if hop['action'] == 'deny':
                allowed = False
                denied_hop = hop
                break
        
        result = {
            'path': path,
            'allowed': allowed,
            'final_destination': scenario['destination'],
            'blocked_by': {
                'firewall': denied_hop['firewall_name'],
                'policy_id': denied_hop['policy_id'],
                'policy_name': denied_hop['policy']['name'],
                'reason': f"Traffic denied by policy {denied_hop['policy_id']}"
            } if denied_hop else None,
            'analysis_summary': {
                'source_ip': scenario['source'],
                'destination_ip': scenario['destination'],
                'total_hops': len(path),
                'total_latency': sum(h['latency'] for h in path),
                'protocol': scenario['protocol'],
                'port': scenario['port'],
                'analysis_time': datetime.now().isoformat(),
                'scenario_description': self._get_scenario_description(scenario)
            }
        }
        
        return result
    
    def _get_fw01_policies(self):
        """본사 방화벽(FW-01) 정책 정의"""
        return [
            {
                'id': 101,
                'name': 'LAN-to-DMZ-WebServices',
                'hostname': 'FortiGate-HQ-01',
                'source': '192.168.0.0/16',
                'destination': '172.16.10.0/24',
                'service': 'HTTPS',
                'port': 443,
                'action': 'allow',
                'srcintf': 'internal',
                'dstintf': 'dmz',
                'nat': 'disable',
                'logtraffic': 'all',
                'comments': 'Allow internal users to access DMZ web servers',
                'description': '내부 사용자의 DMZ 웹서버 접근 허용'
            },
            {
                'id': 102,
                'name': 'LAN-to-WAN-Internet',
                'hostname': 'FortiGate-HQ-01',
                'source': '192.168.0.0/16',
                'destination': '0.0.0.0/0',
                'service': 'HTTP/HTTPS',
                'port': [80, 443],
                'action': 'allow',
                'srcintf': 'internal',
                'dstintf': 'wan1',
                'nat': 'enable',
                'logtraffic': 'utm',
                'comments': 'Allow internal users to access Internet with NAT',
                'description': '내부 사용자의 인터넷 접근 허용'
            },
            {
                'id': 103,
                'name': 'Branch-to-LAN-Management',
                'hostname': 'FortiGate-HQ-01',
                'source': '10.10.0.0/16',
                'destination': '192.168.0.0/16',
                'service': 'SSH/RDP',
                'port': [22, 3389],
                'action': 'allow',
                'srcintf': 'vpn',
                'dstintf': 'internal',
                'nat': 'disable',
                'logtraffic': 'all',
                'comments': 'Allow branch office to access HQ systems via VPN',
                'description': '지사에서 본사 내부 시스템 접근 허용'
            },
            {
                'id': 199,
                'name': 'Block-DMZ-to-LAN',
                'hostname': 'FortiGate-HQ-01',
                'source': '172.16.0.0/16',
                'destination': '192.168.0.0/16',
                'service': 'ALL',
                'port': 'ALL',
                'action': 'deny',
                'srcintf': 'dmz',
                'dstintf': 'internal',
                'logtraffic': 'all',
                'comments': 'Security policy - Block all DMZ to Internal traffic',
                'description': 'DMZ에서 내부망 접근 차단'
            }
        ]
    
    def _get_fw02_policies(self):
        """DMZ 방화벽(FW-02) 정책 정의"""
        return [
            {
                'id': 201,
                'name': 'WAN-to-DMZ-PublicWeb',
                'hostname': 'FortiGate-DMZ-01',
                'source': '0.0.0.0/0',
                'destination': '172.16.10.80/32',
                'service': 'HTTPS',
                'port': 443,
                'action': 'allow',
                'srcintf': 'wan1',
                'dstintf': 'dmz',
                'nat': 'enable',
                'logtraffic': 'all',
                'comments': 'Allow public access to web server with virtual IP',
                'description': '외부에서 공개 웹서버 접근 허용'
            },
            {
                'id': 202,
                'name': 'LAN-to-DMZ-Management',
                'hostname': 'FortiGate-DMZ-01',
                'source': '192.168.0.0/16',
                'destination': '172.16.0.0/16',
                'service': 'HTTPS/SSH',
                'port': [443, 22],
                'action': 'allow',
                'srcintf': 'internal',
                'dstintf': 'dmz',
                'nat': 'disable',
                'logtraffic': 'utm',
                'comments': 'Allow internal admins to manage DMZ servers',
                'description': '내부에서 DMZ 서비스 관리'
            },
            {
                'id': 203,
                'name': 'DMZ-to-WAN-Updates',
                'hostname': 'FortiGate-DMZ-01',
                'source': '172.16.0.0/16',
                'destination': '0.0.0.0/0',
                'service': 'HTTP/HTTPS',
                'port': [80, 443],
                'action': 'allow',
                'srcintf': 'dmz',
                'dstintf': 'wan1',
                'nat': 'enable',
                'logtraffic': 'utm',
                'comments': 'Allow DMZ servers to download updates',
                'description': 'DMZ 서버의 업데이트 허용'
            },
            {
                'id': 298,
                'name': 'Block-DMZ-to-Internal',
                'hostname': 'FortiGate-DMZ-01',
                'source': '172.16.0.0/16',
                'destination': '192.168.0.0/16',
                'service': 'ALL',
                'port': 'ALL',
                'action': 'deny',
                'srcintf': 'dmz',
                'dstintf': 'internal',
                'logtraffic': 'all',
                'comments': 'Security policy - Block all DMZ to Internal traffic',
                'description': 'DMZ에서 내부망 접근 차단'
            }
        ]
    
    def _get_fw03_policies(self):
        """인터넷 엣지 방화벽(FW-03) 정책 정의"""
        return [
            {
                'id': 301,
                'name': 'Internet-to-DMZ-Services',
                'hostname': 'FortiGate-Edge-01',
                'source': '0.0.0.0/0',
                'destination': '172.16.10.0/24',
                'service': 'HTTPS',
                'port': 443,
                'action': 'allow',
                'srcintf': 'wan1',
                'dstintf': 'dmz',
                'nat': 'enable',
                'logtraffic': 'all',
                'comments': 'Allow Internet access to DMZ public services',
                'description': '인터넷에서 DMZ 공개 서비스 접근'
            },
            {
                'id': 302,
                'name': 'LAN-to-Internet-Outbound',
                'hostname': 'FortiGate-Edge-01',
                'source': '192.168.0.0/16',
                'destination': '0.0.0.0/0',
                'service': 'ALL',
                'port': 'ALL',
                'action': 'allow',
                'srcintf': 'internal',
                'dstintf': 'wan1',
                'nat': 'enable',
                'logtraffic': 'utm',
                'comments': 'Allow internal users to access Internet with NAT and UTM',
                'description': '내부 사용자의 인터넷 접근 (NAT)'
            },
            {
                'id': 397,
                'name': 'Block-Internet-to-Internal',
                'hostname': 'FortiGate-Edge-01',
                'source': '0.0.0.0/0',
                'destination': '192.168.0.0/16',
                'service': 'ALL',
                'port': 'ALL',
                'action': 'deny',
                'srcintf': 'wan1',
                'dstintf': 'internal',
                'logtraffic': 'all',
                'comments': 'Security policy - Block all direct Internet to Internal traffic',
                'description': '인터넷에서 내부망 직접 접근 차단'
            }
        ]
    
    def _get_fw04_policies(self):
        """지사 방화벽(FW-04) 정책 정의"""
        return [
            {
                'id': 401,
                'name': 'Branch-to-HQ-VPN',
                'hostname': 'FortiGate-Branch-01',
                'source': '10.10.0.0/16',
                'destination': '192.168.0.0/16',
                'service': 'Corporate_Services',
                'port': [22, 3389, 443],
                'action': 'allow',
                'srcintf': 'internal',
                'dstintf': 'vpn',
                'nat': 'disable',
                'logtraffic': 'all',
                'comments': 'Allow branch office to access HQ resources via IPSec VPN',
                'description': '지사에서 본사 시스템 접근'
            },
            {
                'id': 402,
                'name': 'Branch-to-Internet-Web',
                'hostname': 'FortiGate-Branch-01',
                'source': '10.10.0.0/16',
                'destination': '0.0.0.0/0',
                'service': 'Web_Browsing',
                'port': [80, 443],
                'action': 'allow',
                'srcintf': 'internal',
                'dstintf': 'wan1',
                'nat': 'enable',
                'logtraffic': 'utm',
                'comments': 'Allow branch users to browse Internet with UTM protection',
                'description': '지사 인터넷 접근'
            }
        ]
    
    def _find_matching_policy(self, policies, src_ip, dst_ip, port, protocol):
        """주어진 트래픽에 매칭되는 정책 찾기"""
        import ipaddress
        
        for policy in policies:
            # IP 주소 매칭 확인
            try:
                src_addr = ipaddress.ip_address(src_ip)
                dst_addr = ipaddress.ip_address(dst_ip)
                
                # 소스 IP 확인
                if policy['source'] != '0.0.0.0/0':
                    if src_addr not in ipaddress.ip_network(policy['source']):
                        continue
                
                # 목적지 IP 확인
                if policy['destination'] != '0.0.0.0/0':
                    if dst_addr not in ipaddress.ip_network(policy['destination']):
                        continue
                
                # 포트 확인
                if policy['port'] != 'ALL':
                    if isinstance(policy['port'], list):
                        if port not in policy['port']:
                            continue
                    else:
                        if port != policy['port']:
                            continue
                
                # 매칭된 정책 반환
                return policy
                
            except:
                continue
        
        return None
    
    def _create_scenario_from_input(self, src_ip, dst_ip, port, protocol):
        """사용자 입력으로부터 시나리오 생성"""
        # IP 주소로 존 판별
        src_zone = self._get_zone_from_ip(src_ip)
        dst_zone = self._get_zone_from_ip(dst_ip)
        
        # 경로 결정 (간단한 라우팅 로직)
        path = []
        
        # 출발지 존에 따른 첫 번째 방화벽
        if src_zone == 'internal':
            path.append('FW-01')
        elif src_zone == 'dmz':
            path.append('FW-02')
        elif src_zone == 'external':
            path.append('FW-03')
        elif src_zone == 'branch':
            path.append('FW-04')
        else:
            # 알 수 없는 존은 기본적으로 엣지 방화벽 통과
            path.append('FW-03')
        
        # 목적지 존에 따른 추가 방화벽
        if dst_zone != src_zone:
            if dst_zone == 'internal':
                if 'FW-01' not in path:
                    path.append('FW-01')
            elif dst_zone == 'dmz':
                if 'FW-02' not in path:
                    path.append('FW-02')
            elif dst_zone == 'external':
                if 'FW-03' not in path:
                    path.append('FW-03')
            elif dst_zone == 'branch':
                if 'FW-04' not in path:
                    path.append('FW-04')
        
        # 프로토콜 매핑
        protocol_map = {
            'tcp': 'TCP',
            'udp': 'UDP',
            'http': 'HTTP',
            'https': 'HTTPS',
            'ssh': 'SSH',
            'ftp': 'FTP',
            'mysql': 'MySQL'
        }
        
        return {
            'source': src_ip,
            'destination': dst_ip,
            'port': int(port) if isinstance(port, str) else port,
            'protocol': protocol_map.get(protocol.lower(), protocol.upper()),
            'path': path,
            'expected': 'allow'  # 실제 정책에 따라 결정됨
        }
    
    def _get_zone_from_ip(self, ip_str):
        """IP 주소로부터 존 판별"""
        try:
            ip = ipaddress.ip_address(ip_str)
            
            # 내부망
            if ip in ipaddress.ip_network('192.168.0.0/16'):
                return 'internal'
            # DMZ
            elif ip in ipaddress.ip_network('172.16.0.0/16'):
                return 'dmz'
            # 지사
            elif ip in ipaddress.ip_network('10.10.0.0/16'):
                return 'branch'
            # 나머지는 외부
            else:
                return 'external'
        except:
            return 'external'
    
    def _get_address_object_name(self, address):
        """주소를 FortiGate 주소 객체 이름으로 변환"""
        if address == '0.0.0.0/0':
            return 'all'
        elif address == '192.168.0.0/16':
            return 'Internal_Network'
        elif address == '172.16.0.0/16':
            return 'DMZ_Network'
        elif address == '172.16.10.0/24':
            return 'DMZ_Web_Subnet'
        elif address == '172.16.10.80/32':
            return 'Web_Server_01'
        elif address == '10.10.0.0/16':
            return 'Branch_Network'
        elif address == '192.168.30.100/32':
            return 'Internal_DB_Server'
        else:
            # IP 주소를 간단한 이름으로 변환
            if '/' in address:
                ip_part = address.split('/')[0]
                return f'Host_{ip_part.replace(".", "_")}'
            return address
    
    def _get_scenario_description(self, scenario):
        """시나리오 설명 생성"""
        descriptions = {
            '192.168.10.100': '본사 직원 PC',
            '172.16.10.80': 'DMZ 웹서버',
            '8.8.8.8': '외부 인터넷(Google DNS)',
            '1.1.1.1': '외부 인터넷(Cloudflare DNS)',
            '192.168.30.100': '내부 데이터베이스 서버',
            '10.10.20.100': '지사 직원 PC',
            '192.168.10.50': '본사 업무 서버'
        }
        
        src_desc = descriptions.get(scenario['source'], scenario['source'])
        dst_desc = descriptions.get(scenario['destination'], scenario['destination'])
        
        return f"{src_desc}에서 {dst_desc}로 {scenario['protocol']} 접속 (포트 {scenario['port']})"
    
    def generate_packet_data(self, count=100):
        """패킷 캡처 데이터 생성"""
        packets = []
        base_time = time.time()
        
        for i in range(count):
            protocol = secrets.choice(self.protocols)
            packet = {
                'id': i + 1,
                'timestamp': base_time + i * random.uniform(0.001, 0.1),
                'src_ip': self.generate_ip(),
                'dst_ip': self.generate_ip(),
                'src_port': secrets.randbelow(64511) + 1024,  # 1024-65535
                'dst_port': secrets.choice([80, 443, 22, 25, 53, 3389, 8080]),
                'protocol': protocol,
                'length': secrets.randbelow(1460) + 40,  # 40-1500
                'info': self._generate_packet_info(protocol),
                'flags': self._generate_tcp_flags() if protocol == 'TCP' else '',
                'ttl': secrets.randbelow(254) + 1  # 1-255
            }
            packets.append(packet)
        
        return packets
    
    def _generate_packet_info(self, protocol):
        """프로토콜별 패킷 정보 생성"""
        if protocol == 'HTTP':
            return secrets.choice(['GET /', 'POST /api/data', 'HTTP/1.1 200 OK'])
        elif protocol == 'HTTPS':
            return 'TLS 1.2 Application Data'
        elif protocol == 'DNS':
            return f'Standard query A {secrets.choice(["www.example.com", "api.service.com", "mail.domain.com"])}'
        elif protocol == 'SSH':
            return 'SSH-2.0 Protocol'
        elif protocol == 'TCP':
            return secrets.choice(['ACK', 'SYN', 'FIN', 'RST'])
        else:
            return f'{protocol} Data'
    
    def _generate_tcp_flags(self):
        """TCP 플래그 생성"""
        flags = []
        if secrets.SystemRandom().random() > 0.5:
            flags.append('ACK')
        if secrets.SystemRandom().random() > 0.8:
            flags.append('SYN')
        if secrets.SystemRandom().random() > 0.9:
            flags.append('FIN')
        if secrets.SystemRandom().random() > 0.95:
            flags.append('RST')
        return ' '.join(flags) if flags else 'ACK'
    
    
    def generate_network_topology(self):
        """네트워크 토폴로지 데이터 생성"""
        # 노드 생성
        nodes = []
        node_count = secrets.randbelow(10) + 10  # 10-20
        
        for i in range(node_count):
            node_type = secrets.choice(self.device_types)
            node = {
                'id': f'node_{i+1}',
                'label': f'{node_type.upper()}-{i+1:02d}',
                'type': node_type,
                'x': secrets.randbelow(700) + 50,  # 50-750
                'y': secrets.randbelow(500) + 50,  # 50-550
                'zone': secrets.choice(self.zones),
                'status': secrets.choice(['online', 'online', 'online', 'offline'])
            }
            nodes.append(node)
        
        # 링크 생성 (연결된 그래프 보장)
        links = []
        # 먼저 모든 노드가 연결되도록 스패닝 트리 생성
        for i in range(1, node_count):
            source_idx = secrets.randbelow(i)
            link = {
                'id': f'link_{len(links)+1}',
                'source': nodes[source_idx]['id'],
                'target': nodes[i]['id'],
                'bandwidth': secrets.randbelow(9900) + 100,  # 100-10000 Mbps
                'utilization': random.uniform(10, 90),  # percentage
                'status': secrets.choice(['active', 'active', 'inactive'])
            }
            links.append(link)
        
        # 추가 링크 생성
        additional_links = secrets.randbelow(node_count // 2)
        for _ in range(additional_links):
            source_idx = secrets.randbelow(node_count)
            target_idx = secrets.randbelow(node_count)
            if source_idx != target_idx:
                link = {
                    'id': f'link_{len(links)+1}',
                    'source': nodes[source_idx]['id'],
                    'target': nodes[target_idx]['id'],
                    'bandwidth': secrets.randbelow(9900) + 100,
                    'utilization': random.uniform(10, 90),
                    'status': secrets.choice(['active', 'active', 'inactive'])
                }
                links.append(link)
        
        return {
            'nodes': nodes,
            'links': links,
            'generated_at': datetime.now().isoformat()
        }
    
    def generate_security_events(self, count=20):
        """보안 이벤트 생성"""
        event_types = ['critical', 'warning', 'info', 'error']
        event_sources = ['FortiGate-01', 'FortiGate-02', 'FortiGate-03', 'IPS Sensor', 'Web Filter', 'AV Scanner']
        event_messages = [
            'Intrusion attempt detected from {ip}',
            'Malware blocked: {malware}',
            'Suspicious traffic pattern detected',
            'Failed authentication attempt from {ip}',
            'DDoS attack detected and mitigated',
            'Policy violation: Unauthorized access attempt',
            'VPN connection established from {ip}',
            'System resource usage high: CPU {cpu}%',
            'Firewall policy {policy} triggered',
            'Web category blocked: {category}',
            'SSL inspection certificate warning',
            'FortiSandbox analysis completed',
            'Bandwidth limit exceeded on interface {interface}',
            'HA failover event detected',
            'Configuration backup completed successfully'
        ]
        
        events = []
        base_time = datetime.now()
        
        for i in range(count):
            event_type = secrets.choice(event_types)
            source = secrets.choice(event_sources)
            message_template = secrets.choice(event_messages)
            
            # 메시지 변수 치환
            message = message_template.format(
                ip=self.generate_ip(),
                malware=f'Trojan.{secrets.choice(["Win32", "Linux", "Android"])}.{secrets.randbelow(9000) + 1000}',
                cpu=secrets.randbelow(25) + 70,  # 70-95
                policy=f'Policy_{secrets.randbelow(99) + 1}',
                category=secrets.choice(['Social Media', 'Gambling', 'Adult Content', 'P2P', 'Streaming']),
                interface=f'port{secrets.randbelow(3) + 1}'
            )
            
            event = {
                'id': f'event_{i+1}',
                'type': event_type,
                'source': source,
                'message': message,
                'timestamp': (base_time - timedelta(minutes=secrets.randbelow(1440))).isoformat(),
                'severity': secrets.choice(['low', 'medium', 'high', 'critical']),
                'status': secrets.choice(['new', 'acknowledged', 'resolved']),
                'user': secrets.choice(['admin', 'security_analyst', 'network_admin', 'system']),
                'src_ip': self.generate_ip() if secrets.choice([True, False]) else None,
                'dst_ip': self.generate_ip() if secrets.choice([True, False]) else None,
                'count': secrets.randbelow(99) + 1
            }
            events.append(event)
        
        # 시간순 정렬 (최신 순)
        events.sort(key=lambda x: x['timestamp'], reverse=True)
        return events
    
    def generate_dashboard_stats(self):
        """대시보드 통계 데이터 생성"""
        device_count = secrets.randbelow(20) + 40  # 40-60
        online_count = min(secrets.randbelow(20) + 35, device_count)  # 35-55, max device_count
        
        return {
            'total_devices': device_count,
            'online_devices': online_count,
            'offline_devices': device_count - online_count,
            'total_sessions': secrets.randbelow(1500) + 500,  # 500-2000
            'active_policies': secrets.randbelow(70) + 80,  # 80-150
            'total_bandwidth_in': round(random.uniform(1.5, 4.2), 1),
            'total_bandwidth_out': round(random.uniform(0.8, 2.5), 1),
            'avg_cpu_usage': secrets.randbelow(40) + 45,  # 45-85%
            'avg_memory_usage': secrets.randbelow(30) + 60,  # 60-90%
            'threat_count': secrets.randbelow(40) + 10,  # 10-50
            'alert_count': secrets.randbelow(12) + 3,  # 3-15
            'last_update': datetime.now().isoformat()
        }
    
    def generate_cpu_usage(self):
        """CPU 사용률 데이터 생성"""
        return {
            'current': secrets.randbelow(60) + 20,  # 20-80%
            'average': secrets.randbelow(55) + 15,  # 15-70%
            'peak': secrets.randbelow(35) + 60,  # 60-95%
            'history': [secrets.randbelow(80) + 10 for _ in range(24)]  # 10-90%
        }
    
    def generate_memory_usage(self):
        """메모리 사용률 데이터 생성"""
        return {
            'current': secrets.randbelow(45) + 30,  # 30-75%
            'total': 16384,  # MB
            'used': secrets.randbelow(8000) + 4000,  # 4000-12000
            'free': secrets.randbelow(6000) + 2000,  # 2000-8000
            'history': [secrets.randbelow(60) + 20 for _ in range(24)]  # 20-80%
        }
    
    def generate_network_traffic(self):
        """네트워크 트래픽 데이터 생성"""
        return {
            'incoming': secrets.randbelow(900) + 100,  # 100-1000 Mbps
            'outgoing': secrets.randbelow(750) + 50,  # 50-800
            'total_sessions': secrets.randbelow(9000) + 1000,  # 1000-10000
            'active_sessions': secrets.randbelow(1900) + 100,  # 100-2000
            'history': {
                'incoming': [secrets.randbelow(1150) + 50 for _ in range(24)],  # 50-1200
                'outgoing': [secrets.randbelow(870) + 30 for _ in range(24)]  # 30-900
            }
        }
    
    def generate_active_sessions(self):
        """활성 세션 데이터 생성"""
        return {
            'total': secrets.randbelow(4000) + 1000,  # 1000-5000
            'tcp': secrets.randbelow(2500) + 500,  # 500-3000
            'udp': secrets.randbelow(1300) + 200,  # 200-1500
            'http': secrets.randbelow(700) + 100,  # 100-800
            'https': secrets.randbelow(1050) + 150,  # 150-1200
            'by_zone': {
                'internal': secrets.randbelow(1100) + 400,  # 400-1500
                'external': secrets.randbelow(600) + 200,  # 200-800
                'dmz': secrets.randbelow(400) + 100,  # 100-500
                'guest': secrets.randbelow(250) + 50  # 50-300
            }
        }
    
    def generate_threat_count(self):
        """위협 감지 데이터 생성"""
        return {
            'today': secrets.randbelow(90) + 10,  # 10-100
            'this_week': secrets.randbelow(450) + 50,  # 50-500
            'this_month': secrets.randbelow(1800) + 200,  # 200-2000
            'by_type': {
                'virus': secrets.randbelow(45) + 5,  # 5-50
                'malware': secrets.randbelow(27) + 3,  # 3-30
                'intrusion': secrets.randbelow(70) + 10,  # 10-80
                'spam': secrets.randbelow(180) + 20,  # 20-200
                'phishing': secrets.randbelow(18) + 2  # 2-20
            },
            'blocked': secrets.randbelow(4) + 95,  # 95-99%
            'quarantined': secrets.randbelow(4) + 1  # 1-5%
        }
    
    def generate_alerts(self, count=5):
        """알림 데이터 생성"""
        alerts = []
        alert_types = ['critical', 'warning', 'info']
        alert_messages = [
            'High CPU usage detected',
            'Memory usage above threshold',
            'Network traffic spike detected', 
            'Suspicious connection attempt',
            'Policy violation detected',
            'System update available',
            'Certificate expiring soon',
            'Backup completed successfully'
        ]
        
        for i in range(count):
            alerts.append({
                'id': f'alert_{i+1}',
                'type': secrets.choice(alert_types),
                'message': secrets.choice(alert_messages),
                'timestamp': (datetime.now() - timedelta(hours=secrets.randbelow(24))).isoformat(),
                'source': f'FW-{secrets.randbelow(3) + 1:02d}',
                'acknowledged': secrets.choice([True, False])
            })
        
        return alerts
    
    def generate_events(self, count=10):
        """이벤트 데이터 생성"""
        events = []
        event_types = ['login', 'logout', 'policy_match', 'connection', 'error']
        
        for i in range(count):
            events.append({
                'id': f'event_{i+1}',
                'type': secrets.choice(event_types),
                'description': f'Event {i+1} description',
                'timestamp': (datetime.now() - timedelta(minutes=secrets.randbelow(1440))).isoformat(),
                'source_ip': self.generate_ip(),
                'destination_ip': self.generate_ip(),
                'user': f'user{secrets.randbelow(99) + 1}',
                'severity': secrets.choice(['low', 'medium', 'high'])
            })
        
        return events
    
    def generate_top_threats(self, count=5):
        """상위 위협 데이터 생성"""
        threats = []
        threat_names = [
            'Trojan.Win32.Agent',
            'Backdoor.Generic',
            'Malware.Suspicious',
            'Adware.BrowserModifier',
            'PUP.Optional.Bundle'
        ]
        
        for i, threat in enumerate(threat_names[:count]):
            threats.append({
                'name': threat,
                'count': secrets.randbelow(190) + 10,  # 10-200
                'severity': secrets.choice(['low', 'medium', 'high', 'critical']),
                'first_seen': (datetime.now() - timedelta(days=secrets.randbelow(29) + 1)).isoformat(),
                'last_seen': (datetime.now() - timedelta(hours=secrets.randbelow(23) + 1)).isoformat()
            })
        
        return threats
    
    def generate_bandwidth_usage(self):
        """대역폭 사용량 데이터 생성"""
        return {
            'total_capacity': 1000,  # Mbps
            'current_usage': secrets.randbelow(700) + 100,  # 100-800
            'peak_usage': secrets.randbelow(350) + 600,  # 600-950
            'average_usage': secrets.randbelow(400) + 200,  # 200-600
            'by_interface': {
                'wan1': secrets.randbelow(300) + 100,  # 100-400
                'wan2': secrets.randbelow(250) + 50,  # 50-300
                'internal': secrets.randbelow(400) + 200,  # 200-600
                'dmz': secrets.randbelow(150) + 50  # 50-200
            },
            'history': [secrets.randbelow(800) + 100 for _ in range(24)]  # 100-900
        }

# 싱글톤 인스턴스 생성
dummy_generator = DummyDataGenerator()