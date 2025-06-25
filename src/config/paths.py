"""
File paths configuration module

모든 파일 경로 설정을 중앙화하여 관리합니다.
환경에 따라 동적으로 경로를 설정할 수 있습니다.
"""

import os
from pathlib import Path
from typing import Dict, Optional

# 기본 디렉토리
BASE_DIR = os.getenv('APP_BASE_DIR', '/app')
PROJECT_ROOT = os.getenv('PROJECT_ROOT', '/home/jclee/app/fortinet')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')

# 환경별 기본 경로
if ENVIRONMENT == 'development':
    BASE_DIR = PROJECT_ROOT
elif ENVIRONMENT == 'test':
    BASE_DIR = os.path.join(PROJECT_ROOT, 'test')

# 애플리케이션 경로
APP_PATHS: Dict[str, str] = {
    'base': BASE_DIR,
    'src': os.path.join(BASE_DIR, 'src'),
    'data': os.path.join(BASE_DIR, 'data'),
    'logs': os.path.join(BASE_DIR, 'logs'),
    'config': os.path.join(BASE_DIR, 'data'),
    'static': os.path.join(BASE_DIR, 'src', 'static'),
    'templates': os.path.join(BASE_DIR, 'src', 'templates'),
    'tests': os.path.join(BASE_DIR, 'tests'),
    'docs': os.path.join(BASE_DIR, 'docs'),
    'scripts': os.path.join(BASE_DIR, 'scripts'),
    'migrations': os.path.join(BASE_DIR, 'migrations')
}

# 설정 파일 경로
CONFIG_FILES: Dict[str, str] = {
    'main': os.path.join(APP_PATHS['config'], 'config.json'),
    'default': os.path.join(APP_PATHS['config'], 'default_config.json'),
    'env': os.path.join(BASE_DIR, '.env'),
    'env_example': os.path.join(BASE_DIR, '.env.example'),
    'docker_compose': os.path.join(BASE_DIR, 'docker-compose.yml'),
    'dockerfile': os.path.join(BASE_DIR, 'Dockerfile'),
    'requirements': os.path.join(BASE_DIR, 'requirements.txt'),
    'package_json': os.path.join(BASE_DIR, 'package.json')
}

# 로그 파일 경로
LOG_FILES: Dict[str, str] = {
    'app': os.path.join(APP_PATHS['logs'], 'app.log'),
    'error': os.path.join(APP_PATHS['logs'], 'error.log'),
    'access': os.path.join(APP_PATHS['logs'], 'access.log'),
    'api': os.path.join(APP_PATHS['logs'], 'api.log'),
    'security': os.path.join(APP_PATHS['logs'], 'security.log'),
    'performance': os.path.join(APP_PATHS['logs'], 'performance.log'),
    'audit': os.path.join(APP_PATHS['logs'], 'audit.log'),
    'fortigate': os.path.join(APP_PATHS['logs'], 'fortigate.log'),
    'fortimanager': os.path.join(APP_PATHS['logs'], 'fortimanager.log')
}

# 임시 파일 경로
TEMP_PATHS: Dict[str, str] = {
    'base': os.getenv('TEMP_DIR', '/tmp'),
    'upload': os.getenv('UPLOAD_DIR', '/tmp/uploads'),
    'download': os.getenv('DOWNLOAD_DIR', '/tmp/downloads'),
    'cache': os.path.join(os.getenv('TEMP_DIR', '/tmp'), 'cache'),
    'sessions': os.path.join(os.getenv('TEMP_DIR', '/tmp'), 'sessions'),
    'export': os.path.join(os.getenv('TEMP_DIR', '/tmp'), 'export'),
    'backup': os.path.join(os.getenv('TEMP_DIR', '/tmp'), 'backup')
}

# 시스템 로그 경로 (모니터링용)
SYSTEM_LOG_PATHS: Dict[str, str] = {
    'auth': '/var/log/auth.log',
    'syslog': '/var/log/syslog',
    'messages': '/var/log/messages',
    'docker': '/var/log/docker.log',
    'nginx_access': '/var/log/nginx/access.log',
    'nginx_error': '/var/log/nginx/error.log'
}

# 배포 관련 경로
DEPLOYMENT_PATHS: Dict[str, str] = {
    'monitor_log': '/tmp/deployment_monitor.log',
    'pipeline_log': '/tmp/pipeline_monitor.log',
    'deploy_script': os.path.join(BASE_DIR, 'deploy.sh'),
    'docker_socket': '/var/run/docker.sock',
    'pid_file': '/var/run/fortigate-nextrade.pid'
}

# 서비스별 로그 경로
SERVICE_LOG_PATHS: Dict[str, str] = {
    'fortigate': os.path.join(APP_PATHS['logs'], 'service', 'fortigate'),
    'fortimanager': os.path.join(APP_PATHS['logs'], 'service', 'fortimanager'),
    'fortianalyzer': os.path.join(APP_PATHS['logs'], 'service', 'fortianalyzer'),
    'mock_server': os.path.join(APP_PATHS['logs'], 'service', 'mock')
}

def ensure_directory(path: str) -> str:
    """
    디렉토리가 존재하지 않으면 생성합니다.
    
    Args:
        path: 확인/생성할 디렉토리 경로
        
    Returns:
        디렉토리 경로
    """
    Path(path).mkdir(parents=True, exist_ok=True)
    return path

def get_log_file_path(log_type: str) -> str:
    """
    로그 파일 경로를 반환합니다.
    
    Args:
        log_type: 로그 타입 (app, error, api 등)
        
    Returns:
        로그 파일 경로
    """
    log_dir = ensure_directory(APP_PATHS['logs'])
    return LOG_FILES.get(log_type, os.path.join(log_dir, f'{log_type}.log'))

def get_temp_file_path(filename: str, category: str = 'base') -> str:
    """
    임시 파일 경로를 생성합니다.
    
    Args:
        filename: 파일명
        category: 카테고리 (upload, download, cache 등)
        
    Returns:
        임시 파일 경로
    """
    temp_dir = ensure_directory(TEMP_PATHS.get(category, TEMP_PATHS['base']))
    return os.path.join(temp_dir, filename)

def get_config_file_path(config_type: str = 'main') -> str:
    """
    설정 파일 경로를 반환합니다.
    
    Args:
        config_type: 설정 파일 타입
        
    Returns:
        설정 파일 경로
    """
    return CONFIG_FILES.get(config_type, CONFIG_FILES['main'])

def is_safe_path(path: str, base_path: Optional[str] = None) -> bool:
    """
    경로가 안전한지 확인합니다 (디렉토리 트래버설 방지).
    
    Args:
        path: 확인할 경로
        base_path: 기본 경로 (없으면 BASE_DIR 사용)
        
    Returns:
        안전한 경로 여부
    """
    if base_path is None:
        base_path = BASE_DIR
    
    try:
        # 절대 경로로 변환
        abs_path = os.path.abspath(path)
        abs_base = os.path.abspath(base_path)
        
        # 경로가 base_path 내에 있는지 확인
        return abs_path.startswith(abs_base)
    except Exception:
        return False

# 모든 디렉토리 생성
def initialize_directories():
    """애플리케이션 시작 시 필요한 모든 디렉토리를 생성합니다."""
    for path in APP_PATHS.values():
        ensure_directory(path)
    
    for path in TEMP_PATHS.values():
        ensure_directory(path)
    
    for path in SERVICE_LOG_PATHS.values():
        ensure_directory(path)

# 모든 설정값 내보내기
__all__ = [
    'BASE_DIR',
    'PROJECT_ROOT',
    'ENVIRONMENT',
    'APP_PATHS',
    'CONFIG_FILES',
    'LOG_FILES',
    'TEMP_PATHS',
    'SYSTEM_LOG_PATHS',
    'DEPLOYMENT_PATHS',
    'SERVICE_LOG_PATHS',
    'ensure_directory',
    'get_log_file_path',
    'get_temp_file_path',
    'get_config_file_path',
    'is_safe_path',
    'initialize_directories'
]