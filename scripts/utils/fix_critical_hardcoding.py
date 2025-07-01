#!/usr/bin/env python3
"""
중요한 하드코딩 값들 우선 수정 스크립트
"""
import os
import re
import sys
from pathlib import Path

def fix_fortimanager_hardcoding():
    """FortiManager 하드코딩된 호스트 수정"""
    print("🔧 FortiManager 하드코딩 수정 중...")
    
    # 수정할 파일들과 패턴
    files_to_fix = [
        'tests/manual/test_*.py',
        'scripts/utils/*.py'
    ]
    
    # 패턴 매칭
    patterns = [
        (r'BASE_URL = "https://hjsim-1034-\d+-\d+\.fortidemo\.fortinet\.com:\d+"',
         'BASE_URL = f"https://{os.getenv(\'FORTIMANAGER_DEMO_HOST\', \'demo.fortinet.com\')}:{os.getenv(\'FORTIMANAGER_PORT\', \'14005\')}"'),
        
        (r"host = \"hjsim-1034-\d+-\d+\.fortidemo\.fortinet\.com\"",
         'host = os.getenv(\'FORTIMANAGER_DEMO_HOST\', \'demo.fortinet.com\')'),
         
        (r"'host': 'hjsim-1034-\d+-\d+\.fortidemo\.fortinet\.com'",
         "'host': os.getenv('FORTIMANAGER_DEMO_HOST', 'demo.fortinet.com')"),
    ]
    
    project_root = Path('.')
    
    # 모든 Python 파일에서 패턴 찾아 수정
    for pattern_glob in files_to_fix:
        for file_path in project_root.glob(pattern_glob):
            if file_path.is_file():
                fix_file_patterns(file_path, patterns)

def fix_port_hardcoding():
    """포트 하드코딩 수정"""
    print("🔧 포트 하드코딩 수정 중...")
    
    patterns = [
        # 웹앱 포트
        (r"port=7777", "port=int(os.getenv('WEB_APP_PORT', '7777'))"),
        (r"'port': 7777", "'port': int(os.getenv('WEB_APP_PORT', '7777'))"),
        (r":7777", f":{os.getenv('WEB_APP_PORT', '7777')}"),
        
        # 목 서버 포트
        (r"port=6666", "port=int(os.getenv('MOCK_SERVER_PORT', '6666'))"),
        (r"'port': 6666", "'port': int(os.getenv('MOCK_SERVER_PORT', '6666'))"),
        
        # Flask 포트
        (r"port=5000", "port=int(os.getenv('FLASK_PORT', '5000'))"),
        (r"'port': 5000", "'port': int(os.getenv('FLASK_PORT', '5000'))"),
    ]
    
    # 주요 설정 파일들
    critical_files = [
        'src/config/unified_settings.py',
        'src/config/ports.py', 
        'src/web_app.py',
        'src/main.py'
    ]
    
    for file_path in critical_files:
        if Path(file_path).exists():
            fix_file_patterns(Path(file_path), patterns)

def fix_url_hardcoding():
    """URL 하드코딩 수정"""
    print("🔧 URL 하드코딩 수정 중...")
    
    patterns = [
        # localhost URLs
        (r'f"http://localhost:{os.getenv('WEB_APP_PORT', '7777')}', 'f"http://localhost:{os.getenv(\'WEB_APP_PORT\', \'7777\')}'),
        (r"f'http://localhost:{os.getenv('WEB_APP_PORT', '7777')}", "f'http://localhost:{os.getenv('WEB_APP_PORT', '7777')}"),
        
        # ITSM URLs
        (r'"https://itsm2\.nxtd\.co\.kr"', 'os.getenv(\'ITSM_BASE_URL\', \'\')'),
        (r"'https://itsm2\.nxtd\.co\.kr'", "os.getenv('ITSM_BASE_URL', '')"),
    ]
    
    files_to_check = [
        'src/routes/*.py',
        'src/utils/*.py',
        'scripts/utils/*.py'
    ]
    
    project_root = Path('.')
    for pattern_glob in files_to_check:
        for file_path in project_root.glob(pattern_glob):
            if file_path.is_file():
                fix_file_patterns(file_path, patterns)

def fix_file_patterns(file_path: Path, patterns: list):
    """파일에서 패턴 수정"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        modified = False
        
        for pattern, replacement in patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                modified = True
                print(f"  ✅ {file_path}: 패턴 수정됨")
        
        # os 임포트 추가 (필요한 경우)
        if modified and 'os.getenv' in content and 'import os' not in content:
            if content.startswith('#!/usr/bin/env python3'):
                # shebang 다음에 추가
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('#') or line.strip() == '':
                        continue
                    lines.insert(i, 'import os')
                    break
                content = '\n'.join(lines)
            else:
                content = 'import os\n' + content
            print(f"  📦 {file_path}: os 임포트 추가됨")
        
        # 변경사항이 있으면 파일 저장
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  💾 {file_path}: 파일 저장됨")
            
    except Exception as e:
        print(f"  ❌ {file_path}: 오류 발생 - {e}")

def create_production_env():
    """운영 환경 .env 파일 생성"""
    print("📝 운영 환경 .env 파일 생성...")
    
    env_content = f"""# FortiGate Nextrade 운영 환경 설정
# 생성일: {os.popen('date').read().strip()}

# 네트워크 포트 설정
WEB_APP_HOST=0.0.0.0
WEB_APP_PORT=7777
APP_PORT=7777

# 애플리케이션 설정
APP_MODE=production
DEBUG=false
PROJECT_NAME=fortinet

# 목 서버 설정 (개발용)
MOCK_SERVER_HOST=localhost
MOCK_SERVER_PORT=6666

# 인프라 포트
REDIS_PORT=6379
FLASK_PORT=5000
METRICS_PORT=9090
HEALTH_CHECK_PORT=8080
WEBSOCKET_PORT=8765

# FortiManager 설정 (보안상 별도 설정 필요)
# FORTIMANAGER_DEMO_HOST=your-demo-host
# FORTIMANAGER_DEMO_USER=your-username  
# FORTIMANAGER_DEMO_PASS=your-password
FORTIMANAGER_PORT=14005
FORTIMANAGER_TIMEOUT=30
FORTIMANAGER_VERIFY_SSL=false
FORTIMANAGER_DEFAULT_ADOM=root

# FortiGate 설정
FORTIGATE_PORT=443
FORTIGATE_USERNAME=admin
FORTIGATE_TIMEOUT=30
FORTIGATE_VERIFY_SSL=false

# 보안 임계값
TRAFFIC_HIGH_THRESHOLD=5000
TRAFFIC_MEDIUM_THRESHOLD=1000
RESPONSE_TIME_WARNING=1000
RESPONSE_TIME_CRITICAL=3000

# 외부 서비스
INTERNET_CHECK_URL=http://8.8.8.8
DNS_SERVER=8.8.8.8

# 보안 설정
MAX_SECURITY_EVENTS=5000
SECURITY_ALLOWED_PORTS=22,80,443,7777

# 기능 플래그
OFFLINE_MODE=false
DISABLE_SOCKETIO=false
DISABLE_EXTERNAL_CALLS=false
REDIS_ENABLED=true
"""

    with open('.env.production', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ .env.production 파일 생성됨")

def main():
    print("🚀 중요 하드코딩 수정 시작")
    
    # 1. FortiManager 하드코딩 수정
    fix_fortimanager_hardcoding()
    
    # 2. 포트 하드코딩 수정
    fix_port_hardcoding()
    
    # 3. URL 하드코딩 수정  
    fix_url_hardcoding()
    
    # 4. 운영 환경 파일 생성
    create_production_env()
    
    print("\n✅ 중요 하드코딩 수정 완료!")
    print("📋 수정된 내용:")
    print("  - FortiManager 데모 호스트 → 환경변수")
    print("  - 포트 번호 → 환경변수")
    print("  - URL → 환경변수")
    print("  - .env.production 파일 생성")
    print("\n⚠️  주의사항:")
    print("  - FortiManager 데모 환경변수를 설정하세요")
    print("  - 운영 환경에서는 민감한 정보를 별도 관리하세요")
    print("  - 변경된 코드를 테스트하세요")

if __name__ == "__main__":
    main()