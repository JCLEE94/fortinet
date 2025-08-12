# 🔐 GitHub Repository Secrets 설정 가이드

## GitOps 보안 모델 기반 인증정보 설정

**경로**: Repository Settings → Secrets and Variables → Actions

### 🔑 Secrets (민감 정보 - 암호화 저장)

#### ArgoCD 인증
```bash
# ArgoCD GitOps 컨트롤러 (읽기 전용 권한)
ARGOCD_TOKEN=<ArgoCD API 토큰>
# 얻는 방법:
# argocd account generate-token --account=admin --server=argo.jclee.me
```

#### Docker Registry 인증 (Harbor)
```bash
# Harbor Registry 접근
REGISTRY_USERNAME=<Harbor Registry 사용자명>
REGISTRY_PASSWORD=<Harbor Registry 비밀번호>
# 
# Harbor Admin Console에서 Service Account 생성:
# - registry.jclee.me → Administration → Users → New User
# - Robot Account 생성 (권한: Push + Pull)
```

#### Helm Chart Repository 인증
```bash
# ChartMuseum 접근 (선택적)
CHARTMUSEUM_USERNAME=<ChartMuseum 사용자명>
CHARTMUSEUM_PASSWORD=<ChartMuseum 비밀번호>
```

#### 알림 설정 (선택적)
```bash
# Slack 배포 알림
SLACK_WEBHOOK=<Slack Webhook URL>

# Discord 알림 (선택적)
DISCORD_WEBHOOK=<Discord Webhook URL>
```

### 🌐 Variables (공개 설정값 - 암호화 불필요)

```bash
# jclee.me 인프라 도메인
REGISTRY_DOMAIN=registry.jclee.me
ARGOCD_DOMAIN=argo.jclee.me
K8S_DOMAIN=k8s.jclee.me

# 프로젝트 설정
PROJECT_NAME=fortinet
K8S_NAMESPACE=fortinet

# GitHub Runner 설정
RUNNER_TYPE=self-hosted  # 또는 ubuntu-latest

# Repository 정보
GIT_REPO_URL=https://github.com/jclee/app.git
GIT_BRANCH=master
GIT_PATH=fortinet
```

---

## 🛡️ GitOps 보안 원칙 (CNCF 표준)

### 1. Pull-Only 배포 모델
- **CI/CD**: Git Repository에만 변경사항 Push
- **ArgoCD**: K8s 클러스터에서 Git Repository를 Pull
- **결과**: K8s 클러스터에 직접 Push 권한 불필요

### 2. 최소 권한 원칙 (Principle of Least Privilege)
- **ArgoCD Token**: 특정 Application 관리 권한만
- **Registry**: 특정 프로젝트 이미지 Push/Pull만
- **K8s RBAC**: 네임스페이스별 권한 분리

### 3. 암호 분리 정책
- **GitHub Secrets**: 민감 정보 (토큰, 비밀번호)
- **GitHub Variables**: 공개 정보 (도메인, 설정값)
- **환경변수**: 런타임 설정만

### 4. 감사 추적 (Audit Trail)
- **모든 배포**: Git Commit History 추적 가능
- **변경 이력**: ArgoCD Dashboard에서 확인
- **롤백**: Git Revert로 즉시 이전 상태 복구

### 5. 드리프트 감지 & 자동 복구
- **Self-Heal**: 수동 변경 자동 복구
- **Sync Policy**: 정기적 상태 확인
- **알림**: 상태 변경시 즉시 통지

---

## 📋 설정 검증 체크리스트

### ✅ GitHub Secrets 확인
- [ ] `ARGOCD_TOKEN` - ArgoCD API 접근 토큰
- [ ] `REGISTRY_USERNAME` - Harbor Registry 사용자명  
- [ ] `REGISTRY_PASSWORD` - Harbor Registry 비밀번호
- [ ] `SLACK_WEBHOOK` - Slack 알림 URL (선택적)

### ✅ GitHub Variables 확인  
- [ ] `REGISTRY_DOMAIN=registry.jclee.me`
- [ ] `ARGOCD_DOMAIN=argo.jclee.me`
- [ ] `K8S_DOMAIN=k8s.jclee.me`
- [ ] `PROJECT_NAME=fortinet`
- [ ] `K8S_NAMESPACE=fortinet`

### ✅ 인프라 연결성 확인
- [ ] ArgoCD 서버 접근 가능: `https://argo.jclee.me`
- [ ] Harbor Registry 접근 가능: `https://registry.jclee.me`
- [ ] K8s API 접근 가능: `https://k8s.jclee.me:6443`
- [ ] 애플리케이션 도메인: `https://fortinet.jclee.me`

### ✅ ArgoCD Application 설정
- [ ] Application Name: `fortinet`
- [ ] Source Repository: `https://github.com/jclee/app.git`  
- [ ] Path: `fortinet/k8s/overlays/production`
- [ ] Target Revision: `master`
- [ ] Destination Namespace: `fortinet`

---

## 🚀 배포 워크플로우

### 자동 배포 트리거
1. **Push to master** → 전체 GitOps 파이프라인 실행
2. **Pull Request** → 코드 품질 검사만 실행
3. **Manual Trigger** → 환경별 수동 배포

### 파이프라인 단계
1. **🧹 Code Quality**: Black, isort, flake8, 보안 스캔
2. **🐳 Docker Build**: Multi-arch 빌드 + Harbor Registry Push
3. **⚡ GitOps Deploy**: Kustomize 업데이트 + ArgoCD Sync
4. **🔍 Verification**: Health Check + 성능 기준선 측정
5. **📢 Notifications**: Slack 알림 + 배포 보고서

### GitOps 플로우
```
GitHub Repository (Source of Truth)
        ↓ (Push)
GitHub Actions (CI/CD)
        ↓ (Build & Push)
Harbor Registry (Image Store)
        ↓ (Git Commit)
Git Repository (Manifest Update)
        ↓ (Pull)
ArgoCD (GitOps Controller)
        ↓ (Apply)
Kubernetes Cluster (Target State)
```

---

## 🔧 트러블슈팅

### ArgoCD 연결 실패
```bash
# ArgoCD CLI 테스트
argocd version --server argo.jclee.me --auth-token $ARGOCD_TOKEN --grpc-web

# 토큰 재생성
argocd account generate-token --account=admin --server=argo.jclee.me
```

### Harbor Registry 인증 실패  
```bash
# Docker 로그인 테스트
docker login registry.jclee.me -u $USERNAME -p $PASSWORD

# Harbor UI에서 Robot Account 확인
# https://registry.jclee.me → Robot Accounts
```

### K8s 리소스 확인
```bash
# Pod 상태 확인
kubectl get pods -n fortinet

# ArgoCD Application 상태
argocd app get fortinet --server argo.jclee.me
```

---

**🎯 목표**: 완전 자동화된 GitOps 기반 CI/CD 파이프라인으로 jclee.me 인프라에서 무중단 배포 실현