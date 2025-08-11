# ArgoCD Pipeline Troubleshooting Guide

## 🚨 문제 해결 가이드

### 1. ArgoCD 원격 접속 실패 문제

#### 증상
- GitHub Actions에서 ArgoCD sync 실패
- "Failed to get app status" 에러
- API 토큰 인증 실패

#### 원인
1. **ArgoCD API 토큰 만료 또는 미설정**
2. **Self-hosted runner 환경 문제**
3. **네트워크 접근 제한**

#### 해결 방법

##### Step 1: ArgoCD API 토큰 재생성
```bash
# 1. ArgoCD 로그인
argocd login argo.jclee.me --username admin --password bingogo1 --insecure --grpc-web

# 2. 새 토큰 생성
argocd account generate-token --account admin --grpc-web

# 3. 생성된 토큰을 GitHub Secrets에 추가
# https://github.com/JCLEE94/fortinet/settings/secrets/actions
# ARGOCD_AUTH_TOKEN: <생성된 토큰>
# ARGOCD_PASSWORD: bingogo1
```

##### Step 2: 워크플로우 개선사항 적용
- `self-hosted` runner를 `ubuntu-latest`로 변경
- ArgoCD CLI 자동 설치 추가
- 재시도 로직 추가
- 상세한 로깅 추가

##### Step 3: 수동 동기화 (긴급시)
```bash
# ArgoCD 수동 동기화
argocd app sync fortinet --prune --force

# 또는 ArgoCD UI에서 직접 동기화
# https://argo.jclee.me/applications/fortinet
```

### 2. 파이프라인 안정화 개선사항

#### 주요 변경사항

1. **Runner 환경 변경**
   - `self-hosted` → `ubuntu-latest`
   - 일관된 실행 환경 보장

2. **ArgoCD CLI 설치**
   - 매 실행시 최신 버전 자동 설치
   - 의존성 문제 해결

3. **인증 방식 개선**
   - CLI 로그인 추가 (API 토큰 백업)
   - Password 인증 병행

4. **에러 처리 강화**
   - 재시도 로직 추가
   - 상세 로깅 추가
   - 실패시에도 auto-sync 의존

5. **Git Push 안정성**
   - 재시도 로직 (3회)
   - Rebase 자동 처리

### 3. 모니터링 및 검증

#### 배포 상태 확인
```bash
# ArgoCD 애플리케이션 상태
argocd app get fortinet

# Kubernetes 파드 상태
kubectl get pods -n fortinet

# 애플리케이션 헬스체크
curl -k https://fortinet.jclee.me/api/health
```

#### 로그 확인
```bash
# ArgoCD 로그
kubectl logs -n argocd deployment/argocd-server

# 애플리케이션 로그
kubectl logs -n fortinet -l app=fortinet-app --tail=100
```

### 4. 필수 GitHub Secrets

| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `ARGOCD_AUTH_TOKEN` | ArgoCD API 토큰 | `eyJhbGciOiJIUzI1NiI...` |
| `ARGOCD_PASSWORD` | ArgoCD admin 비밀번호 | `bingogo1` |
| `REGISTRY_USERNAME` | Docker Registry 사용자명 | `qws9411` |
| `REGISTRY_PASSWORD` | Docker Registry 비밀번호 | `your-password` |

### 5. 문제 발생시 체크리스트

- [ ] ArgoCD 서버 접근 가능 여부 확인
- [ ] GitHub Secrets 올바르게 설정되었는지 확인
- [ ] ArgoCD 애플리케이션 상태 확인
- [ ] Kubernetes 클러스터 상태 확인
- [ ] 네트워크 연결 확인

### 6. 자동화 스크립트

토큰 설정을 위한 스크립트:
```bash
./scripts/setup-argocd-auth.sh
```

### 7. 참고 링크

- [ArgoCD Dashboard](https://argo.jclee.me)
- [GitHub Actions](https://github.com/JCLEE94/fortinet/actions)
- [Application URL](https://fortinet.jclee.me)
- [GitHub Secrets Settings](https://github.com/JCLEE94/fortinet/settings/secrets/actions)