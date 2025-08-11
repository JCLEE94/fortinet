# 하드코딩 제거 리팩토링 보고서

## 개요
총 71 개 파일에서 425 개의 하드코딩된 값을 발견했습니다.

## 카테고리별 분석
- ip_addresses: 229개
- ports: 103개
- urls: 55개
- credentials: 19개
- paths: 19개

## 파일별 상세 내역

### /home/jclee/app/fortinet/src/analysis/analyzer.py
- Line 942 (ip_addresses): `ipaddress.ip_network("10.0.0.0/8"),`
- Line 943 (ip_addresses): `ipaddress.ip_network("172.16.0.0/12"),`
- Line 944 (ip_addresses): `ipaddress.ip_network("192.168.0.0/16")`
- Line 949 (ip_addresses): `ipaddress.ip_network("10.10.0.0/16"),     # 가정: 10.10.x.x 대역은 DMZ`
- Line 950 (ip_addresses): `ipaddress.ip_network("172.16.10.0/24")    # 가정: 172.16.10.x 대역은 DMZ`
- Line 1645 (ip_addresses): `ipaddress.ip_network("10.0.0.0/8"),`
- Line 1646 (ip_addresses): `ipaddress.ip_network("172.16.0.0/12"),`
- Line 1647 (ip_addresses): `ipaddress.ip_network("192.168.0.0/16")`
- Line 1652 (ip_addresses): `ipaddress.ip_network("10.10.0.0/16"),     # 가정: 10.10.x.x 대역은 DMZ`
- Line 1653 (ip_addresses): `ipaddress.ip_network("172.16.10.0/24")    # 가정: 172.16.10.x 대역은 DMZ`
- Line 1663 (ip_addresses): `if ip_obj in ipaddress.ip_network("10.0.0.0/8"):`
- Line 1665 (ip_addresses): `elif ip_obj in ipaddress.ip_network("172.16.0.0/12"):`
- Line 1667 (ip_addresses): `elif ip_obj in ipaddress.ip_network("192.168.0.0/16"):`

### /home/jclee/app/fortinet/src/analysis/fixed_path_analyzer.py
- Line 18 (ip_addresses): `'internal': '192.168.0.0/16',`
- Line 19 (ip_addresses): `'dmz': '172.16.0.0/16',`
- Line 21 (ip_addresses): `'guest': '10.10.0.0/16',`
- Line 22 (ip_addresses): `'management': '10.100.0.0/24'`
- Line 32 (ip_addresses): `'source_net': '192.168.0.0/16',`
- Line 33 (ip_addresses): `'dest_net': '172.16.10.0/24',`
- Line 43 (ip_addresses): `'source_net': '192.168.10.0/24',`
- Line 44 (ip_addresses): `'dest_net': '172.16.20.0/24',`
- Line 54 (ip_addresses): `'source_net': '172.16.0.0/16',`
- Line 66 (ip_addresses): `'dest_net': '172.16.10.100/32',`
- Line 76 (ip_addresses): `'source_net': '192.168.0.0/16',`
- Line 87 (ip_addresses): `'source_net': '10.10.0.0/16',`
- Line 88 (ip_addresses): `'dest_net': '192.168.0.0/16',`
- Line 98 (ip_addresses): `'source_net': '10.100.0.0/24',`
- Line 99 (ip_addresses): `'dest_net': '192.168.0.0/16',`
- Line 120 (ip_addresses): `'192.168.0.0/16': {'gateway': '192.168.1.1', 'interface': 'internal', 'metric': 1},`
- Line 121 (ip_addresses): `'172.16.0.0/16': {'gateway': '172.16.1.1', 'interface': 'dmz', 'metric': 1},`
- Line 122 (ip_addresses): `'10.10.0.0/16': {'gateway': '10.10.1.1', 'interface': 'guest', 'metric': 1},`
- Line 123 (ip_addresses): `'10.100.0.0/24': {'gateway': '10.100.0.1', 'interface': 'management', 'metric': 1},`
- Line 201 (ip_addresses): `self.routing_table.get('192.168.0.0/16') or \`
- Line 235 (ports): `def analyze_path(self, src_ip, dst_ip, port=80, protocol='tcp'):`
- Line 248 (ports): `'firewall_name': f'FW-{i+1:02d}',`

### /home/jclee/app/fortinet/src/api/clients/faz_client.py
- Line 72 (urls): `self.base_url = f"https://{self.host}{API_VERSIONS['fortianalyzer']}" if self.host else ""`
- Line 286 (ip_addresses): `'ip': '192.168.1.1',`
- Line 292 (ports): `'last_seen': '2025-05-13 05:00:00',`
- Line 298 (ip_addresses): `'ip': '192.168.2.1',`
- Line 304 (ports): `'last_seen': '2025-05-13 05:00:00',`
- Line 312 (credentials): `Get list of administrative domains (ADOMs)`

### /home/jclee/app/fortinet/src/api/clients/fortigate_api_client.py
- Line 29 (ports): `DEFAULT_PORT = 443`

### /home/jclee/app/fortinet/src/api/clients/fortimanager_api_client.py
- Line 58 (credentials): `self.adom = 'root'  # Default administrative domain`

### /home/jclee/app/fortinet/src/api/integration/api_data_collector.py
- Line 226 (ip_addresses): `'source': '192.168.1.100',`
- Line 227 (ip_addresses): `'destination': '10.0.0.5',`
- Line 233 (ip_addresses): `'source': '172.16.0.50',`

### /home/jclee/app/fortinet/src/automation/auto_recovery.py
- Line 299 (ip_addresses): `r = redis.Redis(host='localhost', port=6379, db=0)`
- Line 299 (ports): `r = redis.Redis(host='localhost', port=6379, db=0)`
- Line 454 (urls): `response = requests.get('http://8.8.8.8', timeout=5)`
- Line 462 (ip_addresses): `response = requests.get(f'http://localhost:{APP_CONFIG["web_port"]}/api/settings', timeout=5)`
- Line 462 (urls): `response = requests.get(f'http://localhost:{APP_CONFIG["web_port"]}/api/settings', timeout=5)`
- Line 476 (ip_addresses): `response = requests.get(f'http://localhost:{APP_CONFIG["web_port"]}/api/settings', timeout=10)`
- Line 476 (urls): `response = requests.get(f'http://localhost:{APP_CONFIG["web_port"]}/api/settings', timeout=10)`
- Line 547 (urls): `response = requests.get('http://8.8.8.8', timeout=5)`

### /home/jclee/app/fortinet/src/automation/engine.py
- Line 321 (ip_addresses): `{"ip": "192.168.1.100", "traffic": "23.4 GB"},`
- Line 322 (ip_addresses): `{"ip": "192.168.1.150", "traffic": "18.7 GB"}`

### /home/jclee/app/fortinet/src/config/config_helper.py
- Line 30 (ip_addresses): `return NETWORK_RANGES.get(network_type, '192.168.0.0/16')`
- Line 35 (ip_addresses): `return GATEWAY_IPS.get(network_type, '192.168.1.1')`
- Line 40 (ip_addresses): `return TEST_ADDRESSES.get(address_type, '192.168.1.100')`
- Line 60 (urls): `return f"https://{host}:{port}{api_version}"`
- Line 62 (ip_addresses): `def build_health_check_url(host: str = 'localhost', port: Optional[int] = None) -> str:`
- Line 66 (urls): `return f"http://{host}:{port}/health"`

### /home/jclee/app/fortinet/src/config/constants.py
- Line 121 (ip_addresses): `'INTERNAL': ['192.168.1.0/24', '192.168.2.0/24', '10.0.0.0/8'],`
- Line 122 (ip_addresses): `'DMZ': ['172.16.0.0/16'],`

### /home/jclee/app/fortinet/src/config/network.py
- Line 18 (ip_addresses): `'private': '10.0.0.0/8',  # 전체 사설 네트워크`
- Line 19 (ip_addresses): `'localhost': '127.0.0.0/8',`
- Line 20 (ip_addresses): `'ipv6_localhost': '::1/128'`
- Line 42 (ip_addresses): `'internal_gateway': '192.168.1.1',`
- Line 43 (ip_addresses): `'internal_dns': '192.168.1.10',`
- Line 45 (ip_addresses): `'dmz_gateway': '172.16.1.1',`
- Line 49 (ip_addresses): `'localhost': '127.0.0.1',`
- Line 50 (ip_addresses): `'ipv6_localhost': '::1',`
- Line 58 (ip_addresses): `'localhost': '127.0.0.1',`
- Line 59 (ip_addresses): `'ipv6_localhost': '::1',`

### /home/jclee/app/fortinet/src/config/paths.py
- Line 76 (paths): `'auth': '/var/log/auth.log',`
- Line 77 (paths): `'syslog': '/var/log/syslog',`
- Line 78 (paths): `'messages': '/var/log/messages',`
- Line 79 (paths): `'docker': '/var/log/docker.log',`
- Line 80 (paths): `'nginx_access': '/var/log/nginx/access.log',`
- Line 81 (paths): `'nginx_error': '/var/log/nginx/error.log'`
- Line 86 (paths): `'monitor_log': '/tmp/deployment_monitor.log',`
- Line 87 (paths): `'pipeline_log': '/tmp/pipeline_monitor.log',`
- Line 89 (paths): `'docker_socket': '/var/run/docker.sock',`
- Line 90 (paths): `'pid_file': '/var/run/fortigate-nextrade.pid'`

### /home/jclee/app/fortinet/src/config/refactored/endpoints.py
- Line 50 (credentials): `'admin': '/cmdb/system/admin',`

### /home/jclee/app/fortinet/src/config/refactored/example_refactoring.py
- Line 13 (urls): `response = requests.get('http://8.8.8.8', timeout=5)`
- Line 20 (ip_addresses): `response = requests.get('http://localhost:7777/api/settings', timeout=5)`
- Line 20 (ports): `response = requests.get('http://localhost:7777/api/settings', timeout=5)`
- Line 20 (urls): `response = requests.get('http://localhost:7777/api/settings', timeout=5)`
- Line 28 (urls): `self.base_url = "https://itsm2.nxtd.co.kr"`
- Line 33 (ip_addresses): `if ip in ipaddress.ip_network('192.168.0.0/16'):`
- Line 35 (ip_addresses): `elif ip in ipaddress.ip_network('172.16.0.0/16'):`
- Line 37 (ip_addresses): `elif ip in ipaddress.ip_network('10.10.0.0/16'):`
- Line 58 (urls): `dns_check_url = EXTERNAL_SERVICES.get('dns_check', {}).get('url', 'http://8.8.8.8')`
- Line 70 (ip_addresses): `url = f"http://localhost:{port}{endpoint}"`
- Line 70 (urls): `url = f"http://localhost:{port}{endpoint}"`
- Line 176 (credentials): `port = FORTIGATE_PORTS['admin_https']`
- Line 182 (urls): `return f"https://{host}:{port}{status_endpoint}"`

### /home/jclee/app/fortinet/src/config/refactored/network.py
- Line 37 (ip_addresses): `ipaddress.ip_network('10.0.0.0/8'),`
- Line 38 (ip_addresses): `ipaddress.ip_network('172.16.0.0/12'),`
- Line 39 (ip_addresses): `ipaddress.ip_network('192.168.0.0/16'),`
- Line 44 (ip_addresses): `'localhost': '127.0.0.1',`
- Line 45 (ip_addresses): `'localhost_v6': '::1',`

### /home/jclee/app/fortinet/src/config/refactored/paths.py
- Line 44 (paths): `'docker_socket': Path('/var/run/docker.sock'),`
- Line 46 (paths): `'auth': Path('/var/log/auth.log'),`
- Line 47 (paths): `'syslog': Path('/var/log/syslog'),`

### /home/jclee/app/fortinet/src/config/refactored/services.py
- Line 25 (urls): `'cloudflare': 'https://cdnjs.cloudflare.com',`
- Line 26 (urls): `'jsdelivr': 'https://cdn.jsdelivr.net',`
- Line 27 (urls): `'google_fonts': 'https://fonts.googleapis.com',`
- Line 28 (urls): `'gstatic': 'https://fonts.gstatic.com',`

### /home/jclee/app/fortinet/src/config/services.py
- Line 23 (urls): `'cloudflare': 'https://cdnjs.cloudflare.com',`
- Line 24 (urls): `'jsdelivr': 'https://cdn.jsdelivr.net',`
- Line 25 (urls): `'google_fonts': 'https://fonts.googleapis.com',`
- Line 26 (urls): `'gstatic': 'https://fonts.gstatic.com',`
- Line 27 (urls): `'bootstrap': 'https://stackpath.bootstrapcdn.com',`
- Line 28 (urls): `'jquery': 'https://code.jquery.com'`
- Line 38 (urls): `'https://cdnjs.cloudflare.com',`
- Line 39 (urls): `'https://cdn.jsdelivr.net',`
- Line 40 (urls): `'https://code.jquery.com',`
- Line 41 (urls): `'https://stackpath.bootstrapcdn.com'`
- Line 46 (urls): `'https://cdnjs.cloudflare.com',`
- Line 47 (urls): `'https://cdn.jsdelivr.net',`
- Line 48 (urls): `'https://fonts.googleapis.com',`
- Line 49 (urls): `'https://stackpath.bootstrapcdn.com'`
- Line 53 (urls): `'https://fonts.gstatic.com',`
- Line 54 (urls): `'https://cdnjs.cloudflare.com'`

### /home/jclee/app/fortinet/src/config/unified_settings.py
- Line 304 (urls): `print(f"🌐 웹서버: http://{self.webapp.host}:{self.webapp.port}")`

### /home/jclee/app/fortinet/src/core/auth_manager.py
- Line 281 (urls): `login_url = f"https://{host}:{port}/jsonrpc"`
- Line 370 (urls): `logout_url = f"https://{session.host}:{session.port}/jsonrpc"`
- Line 412 (ports): `return hashlib.sha256((timestamp + random_bytes.hex()).encode()).hexdigest()[:32]`

### /home/jclee/app/fortinet/src/core/base_client.py
- Line 127 (urls): `self.base_url = f"https://{self.host}:{self.port}{API_VERSIONS['fortigate']}"`
- Line 131 (urls): `self.base_url = f"https://{self.host}:{self.port}{API_VERSIONS['fortimanager']}"`
- Line 135 (urls): `self.base_url = f"https://{self.host}:{self.port}{API_VERSIONS['fortianalyzer']}"`
- Line 139 (urls): `self.base_url = f"https://{self.host}:{self.port}{API_VERSIONS['fortiweb']}"`

### /home/jclee/app/fortinet/src/fortimanager/advanced_hub.py
- Line 16 (credentials): `from .fortimanager_security_fabric import SecurityFabricIntegration`
- Line 41 (credentials): `self.security_fabric = SecurityFabricIntegration(self.api_client)`

### /home/jclee/app/fortinet/src/fortimanager/fortimanager_analytics_engine.py
- Line 382 (ports): `).hexdigest()[:16],`

### /home/jclee/app/fortinet/src/fortimanager/fortimanager_compliance_automation.py
- Line 130 (credentials): `description="Ensure default admin account is disabled or renamed",`
- Line 133 (credentials): `check_function="check_default_admin",`
- Line 134 (credentials): `remediation_function="disable_default_admin",`
- Line 181 (credentials): `description="Ensure MFA is enabled for administrative access",`

### /home/jclee/app/fortinet/src/fortimanager/fortimanager_policy_orchestrator.py
- Line 111 (urls): `"redirect-url": "https://{app_domain}",`
- Line 388 (ports): `).hexdigest()[:16]`

### /home/jclee/app/fortinet/src/fortimanager/fortimanager_security_fabric.py
- Line 90 (credentials): `class SecurityFabricIntegration:`
- Line 281 (ports): `).hexdigest()[:16],`
- Line 347 (ports): `).hexdigest()[:16],`
- Line 455 (ports): `)[:10]`
- Line 543 (ports): `).hexdigest()[:16],`

### /home/jclee/app/fortinet/src/itsm/automation_service.py
- Line 76 (urls): `return "https://itsm2.nxtd.co.kr"  # fallback`

### /home/jclee/app/fortinet/src/itsm/external_connector.py
- Line 348 (ports): `created_at=datetime.fromisoformat(ticket.get('opened_at', '').replace('Z', '+00:00')),`
- Line 374 (ports): `created_at=datetime.fromisoformat(fields.get('created', '').replace('Z', '+00:00')),`
- Line 477 (ports): `return datetime.fromisoformat(date_str.replace('Z', '+00:00'))`

### /home/jclee/app/fortinet/src/itsm/fortigate_bridge.py
- Line 35 (urls): `'base_url': 'https://itsm2.nxtd.co.kr',`
- Line 41 (ip_addresses): `{'id': 'FW-01', 'ip': '192.168.1.1', 'token': 'xxx'},`
- Line 46 (ip_addresses): `'host': '172.28.174.31',`
- Line 61 (urls): `base_url=config.get('itsm', {}).get('base_url', 'https://itsm2.nxtd.co.kr'),`

### /home/jclee/app/fortinet/src/itsm/integration.py
- Line 61 (ip_addresses): `'source_ip': '192.168.1.100',`
- Line 62 (ip_addresses): `'destination_ip': '10.0.0.50',`
- Line 122 (ip_addresses): `if ip in ipaddress.ip_network('192.168.0.0/16'):`
- Line 124 (ip_addresses): `elif ip in ipaddress.ip_network('10.0.0.0/8'):`
- Line 126 (ip_addresses): `if ip in ipaddress.ip_network('10.10.0.0/16'):`
- Line 129 (ip_addresses): `elif ip in ipaddress.ip_network('172.16.0.0/16'):`
- Line 131 (ip_addresses): `elif ip in ipaddress.ip_network('172.17.0.0/16'):`
- Line 133 (ip_addresses): `elif ip in ipaddress.ip_network('172.28.0.0/16'):`
- Line 316 (ports): `restrictions.append('업무 시간(09:00-18:00)으로 접근 시간 제한 권장')`
- Line 494 (ports): `ticket_id = f"FW-{datetime.now().strftime('%Y%m%d')}-{hash(str(ticket_data)) % 10000:04d}"`

### /home/jclee/app/fortinet/src/itsm/policy_automation.py
- Line 111 (ip_addresses): `cidr="192.168.0.0/16",`
- Line 118 (ip_addresses): `cidr="172.16.0.0/16",`
- Line 132 (ip_addresses): `cidr="10.0.0.0/16",`
- Line 139 (ip_addresses): `cidr="10.10.0.0/16",`
- Line 156 (ip_addresses): `host="192.168.1.1",`
- Line 158 (ip_addresses): `management_ip="192.168.1.1",`
- Line 164 (ip_addresses): `host="172.16.1.1",`
- Line 166 (ip_addresses): `management_ip="172.16.1.1",`
- Line 180 (ip_addresses): `host="10.10.1.1",`
- Line 182 (ip_addresses): `management_ip="10.10.1.1",`
- Line 608 (credentials): `username="admin",  # 실제로는 설정에서 가져와야 함`

### /home/jclee/app/fortinet/src/itsm/policy_mapper.py
- Line 27 (ip_addresses): `'networks': ['192.168.0.0/16', '10.0.0.0/8'],`
- Line 33 (ip_addresses): `'networks': ['172.16.0.0/16', '172.17.0.0/16'],`
- Line 45 (ip_addresses): `'networks': ['10.10.0.0/16'],`
- Line 51 (ip_addresses): `'networks': ['172.28.0.0/16'],`
- Line 81 (ip_addresses): `'ip': '192.168.1.1',`
- Line 84 (ip_addresses): `'management_ip': '172.28.174.31'`
- Line 88 (ip_addresses): `'ip': '172.16.1.1',`
- Line 91 (ip_addresses): `'management_ip': '172.28.174.32'`
- Line 98 (ip_addresses): `'management_ip': '172.28.174.33'`
- Line 102 (ip_addresses): `'ip': '10.10.1.1',`
- Line 105 (ip_addresses): `'management_ip': '172.28.174.34'`

### /home/jclee/app/fortinet/src/itsm/scraper.py
- Line 324 (ports): `'request_date': '2025-06-05 09:30:00',`
- Line 334 (ports): `'request_date': '2025-06-05 10:15:00',`
- Line 344 (ports): `'request_date': '2025-06-04 16:20:00',`
- Line 354 (ports): `'request_date': '2025-06-05 11:45:00',`
- Line 371 (ports): `'request_date': '2025-06-05 09:30:00',`
- Line 374 (ip_addresses): `'source_ip': '192.168.1.0/24',`
- Line 375 (ip_addresses): `'destination_ip': '172.16.10.100',`
- Line 390 (ports): `'request_date': '2025-06-05 10:15:00',`
- Line 393 (ip_addresses): `'source_ip': '172.16.20.0/24',`
- Line 394 (ip_addresses): `'destination_ip': '172.16.30.50',`

### /home/jclee/app/fortinet/src/mock/data_generator.py
- Line 30 (ports): `return ':'.join([f'{secrets.randbelow(256):02x}' for _ in range(6)])`
- Line 41 (ports): `'name': f'{device_type.upper()}-{i+1:02d}',`
- Line 97 (ports): `'name': f'Policy_{i+1:03d}',`
- Line 121 (ip_addresses): `'ip': '192.168.1.1',`
- Line 128 (ip_addresses): `'ip': '172.16.1.1',`
- Line 142 (ip_addresses): `'ip': '10.10.1.1',`
- Line 156 (ip_addresses): `'source': '192.168.10.100',`
- Line 157 (ip_addresses): `'destination': '172.16.10.80',`
- Line 166 (ip_addresses): `'destination': '172.16.10.80',`
- Line 174 (ip_addresses): `'source': '192.168.20.50',`
- Line 183 (ip_addresses): `'source': '172.16.10.80',`
- Line 184 (ip_addresses): `'destination': '192.168.30.100',`
- Line 192 (ip_addresses): `'source': '10.10.20.100',`
- Line 193 (ip_addresses): `'destination': '192.168.10.50',`
- Line 244 (ports): `'name': matching_policy.get('name', f'Policy_{policy_id:03d}'),`
- Line 322 (ip_addresses): `'source': '192.168.0.0/16',`
- Line 323 (ip_addresses): `'destination': '172.16.10.0/24',`
- Line 338 (ip_addresses): `'source': '192.168.0.0/16',`
- Line 354 (ip_addresses): `'source': '10.10.0.0/16',`
- Line 355 (ip_addresses): `'destination': '192.168.0.0/16',`
- Line 370 (ip_addresses): `'source': '172.16.0.0/16',`
- Line 371 (ip_addresses): `'destination': '192.168.0.0/16',`
- Line 391 (ip_addresses): `'destination': '172.16.10.80/32',`
- Line 406 (ip_addresses): `'source': '192.168.0.0/16',`
- Line 407 (ip_addresses): `'destination': '172.16.0.0/16',`
- Line 415 (credentials): `'comments': 'Allow internal admins to manage DMZ servers',`
- Line 422 (ip_addresses): `'source': '172.16.0.0/16',`
- Line 438 (ip_addresses): `'source': '172.16.0.0/16',`
- Line 439 (ip_addresses): `'destination': '192.168.0.0/16',`
- Line 459 (ip_addresses): `'destination': '172.16.10.0/24',`
- Line 474 (ip_addresses): `'source': '192.168.0.0/16',`
- Line 491 (ip_addresses): `'destination': '192.168.0.0/16',`
- Line 510 (ip_addresses): `'source': '10.10.0.0/16',`
- Line 511 (ip_addresses): `'destination': '192.168.0.0/16',`
- Line 526 (ip_addresses): `'source': '10.10.0.0/16',`
- Line 640 (ip_addresses): `if ip in ipaddress.ip_network('192.168.0.0/16'):`
- Line 643 (ip_addresses): `elif ip in ipaddress.ip_network('172.16.0.0/16'):`
- Line 646 (ip_addresses): `elif ip in ipaddress.ip_network('10.10.0.0/16'):`
- Line 658 (ip_addresses): `elif address == '192.168.0.0/16':`
- Line 660 (ip_addresses): `elif address == '172.16.0.0/16':`
- Line 662 (ip_addresses): `elif address == '172.16.10.0/24':`
- Line 664 (ip_addresses): `elif address == '172.16.10.80/32':`
- Line 666 (ip_addresses): `elif address == '10.10.0.0/16':`
- Line 668 (ip_addresses): `elif address == '192.168.30.100/32':`
- Line 680 (ip_addresses): `'192.168.10.100': '본사 직원 PC',`
- Line 681 (ip_addresses): `'172.16.10.80': 'DMZ 웹서버',`
- Line 684 (ip_addresses): `'192.168.30.100': '내부 데이터베이스 서버',`
- Line 685 (ip_addresses): `'10.10.20.100': '지사 직원 PC',`
- Line 686 (ip_addresses): `'192.168.10.50': '본사 업무 서버'`
- Line 725 (urls): `return f'Standard query A {secrets.choice(["www.example.com", "api.service.com", "mail.domain.com"])...`
- Line 757 (ports): `'label': f'{node_type.upper()}-{i+1:02d}',`
- Line 851 (credentials): `'user': secrets.choice(['admin', 'security_analyst', 'network_admin', 'system']),`
- Line 968 (ports): `'source': f'FW-{secrets.randbelow(3) + 1:02d}',`

### /home/jclee/app/fortinet/src/mock/fortigate.py
- Line 143 (ip_addresses): `('db_server', 'ipmask', '172.16.20.50/32'),`
- Line 144 (ip_addresses): `('mail_server', 'ipmask', '172.16.30.10/32')`
- Line 224 (ip_addresses): `'srcaddr': ['192.168.1.100/32'],`

### /home/jclee/app/fortinet/src/modules/device_manager.py
- Line 171 (ip_addresses): `'ip': '192.168.1.1',`
- Line 185 (ip_addresses): `'ip': '10.0.0.1',`
- Line 213 (ip_addresses): `'ip': '172.16.0.1',`
- Line 389 (ip_addresses): `'dest': '192.168.1.0/24',`
- Line 398 (ip_addresses): `'dest': '10.0.0.0/24',`
- Line 407 (ip_addresses): `'dest': '172.16.0.0/24',`
- Line 416 (ip_addresses): `'dest': '192.168.2.0/24',`
- Line 417 (ip_addresses): `'gateway': '10.0.0.254',`
- Line 516 (ip_addresses): `'ip': '192.168.1.10',`
- Line 517 (ports): `'mac': '00:11:22:33:44:55',`
- Line 526 (ip_addresses): `'ip': '192.168.1.11',`
- Line 527 (ports): `'mac': '00:11:22:33:44:66',`
- Line 536 (ip_addresses): `'ip': '10.0.0.10',`
- Line 546 (ip_addresses): `'ip': '172.16.0.10',`
- Line 547 (ports): `'mac': 'AA:BB:CC:11:22:33',`

### /home/jclee/app/fortinet/src/monitoring/collectors/system_metrics.py
- Line 324 (ports): `'high_usage_processes': processes[:10]  # 상위 10개만`

### /home/jclee/app/fortinet/src/routes/api_routes.py
- Line 662 (ports): `for event in security_events[:10]:`

### /home/jclee/app/fortinet/src/routes/fortimanager/device_routes.py
- Line 239 (ports): `'uptime': '5 days, 12:34:56',`
- Line 256 (ip_addresses): `'ip': '192.168.1.1',`
- Line 263 (ip_addresses): `'ip': '10.0.0.1',`

### /home/jclee/app/fortinet/src/routes/fortimanager_routes.py
- Line 156 (ports): `'name': f'ADDR_HOST_{i+1:03d}',`
- Line 216 (ports): `'name': f'Policy_{i+1:03d}',`
- Line 656 (ip_addresses): `{'src_ip': '192.168.1.100', 'dst_ip': '172.16.10.100', 'port': 80, 'protocol': 'tcp'},`
- Line 657 (ip_addresses): `{'src_ip': '192.168.1.100', 'dst_ip': '203.0.113.50', 'port': 443, 'protocol': 'tcp'},`
- Line 658 (ip_addresses): `{'src_ip': '10.10.1.50', 'dst_ip': '192.168.1.100', 'port': 22, 'protocol': 'tcp'},`
- Line 659 (ip_addresses): `{'src_ip': '172.16.10.100', 'dst_ip': '203.0.113.100', 'port': 80, 'protocol': 'tcp'}`
- Line 966 (ports): `'incident_id': f'THREAT-{datetime.now().strftime("%Y%m%d")}-{i+1:03d}',`
- Line 1220 (ports): `'insight_id': f'ANOMALY-{datetime.now().strftime("%Y%m%d")}-{i+1:03d}',`

### /home/jclee/app/fortinet/src/routes/itsm_api_routes.py
- Line 27 (ip_addresses): `'source_ip': '10.10.10.0/24',`
- Line 28 (ip_addresses): `'destination_ip': '192.168.100.50',`
- Line 41 (ip_addresses): `'source_ip': '192.168.20.0/24',`
- Line 42 (ip_addresses): `'destination_ip': '192.168.10.100',`
- Line 55 (ip_addresses): `'source_ip': '192.168.30.0/24',`
- Line 56 (ip_addresses): `'destination_ip': '172.16.10.20',`
- Line 178 (ports): `request_id = f"FW-{datetime.now().strftime('%Y%m%d')}-{secrets.randbelow(1000) + 1000:04d}"`
- Line 236 (ip_addresses): `1. 출발지: 10.10.10.0/24 (개발팀 네트워크)`
- Line 237 (ip_addresses): `2. 목적지: 192.168.100.50 (웹 서버)`
- Line 265 (ports): `port=80`

### /home/jclee/app/fortinet/src/routes/main_routes.py
- Line 31 (ip_addresses): `'src_ip': '192.168.1.10',`
- Line 32 (ip_addresses): `'dst_ip': '10.0.0.50',`
- Line 43 (ip_addresses): `'src_ip': '192.168.1.10',`
- Line 44 (ip_addresses): `'dst_ip': '10.0.0.50',`
- Line 51 (ip_addresses): `'src_ip': '172.16.10.20',`
- Line 70 (ip_addresses): `'src_ip': '172.16.10.20',`
- Line 177 (ip_addresses): `'src_ip': '192.168.1.10',`
- Line 178 (ip_addresses): `'dst_ip': '10.0.0.50',`
- Line 191 (ip_addresses): `'source_ip': '192.168.1.10',`
- Line 192 (ip_addresses): `'destination_ip': '10.0.0.50',`
- Line 202 (ip_addresses): `'src_ip': '192.168.1.10',`
- Line 203 (ip_addresses): `'dst_ip': '10.0.0.50'`

### /home/jclee/app/fortinet/src/security/packet_sniffer/analyzers/application_analyzer.py
- Line 232 (ports): `if b'IMAP' in payload[:50] or payload.startswith((b'* OK', b'* BAD', b'* NO')):`
- Line 841 (ports): `'is_printable': all(32 <= b <= 126 for b in payload[:100])`
- Line 846 (ports): `analysis['text_preview'] = payload.decode('utf-8', errors='ignore')[:200]`
- Line 985 (ports): `start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))`
- Line 986 (ports): `current = datetime.fromisoformat(current_time.replace('Z', '+00:00'))`

### /home/jclee/app/fortinet/src/security/packet_sniffer/analyzers/dns_analyzer.py
- Line 104 (ports): `header = struct.unpack('!HHHHHH', payload[:12])`
- Line 131 (ports): `header = struct.unpack('!HHHHHH', payload[:12])`
- Line 294 (ports): `return ':'.join(f'{rdata[i]:02x}{rdata[i+1]:02x}' for i in range(0, 16, 2))`
- Line 304 (ports): `return rdata.hex() if len(rdata) <= 32 else f'{rdata[:32].hex()}...'`

### /home/jclee/app/fortinet/src/security/packet_sniffer/analyzers/fortimanager_analyzer.py
- Line 325 (ports): `timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).timestamp()`
- Line 420 (ports): `'error_details': errors[:10],  # 최대 10개까지만`
- Line 502 (ports): `timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).timestamp()`

### /home/jclee/app/fortinet/src/security/packet_sniffer/analyzers/http_analyzer.py
- Line 129 (ports): `for line in lines[:10]:  # 첫 10줄만 확인`
- Line 379 (ports): `analysis['keys'] = list(json_data.keys())[:10]  # 최대 10개 키만`
- Line 383 (ports): `analysis['array_item_keys'] = list(json_data[0].keys())[:10]`

### /home/jclee/app/fortinet/src/security/packet_sniffer/analyzers/network_analyzer.py
- Line 187 (ports): `checksum = struct.unpack('>H', packet_data[10:12])[0]`
- Line 188 (ports): `src_ip = socket.inet_ntoa(packet_data[12:16])`
- Line 189 (ports): `dst_ip = socket.inet_ntoa(packet_data[16:20])`
- Line 249 (ports): `src_ip = socket.inet_ntop(socket.AF_INET6, packet_data[8:24])`
- Line 250 (ports): `dst_ip = socket.inet_ntop(socket.AF_INET6, packet_data[24:40])`
- Line 330 (ports): `ack_num = struct.unpack('>I', tcp_data[8:12])[0]`
- Line 332 (ports): `data_offset_flags = struct.unpack('>H', tcp_data[12:14])[0]`
- Line 337 (ports): `window_size = struct.unpack('>H', tcp_data[14:16])[0]`
- Line 338 (ports): `checksum = struct.unpack('>H', tcp_data[16:18])[0]`
- Line 339 (ports): `urgent_pointer = struct.unpack('>H', tcp_data[18:20])[0]`
- Line 658 (ports): `)[:10]`
- Line 665 (ports): `)[:10]`
- Line 869 (ports): `start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))`
- Line 870 (ports): `current = datetime.fromisoformat(current_time.replace('Z', '+00:00'))`

### /home/jclee/app/fortinet/src/security/packet_sniffer/analyzers/pattern_detector.py
- Line 337 (ports): `'ports': sorted(list(scan['ports']))[:20],  # 최대 20개 포트만 표시`
- Line 392 (ports): `'dst_ips': sorted(list(scan['dst_ips']))[:10],  # 최대 10개 호스트만 표시`

### /home/jclee/app/fortinet/src/security/packet_sniffer/analyzers/protocol_analyzer.py
- Line 397 (ports): `str(hash(packet.payload[:100]))  # 페이로드 앞부분 해시`

### /home/jclee/app/fortinet/src/security/packet_sniffer/analyzers/tls_analyzer.py
- Line 161 (ports): `'version': self.TLS_VERSIONS.get(version, f'unknown_{version:04x}'),`
- Line 254 (ports): `cipher_suites.append(f"0x{suite:04x}")`
- Line 258 (ports): `'client_version': self.TLS_VERSIONS.get(client_version, f'unknown_{client_version:04x}'),`
- Line 301 (ports): `'server_version': self.TLS_VERSIONS.get(server_version, f'unknown_{server_version:04x}'),`
- Line 304 (ports): `'chosen_cipher_suite': f"0x{chosen_cipher_suite:04x}",`

### /home/jclee/app/fortinet/src/security/packet_sniffer/base_sniffer.py
- Line 297 (urls): `'HTTP': b'GET / HTTP/1.1\r\nHost: example.com\r\n\r\n',`
- Line 301 (urls): `'SMTP': b'220 mail.example.com ESMTP ready\r\n'`

### /home/jclee/app/fortinet/src/security/packet_sniffer/device_manager.py
- Line 204 (ip_addresses): `'127.0.0.1' in ip_addresses`
- Line 261 (ip_addresses): `ip_addresses=["127.0.0.1"],`
- Line 278 (ip_addresses): `'host': '192.168.1.99',`
- Line 404 (ip_addresses): `'host': '192.168.1.1',`
- Line 411 (ip_addresses): `{'name': 'port1', 'ip': '192.168.1.1', 'status': 'up'},`
- Line 412 (ip_addresses): `{'name': 'port2', 'ip': '10.0.0.1', 'status': 'up'},`
- Line 422 (ip_addresses): `'host': '192.168.1.2',`
- Line 429 (ip_addresses): `{'name': 'port1', 'ip': '192.168.2.1', 'status': 'up'},`
- Line 430 (ip_addresses): `{'name': 'port2', 'ip': '10.0.1.1', 'status': 'up'}`
- Line 474 (ip_addresses): `{'name': 'port1', 'ip': '192.168.1.1', 'status': 'up', 'type': 'internal'},`
- Line 475 (ip_addresses): `{'name': 'port2', 'ip': '10.0.0.1', 'status': 'up', 'type': 'internal'},`
- Line 477 (ip_addresses): `{'name': 'dmz', 'ip': '172.16.0.1', 'status': 'down', 'type': 'dmz'}`

### /home/jclee/app/fortinet/src/security/packet_sniffer/exporters/csv_exporter.py
- Line 475 (ports): `for i, (ip, count) in enumerate(summary_data['top_src_ips'][:10]):`
- Line 483 (ports): `for i, (port, count) in enumerate(summary_data['top_dst_ports'][:10]):`

### /home/jclee/app/fortinet/src/security/packet_sniffer/exporters/data_exporter.py
- Line 323 (ports): `simple_packet['payload_preview'] = payload_str[:100] + ('...' if len(payload_str) > 100 else '')`
- Line 349 (ports): `row[field] = payload_str[:50] + ('...' if len(payload_str) > 50 else '')`

### /home/jclee/app/fortinet/src/security/packet_sniffer/exporters/json_exporter.py
- Line 492 (ports): `top_ips = statistics['top_src_ips'][:10]`

### /home/jclee/app/fortinet/src/security/packet_sniffer/exporters/pcap_exporter.py
- Line 250 (ports): `timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))`
- Line 356 (ip_addresses): `src_ip = packet.get('src_ip', '127.0.0.1')`
- Line 357 (ip_addresses): `dst_ip = packet.get('dst_ip', '127.0.0.1')`
- Line 414 (ip_addresses): `src_addr = socket.inet_aton('127.0.0.1')`
- Line 415 (ip_addresses): `dst_addr = socket.inet_aton('127.0.0.1')`
- Line 465 (ports): `dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))`
- Line 587 (ports): `caplen = struct.unpack('<I', packet_header[8:12])[0]`

### /home/jclee/app/fortinet/src/security/packet_sniffer/exporters/report_exporter.py
- Line 378 (ports): `dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))`
- Line 457 (ports): `'anomaly_details': anomalies[:20]  # 상위 20개만`
- Line 752 (urls): `<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>`

### /home/jclee/app/fortinet/src/security/packet_sniffer/filters/bpf_filter.py
- Line 361 (ip_addresses): `'private_networks': 'net 192.168.0.0/16 or net 10.0.0.0/8 or net 172.16.0.0/12',`
- Line 362 (ip_addresses): `'local_traffic': 'host 127.0.0.1',`
- Line 444 (ip_addresses): `'filter': 'host 192.168.1.100',`
- Line 445 (ip_addresses): `'description': '192.168.1.100과 주고받는 모든 패킷'`
- Line 459 (ip_addresses): `'filter': 'src net 192.168.0.0/24',`
- Line 474 (ip_addresses): `'filter': 'not (net 192.168.0.0/16 or net 10.0.0.0/8)',`

### /home/jclee/app/fortinet/src/security/packet_sniffer/filters/packet_filter.py
- Line 248 (ip_addresses): `self.add_rule('src_ip', 'subnet', '192.168.0.0/16', 'allow')`
- Line 249 (ip_addresses): `self.add_rule('src_ip', 'subnet', '10.0.0.0/8', 'allow')`
- Line 250 (ip_addresses): `self.add_rule('src_ip', 'subnet', '172.16.0.0/12', 'allow')`
- Line 277 (credentials): `admin_ports = [22, 23, 3389, 5900, 5901]`
- Line 278 (credentials): `for port in admin_ports:`

### /home/jclee/app/fortinet/src/security/packet_sniffer/inspectors/deep_inspector.py
- Line 245 (ports): `analysis['tls_version'] = version_map.get(version, f'Unknown (0x{version:04x})')`
- Line 312 (ports): `header = struct.unpack('>HHHHHH', payload[:12])`
- Line 680 (ports): `return f'0x{cipher_id:04x}'`

### /home/jclee/app/fortinet/src/security/packet_sniffer/web_compatibility.py
- Line 219 (ip_addresses): `{'name': 'port1', 'type': 'physical', 'ip': '192.168.1.1/24', 'status': 'up'},`
- Line 220 (ip_addresses): `{'name': 'port2', 'type': 'physical', 'ip': '10.0.0.1/24', 'status': 'up'}`
- Line 236 (ip_addresses): `{'name': 'port1', 'type': 'physical', 'ip': '192.168.1.1/24', 'status': 'up'},`
- Line 237 (ip_addresses): `{'name': 'port2', 'type': 'physical', 'ip': '10.0.0.1/24', 'status': 'up'}`
- Line 294 (ports): `start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))`

### /home/jclee/app/fortinet/src/security/packet_sniffer_api.py
- Line 499 (ports): `'top_ports': dict(sorted(port_stats.items(), key=lambda x: x[1], reverse=True)[:10]),`
- Line 500 (ports): `'top_connections': dict(sorted(ip_pairs.items(), key=lambda x: x[1], reverse=True)[:10])`

### /home/jclee/app/fortinet/src/security/scanner.py
- Line 48 (paths): `'/home/jclee/dev/fortinet/.env',`
- Line 49 (paths): `'/home/jclee/dev/fortinet/data/config.json'`
- Line 465 (ip_addresses): `if conn.raddr.ip not in ['127.0.0.1', '::1']:`
- Line 552 (paths): `'/var/log/auth.log',`
- Line 553 (paths): `'/var/log/syslog',`
- Line 554 (paths): `'/home/jclee/dev/fortinet/logs/app.log'`

### /home/jclee/app/fortinet/src/utils/api_optimizer.py
- Line 458 (ports): `devices = [f"Device-{i:03d}" for i in range(1, 501)]  # 500개 장치`

### /home/jclee/app/fortinet/src/utils/diagnostic.py
- Line 81 (urls): `test_domains = ['google.com', 'fortinet.com']`
- Line 94 (ip_addresses): `result = sock.connect_ex(('localhost', port))`
- Line 105 (paths): `'docker_socket': os.path.exists('/var/run/docker.sock')`
- Line 177 (urls): `url = f"https://{host}/jsonrpc"`
- Line 257 (urls): `if not network.get('dns_resolution', {}).get('fortinet.com'):`

### /home/jclee/app/fortinet/src/utils/mock_server.py
- Line 35 (ip_addresses): `'ip': '192.168.1.100',`
- Line 44 (ip_addresses): `'ip': '192.168.2.100',`
- Line 53 (ip_addresses): `'ip': '192.168.3.100',`
- Line 83 (ip_addresses): `'ip': '192.168.1.1',`
- Line 92 (ip_addresses): `'ip': '10.0.0.1',`
- Line 101 (ip_addresses): `'ip': '192.168.1.110',`
- Line 128 (ip_addresses): `'srcaddr': ['10.0.0.0/24'],`
- Line 129 (ip_addresses): `'dstaddr': ['192.168.0.0/16'],`

### /home/jclee/app/fortinet/src/utils/performance_optimizer.py
- Line 182 (ports): `metrics_list[:500] = []  # 오래된 절반 삭제`
- Line 311 (ports): `optimized[key] = value[:100]  # 샘플만 유지`
- Line 315 (ports): `important_keys = list(value.keys())[:50]`

### /home/jclee/app/fortinet/src/utils/security.py
- Line 37 (urls): `"script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com https://cdn.jsdelivr.n...`
- Line 38 (urls): `"style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com; "`
- Line 39 (urls): `"font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com data:; "`
- Line 91 (ports): `r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'`
- Line 92 (ports): `r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'`

### /home/jclee/app/fortinet/src/utils/security_fixes.py
- Line 64 (credentials): `r"@app\.route\(['\"][^'\"]*/(api|admin|config|settings|delete|create|update)[^'\"]*['\"][^)]*\)",`
- Line 65 (credentials): `r"@.*\.route\(['\"][^'\"]*/(api|admin|config|settings|delete|create|update)[^'\"]*['\"][^)]*\)",`
- Line 186 (credentials): `elif re.search(r'@app\.route\([\'"][^\'\"]*/(api|admin|config|settings|delete|create|update)', line)...`

### /home/jclee/app/fortinet/src/utils/unified_cache_manager.py
- Line 121 (ip_addresses): `def __init__(self, host='localhost', port=6379, db=0, password=None):`
- Line 121 (ports): `def __init__(self, host='localhost', port=6379, db=0, password=None):`

### /home/jclee/app/fortinet/src/web_app.py
- Line 273 (urls): `print(f"🌐 서버 시작: http://{host}:{port}")`


## 권장 조치사항

1. **환경변수 사용**
   - 민감한 정보(비밀번호, API 키 등)는 환경변수로 이동
   - `.env.template` 파일 참조

2. **설정 파일 사용**
   - 포트 번호, URL 등은 설정 파일로 이동
   - `config/settings.json` 템플릿 참조

3. **상수 모듈 사용**
   - 반복되는 값들은 상수 모듈로 추출
   - `src/config/constants.py` 활용

4. **동적 설정**
   - 실행 시점에 결정되는 값은 런타임 설정으로
   - 환경별 설정 분리 (dev, staging, prod)
