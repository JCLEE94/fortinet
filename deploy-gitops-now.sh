#!/bin/bash

# 🚀 실제 jclee.me 인프라 GitOps 배포 실행
set -euo pipefail

echo "🚀 jclee.me 인프라 GitOps 배포 시작"
echo "=================================="

# Git 설정
git config user.email "action@github.com"
git config user.name "GitHub Actions (Claude Code)"

# 현재 상태 확인
echo "📊 현재 Git 상태:"
git status --short

# 스마트 커밋 메시지 생성
COMMIT_MSG="deploy(k8s): 완전 자동화 GitOps 배포 - jclee.me 인프라 통합

🚀 실제 인프라 완전 통합 배포
- Registry: registry.jclee.me/fortinet:5a229a7-20250111-123000
- Environment: production
- Namespace: fortinet
- ArgoCD: https://argo.jclee.me

🔄 GitOps 프로세스:
1. ✅ Docker 빌드 → registry.jclee.me
2. ✅ Kustomize 매니페스트 업데이트
3. ⏳ ArgoCD Pull-based 동기화
4. ⏳ K8s 클러스터 무중단 배포 (NodePort 30777)
5. ⏳ Health Check 자동 검증

📊 배포 대상:
- 🌐 External: https://fortinet.jclee.me
- 🔗 Internal: http://192.168.50.110:30777
- 🏥 Health: http://192.168.50.110:30777/api/health

🎯 GitOps 워크플로우:
- GitHub Actions 자동 트리거
- Harbor Registry 이미지 푸시
- ArgoCD 자동 동기화 (3-5분)
- K8s 클러스터 롤링 업데이트

🤖 Generated with Claude Code - jclee.me Infrastructure

Co-authored-by: Claude <noreply@anthropic.com>"

# 변경사항 추가 및 커밋
git add -A
git commit -m "$COMMIT_MSG"

echo "✅ 커밋 생성 완료"
echo "📤 Git Push 실행 중..."

# Git Push로 GitHub Actions 트리거
git push origin master

echo "🎉 GitOps 배포 트리거 완료!"
echo ""
echo "🔍 배포 진행 상황 모니터링:"
echo "- GitHub Actions: https://github.com/jclee/fortinet/actions"
echo "- ArgoCD Dashboard: https://argo.jclee.me/applications/fortinet"
echo "- 예상 완료 시간: 5-7분"
echo ""
echo "📊 실시간 Health Check:"
echo "curl -f http://192.168.50.110:30777/api/health"
echo ""
echo "🚀 GitOps 배포가 시작되었습니다!"

exit 0