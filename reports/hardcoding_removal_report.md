# 하드코딩 제거 보고서
생성일: 2025-07-01 22:41:55
총 발견된 패턴: 479개

## 패턴 타입별 통계
- fortimanager_demo_host: 29개
- host_hardcoding: 27개
- limit_hardcoding: 77개
- localhost_hardcoding: 64개
- port_hardcoding: 51개
- port_in_url: 106개
- threshold_hardcoding: 12개
- url_hardcoding: 113개

## 파일별 하드코딩 항목
### src/web_app.py
- 라인 153: `max_requests=30`
  - 제안: `max_requests=30`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 168: `max_requests=30`
  - 제안: `max_requests=30`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 196: `max_requests=30`
  - 제안: `max_requests=30`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 228: `max_requests=30`
  - 제안: `max_requests=30`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 230: `max_requests=60`
  - 제안: `max_requests=60`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 284: `http://{host}:{port}`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://{host}:{port}')`
  - 환경변수: `CUSTOM_ENV_VAR`

### tests/test_coverage_boost.py
- 라인 44: `host="localhost"`
  - 제안: `host=os.getenv('SERVICE_HOST', 'localhost')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 44: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 48: `host="localhost"`
  - 제안: `host=os.getenv('SERVICE_HOST', 'localhost')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 48: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 51: `host="localhost"`
  - 제안: `host=os.getenv('SERVICE_HOST', 'localhost')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 51: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`

### tests/test_fortimanager_api_refactored.py
- 라인 22: `host='192.168.1.100'`
  - 제안: `host=os.getenv('CUSTOM_HOST', 'host='192.168.1.100'')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 211: `port=80`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '80'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 269: `host='192.168.1.100'`
  - 제안: `host=os.getenv('CUSTOM_HOST', 'host='192.168.1.100'')`
  - 환경변수: `CUSTOM_ENV_VAR`

### tests/test_performance.py
- 라인 181: `max_per_page=50`
  - 제안: `max_per_page=50`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 195: `max_workers=4`
  - 제안: `max_workers=4`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 265: `max_retries=0`
  - 제안: `max_retries=0`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 295: `max_retries=3`
  - 제안: `max_retries=3`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 347: `max_retries=5`
  - 제안: `max_retries=5`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 374: `max_concurrent=5`
  - 제안: `max_concurrent=5`
  - 환경변수: `CUSTOM_ENV_VAR`

### tests/test_suite.py
- 라인 57: `host="192.168.1.1"`
  - 제안: `host=os.getenv('CUSTOM_HOST', 'host="192.168.1.1"')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 72: `host="192.168.1.2"`
  - 제안: `host=os.getenv('CUSTOM_HOST', 'host="192.168.1.2"')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 79: `host="192.168.1.3"`
  - 제안: `host=os.getenv('CUSTOM_HOST', 'host="192.168.1.3"')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 136: `host="192.168.1.2"`
  - 제안: `host=os.getenv('CUSTOM_HOST', 'host="192.168.1.2"')`
  - 환경변수: `CUSTOM_ENV_VAR`

### tests/test_api_clients.py
- 라인 90: `http://test.com`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://test.com')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 205: `host='192.168.1.100'`
  - 제안: `host=os.getenv('CUSTOM_HOST', 'host='192.168.1.100'')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 288: `host='192.168.1.200'`
  - 제안: `host=os.getenv('CUSTOM_HOST', 'host='192.168.1.200'')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 335: `host='192.168.1.150'`
  - 제안: `host=os.getenv('CUSTOM_HOST', 'host='192.168.1.150'')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 383: `host='192.168.1.100'`
  - 제안: `host=os.getenv('CUSTOM_HOST', 'host='192.168.1.100'')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 384: `host='192.168.1.100'`
  - 제안: `host=os.getenv('CUSTOM_HOST', 'host='192.168.1.100'')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 385: `host='192.168.1.200'`
  - 제안: `host=os.getenv('CUSTOM_HOST', 'host='192.168.1.200'')`
  - 환경변수: `CUSTOM_ENV_VAR`

### scripts/monitor_deployment.py
- 라인 27: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 29: `http://{self.deploy_host}:{self.deploy_port}`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://{self.deploy_host}:{self.deploy_port}')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 35: `max_checks = 20`
  - 제안: `max_checks = 20`
  - 환경변수: `CUSTOM_ENV_VAR`

### scripts/monitor_pipeline.py
- 라인 28: `https://gitlab.com`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://gitlab.com')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 250: `max_wait_time=3600`
  - 제안: `max_wait_time=3600`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/fortimanager/fortimanager_security_fabric.py
- 라인 101: `max_workers=10`
  - 제안: `max_workers=10`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/fortimanager/fortimanager_analytics_engine.py
- 라인 111: `max_workers=10`
  - 제안: `max_workers=10`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 141: `threshold_warning=70`
  - 제안: `threshold_warning=70`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 142: `threshold_critical=90`
  - 제안: `threshold_critical=90`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 155: `threshold_warning=100`
  - 제안: `threshold_warning=100`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 156: `threshold_critical=500`
  - 제안: `threshold_critical=500`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 167: `threshold_warning=5`
  - 제안: `threshold_warning=5`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 168: `threshold_critical=10`
  - 제안: `threshold_critical=10`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 181: `threshold_warning=100`
  - 제안: `threshold_warning=100`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 182: `threshold_critical=500`
  - 제안: `threshold_critical=500`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 194: `threshold_warning=50000`
  - 제안: `int(os.getenv('TRAFFIC_HIGH_THRESHOLD', '5000'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 195: `threshold_critical=80000`
  - 제안: `threshold_critical=80000`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/fortimanager/fortimanager_policy_orchestrator.py
- 라인 62: `max_workers=10`
  - 제안: `max_workers=10`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 111: `https://{app_domain}`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://{app_domain}')`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/fortimanager/fortimanager_compliance_automation.py
- 라인 83: `max_workers=10`
  - 제안: `max_workers=10`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/core/auth_manager.py
- 라인 8: `: 2025`
  - 제안: `: 2025`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 281: `https://{host}:{port}/jsonrpc`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://{host}:{port}/jsonrpc')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 370: `https://{session.host}:{session.port}/jsonrpc`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://{session.host}:{session.port}/jsonrpc')`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/core/cache_manager.py
- 라인 8: `: 2025`
  - 제안: `: 2025`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 254: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/core/config_manager.py
- 라인 8: `: 2025`
  - 제안: `: 2025`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 60: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 580: `: 7777`
  - 제안: `: 7777`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 582: `: 7777`
  - 제안: `: 7777`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/core/base_client.py
- 라인 8: `: 2025`
  - 제안: `: 2025`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 127: `https://{self.host}:{self.port}{API_VERSIONS[`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://{self.host}:{self.port}{API_VERSIONS[')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 131: `https://{self.host}:{self.port}{API_VERSIONS[`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://{self.host}:{self.port}{API_VERSIONS[')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 135: `https://{self.host}:{self.port}{API_VERSIONS[`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://{self.host}:{self.port}{API_VERSIONS[')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 139: `https://{self.host}:{self.port}{API_VERSIONS[`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://{self.host}:{self.port}{API_VERSIONS[')`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/modules/device_manager.py
- 라인 179: `: 1500`
  - 제안: `: 1500`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 193: `: 1500`
  - 제안: `: 1500`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 207: `: 1500`
  - 제안: `: 1500`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 221: `: 1500`
  - 제안: `: 1500`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/config/constants.py
- 라인 95: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 95: `http://localhost:{port}/health`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://localhost:{port}/health')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 96: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 96: `http://localhost:{port}{api_version}/monitor/system/status`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://localhost:{port}{api_version}/monitor/system/status')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 97: `:6379`
  - 제안: `:6379`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/config/network.py
- 라인 19: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 20: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 49: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 50: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 58: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 59: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/config/env_defaults.py
- 라인 27: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 28: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 29: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 80: `http://8.8.8.8`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://8.8.8.8')`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/config/limits.py
- 라인 38: `: 1800`
  - 제안: `: 1800`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 67: `: 2048`
  - 제안: `: 2048`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 80: `: 10000`
  - 제안: `: 10000`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 136: `: 10000`
  - 제안: `: 10000`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/config/config_helper.py
- 라인 60: `https://{host}:{port}{api_version}`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://{host}:{port}{api_version}')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 62: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 66: `http://{host}:{port}/health`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://{host}:{port}/health')`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/config/unified_settings.py
- 라인 304: `http://{self.webapp.host}:{self.webapp.port}`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://{self.webapp.host}:{self.webapp.port}')`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/config/ports.py
- 라인 32: `: 8008`
  - 제안: `: 8008`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 33: `: 8890`
  - 제안: `: 8890`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 34: `: 8009`
  - 제안: `: 8009`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 36: `: 8013`
  - 제안: `: 8013`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 62: `: 3389`
  - 제안: `: 3389`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 63: `: 5900`
  - 제안: `: 5900`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 71: `: 8080`
  - 제안: `: 8080`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 72: `: 8443`
  - 제안: `: 8443`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 93: `: 3389`
  - 제안: `: 3389`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 94: `: 5900`
  - 제안: `: 5900`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 97: `: 3306`
  - 제안: `: 3306`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 98: `: 5432`
  - 제안: `: 5432`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 99: `: 27017`
  - 제안: `: 27017`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 100: `: 6379`
  - 제안: `: 6379`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 101: `: 9042`
  - 제안: `: 9042`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 102: `: 9200`
  - 제안: `: 9200`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 108: `: 9090`
  - 제안: `: 9090`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 109: `: 3000`
  - 제안: `: 3000`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 110: `: 10051`
  - 제안: `: 10051`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/config/services.py
- 라인 12: `https://itsm2.nxtd.co.kr`
  - 제안: `os.getenv('ITSM_BASE_URL', '')`
  - 환경변수: `ITSM_BASE_URL`
- 라인 14: `https://gitlab.com`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://gitlab.com')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 17: `http://8.8.8.8`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://8.8.8.8')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 18: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 18: `http://localhost:{os.getenv(`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://localhost:{os.getenv(')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 23: `https://cdnjs.cloudflare.com`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://cdnjs.cloudflare.com')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 24: `https://cdn.jsdelivr.net`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://cdn.jsdelivr.net')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 25: `https://fonts.googleapis.com`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://fonts.googleapis.com')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 26: `https://fonts.gstatic.com`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://fonts.gstatic.com')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 27: `https://stackpath.bootstrapcdn.com`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://stackpath.bootstrapcdn.com')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 28: `https://code.jquery.com`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://code.jquery.com')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 38: `https://cdnjs.cloudflare.com`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://cdnjs.cloudflare.com')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 39: `https://cdn.jsdelivr.net`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://cdn.jsdelivr.net')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 40: `https://code.jquery.com`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://code.jquery.com')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 41: `https://stackpath.bootstrapcdn.com`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://stackpath.bootstrapcdn.com')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 46: `https://cdnjs.cloudflare.com`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://cdnjs.cloudflare.com')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 47: `https://cdn.jsdelivr.net`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://cdn.jsdelivr.net')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 48: `https://fonts.googleapis.com`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://fonts.googleapis.com')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 49: `https://stackpath.bootstrapcdn.com`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://stackpath.bootstrapcdn.com')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 53: `https://fonts.gstatic.com`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://fonts.gstatic.com')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 54: `https://cdnjs.cloudflare.com`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://cdnjs.cloudflare.com')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 81: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 81: `http://localhost:{os.getenv(`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://localhost:{os.getenv(')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 82: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 82: `http://localhost:{os.getenv(`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://localhost:{os.getenv(')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 83: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 83: `http://localhost:{os.getenv(`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://localhost:{os.getenv(')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 84: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 84: `http://localhost:{os.getenv(`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://localhost:{os.getenv(')`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/utils/troubleshooting_loop.py
- 라인 32: `max_recovery_attempts = 3`
  - 제안: `max_recovery_attempts = 3`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/utils/api_common.py
- 라인 270: `max_retries = 3`
  - 제안: `max_retries = 3`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/utils/security_fixes.py
- 라인 188: `max_requests=30`
  - 제안: `max_requests=30`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 265: `max_requests=30`
  - 제안: `max_requests=30`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/utils/mock_server.py
- 라인 111: `: 1000`
  - 제안: `: 1000`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 113: `: 1000`
  - 제안: `: 1000`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 114: `: 10000`
  - 제안: `: 10000`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 115: `: 1000`
  - 제안: `: 1000`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 117: `: 1000`
  - 제안: `: 1000`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 345: `host='0.0.0.0'`
  - 제안: `host=os.getenv('BIND_HOST', '0.0.0.0')`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/utils/diagnostic.py
- 라인 94: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 177: `https://{host}/jsonrpc`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://{host}/jsonrpc')`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/utils/api_optimizer.py
- 라인 24: `threshold = 1024`
  - 제안: `threshold = 1024`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 26: `max_page_size = 100`
  - 제안: `max_page_size = 100`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/utils/security.py
- 라인 37: `https://cdnjs.cloudflare.com`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://cdnjs.cloudflare.com')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 37: `https://cdn.jsdelivr.net;`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://cdn.jsdelivr.net;')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 38: `https://cdnjs.cloudflare.com`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://cdnjs.cloudflare.com')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 38: `https://fonts.googleapis.com;`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://fonts.googleapis.com;')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 39: `https://cdnjs.cloudflare.com`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://cdnjs.cloudflare.com')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 39: `https://fonts.gstatic.com`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://fonts.gstatic.com')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 124: `max_length=255`
  - 제안: `max_length=255`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/utils/unified_cache_manager.py
- 라인 121: `port=6379`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '6379'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 121: `host='localhost'`
  - 제안: `host=os.getenv('SERVICE_HOST', 'localhost')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 121: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 230: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/mock/fortigate.py
- 라인 535: `: 1847`
  - 제안: `: 1847`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/mock/data_generator.py
- 라인 82: `: 1500`
  - 제안: `: 1500`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 185: `: 3306`
  - 제안: `: 3306`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 895: `: 16384`
  - 제안: `: 16384`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 1018: `: 1000`
  - 제안: `: 1000`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/analysis/analyzer.py
- 라인 838: `max_hops = 10`
  - 제안: `max_hops = 10`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 1480: `max_hops = 10`
  - 제안: `max_hops = 10`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/analysis/fixed_path_analyzer.py
- 라인 235: `port=80`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '80'))`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/analysis/advanced_analytics.py
- 라인 38: `threshold = 2`
  - 제안: `threshold = 2`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/routes/api_routes.py
- 라인 86: `max_requests=60`
  - 제안: `max_requests=60`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 529: `: 16384`
  - 제안: `: 16384`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 736: `: 1000`
  - 제안: `: 1000`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/routes/performance_routes.py
- 라인 51: `max_requests=5`
  - 제안: `max_requests=5`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 90: `max_requests=3`
  - 제안: `max_requests=3`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 270: `max_requests=5`
  - 제안: `max_requests=5`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 296: `max_requests=5`
  - 제안: `max_requests=5`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/routes/itsm_automation_routes.py
- 라인 35: `max_requests=30`
  - 제안: `max_requests=30`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 55: `max_requests=5`
  - 제안: `max_requests=5`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 84: `max_requests=10`
  - 제안: `max_requests=10`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 112: `max_requests=10`
  - 제안: `max_requests=10`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 159: `max_requests=60`
  - 제안: `max_requests=60`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 179: `max_requests=60`
  - 제안: `max_requests=60`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 205: `max_requests=10`
  - 제안: `max_requests=10`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 234: `max_requests=30`
  - 제안: `max_requests=30`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 272: `max_requests=5`
  - 제안: `max_requests=5`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 301: `max_requests=60`
  - 제안: `max_requests=60`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 341: `max_requests=60`
  - 제안: `max_requests=60`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 379: `max_requests=20`
  - 제안: `max_requests=20`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/routes/logs_routes.py
- 라인 53: `max_requests=30`
  - 제안: `max_requests=30`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 138: `max_requests=30`
  - 제안: `max_requests=30`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 205: `max_requests=10`
  - 제안: `max_requests=10`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 256: `max_requests=20`
  - 제안: `max_requests=20`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 325: `max_requests=10`
  - 제안: `max_requests=10`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 405: `: 2025`
  - 제안: `: 2025`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 423: `: 2025`
  - 제안: `: 2025`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 440: `max_requests=5`
  - 제안: `max_requests=5`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/routes/fortimanager_routes.py
- 라인 361: `max_requests=10`
  - 제안: `max_requests=10`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 449: `max_requests=5`
  - 제안: `max_requests=5`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 626: `max_requests=10`
  - 제안: `max_requests=10`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 637: `max_requests=5`
  - 제안: `max_requests=5`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/routes/itsm_api_routes.py
- 라인 265: `port=80`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '80'))`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/itsm/automation_service.py
- 라인 76: `https://itsm2.nxtd.co.kr`
  - 제안: `os.getenv('ITSM_BASE_URL', '')`
  - 환경변수: `ITSM_BASE_URL`

### src/itsm/external_connector.py
- 라인 223: `: 1000`
  - 제안: `: 1000`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 243: `: 1000`
  - 제안: `: 1000`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 262: `: 1000`
  - 제안: `: 1000`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/itsm/policy_automation.py
- 라인 156: `host="192.168.1.1"`
  - 제안: `host=os.getenv('CUSTOM_HOST', 'host="192.168.1.1"')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 164: `host="172.16.1.1"`
  - 제안: `host=os.getenv('CUSTOM_HOST', 'host="172.16.1.1"')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 172: `host="203.0.113.1"`
  - 제안: `host=os.getenv('CUSTOM_HOST', 'host="203.0.113.1"')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 180: `host="10.10.1.1"`
  - 제안: `host=os.getenv('CUSTOM_HOST', 'host="10.10.1.1"')`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/itsm/fortigate_bridge.py
- 라인 35: `https://itsm2.nxtd.co.kr`
  - 제안: `os.getenv('ITSM_BASE_URL', '')`
  - 환경변수: `ITSM_BASE_URL`
- 라인 61: `https://itsm2.nxtd.co.kr`
  - 제안: `os.getenv('ITSM_BASE_URL', '')`
  - 환경변수: `ITSM_BASE_URL`

### src/automation/auto_recovery.py
- 라인 299: `port=6379`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '6379'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 299: `host='localhost'`
  - 제안: `host=os.getenv('SERVICE_HOST', 'localhost')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 299: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 454: `http://8.8.8.8`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://8.8.8.8')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 462: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 462: `http://localhost:{APP_CONFIG[`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://localhost:{APP_CONFIG[')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 476: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 476: `http://localhost:{APP_CONFIG[`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://localhost:{APP_CONFIG[')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 547: `http://8.8.8.8`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://8.8.8.8')`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/monitoring/realtime/monitor.py
- 라인 105: `: 86400`
  - 제안: `: 86400`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 111: `: 1500`
  - 제안: `: 1500`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 112: `: 1200`
  - 제안: `: 1200`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 116: `: 1500`
  - 제안: `: 1500`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/api/clients/faz_client.py
- 라인 72: `https://{self.host}{API_VERSIONS[`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://{self.host}{API_VERSIONS[')`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/api/clients/fortigate_api_client.py
- 라인 29: `PORT = 443`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '443'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 425: `max_packets=1000`
  - 제안: `int(os.getenv('TRAFFIC_MEDIUM_THRESHOLD', '1000'))`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/api/clients/base_api_client.py
- 라인 120: `max_retries=3`
  - 제안: `max_retries=3`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 404: `max_connection_errors = 5`
  - 제안: `max_connection_errors = 5`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/config/refactored/network.py
- 라인 44: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 45: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/config/refactored/ports.py
- 라인 34: `: 3389`
  - 제안: `: 3389`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 35: `: 5900`
  - 제안: `: 5900`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/config/refactored/example_refactoring.py
- 라인 13: `http://8.8.8.8`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://8.8.8.8')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 20: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 20: `http://localhost:{os.getenv(`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://localhost:{os.getenv(')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 28: `https://itsm2.nxtd.co.kr`
  - 제안: `os.getenv('ITSM_BASE_URL', '')`
  - 환경변수: `ITSM_BASE_URL`
- 라인 58: `http://8.8.8.8`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://8.8.8.8')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 70: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 70: `http://localhost:{port}{endpoint}`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://localhost:{port}{endpoint}')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 182: `https://{host}:{port}{status_endpoint}`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://{host}:{port}{status_endpoint}')`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/config/refactored/services.py
- 라인 9: `https://itsm2.nxtd.co.kr`
  - 제안: `os.getenv('ITSM_BASE_URL', '')`
  - 환경변수: `ITSM_BASE_URL`
- 라인 13: `https://gitlab.com`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://gitlab.com')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 25: `https://cdnjs.cloudflare.com`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://cdnjs.cloudflare.com')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 26: `https://cdn.jsdelivr.net`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://cdn.jsdelivr.net')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 27: `https://fonts.googleapis.com`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://fonts.googleapis.com')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 28: `https://fonts.gstatic.com`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://fonts.gstatic.com')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 80: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 80: `http://localhost:{port}/health`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://localhost:{port}/health')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 81: `http://8.8.8.8`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://8.8.8.8')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 82: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 82: `http://localhost:{port}/api/v2/monitor/system/status`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://localhost:{port}/api/v2/monitor/system/status')`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/security/packet_sniffer/web_compatibility.py
- 라인 258: `max_packets=1000`
  - 제안: `int(os.getenv('TRAFFIC_MEDIUM_THRESHOLD', '1000'))`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/security/packet_sniffer/session_manager.py
- 라인 304: `max_sessions = 50`
  - 제안: `max_sessions = 50`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/security/packet_sniffer/packet_capturer.py
- 라인 374: `max_packets = 20`
  - 제안: `max_packets = 20`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 410: `: 3600`
  - 제안: `: 3600`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/security/packet_sniffer/analyzers/protocol_analyzer.py
- 라인 66: `max_size = 1000`
  - 제안: `int(os.getenv('TRAFFIC_MEDIUM_THRESHOLD', '1000'))`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/security/packet_sniffer/analyzers/pattern_detector.py
- 라인 44: `: 1500`
  - 제안: `: 1500`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/security/packet_sniffer/analyzers/dns_analyzer.py
- 라인 427: `max_consecutive = 0`
  - 제안: `max_consecutive = 0`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/security/packet_sniffer/exporters/report_exporter.py
- 라인 654: `: 1200`
  - 제안: `: 1200`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 752: `https://cdn.jsdelivr.net/npm/chart.js`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://cdn.jsdelivr.net/npm/chart.js')`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/security/packet_sniffer/filters/advanced_filter.py
- 라인 494: `max_distance = 100000`
  - 제안: `int(os.getenv('TRAFFIC_MEDIUM_THRESHOLD', '1000'))`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/routes/fortimanager/policy_routes.py
- 라인 57: `max_requests=10`
  - 제안: `max_requests=10`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 101: `max_requests=15`
  - 제안: `max_requests=15`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 144: `max_requests=5`
  - 제안: `max_requests=5`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 181: `max_requests=30`
  - 제안: `max_requests=30`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/routes/fortimanager/analytics_routes.py
- 라인 21: `max_requests=5`
  - 제안: `max_requests=5`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 70: `max_requests=10`
  - 제안: `max_requests=10`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 152: `max_requests=20`
  - 제안: `max_requests=20`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 204: `max_requests=15`
  - 제안: `max_requests=15`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 256: `max_requests=10`
  - 제안: `max_requests=10`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 308: `max_requests=25`
  - 제안: `max_requests=25`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 360: `max_requests=5`
  - 제안: `max_requests=5`
  - 환경변수: `CUSTOM_ENV_VAR`

### src/routes/fortimanager/compliance_routes.py
- 라인 20: `max_requests=20`
  - 제안: `max_requests=20`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 77: `max_requests=10`
  - 제안: `max_requests=10`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 178: `max_requests=5`
  - 제안: `max_requests=5`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 326: `max_requests=10`
  - 제안: `max_requests=10`
  - 환경변수: `CUSTOM_ENV_VAR`

### tests/integration/test_all_endpoints_mcp.py
- 라인 49: `:7777`
  - 제안: `:7777`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 49: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 49: `http://localhost:7777`
  - 제안: `f"http://localhost:{os.getenv('WEB_APP_PORT', '7777')}"`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 53: `:6666`
  - 제안: `:6666`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 53: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 53: `http://localhost:6666`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://localhost:6666')`
  - 환경변수: `CUSTOM_ENV_VAR`

### tests/integration/endpoint_tester.py
- 라인 20: `:7778`
  - 제안: `:7778`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 20: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 20: `http://localhost:7778`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://localhost:7778')`
  - 환경변수: `CUSTOM_ENV_VAR`

### tests/integration/test_endpoints.py
- 라인 13: `: 6666`
  - 제안: `: 6666`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 14: `: 7777`
  - 제안: `: 7777`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 172: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 172: `http://localhost:{port}{path}`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://localhost:{port}{path}')`
  - 환경변수: `CUSTOM_ENV_VAR`

### tests/integration/test_all_endpoints.py
- 라인 208: `:7777`
  - 제안: `:7777`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 208: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 208: `http://localhost:7777`
  - 제안: `f"http://localhost:{os.getenv('WEB_APP_PORT', '7777')}"`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 209: `:7778`
  - 제안: `:7778`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 209: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 209: `http://localhost:7778`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://localhost:7778')`
  - 환경변수: `CUSTOM_ENV_VAR`

### tests/unit/test_packet_sniffer_analysis.py
- 라인 66: `max_size = 1000`
  - 제안: `int(os.getenv('TRAFFIC_MEDIUM_THRESHOLD', '1000'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 331: `port=45678`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '45678'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 332: `port=80`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '80'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 342: `port=45679`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '45679'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 343: `port=443`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '443'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 353: `port=53472`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '53472'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 354: `port=53`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '53'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 418: `port=12345`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '12345'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 419: `port=80`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '80'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 495: `port=45678`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '45678'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 496: `port=80`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '80'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 506: `port=80`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '80'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 507: `port=45678`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '45678'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 509: `: 1234`
  - 제안: `: 1234`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 558: `port=443`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '443'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 559: `port=45679`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '45679'))`
  - 환경변수: `CUSTOM_ENV_VAR`

### tests/manual/test_packet_analysis.py
- 라인 40: `: 3306`
  - 제안: `: 3306`
  - 환경변수: `CUSTOM_ENV_VAR`

### tests/manual/test_with_hjsim_session.py
- 라인 14: `:14005`
  - 제안: `:14005`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 14: `https://hjsim-1034-451984.fortidemo.fortinet.com:14005`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://hjsim-1034-451984.fortidemo.fortinet.com:14005')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 14: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`

### tests/manual/test_fortimanager_working.py
- 라인 15: `:14005`
  - 제안: `:14005`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 15: `https://hjsim-1034-451984.fortidemo.fortinet.com:14005`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://hjsim-1034-451984.fortidemo.fortinet.com:14005')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 15: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`

### tests/manual/test_fortimanager_demo.py
- 라인 25: `:14005`
  - 제안: `:14005`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 25: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`
- 라인 33: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`
- 라인 34: `: 14005`
  - 제안: `: 14005`
  - 환경변수: `CUSTOM_ENV_VAR`

### tests/manual/test_fortimanager_user_1411.py
- 라인 13: `:14005`
  - 제안: `:14005`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 13: `https://hjsim-1034-451984.fortidemo.fortinet.com:14005`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://hjsim-1034-451984.fortidemo.fortinet.com:14005')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 13: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`
- 라인 24: `: 1411`
  - 제안: `: 1411`
  - 환경변수: `CUSTOM_ENV_VAR`

### tests/manual/test_fortimanager_final.py
- 라인 14: `:14005`
  - 제안: `:14005`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 14: `https://hjsim-1034-451984.fortidemo.fortinet.com:14005`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://hjsim-1034-451984.fortidemo.fortinet.com:14005')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 14: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`

### tests/manual/test_fortimanager_raw.py
- 라인 14: `:14005`
  - 제안: `:14005`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 14: `https://hjsim-1034-451984.fortidemo.fortinet.com:14005`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://hjsim-1034-451984.fortidemo.fortinet.com:14005')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 14: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`

### tests/manual/test_hjsim_login.py
- 라인 16: `:14005`
  - 제안: `:14005`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 16: `https://hjsim-1034-451984.fortidemo.fortinet.com:14005`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://hjsim-1034-451984.fortidemo.fortinet.com:14005')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 16: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`

### tests/manual/test_api_user_auth.py
- 라인 14: `:14005`
  - 제안: `:14005`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 14: `https://hjsim-1034-451984.fortidemo.fortinet.com:14005`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://hjsim-1034-451984.fortidemo.fortinet.com:14005')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 14: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`

### tests/manual/test_fortimanager_permissions.py
- 라인 16: `:14005`
  - 제안: `:14005`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 16: `https://hjsim-1034-451984.fortidemo.fortinet.com:14005`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://hjsim-1034-451984.fortidemo.fortinet.com:14005')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 16: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`

### tests/manual/test_api_key_after_config.py
- 라인 14: `:14005`
  - 제안: `:14005`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 14: `https://hjsim-1034-451984.fortidemo.fortinet.com:14005`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://hjsim-1034-451984.fortidemo.fortinet.com:14005')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 14: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`

### tests/manual/test_fortimanager_debug.py
- 라인 14: `:14005`
  - 제안: `:14005`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 14: `https://hjsim-1034-451984.fortidemo.fortinet.com:14005`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://hjsim-1034-451984.fortidemo.fortinet.com:14005')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 14: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`

### tests/manual/test_new_api_key.py
- 라인 21: `host = "hjsim-1034-451984.fortidemo.fortinet.com"`
  - 제안: `host=os.getenv('CUSTOM_HOST', 'host = "hjsim-1034-451984.fortidemo.fortinet.com"')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 21: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`
- 라인 22: `port = 14005`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '14005'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 23: `https://{host}:{port}/jsonrpc`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://{host}:{port}/jsonrpc')`
  - 환경변수: `CUSTOM_ENV_VAR`

### tests/manual/simple_fortimanager_test.py
- 라인 40: `host = "hjsim-1034-451984.fortidemo.fortinet.com"`
  - 제안: `host=os.getenv('CUSTOM_HOST', 'host = "hjsim-1034-451984.fortidemo.fortinet.com"')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 40: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`
- 라인 41: `port = 14005`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '14005'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 43: `https://{host}:{port}/jsonrpc`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://{host}:{port}/jsonrpc')`
  - 환경변수: `CUSTOM_ENV_VAR`

### tests/manual/test_hjsim_comprehensive.py
- 라인 14: `:14005`
  - 제안: `:14005`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 14: `https://hjsim-1034-451984.fortidemo.fortinet.com:14005`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://hjsim-1034-451984.fortidemo.fortinet.com:14005')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 14: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`

### tests/manual/test_adom_permissions.py
- 라인 14: `:14005`
  - 제안: `:14005`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 14: `https://hjsim-1034-451984.fortidemo.fortinet.com:14005`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://hjsim-1034-451984.fortidemo.fortinet.com:14005')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 14: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`

### tests/manual/test_fortimanager_simple.py
- 라인 13: `:14005`
  - 제안: `:14005`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 13: `https://hjsim-1034-451984.fortidemo.fortinet.com:14005`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://hjsim-1034-451984.fortidemo.fortinet.com:14005')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 13: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`

### tests/manual/test_session_login.py
- 라인 14: `:14005`
  - 제안: `:14005`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 14: `https://hjsim-1034-451984.fortidemo.fortinet.com:14005`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://hjsim-1034-451984.fortidemo.fortinet.com:14005')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 14: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`

### tests/manual/test_basic_connection.py
- 라인 12: `:14005`
  - 제안: `:14005`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 12: `https://hjsim-1034-451984.fortidemo.fortinet.com:14005`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://hjsim-1034-451984.fortidemo.fortinet.com:14005')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 12: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`

### tests/manual/test_api_key_session.py
- 라인 14: `:14005`
  - 제안: `:14005`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 14: `https://hjsim-1034-451984.fortidemo.fortinet.com:14005`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://hjsim-1034-451984.fortidemo.fortinet.com:14005')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 14: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`

### tests/manual/test_fortimanager_correct_auth.py
- 라인 14: `:14005`
  - 제안: `:14005`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 14: `https://hjsim-1034-451984.fortidemo.fortinet.com:14005`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://hjsim-1034-451984.fortidemo.fortinet.com:14005')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 14: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`

### tests/manual/test_fortimanager_auth_methods.py
- 라인 16: `:14005`
  - 제안: `:14005`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 16: `https://hjsim-1034-451984.fortidemo.fortinet.com:14005`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://hjsim-1034-451984.fortidemo.fortinet.com:14005')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 16: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`

### tests/manual/check_1411_config.py
- 라인 13: `:14005`
  - 제안: `:14005`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 13: `https://hjsim-1034-451984.fortidemo.fortinet.com:14005`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://hjsim-1034-451984.fortidemo.fortinet.com:14005')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 13: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`

### tests/unit/test_monitoring/test_monitoring_system.py
- 라인 33: `: 3600`
  - 제안: `: 3600`
  - 환경변수: `CUSTOM_ENV_VAR`

### tests/unit/test_api/test_base_client.py
- 라인 30: `host='test.example.com'`
  - 제안: `host=os.getenv('CUSTOM_HOST', 'host='test.example.com'')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 44: `https://test.example.com`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://test.example.com')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 49: `host='test.example.com'`
  - 제안: `host=os.getenv('CUSTOM_HOST', 'host='test.example.com'')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 50: `port=8080`
  - 제안: `port=int(os.getenv('HEALTH_CHECK_PORT', '8080'))`
  - 환경변수: `HEALTH_CHECK_PORT`
- 라인 52: `:8080`
  - 제안: `:8080`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 52: `https://test.example.com:8080`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://test.example.com:8080')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 90: `http://test.com/api`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://test.com/api')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 99: `http://test.com/api`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://test.com/api')`
  - 환경변수: `CUSTOM_ENV_VAR`

### tests/unit/test_core/test_config_manager.py
- 라인 41: `: 7777`
  - 제안: `: 7777`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 71: `: 8080`
  - 제안: `: 8080`
  - 환경변수: `CUSTOM_ENV_VAR`

### scripts/utils/remove_hardcoded_values.py
- 라인 22: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 27: `:7777`
  - 제안: `:7777`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 140: `: 7777`
  - 제안: `: 7777`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 141: `: 6666`
  - 제안: `: 6666`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 142: `: 8765`
  - 제안: `: 8765`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 183: `PORT=7777`
  - 제안: `port=int(os.getenv('WEB_APP_PORT', '7777'))`
  - 환경변수: `WEB_APP_PORT`
- 라인 184: `PORT=6666`
  - 제안: `port=int(os.getenv('MOCK_SERVER_PORT', '6666'))`
  - 환경변수: `MOCK_SERVER_PORT`
- 라인 185: `PORT=8765`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '8765'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 189: `PORT=541`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '541'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 196: `PORT=443`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '443'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 202: `PORT=514`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '514'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 213: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 214: `PORT=5432`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '5432'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 220: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 221: `PORT=6379`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '6379'))`
  - 환경변수: `CUSTOM_ENV_VAR`

### scripts/utils/remove_hardcoding.py
- 라인 40: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 40: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 115: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 116: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 128: `:7777`
  - 제안: `:7777`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 128: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 129: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 129: `http://localhost:{os.getenv(`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://localhost:{os.getenv(')`
  - 환경변수: `CUSTOM_ENV_VAR`

### scripts/utils/fix_critical_hardcoding.py
- 라인 23: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 29: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 43: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 44: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 64: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 65: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 147: `PORT=7777`
  - 제안: `port=int(os.getenv('WEB_APP_PORT', '7777'))`
  - 환경변수: `WEB_APP_PORT`
- 라인 148: `PORT=7777`
  - 제안: `port=int(os.getenv('WEB_APP_PORT', '7777'))`
  - 환경변수: `WEB_APP_PORT`
- 라인 150: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 151: `PORT=6666`
  - 제안: `port=int(os.getenv('MOCK_SERVER_PORT', '6666'))`
  - 환경변수: `MOCK_SERVER_PORT`
- 라인 160: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 166: `PORT=443`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '443'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 175: `PORT=541`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '541'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 186: `PORT=514`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '514'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 193: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 194: `PORT=5432`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '5432'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 202: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 203: `PORT=6379`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '6379'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 224: `PORT=9090`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '9090'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 225: `PORT=8080`
  - 제안: `port=int(os.getenv('HEALTH_CHECK_PORT', '8080'))`
  - 환경변수: `HEALTH_CHECK_PORT`
- 라인 226: `PORT=8765`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '8765'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 232: `PORT=587`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '587'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 257: `PORT=7777`
  - 제안: `port=int(os.getenv('WEB_APP_PORT', '7777'))`
  - 환경변수: `WEB_APP_PORT`

### scripts/utils/fortimanager_improvements_completed.py
- 라인 245: `:7777`
  - 제안: `:7777`
  - 환경변수: `CUSTOM_ENV_VAR`

### scripts/utils/refactoring_examples.py
- 라인 17: `port = 7777`
  - 제안: `port=int(os.getenv('WEB_APP_PORT', '7777'))`
  - 환경변수: `WEB_APP_PORT`
- 라인 18: `port = 6666`
  - 제안: `port=int(os.getenv('MOCK_SERVER_PORT', '6666'))`
  - 환경변수: `MOCK_SERVER_PORT`
- 라인 19: `port = 6379`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '6379'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 42: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 42: `http://localhost:{os.getenv(`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://localhost:{os.getenv(')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 108: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 108: `http://localhost:{app_port}/health`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'http://localhost:{app_port}/health')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 147: `port = 443`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '443'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 148: `https://{host}:443/api/v2`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://{host}:443/api/v2')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 167: `https://{host}:{self.port}{get_api_endpoint(`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://{host}:{self.port}{get_api_endpoint(')`
  - 환경변수: `CUSTOM_ENV_VAR`

### scripts/utils/docker_fortimanager_test.py
- 라인 23: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`
- 라인 24: `: 14005`
  - 제안: `: 14005`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 159: `https://{report_data[`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://{report_data[')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 234: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`
- 라인 235: `PORT=14005`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '14005'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 256: `https://{{host}}/jsonrpc`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://{{host}}/jsonrpc')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 321: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`
- 라인 326: `https://{self.host}:{self.port}/jsonrpc`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://{self.host}:{self.port}/jsonrpc')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 480: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`
- 라인 481: `PORT=14005`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '14005'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 501: `:2000`
  - 제안: `:2000`
  - 환경변수: `CUSTOM_ENV_VAR`

### scripts/utils/create_ppt_report.py
- 라인 20: `host = "hjsim-1034-451984.fortidemo.fortinet.com"`
  - 제안: `host=os.getenv('CUSTOM_HOST', 'host = "hjsim-1034-451984.fortidemo.fortinet.com"')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 20: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`
- 라인 21: `port = 14005`
  - 제안: `port=int(os.getenv('CUSTOM_PORT', '14005'))`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 22: `https://{host}:{port}/jsonrpc`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://{host}:{port}/jsonrpc')`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 131: `: 1200`
  - 제안: `: 1200`
  - 환경변수: `CUSTOM_ENV_VAR`

### scripts/utils/verify_hardcoding_removal.py
- 라인 61: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 61: `localhost`
  - 제안: `localhost`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 62: `:7777`
  - 제안: `:7777`
  - 환경변수: `CUSTOM_ENV_VAR`
- 라인 120: `:7777`
  - 제안: `:7777`
  - 환경변수: `CUSTOM_ENV_VAR`

### scripts/utils/docker_fortimanager_tester.py
- 라인 18: `hjsim-1034-451984.fortidemo.fortinet.com`
  - 제안: `os.getenv('FORTIMANAGER_DEMO_HOST', '')`
  - 환경변수: `FORTIMANAGER_DEMO_HOST`
- 라인 23: `https://{self.host}:{self.port}/jsonrpc`
  - 제안: `os.getenv('EXTERNAL_SERVICE_URL', 'https://{self.host}:{self.port}/jsonrpc')`
  - 환경변수: `CUSTOM_ENV_VAR`
