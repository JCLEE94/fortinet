#!/usr/bin/env python3
"""
하드코딩된 값 제거 및 환경변수화 자동화 스크립트
"""
import os
import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime

# 환경변수 기본값 가져오기
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))
from config.env_defaults import EnvironmentDefaults

class HardcodingRemover:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.config_db_path = self.project_root / 'data' / 'hardcoded_values_db.json'
        self.load_config_db()
        
    def load_config_db(self):
        """설정 데이터베이스 로드"""
        try:
            with open(self.config_db_path, 'r', encoding='utf-8') as f:
                self.config_db = json.load(f)
        except FileNotFoundError:
            print(f"❌ 설정 DB를 찾을 수 없습니다: {self.config_db_path}")
            sys.exit(1)
    
    def find_hardcoded_patterns(self) -> List[Tuple[str, str, int, str]]:
        """하드코딩된 패턴 찾기"""
        patterns = [
            # 포트 하드코딩
            (r'port\s*=\s*(\d+)', 'port_hardcoding'),
            (r':\s*(\d{4,5})(?!\d)', 'port_in_url'),
            # 호스트 하드코딩  
            (r'host\s*=\s*[\'"]([^\'\"]+)[\'"]', 'host_hardcoding'),
            (r'localhost', 'localhost_hardcoding'),
            # URL 하드코딩
            (r'https?://[^\s\'"]+', 'url_hardcoding'),
            # FortiManager 하드코딩
            (r'hjsim-1034-[^\.]+\.fortidemo\.fortinet\.com', 'fortimanager_demo_host'),
            # 임계값 하드코딩
            (r'threshold[_\w]*\s*=\s*(\d+)', 'threshold_hardcoding'),
            (r'max_[a-z_]+\s*=\s*(\d+)', 'limit_hardcoding'),
        ]
        
        found_patterns = []
        
        # Python 파일만 검색
        python_files = list(self.project_root.rglob('*.py'))
        
        for file_path in python_files:
            # 제외할 디렉토리
            if any(exclude in str(file_path) for exclude in ['.git', '__pycache__', '.pytest_cache', 'venv']):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                for line_num, line in enumerate(lines, 1):
                    for pattern, pattern_type in patterns:
                        matches = re.finditer(pattern, line, re.IGNORECASE)
                        for match in matches:
                            found_patterns.append((
                                str(file_path.relative_to(self.project_root)),
                                pattern_type,
                                line_num,
                                match.group(0)
                            ))
            except Exception as e:
                print(f"⚠️  파일 읽기 오류 {file_path}: {e}")
                
        return found_patterns
    
    def generate_replacement_suggestions(self, patterns: List[Tuple[str, str, int, str]]) -> Dict[str, List[Dict]]:
        """교체 제안 생성"""
        suggestions = {}
        
        for file_path, pattern_type, line_num, matched_text in patterns:
            if file_path not in suggestions:
                suggestions[file_path] = []
                
            suggestion = {
                'line': line_num,
                'pattern_type': pattern_type,
                'original': matched_text,
                'suggested_replacement': self._get_replacement_suggestion(pattern_type, matched_text),
                'env_var_needed': self._get_env_var_name(pattern_type, matched_text)
            }
            
            suggestions[file_path].append(suggestion)
            
        return suggestions
    
    def _get_replacement_suggestion(self, pattern_type: str, matched_text: str) -> str:
        """교체 제안 생성"""
        if pattern_type == 'port_hardcoding':
            if '7777' in matched_text:
                return "port=int(os.getenv('WEB_APP_PORT', '7777'))"
            elif '6666' in matched_text:
                return "port=int(os.getenv('MOCK_SERVER_PORT', '6666'))"
            elif '5000' in matched_text:
                return "port=int(os.getenv('FLASK_PORT', '5000'))"
            elif '8080' in matched_text:
                return "port=int(os.getenv('HEALTH_CHECK_PORT', '8080'))"
            else:
                return f"port=int(os.getenv('CUSTOM_PORT', '{matched_text.split('=')[1].strip()}'))"
                
        elif pattern_type == 'host_hardcoding':
            if 'localhost' in matched_text:
                return "host=os.getenv('SERVICE_HOST', 'localhost')"
            elif '0.0.0.0' in matched_text:
                return "host=os.getenv('BIND_HOST', '0.0.0.0')"
            else:
                return f"host=os.getenv('CUSTOM_HOST', '{matched_text}')"
                
        elif pattern_type == 'fortimanager_demo_host':
            return "os.getenv('FORTIMANAGER_DEMO_HOST', '')"
            
        elif pattern_type == 'url_hardcoding':
            if 'itsm' in matched_text.lower():
                return "os.getenv('ITSM_BASE_URL', '')"
            elif 'localhost:7777' in matched_text:
                return "f\"http://localhost:{os.getenv('WEB_APP_PORT', '7777')}\""
            else:
                return f"os.getenv('EXTERNAL_SERVICE_URL', '{matched_text}')"
                
        elif pattern_type in ['threshold_hardcoding', 'limit_hardcoding']:
            if '5000' in matched_text:
                return f"int(os.getenv('TRAFFIC_HIGH_THRESHOLD', '5000'))"
            elif '1000' in matched_text:
                return f"int(os.getenv('TRAFFIC_MEDIUM_THRESHOLD', '1000'))"
            elif '3000' in matched_text:
                return f"int(os.getenv('RESPONSE_TIME_CRITICAL', '3000'))"
            else:
                return matched_text  # 변경하지 않음
                
        return matched_text
    
    def _get_env_var_name(self, pattern_type: str, matched_text: str) -> str:
        """필요한 환경변수 이름 반환"""
        if pattern_type == 'port_hardcoding':
            if '7777' in matched_text:
                return 'WEB_APP_PORT'
            elif '6666' in matched_text:
                return 'MOCK_SERVER_PORT'
            elif '5000' in matched_text:
                return 'FLASK_PORT'
            elif '8080' in matched_text:
                return 'HEALTH_CHECK_PORT'
        elif pattern_type == 'fortimanager_demo_host':
            return 'FORTIMANAGER_DEMO_HOST'
        elif pattern_type == 'url_hardcoding':
            if 'itsm' in matched_text.lower():
                return 'ITSM_BASE_URL'
                
        return 'CUSTOM_ENV_VAR'
    
    def create_env_file(self, output_path: str = '.env'):
        """환경변수 파일 생성"""
        EnvironmentDefaults.create_env_file(output_path)
        print(f"✅ 환경변수 파일 생성됨: {output_path}")
    
    def generate_report(self, patterns: List[Tuple[str, str, int, str]], 
                       suggestions: Dict[str, List[Dict]]) -> str:
        """하드코딩 제거 보고서 생성"""
        report = []
        report.append("# 하드코딩 제거 보고서")
        report.append(f"생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"총 발견된 패턴: {len(patterns)}개")
        report.append("")
        
        # 패턴 타입별 통계
        pattern_stats = {}
        for _, pattern_type, _, _ in patterns:
            pattern_stats[pattern_type] = pattern_stats.get(pattern_type, 0) + 1
            
        report.append("## 패턴 타입별 통계")
        for pattern_type, count in sorted(pattern_stats.items()):
            report.append(f"- {pattern_type}: {count}개")
        report.append("")
        
        # 파일별 상세 내용
        report.append("## 파일별 하드코딩 항목")
        for file_path, file_suggestions in suggestions.items():
            report.append(f"### {file_path}")
            for suggestion in file_suggestions:
                report.append(f"- 라인 {suggestion['line']}: `{suggestion['original']}`")
                report.append(f"  - 제안: `{suggestion['suggested_replacement']}`")
                report.append(f"  - 환경변수: `{suggestion['env_var_needed']}`")
            report.append("")
            
        return '\n'.join(report)
    
    def run_analysis(self) -> Tuple[List[Tuple[str, str, int, str]], Dict[str, List[Dict]]]:
        """하드코딩 분석 실행"""
        print("🔍 하드코딩된 값 검색 중...")
        patterns = self.find_hardcoded_patterns()
        
        print(f"📊 총 {len(patterns)}개의 하드코딩 패턴 발견")
        
        print("💡 교체 제안 생성 중...")
        suggestions = self.generate_replacement_suggestions(patterns)
        
        return patterns, suggestions

def main():
    if len(sys.argv) < 2:
        print("사용법: python remove_hardcoding.py <project_root>")
        sys.exit(1)
        
    project_root = sys.argv[1]
    
    print("🚀 하드코딩 제거 도구 시작")
    print(f"📁 프로젝트 루트: {project_root}")
    
    remover = HardcodingRemover(project_root)
    
    # 분석 실행
    patterns, suggestions = remover.run_analysis()
    
    # 환경변수 파일 생성
    print("📝 환경변수 파일 생성 중...")
    remover.create_env_file(os.path.join(project_root, '.env.template'))
    
    # 보고서 생성
    print("📋 보고서 생성 중...")
    report = remover.generate_report(patterns, suggestions)
    
    report_path = os.path.join(project_root, 'hardcoding_removal_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 보고서 생성됨: {report_path}")
    
    # 요약 출력
    print("\n📊 요약:")
    print(f"- 총 하드코딩 패턴: {len(patterns)}개")
    print(f"- 영향받는 파일: {len(suggestions)}개")
    print(f"- 환경변수 파일: .env.template")
    print(f"- 상세 보고서: {report_path}")
    
    if len(patterns) > 0:
        print("\n⚠️  하드코딩된 값들이 발견되었습니다. 보고서를 확인하여 수동으로 수정하세요.")
    else:
        print("\n✅ 하드코딩된 값이 발견되지 않았습니다!")

if __name__ == "__main__":
    main()