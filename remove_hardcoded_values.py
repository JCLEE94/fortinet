#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remove Hardcoded Values Script
하드코딩된 값들을 찾아서 환경변수나 설정 파일로 이동
"""

import os
import re
import json
from typing import Dict, List, Tuple
from pathlib import Path

# 검색할 하드코딩 패턴들
HARDCODED_PATTERNS = {
    # IP 주소 패턴
    'ip_addresses': [
        r'192\.168\.\d+\.\d+',
        r'172\.(1[6-9]|2[0-9]|3[0-1])\.\d+\.\d+',
        r'10\.\d+\.\d+\.\d+',
        r'127\.0\.0\.1',
        r'localhost'
    ],
    
    # 포트 번호 패턴
    'ports': [
        r':\d{2,5}(?!\d)',  # :80, :443, :7777 등
        r'port\s*=\s*\d{2,5}',
        r'PORT\s*=\s*\d{2,5}'
    ],
    
    # URL 패턴
    'urls': [
        r'https?://[^\s\'"]+',
        r'fortinet\.com',
        r'fortidemo\.fortinet\.com',
        r'example\.com'
    ],
    
    # 자격증명 패턴
    'credentials': [
        r'(password|passwd|pwd)\s*=\s*["\'][^"\']+["\']',
        r'(api_key|api_token|token)\s*=\s*["\'][^"\']+["\']',
        r'(username|user)\s*=\s*["\'][^"\']+["\']',
        r'SecurityFabric',
        r'admin',
        r'test123',
        r'password123'
    ],
    
    # 파일 경로 패턴
    'paths': [
        r'/home/[^/\s]+',
        r'/var/[^/\s]+',
        r'/tmp/[^/\s]+',
        r'C:\\[^\\]+',
        r'D:\\[^\\]+'
    ]
}

# 제외할 파일/디렉토리
EXCLUDE_PATTERNS = [
    '*.pyc',
    '__pycache__',
    '.git',
    '.env*',
    'node_modules',
    'venv',
    'env',
    '*.log',
    '*.md',
    '*.txt',
    '*.html',
    '*.css',
    '*.js'
]

def find_hardcoded_values(directory: str) -> Dict[str, List[Tuple[str, int, str]]]:
    """
    디렉토리에서 하드코딩된 값 찾기
    
    Returns:
        {파일경로: [(라인번호, 라인내용, 패턴타입), ...]}
    """
    results = {}
    
    for root, dirs, files in os.walk(directory):
        # 제외할 디렉토리 건너뛰기
        dirs[:] = [d for d in dirs if not any(d.startswith(ex.replace('*', '')) for ex in EXCLUDE_PATTERNS)]
        
        for file in files:
            # 제외할 파일 건너뛰기
            if any(file.endswith(ex.replace('*', '')) for ex in EXCLUDE_PATTERNS):
                continue
                
            if not file.endswith('.py'):
                continue
                
            filepath = os.path.join(root, file)
            file_results = []
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for line_num, line in enumerate(lines, 1):
                    # 주석 건너뛰기
                    if line.strip().startswith('#'):
                        continue
                        
                    # 각 패턴 카테고리별로 검사
                    for pattern_type, patterns in HARDCODED_PATTERNS.items():
                        for pattern in patterns:
                            if re.search(pattern, line):
                                # 환경변수 사용 라인은 제외
                                if 'os.getenv' in line or 'os.environ' in line:
                                    continue
                                    
                                file_results.append((line_num, line.strip(), pattern_type))
                                break
            
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
                continue
            
            if file_results:
                results[filepath] = file_results
    
    return results

def generate_config_template(hardcoded_values: Dict[str, List[Tuple[str, int, str]]]) -> Dict[str, Dict]:
    """
    하드코딩된 값들을 기반으로 설정 템플릿 생성
    """
    config_template = {
        'network': {
            'allowed_hosts': [],
            'internal_subnets': ['192.168.0.0/16', '172.16.0.0/12', '10.0.0.0/8'],
            'default_ports': {
                'web_app': 7777,
                'mock_server': 6666,
                'websocket': 8765
            }
        },
        'services': {
            'fortimanager': {
                'host': '${FORTIMANAGER_HOST}',
                'port': '${FORTIMANAGER_PORT:541}',
                'username': '${FORTIMANAGER_USERNAME}',
                'password': '${FORTIMANAGER_PASSWORD}',
                'verify_ssl': '${FORTIMANAGER_VERIFY_SSL:false}'
            },
            'fortigate': {
                'host': '${FORTIGATE_HOST}',
                'port': '${FORTIGATE_PORT:443}',
                'api_token': '${FORTIGATE_API_TOKEN}',
                'verify_ssl': '${FORTIGATE_VERIFY_SSL:false}'
            }
        },
        'paths': {
            'base_dir': '${BASE_DIR:.}',
            'data_dir': '${DATA_DIR:./data}',
            'log_dir': '${LOG_DIR:./logs}',
            'temp_dir': '${TEMP_DIR:/tmp}'
        }
    }
    
    return config_template

def generate_env_template(hardcoded_values: Dict[str, List[Tuple[str, int, str]]]) -> str:
    """
    환경변수 템플릿 생성
    """
    env_template = """# FortiGate Nextrade 환경변수 설정
# 이 파일을 .env로 복사하고 실제 값으로 채워주세요

# 애플리케이션 설정
APP_MODE=production
DEBUG=false
LOG_LEVEL=info

# 네트워크 설정
WEB_APP_PORT=7777
MOCK_SERVER_PORT=6666
WEBSOCKET_PORT=8765

# FortiManager 설정
FORTIMANAGER_HOST=your-fortimanager-host.com
FORTIMANAGER_PORT=541
FORTIMANAGER_USERNAME=your-username
FORTIMANAGER_PASSWORD=your-password
FORTIMANAGER_VERIFY_SSL=false

# FortiGate 설정
FORTIGATE_HOST=your-fortigate-host.com
FORTIGATE_PORT=443
FORTIGATE_API_TOKEN=your-api-token
FORTIGATE_VERIFY_SSL=false

# FortiAnalyzer 설정
FORTIANALYZER_HOST=your-fortianalyzer-host.com
FORTIANALYZER_PORT=514
FORTIANALYZER_USERNAME=your-username
FORTIANALYZER_PASSWORD=your-password

# 경로 설정
BASE_DIR=.
DATA_DIR=./data
LOG_DIR=./logs
TEMP_DIR=/tmp

# 데이터베이스 설정 (선택사항)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fortigate_nextrade
DB_USER=dbuser
DB_PASSWORD=dbpassword

# Redis 설정 (선택사항)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# 보안 설정
SECRET_KEY=generate-a-secure-secret-key
JWT_SECRET_KEY=generate-another-secure-key
ENCRYPTION_KEY=generate-encryption-key
"""
    
    return env_template

def generate_refactoring_report(hardcoded_values: Dict[str, List[Tuple[str, int, str]]]) -> str:
    """
    리팩토링 보고서 생성
    """
    report = """# 하드코딩 제거 리팩토링 보고서

## 개요
총 {} 개 파일에서 {} 개의 하드코딩된 값을 발견했습니다.

## 카테고리별 분석
""".format(len(hardcoded_values), sum(len(v) for v in hardcoded_values.values()))
    
    # 카테고리별 집계
    category_counts = {}
    for file_path, issues in hardcoded_values.items():
        for _, _, category in issues:
            category_counts[category] = category_counts.get(category, 0) + 1
    
    for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        report += f"- {category}: {count}개\n"
    
    report += "\n## 파일별 상세 내역\n\n"
    
    for file_path, issues in sorted(hardcoded_values.items()):
        report += f"### {file_path}\n"
        for line_num, line, category in issues:
            report += f"- Line {line_num} ({category}): `{line[:100]}{'...' if len(line) > 100 else ''}`\n"
        report += "\n"
    
    report += """
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
"""
    
    return report

def main():
    """메인 실행 함수"""
    print("🔍 하드코딩된 값 검색 시작...")
    
    # src 디렉토리 검색
    src_dir = os.path.join(os.path.dirname(__file__), 'src')
    hardcoded_values = find_hardcoded_values(src_dir)
    
    if not hardcoded_values:
        print("✅ 하드코딩된 값을 찾지 못했습니다!")
        return
    
    # 보고서 생성
    report = generate_refactoring_report(hardcoded_values)
    report_path = 'HARDCODED_VALUES_REPORT.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"📄 리팩토링 보고서 생성: {report_path}")
    
    # 환경변수 템플릿 생성
    env_template = generate_env_template(hardcoded_values)
    env_path = '.env.template'
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_template)
    print(f"📄 환경변수 템플릿 생성: {env_path}")
    
    # 설정 템플릿 생성
    config_template = generate_config_template(hardcoded_values)
    config_path = 'config_template.json'
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_template, f, indent=2)
    print(f"📄 설정 템플릿 생성: {config_path}")
    
    # 요약 출력
    print(f"\n📊 요약:")
    print(f"- 검사한 파일: {len(hardcoded_values)}개")
    print(f"- 발견된 하드코딩: {sum(len(v) for v in hardcoded_values.values())}개")
    print(f"\n자세한 내용은 {report_path}를 확인하세요.")

if __name__ == "__main__":
    main()