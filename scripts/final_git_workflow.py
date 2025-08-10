#!/usr/bin/env python3
"""
Git 워크플로우 실행 스크립트
1) git diff로 모든 변경사항 분석
2) conventional commit 메시지 생성 (feat/fix/chore)
3) 공동 작성자 추가: Co-authored-by: Claude <noreply@anthropic.com>
4) origin/master로 푸시하여 GitHub Actions 트리거
5) github.com/JCLEE94에서 워크플로우 시작 확인
"""
import subprocess
import sys
import re
from datetime import datetime

def run_command(cmd):
    """명령어 실행 및 결과 반환"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd='/home/jclee/app/fortinet')
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return -1, "", str(e)

def analyze_changes():
    """1단계: Git 변경사항 분석"""
    print("🔍 1단계: Git 변경사항 분석 중...")
    
    # Git status 확인
    retcode, status_output, stderr = run_command("git status --porcelain")
    if retcode != 0:
        print(f"❌ Git status 실패: {stderr}")
        return None
    
    # Git diff --stat으로 변경 통계
    retcode, diff_stat, _ = run_command("git diff --stat")
    
    # Git diff --name-only로 변경된 파일 목록
    retcode, changed_files, _ = run_command("git diff --name-only")
    changed_files_list = changed_files.split('\n') if changed_files else []
    
    # 스테이징되지 않은 변경사항 분석
    changes = status_output.split('\n') if status_output else []
    
    modified_files = []
    deleted_files = []
    added_files = []
    
    for line in changes:
        if line.strip():
            status = line[:2]
            filename = line[3:] if len(line) > 3 else ""
            
            if 'M' in status:
                modified_files.append(filename)
            elif 'D' in status:
                deleted_files.append(filename)
            elif '??' in status or 'A' in status:
                added_files.append(filename)
    
    print(f"📊 변경사항 요약:")
    print(f"  - 수정된 파일: {len(modified_files)}개")
    print(f"  - 삭제된 파일: {len(deleted_files)}개")
    print(f"  - 새 파일: {len(added_files)}개")
    
    if diff_stat:
        print(f"📈 변경 통계:")
        print(diff_stat)
    
    return {
        'modified': modified_files,
        'deleted': deleted_files,
        'added': added_files,
        'changed_files': changed_files_list,
        'diff_stat': diff_stat
    }

def generate_commit_message(changes):
    """2단계: Conventional commit 메시지 생성"""
    print("\n📝 2단계: 커밋 메시지 생성 중...")
    
    modified_files = changes['modified']
    deleted_files = changes['deleted']
    added_files = changes['added']
    
    # 커밋 타입 결정
    commit_type = "chore"
    description = "프로젝트 정리 및 구조 개선"
    
    # 파일 패턴 분석
    if any('src/' in f for f in modified_files):
        if any('test' in f for f in modified_files):
            commit_type = "test"
            description = "테스트 코드 개선"
        else:
            commit_type = "feat"
            description = "기능 개선 및 코드 정리"
    
    if len(deleted_files) > 5:
        commit_type = "refactor"
        description = "코드 구조 정리 및 불필요한 파일 제거"
    
    if any(f.endswith(('.yml', '.yaml', 'docker', 'requirements.txt')) for f in modified_files):
        commit_type = "chore"
        description = "설정 파일 및 의존성 업데이트"
    
    # 영향 영역 식별
    areas = []
    all_files = modified_files + added_files
    
    if any('src/api' in f or 'src/routes' in f for f in all_files):
        areas.append("API")
    if any('src/fortimanager' in f for f in all_files):
        areas.append("FortiManager")
    if any('src/itsm' in f for f in all_files):
        areas.append("ITSM")
    if any('test' in f for f in all_files):
        areas.append("테스트")
    if any(f.startswith('k8s/') or 'docker' in f or 'helm' in f for f in all_files):
        areas.append("인프라")
    if any('src/analysis' in f for f in all_files):
        areas.append("분석")
    
    # 커밋 메시지 구성
    area_text = f" ({', '.join(areas)})" if areas else ""
    
    commit_message = f"{commit_type}: {description}{area_text}\n\n"
    
    # 상세 정보
    details = []
    if len(modified_files) > 0:
        details.append(f"수정: {len(modified_files)}개 파일")
    if len(deleted_files) > 0:
        details.append(f"삭제: {len(deleted_files)}개 파일")
    if len(added_files) > 0:
        details.append(f"추가: {len(added_files)}개 파일")
    
    commit_message += f"변경사항: {', '.join(details)}\n"
    
    if areas:
        commit_message += f"영향 영역: {', '.join(areas)}\n"
    
    # 공동 작성자 추가
    commit_message += "\nCo-authored-by: Claude <noreply@anthropic.com>"
    
    print(f"✅ 생성된 커밋 메시지:")
    print("-" * 50)
    print(commit_message)
    print("-" * 50)
    
    return commit_message

def commit_and_push(commit_message):
    """3-4단계: 커밋 생성 및 origin/master로 푸시"""
    print("\n💾 3단계: 변경사항 커밋 중...")
    
    # 모든 변경사항 스테이징
    retcode, stdout, stderr = run_command("git add -A")
    if retcode != 0:
        print(f"❌ Git add 실패: {stderr}")
        return None
    
    # 커밋 실행 (메시지에 따옴표 이스케이프 처리)
    escaped_message = commit_message.replace('"', '\\"').replace('\n', '\\n')
    retcode, stdout, stderr = run_command(f'git commit -m "{escaped_message}"')
    if retcode != 0:
        print(f"❌ 커밋 실패: {stderr}")
        return None
    
    print("✅ 커밋 완료!")
    
    # 커밋 SHA 획득
    retcode, commit_sha, _ = run_command("git rev-parse HEAD")
    commit_sha = commit_sha[:7] if retcode == 0 else "unknown"
    
    print(f"\n🚀 4단계: origin/master로 푸시 중...")
    retcode, stdout, stderr = run_command("git push origin master")
    if retcode != 0:
        print(f"❌ 푸시 실패: {stderr}")
        return None
    
    print("✅ 푸시 완료!")
    
    return commit_sha

def report_results(commit_sha):
    """5단계: 결과 보고"""
    print(f"\n🎉 5단계: GitHub Actions 워크플로우 시작!")
    print("=" * 60)
    print(f"📋 커밋 SHA: {commit_sha}")
    print(f"🔗 GitHub Actions: https://github.com/JCLEE94/fortinet/actions")
    print(f"📦 저장소: https://github.com/JCLEE94/fortinet")
    print(f"🌐 Actions 워크플로우: https://github.com/JCLEE94/fortinet/actions/runs")
    print("\n✅ GitHub Actions에서 CI/CD 파이프라인이 자동으로 시작됩니다.")
    print("📊 워크플로우 진행상황은 위 링크에서 확인하실 수 있습니다.")

def main():
    """메인 워크플로우 실행"""
    print("🔄 Git 작업 워크플로우 시작")
    print("=" * 60)
    
    # 1단계: 변경사항 분석
    changes = analyze_changes()
    if not changes:
        print("❌ 변경사항 분석 실패")
        return
    
    if not any(changes[key] for key in ['modified', 'deleted', 'added']):
        print("✅ 커밋할 변경사항이 없습니다.")
        return
    
    # 2단계: 커밋 메시지 생성
    commit_message = generate_commit_message(changes)
    
    # 3-4단계: 커밋 및 푸시
    commit_sha = commit_and_push(commit_message)
    if not commit_sha:
        print("❌ 커밋 및 푸시 실패")
        return
    
    # 5단계: 결과 보고
    report_results(commit_sha)

if __name__ == "__main__":
    main()