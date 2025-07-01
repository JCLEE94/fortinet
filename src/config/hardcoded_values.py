"""
하드코딩된 값들을 중앙에서 관리하는 설정 파일
환경변수로 오버라이드 가능
"""
import os
from typing import Dict, List, Any


class NetworkConfig:
    """네트워크 관련 설정"""
    
    # 내부 네트워크 범위
    INTERNAL_NETWORKS = os.getenv('INTERNAL_NETWORKS', '192.168.0.0/16,10.0.0.0/8,172.16.0.0/12').split(',')
    
    # 기본 게이트웨이
    DEFAULT_GATEWAY = os.getenv('DEFAULT_GATEWAY', '192.168.1.1')
    
    # 관리 네트워크
    MANAGEMENT_NETWORK = os.getenv('MANAGEMENT_NETWORK', '192.168.1.0/24')
    
    # DMZ 네트워크
    DMZ_NETWORK = os.getenv('DMZ_NETWORK', '172.16.0.0/24')
    
    # 서브넷 마스크
    SUBNET_MASKS = {
        '/8': '255.0.0.0',
        '/16': '255.255.0.0',
        '/24': '255.255.255.0',
        '/32': '255.255.255.255'
    }


class PortConfig:
    """포트 관련 설정"""
    
    # 애플리케이션 포트
    WEB_APP_PORT = int(os.getenv('WEB_APP_PORT', '7777'))
    FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
    MOCK_SERVER_PORT = int(os.getenv('MOCK_SERVER_PORT', '6666'))
    FORTIGUARD_PORT = int(os.getenv('FORTIGUARD_PORT', '8888'))
    
    # 표준 서비스 포트
    SERVICE_PORTS = {
        'http': 80,
        'https': 443,
        'ssh': 22,
        'ftp': 21,
        'telnet': 23,
        'smtp': 25,
        'dns': 53,
        'dhcp': 67,
        'pop3': 110,
        'imap': 143,
        'snmp': 161,
        'mysql': 3306,
        'postgresql': 5432,
        'redis': 6379,
        'elasticsearch': 9200,
        'rdp': 3389,
        'vnc': 5900
    }


class PathConfig:
    """경로 관련 설정"""
    
    # 애플리케이션 경로
    APP_BASE_PATH = os.getenv('APP_BASE_PATH', '/app')
    DATA_PATH = os.getenv('DATA_PATH', os.path.join(APP_BASE_PATH, 'data'))
    LOGS_PATH = os.getenv('LOGS_PATH', os.path.join(APP_BASE_PATH, 'logs'))
    SRC_PATH = os.getenv('SRC_PATH', os.path.join(APP_BASE_PATH, 'src'))
    
    # 임시 경로
    TEMP_UPLOAD_PATH = os.getenv('TEMP_UPLOAD_PATH', '/tmp/uploads')
    TEMP_DOWNLOAD_PATH = os.getenv('TEMP_DOWNLOAD_PATH', '/tmp/downloads')
    
    # 시스템 경로
    SYSTEM_LOG_PATHS = {
        'auth': '/var/log/auth.log',
        'syslog': '/var/log/syslog',
        'messages': '/var/log/messages'
    }
    
    # Docker 소켓
    DOCKER_SOCKET = os.getenv('DOCKER_SOCKET', '/var/run/docker.sock')


class ThresholdConfig:
    """임계값 관련 설정"""
    
    # 트래픽 임계값
    TRAFFIC_HIGH_THRESHOLD = int(os.getenv('TRAFFIC_HIGH_THRESHOLD', '5000'))
    TRAFFIC_MEDIUM_THRESHOLD = int(os.getenv('TRAFFIC_MEDIUM_THRESHOLD', '3000'))
    TRAFFIC_LOW_THRESHOLD = int(os.getenv('TRAFFIC_LOW_THRESHOLD', '1000'))
    
    # 성능 임계값
    RESPONSE_TIME_THRESHOLD = int(os.getenv('RESPONSE_TIME_THRESHOLD', '3000'))  # ms
    CPU_HIGH_THRESHOLD = int(os.getenv('CPU_HIGH_THRESHOLD', '80'))  # %
    MEMORY_HIGH_THRESHOLD = int(os.getenv('MEMORY_HIGH_THRESHOLD', '85'))  # %
    
    # 크기 제한
    MAX_EVENT_QUEUE_SIZE = int(os.getenv('MAX_EVENT_QUEUE_SIZE', '5000'))
    MAX_LOG_BUFFER_SIZE = int(os.getenv('MAX_LOG_BUFFER_SIZE', '10000'))
    
    # ID 범위
    RANDOM_ID_MIN = int(os.getenv('RANDOM_ID_MIN', '1000'))
    RANDOM_ID_MAX = int(os.getenv('RANDOM_ID_MAX', '9999'))


class ServiceConfig:
    """서비스 URL 관련 설정"""
    
    # 기본 URL
    BASE_URL = os.getenv('BASE_URL', 'http://localhost')
    WEB_APP_URL = f"{BASE_URL}:{PortConfig.WEB_APP_PORT}"
    MOCK_SERVER_URL = f"{BASE_URL}:{PortConfig.MOCK_SERVER_PORT}"
    
    # 헬스체크 URL
    HEALTH_CHECK_URL = f"{WEB_APP_URL}/api/health"
    
    # FortiManager API
    FORTIMANAGER_HOST = os.getenv('FORTIMANAGER_HOST', 'fortimanager.local')
    FORTIMANAGER_API_URL = f"https://{FORTIMANAGER_HOST}/jsonrpc"


class MockDataConfig:
    """Mock 데이터 관련 설정"""
    
    # 테스트 IP 주소
    TEST_IPS = [
        '192.168.1.10',
        '192.168.1.100',
        '10.0.0.50',
        '172.16.10.100'
    ]
    
    # 테스트 디바이스
    TEST_DEVICES = {
        'gateway': '192.168.1.1',
        'firewall': '192.168.1.254',
        'server': '10.0.0.10',
        'workstation': '192.168.1.100'
    }
    
    # 테스트 인증 정보 (개발 환경 전용)
    TEST_CREDENTIALS = {
        'username': os.getenv('TEST_USERNAME', 'admin'),
        'password': os.getenv('TEST_PASSWORD', 'password'),
        'api_key': os.getenv('TEST_API_KEY', 'test-api-key')
    }


# 통합 설정 클래스
class HardcodedValues:
    """모든 하드코딩된 값들의 중앙 관리"""
    
    network = NetworkConfig()
    ports = PortConfig()
    paths = PathConfig()
    thresholds = ThresholdConfig()
    services = ServiceConfig()
    mock_data = MockDataConfig()
    
    @classmethod
    def get_all_configs(cls) -> Dict[str, Any]:
        """모든 설정을 딕셔너리로 반환"""
        return {
            'network': {
                'internal_networks': cls.network.INTERNAL_NETWORKS,
                'default_gateway': cls.network.DEFAULT_GATEWAY,
                'management_network': cls.network.MANAGEMENT_NETWORK,
                'dmz_network': cls.network.DMZ_NETWORK
            },
            'ports': {
                'web_app': cls.ports.WEB_APP_PORT,
                'flask': cls.ports.FLASK_PORT,
                'mock_server': cls.ports.MOCK_SERVER_PORT,
                'service_ports': cls.ports.SERVICE_PORTS
            },
            'paths': {
                'app_base': cls.paths.APP_BASE_PATH,
                'data': cls.paths.DATA_PATH,
                'logs': cls.paths.LOGS_PATH,
                'src': cls.paths.SRC_PATH
            },
            'thresholds': {
                'traffic_high': cls.thresholds.TRAFFIC_HIGH_THRESHOLD,
                'cpu_high': cls.thresholds.CPU_HIGH_THRESHOLD,
                'memory_high': cls.thresholds.MEMORY_HIGH_THRESHOLD
            },
            'services': {
                'base_url': cls.services.BASE_URL,
                'web_app_url': cls.services.WEB_APP_URL,
                'health_check_url': cls.services.HEALTH_CHECK_URL
            }
        }


# 싱글톤 인스턴스
CONFIG = HardcodedValues()