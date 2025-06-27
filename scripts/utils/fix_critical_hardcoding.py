#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Critical Hardcoding Fix Script
중요한 하드코딩된 값들을 우선적으로 수정
"""

import os
import re
from pathlib import Path

# 수정할 파일들과 대체 규칙
CRITICAL_FIXES = {
    'src/config/network.py': [
        # 기본 네트워크 설정을 환경변수로 변경
        (r"'internal_networks':\s*\[.*?\]", 
         "'internal_networks': os.getenv('INTERNAL_NETWORKS', '192.168.0.0/16,172.16.0.0/12,10.0.0.0/8').split(',')"),
        
        (r"'trusted_proxies':\s*\[.*?\]",
         "'trusted_proxies': os.getenv('TRUSTED_PROXIES', '127.0.0.1,::1').split(',')"),
        
        (r"'allowed_hosts':\s*\[.*?\]",
         "'allowed_hosts': os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')"),
    ],
    
    'src/config/services.py': [
        # 서비스 설정에서 하드코딩된 호스트/포트 제거
        (r"'default_host':\s*'[^']*'",
         "'default_host': os.getenv('FORTIGATE_DEFAULT_HOST', 'localhost')"),
        
        (r"'default_port':\s*\d+",
         "'default_port': int(os.getenv('FORTIGATE_DEFAULT_PORT', '443'))"),
         
        (r"'fortimanager':\s*{\s*'default_port':\s*\d+",
         "'fortimanager': {'default_port': int(os.getenv('FORTIMANAGER_DEFAULT_PORT', '541'))"),
    ],
    
    'src/web_app.py': [
        # Flask 앱의 하드코딩된 포트 제거
        (r"port\s*=\s*\d+",
         "port=int(os.getenv('WEB_APP_PORT', '7777'))"),
        
        (r"host\s*=\s*['\"]localhost['\"]",
         "host=os.getenv('WEB_APP_HOST', 'localhost')"),
         
        (r"host\s*=\s*['\"]127\.0\.0\.1['\"]",
         "host=os.getenv('WEB_APP_HOST', '127.0.0.1')"),
    ],
    
    'src/main.py': [
        # 메인 실행 파일의 하드코딩 제거
        (r"port\s*=\s*\d+",
         "port=int(os.getenv('APP_PORT', '7777'))"),
        
        (r"debug\s*=\s*(True|False)",
         "debug=os.getenv('DEBUG', 'False').lower() == 'true'"),
    ],
    
    'src/utils/mock_server.py': [
        # Mock 서버의 하드코딩 제거
        (r"port\s*=\s*\d+",
         "port=int(os.getenv('MOCK_SERVER_PORT', '6666'))"),
        
        (r"host\s*=\s*['\"]localhost['\"]",
         "host=os.getenv('MOCK_SERVER_HOST', 'localhost')"),
    ]
}

# 필요한 import 문 추가
IMPORT_ADDITIONS = {
    'src/config/network.py': "import os\n",
    'src/config/services.py': "import os\n",
    'src/web_app.py': "import os\n",
    'src/main.py': "import os\n",
    'src/utils/mock_server.py': "import os\n"
}

def add_import_if_needed(file_path: str, content: str) -> str:
    """필요한 import 문 추가"""
    if file_path in IMPORT_ADDITIONS:
        import_line = IMPORT_ADDITIONS[file_path]
        if 'import os' not in content:
            # 첫 번째 import 문 뒤에 os import 추가
            lines = content.split('\n')
            import_idx = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    import_idx = i + 1
                elif line.strip() and not line.startswith('#'):
                    break
            
            lines.insert(import_idx, import_line.strip())
            content = '\n'.join(lines)
    
    return content

def fix_file(file_path: str) -> bool:
    """파일의 하드코딩 수정"""
    if not os.path.exists(file_path):
        print(f"⚠️  파일을 찾을 수 없습니다: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # import 문 추가
        content = add_import_if_needed(file_path, content)
        
        # 하드코딩 수정
        if file_path in CRITICAL_FIXES:
            for pattern, replacement in CRITICAL_FIXES[file_path]:
                content = re.sub(pattern, replacement, content)
        
        # 변경사항이 있으면 파일 저장
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 수정 완료: {file_path}")
            return True
        else:
            print(f"ℹ️  변경사항 없음: {file_path}")
            return False
    
    except Exception as e:
        print(f"❌ 오류 발생 ({file_path}): {e}")
        return False

def create_enhanced_env_file():
    """향상된 .env.example 파일 생성"""
    env_content = """# FortiGate Nextrade - Environment Configuration
# Copy this file to .env and fill in your actual values

# ============================================================================
# Application Settings
# ============================================================================
APP_MODE=production
DEBUG=false
LOG_LEVEL=info

# ============================================================================
# Network Configuration
# ============================================================================
WEB_APP_HOST=0.0.0.0
WEB_APP_PORT=7777
APP_PORT=7777

MOCK_SERVER_HOST=localhost
MOCK_SERVER_PORT=6666

# Internal network ranges (comma-separated)
INTERNAL_NETWORKS=192.168.0.0/16,172.16.0.0/12,10.0.0.0/8

# Trusted proxy addresses (comma-separated)
TRUSTED_PROXIES=127.0.0.1,::1

# Allowed hosts (comma-separated)
ALLOWED_HOSTS=localhost,127.0.0.1

# ============================================================================
# FortiGate Configuration
# ============================================================================
FORTIGATE_DEFAULT_HOST=your-fortigate-host.com
FORTIGATE_DEFAULT_PORT=443
FORTIGATE_HOST=${FORTIGATE_DEFAULT_HOST}
FORTIGATE_PORT=${FORTIGATE_DEFAULT_PORT}
FORTIGATE_API_TOKEN=your-api-token-here
FORTIGATE_VERIFY_SSL=false

# ============================================================================
# FortiManager Configuration
# ============================================================================
FORTIMANAGER_DEFAULT_PORT=541
FORTIMANAGER_HOST=your-fortimanager-host.com
FORTIMANAGER_PORT=${FORTIMANAGER_DEFAULT_PORT}
FORTIMANAGER_USERNAME=your-username
FORTIMANAGER_PASSWORD=your-password
FORTIMANAGER_VERIFY_SSL=false

# ============================================================================
# FortiAnalyzer Configuration
# ============================================================================
FORTIANALYZER_HOST=your-fortianalyzer-host.com
FORTIANALYZER_PORT=514
FORTIANALYZER_USERNAME=your-username
FORTIANALYZER_PASSWORD=your-password

# ============================================================================
# Database Configuration (Optional)
# ============================================================================
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fortigate_nextrade
DB_USER=dbuser
DB_PASSWORD=dbpassword

# ============================================================================
# Redis Configuration (Optional)
# ============================================================================
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# ============================================================================
# Security Settings
# ============================================================================
SECRET_KEY=change-this-to-a-secure-random-key
JWT_SECRET_KEY=change-this-to-another-secure-key
ENCRYPTION_KEY=change-this-to-encryption-key

# ============================================================================
# Path Configuration
# ============================================================================
BASE_DIR=.
DATA_DIR=./data
LOG_DIR=./logs
TEMP_DIR=/tmp

# ============================================================================
# Monitoring & Metrics (Optional)
# ============================================================================
METRICS_PORT=9090
HEALTH_CHECK_PORT=8080
WEBSOCKET_PORT=8765

# ============================================================================
# External Services (Optional)
# ============================================================================
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-email-password

# ============================================================================
# Development Settings
# ============================================================================
# Uncomment for development
# DEBUG=true
# LOG_LEVEL=debug
# APP_MODE=test
"""

    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(env_content)
    print("✅ 향상된 .env.example 파일 생성 완료")

def create_docker_env():
    """Docker용 환경변수 파일 생성"""
    docker_env = """# Docker Environment Variables
# These variables are automatically loaded in Docker containers

APP_MODE=production
DEBUG=false
WEB_APP_HOST=0.0.0.0
WEB_APP_PORT=7777

# Use Docker network hostnames
FORTIGATE_DEFAULT_HOST=fortigate
FORTIMANAGER_HOST=fortimanager
FORTIANALYZER_HOST=fortianalyzer

# Internal Docker networks
INTERNAL_NETWORKS=172.16.0.0/12,10.0.0.0/8

# Container paths
DATA_DIR=/app/data
LOG_DIR=/app/logs
TEMP_DIR=/tmp
"""
    
    with open('.env.docker', 'w', encoding='utf-8') as f:
        f.write(docker_env)
    print("✅ Docker용 .env.docker 파일 생성 완료")

def main():
    """메인 실행 함수"""
    print("🔧 중요한 하드코딩 값 수정 시작...")
    
    fixed_count = 0
    total_files = len(CRITICAL_FIXES)
    
    for file_path in CRITICAL_FIXES.keys():
        if fix_file(file_path):
            fixed_count += 1
    
    # 환경변수 파일들 생성
    create_enhanced_env_file()
    create_docker_env()
    
    print(f"\n📊 수정 완료:")
    print(f"- 수정된 파일: {fixed_count}/{total_files}개")
    print(f"- 생성된 템플릿: .env.example, .env.docker")
    
    if fixed_count > 0:
        print(f"\n⚠️  중요: .env 파일을 생성하고 실제 값을 입력하세요:")
        print(f"   cp .env.example .env")
        print(f"   # .env 파일을 편집하여 실제 값 입력")

if __name__ == "__main__":
    main()