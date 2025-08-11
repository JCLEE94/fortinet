# 배포 가이드 🚀

## 빠른 시작

### 1. 코드 배포
```bash
# 간단한 배포 (권장)
./scripts/deploy-simple.sh

# 또는 수동으로
git push origin main
```

### 2. 배포 확인
- **GitHub Actions**: 빌드 상태 확인
- **ArgoCD**: 3분 이내 자동 동기화
- **애플리케이션**: https://fortinet.jclee.me

## CI/CD 파이프라인

### 구조
```
코드 푸시 → GitHub Actions → registry.jclee.me → ArgoCD → Kubernetes
```

### 자동화 프로세스
1. `main` 브랜치에 푸시
2. 자동 테스트 실행
3. Docker 이미지 빌드 및 registry.jclee.me 푸시
4. Kubernetes 매니페스트 업데이트
5. ArgoCD 자동 배포

## 수동 작업

### ArgoCD 동기화
```bash
argocd app sync fortinet
```

### 이미지 확인
```bash
# 레지스트리 확인
curl https://registry.jclee.me/v2/fortinet/tags/list

# 이미지 풀 (인증 불필요)
docker pull registry.jclee.me/fortinet:latest
```

### 로컬 테스트
```bash
# 테스트 실행
pytest tests/ -v

# Docker 빌드
docker build -f Dockerfile.production -t fortinet:test .

# 로컬 실행
docker run -p 7777:7777 -e APP_MODE=test fortinet:test
```

## 문제 해결

### 배포 실패 시
1. GitHub Actions 로그 확인
2. ArgoCD 앱 상태 확인
3. Pod 로그 확인: `kubectl logs -n fortinet -l app=fortinet`

### 롤백
```bash
# ArgoCD에서 이전 버전으로
argocd app rollback fortinet

# 또는 Git revert
git revert HEAD
git push origin main
```

## 모니터링 링크
- **GitHub Actions**: https://github.com/JCLEE94/fortinet/actions
- **ArgoCD**: https://argo.jclee.me/applications/fortinet
- **Container Registry**: https://registry.jclee.me