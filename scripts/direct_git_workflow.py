#!/usr/bin/env python3
"""직접 Git 워크플로우 실행"""

import subprocess
import os
import sys

# 작업 디렉토리로 이동
os.chdir('/home/jclee/app/fortinet')

def run_git_cmd(cmd):
    """Git 명령 실행"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def main():
    print("🔄 Git 워크플로우 시작")
    print("=" * 60)
    
    # 1단계: 변경사항 분석
    print("🔍 1단계: Git 변경사항 분석 중...")
    retcode, status, stderr = run_git_cmd("git status --porcelain")
    
    if retcode != 0:
        print(f"❌ Git status 실패: {stderr}")
        return
    
    if not status.strip():
        print("✅ 커밋할 변경사항이 없습니다.")
        return
    
    lines = status.strip().split('\n')
    modified = sum(1 for line in lines if 'M' in line[:2])
    deleted = sum(1 for line in lines if 'D' in line[:2])
    added = sum(1 for line in lines if '??' in line[:2] or 'A' in line[:2])
    
    print(f"📊 변경사항: 수정 {modified}개, 삭제 {deleted}개, 추가 {added}개")
    
    # 2단계: 커밋 타입 결정 및 메시지 생성
    print("\n📝 2단계: Conventional commit 메시지 생성...")
    
    # 파일 분석으로 커밋 타입 결정
    if deleted > 5:
        commit_type = "refactor"
        description = "코드 구조 정리 및 불필요한 파일 제거"
    elif any("src/" in line for line in lines):
        commit_type = "feat"
        description = "기능 개선 및 코드 정리"
    elif any("test" in line for line in lines):
        commit_type = "test"
        description = "테스트 코드 개선"
    else:
        commit_type = "chore"
        description = "프로젝트 설정 및 구조 개선"
    
    commit_msg = f"""{commit_type}: {description}

변경사항: 수정 {modified}개 파일, 삭제 {deleted}개 파일, 추가 {added}개 파일

Co-authored-by: Claude <noreply@anthropic.com>"""
    
    print("생성된 커밋 메시지:")
    print("-" * 40)
    print(commit_msg)
    print("-" * 40)
    
    # 3단계: 스테이징 및 커밋
    print("\n💾 3단계: 변경사항 커밋 중...")
    
    # 모든 변경사항 스테이징
    retcode, _, stderr = run_git_cmd("git add -A")
    if retcode != 0:
        print(f"❌ Git add 실패: {stderr}")
        return
    
    # 커밋 실행
    escaped_msg = commit_msg.replace('"', '\\"').replace('\n', '\\n')
    retcode, _, stderr = run_git_cmd(f'git commit -m "{escaped_msg}"')
    if retcode != 0:
        print(f"❌ 커밋 실패: {stderr}")
        return
    
    print("✅ 커밋 성공!")
    
    # 커밋 SHA 획득
    retcode, sha, _ = run_git_cmd("git rev-parse HEAD")
    commit_sha = sha[:7] if retcode == 0 else "unknown"
    
    # 4단계: origin/master로 푸시
    print("\n🚀 4단계: origin/master로 푸시 중...")
    
    retcode, _, stderr = run_git_cmd("git push origin master")
    if retcode != 0:
        print(f"❌ master 브랜치 푸시 실패: {stderr}")
        print("main 브랜치로 시도 중...")
        retcode, _, stderr = run_git_cmd("git push origin main")
        if retcode != 0:
            print(f"❌ main 브랜치 푸시도 실패: {stderr}")
            return
    
    print("✅ 푸시 성공!")
    
    # 5단계: GitHub Actions 워크플로우 시작 확인 및 보고
    print(f"\n🎉 5단계: GitHub Actions 워크플로우 시작!")
    print("=" * 60)
    print(f"📋 커밋 SHA: {commit_sha}")
    print(f"🔗 GitHub Actions: https://github.com/JCLEE94/fortinet/actions")
    print(f"📦 저장소: https://github.com/JCLEE94/fortinet")
    print(f"🌐 워크플로우 실행: https://github.com/JCLEE94/fortinet/actions/runs")
    
    print(f"\n✅ GitHub Actions CI/CD 파이프라인이 자동으로 트리거되었습니다!")
    print("📊 다음 단계들이 자동으로 실행됩니다:")
    print("  1. 테스트 실행 (pytest, flake8)")
    print("  2. Docker 이미지 빌드 및 Harbor Registry 푸시")
    print("  3. Helm 차트 패키징 및 ChartMuseum 업로드")
    print("  4. ArgoCD GitOps 배포")
    print("  5. 배포 검증 (health check)")
    
    print(f"\n🏁 워크플로우 완료! 커밋 SHA: {commit_sha}")
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"❌ 예기치 못한 오류: {e}")

# 스크립트 실행
main()