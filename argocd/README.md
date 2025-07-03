# ArgoCD GitOps for FortiGate Nextrade

이 디렉토리는 FortiGate Nextrade 애플리케이션의 ArgoCD GitOps 배포 구성을 포함합니다.

## 🏗️ 디렉토리 구조

```
argocd/
├── applications/           # ArgoCD 애플리케이션 정의
│   └── fortinet-app.yaml
├── environments/          # 환경별 Kubernetes 매니페스트
│   ├── base/             # 기본 구성
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   │   ├── pvc.yaml
│   │   ├── namespace.yaml
│   │   └── kustomization.yaml
│   └── production/       # 프로덕션 오버레이
│       ├── deployment-patch.yaml
│       └── kustomization.yaml
├── install-argocd.sh     # ArgoCD 설치 스크립트
├── setup-argocd-app.sh   # 애플리케이션 설정 스크립트
└── README.md            # 이 파일
```

## 🚀 빠른 시작

### 1. ArgoCD 설치

```bash
# ArgoCD 설치 및 설정
./argocd/install-argocd.sh

# 설치 완료 후 ArgoCD UI 접근
# URL: http://localhost:30080
# 사용자명: admin
# 비밀번호: g0nVB3uL4ccsNiSe
```

### 2. 애플리케이션 배포

```bash
# FortiGate Nextrade 애플리케이션 배포
./argocd/setup-argocd-app.sh

# 배포 상태 확인
kubectl get pods -n fortinet
kubectl get svc -n fortinet
```

### 3. CI/CD 파이프라인 연동

GitHub Actions 워크플로우가 자동으로 ArgoCD와 연동됩니다:

1. **코드 푸시** → GitHub Repository
2. **CI/CD 실행** → GitHub Actions
3. **이미지 빌드** → registry.jclee.me에 푸시
4. **GitOps 업데이트** → ArgoCD가 자동 동기화
5. **배포 완료** → Kubernetes 클러스터

## 📊 ArgoCD 애플리케이션 설정

### 동기화 정책
- **자동 동기화**: 활성화
- **Self Heal**: 활성화 (수동 변경 시 자동 복원)
- **Prune**: 활성화 (불필요한 리소스 자동 삭제)

### 배포 전략
- **Rolling Update**: 무중단 배포
- **Health Check**: 헬스 체크 기반 배포 검증
- **Rollback**: 실패 시 자동 롤백

## 🛠️ 관리 명령어

### ArgoCD CLI 명령어

```bash
# 로그인
argocd login localhost:30080 --username admin --password 'g0nVB3uL4ccsNiSe' --insecure

# 애플리케이션 목록
argocd app list

# 애플리케이션 상태 확인
argocd app get fortinet-app

# 수동 동기화
argocd app sync fortinet-app

# 애플리케이션 삭제
argocd app delete fortinet-app

# 애플리케이션 히스토리
argocd app history fortinet-app
```

### Kubernetes 명령어

```bash
# 포드 상태 확인
kubectl get pods -n fortinet -w

# 서비스 확인
kubectl get svc -n fortinet

# 로그 확인
kubectl logs -f deployment/fortinet -n fortinet

# 배포 롤아웃 상태
kubectl rollout status deployment/fortinet -n fortinet

# 설정 확인
kubectl get configmap -n fortinet
kubectl describe configmap fortinet-config -n fortinet
```

## 🔧 설정 커스터마이징

### 환경별 설정

**Base 환경** (`environments/base/`):
- 기본 2개 레플리카
- 512Mi 메모리, 250m CPU 요청
- 1Gi 메모리, 500m CPU 제한

**Production 환경** (`environments/production/`):
- 3개 레플리카로 증가
- 1Gi 메모리, 500m CPU 요청  
- 2Gi 메모리, 1000m CPU 제한
- 프로덕션 환경 변수 추가

### 이미지 태그 업데이트

GitHub Actions가 자동으로 처리하지만, 수동으로도 가능합니다:

```bash
# Kustomization 파일에서 이미지 태그 변경
cd argocd/environments/production
kustomize edit set image registry.jclee.me/fortinet:NEW_TAG

# ArgoCD 동기화
argocd app sync fortinet-app
```

## 🏥 모니터링 및 헬스 체크

### 헬스 체크 엔드포인트
- **내부**: `http://fortinet-service.fortinet.svc.cluster.local/api/health`
- **외부**: `http://localhost:30777/api/health` (NodePort)

### 로그 모니터링

```bash
# 실시간 로그 확인
kubectl logs -f deployment/fortinet -n fortinet

# 특정 포드 로그
kubectl logs -f <pod-name> -n fortinet

# 이전 재시작 로그
kubectl logs -f deployment/fortinet -n fortinet --previous
```

## 🔐 보안 고려사항

### RBAC 설정
ArgoCD는 최소 권한 원칙으로 구성되어 있습니다:
- `fortinet` 네임스페이스에만 배포 권한
- 클러스터 수준 권한 없음

### Secret 관리
- 민감한 정보는 Kubernetes Secret으로 관리
- ConfigMap은 비민감 설정만 포함
- 이미지 풀 시크릿은 별도 관리

## 🐛 문제 해결

### 일반적인 문제들

**1. ArgoCD 애플리케이션이 동기화되지 않는 경우**
```bash
# 동기화 상태 확인
argocd app get fortinet-app

# 수동 동기화 강제 실행
argocd app sync fortinet-app --force
```

**2. 포드가 시작되지 않는 경우**
```bash
# 포드 상태 확인
kubectl describe pod <pod-name> -n fortinet

# 이벤트 확인
kubectl get events -n fortinet --sort-by='.lastTimestamp'
```

**3. 이미지 풀 실패**
```bash
# 이미지 풀 시크릿 확인
kubectl get secret -n fortinet

# 레지스트리 접근 테스트
docker pull registry.jclee.me/fortinet:latest
```

**4. 서비스 접근 불가**
```bash
# 서비스 엔드포인트 확인
kubectl get endpoints -n fortinet

# 포트 포워딩으로 테스트
kubectl port-forward svc/fortinet-service 8080:80 -n fortinet
```

## 📝 참고 자료

- [ArgoCD 공식 문서](https://argo-cd.readthedocs.io/)
- [Kustomize 가이드](https://kustomize.io/)
- [Kubernetes 배포 가이드](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [GitOps 원칙](https://opengitops.dev/)

## 🔄 업데이트 히스토리

| 날짜 | 버전 | 변경사항 |
|------|------|----------|
| 2024-07-03 | v1.0 | 초기 ArgoCD GitOps 구성 |