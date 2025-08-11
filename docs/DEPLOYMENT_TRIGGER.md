# 🚀 GitOps 배포 트리거

## 배포 실행 정보
- **시각**: 2025-01-11 08:40:00 KST
- **전략**: Pull-based GitOps (ArgoCD)
- **대상**: registry.jclee.me/fortinet
- **환경**: Production (fortinet namespace)

## 인프라 준비 완료
- ✅ GitHub Actions 워크플로우 완전 구축
- ✅ K8s 매니페스트 Kustomize 구조 완료
- ✅ ArgoCD Pull-based 전략 적용
- ✅ Docker Compose + Watchtower 자동화

## 배포 실행
이 파일이 추가되면 GitHub Actions가 자동으로 트리거됩니다.

배포 과정:
1. GitHub Actions 실행 (.github/workflows/gitops-pipeline.yml)
2. Docker 빌드 → registry.jclee.me Push
3. Kustomize 매니페스트 업데이트
4. ArgoCD 자동 동기화 감지
5. K8s 클러스터 배포 완료

실시간 모니터링:
- GitHub Actions: https://github.com/jclee/app/actions
- ArgoCD Dashboard: https://argo.jclee.me
- 서비스 접근: https://fortinet.jclee.me