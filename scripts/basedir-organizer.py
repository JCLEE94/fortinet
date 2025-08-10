#!/usr/bin/env python3
"""
Basedir Advanced Organizer - 파일명 표준화 및 프로젝트 구조 정리
"""
import os
import re
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Set
import json

class BasedirOrganizer:
    def __init__(self, root_path="."):
        self.root = Path(root_path).resolve()
        self.changes = []
        self.duplicates = []
        
    def standardize_filename(self, filename: str) -> str:
        """파일명을 kebab-case로 표준화"""
        # React 컴포넌트는 PascalCase 유지
        if filename.endswith(('.tsx', '.jsx')) and filename[0].isupper():
            return filename
            
        # 설정 파일은 lowercase 유지
        if filename.startswith('.') or filename in ['tsconfig.json', 'package.json']:
            return filename
            
        # 특수문자와 공백을 하이픈으로 변환
        name, ext = os.path.splitext(filename)
        name = re.sub(r'[\s_]+', '-', name)  # 공백과 언더스코어를 하이픈으로
        name = re.sub(r'[^\w\-]', '', name)  # 특수문자 제거
        name = name.lower()  # 소문자로
        name = re.sub(r'-+', '-', name)  # 중복 하이픈 제거
        name = name.strip('-')  # 앞뒤 하이픈 제거
        
        return f"{name}{ext}" if name else filename
        
    def find_duplicates(self) -> List[Dict]:
        """MD5 해시 기반 중복 파일 찾기"""
        file_hashes = {}
        
        for file_path in self.root.rglob('*'):
            if file_path.is_file() and '.git' not in str(file_path):
                try:
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                        
                    if file_hash in file_hashes:
                        self.duplicates.append({
                            'original': str(file_hashes[file_hash]),
                            'duplicate': str(file_path),
                            'hash': file_hash
                        })
                    else:
                        file_hashes[file_hash] = file_path
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                    
        return self.duplicates
        
    def organize_structure(self):
        """프로젝트 구조 재구성"""
        moves = []
        
        # scripts 디렉토리로 스크립트 파일 이동
        for file_path in self.root.rglob('*.sh'):
            if 'scripts' not in str(file_path) and '.git' not in str(file_path):
                target = self.root / 'scripts' / file_path.name
                moves.append((file_path, target))
                
        # configs 디렉토리로 설정 파일 이동
        config_patterns = ['*config*.json', '*config*.yaml', '*config*.yml', '.env*']
        for pattern in config_patterns:
            for file_path in self.root.glob(pattern):
                if 'configs' not in str(file_path):
                    target = self.root / 'configs' / file_path.name
                    moves.append((file_path, target))
                    
        return moves
        
    def clean_backup_files(self):
        """백업 및 임시 파일 삭제"""
        patterns = ['*-backup*', '*-old*', '*-copy*', '*.bak', '*~', '*.tmp']
        removed = []
        
        for pattern in patterns:
            for file_path in self.root.rglob(pattern):
                if '.git' not in str(file_path):
                    removed.append(str(file_path))
                    
        return removed
        
    def execute(self, dry_run=True):
        """실행 (dry_run=True면 미리보기만)"""
        results = {
            'standardized': [],
            'duplicates': self.find_duplicates(),
            'structure_changes': self.organize_structure(),
            'removed_backups': self.clean_backup_files()
        }
        
        # 파일명 표준화
        for file_path in self.root.rglob('*'):
            if file_path.is_file() and '.git' not in str(file_path):
                old_name = file_path.name
                new_name = self.standardize_filename(old_name)
                
                if old_name != new_name:
                    new_path = file_path.parent / new_name
                    results['standardized'].append({
                        'old': str(file_path),
                        'new': str(new_path)
                    })
                    
                    if not dry_run and not new_path.exists():
                        file_path.rename(new_path)
                        
        if not dry_run:
            # 중복 파일 삭제
            for dup in results['duplicates']:
                Path(dup['duplicate']).unlink()
                
            # 백업 파일 삭제
            for backup in results['removed_backups']:
                Path(backup).unlink()
                
            # 구조 변경 실행
            for src, dst in results['structure_changes']:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
                
        return results

if __name__ == "__main__":
    import sys
    
    organizer = BasedirOrganizer()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        print("🚀 실제 정리 실행 중...")
        results = organizer.execute(dry_run=False)
    else:
        print("📋 미리보기 모드 (실제 변경 없음)")
        results = organizer.execute(dry_run=True)
        
    print(f"\n📊 정리 결과:")
    print(f"  - 표준화할 파일: {len(results['standardized'])}개")
    print(f"  - 중복 파일: {len(results['duplicates'])}개")
    print(f"  - 구조 변경: {len(results['structure_changes'])}개")
    print(f"  - 삭제할 백업: {len(results['removed_backups'])}개")
    
    # 결과를 JSON으로 저장
    with open('basedir-cleanup-report.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n✅ 상세 리포트: basedir-cleanup-report.json")