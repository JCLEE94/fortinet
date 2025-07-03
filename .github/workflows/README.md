# GitHub Actions Workflows

FortiGate Nextrade 프로젝트의 CI/CD 파이프라인 문서입니다.

## 📋 워크플로우 개요

### 1. **main-cicd.yml** - 메인 CI/CD 파이프라인
- **목적**: 테스트, 빌드, 배포를 수행하는 메인 파이프라인
- **트리거**: 
  - Push to main/master/develop
  - Pull requests to main/master
  - Git tags (v*)
- **주요 기능**:
  - 코드 품질 검사 (black, flake8, mypy)
  - 테스트 실행 (pytest)
  - Docker 이미지 빌드 및 푸시
  - 자동 배포 (Watchtower/K8s/ArgoCD)
  - 헬스 체크

### 2. **gitops-sync.yml** - GitOps 동기화
- **목적**: ArgoCD GitOps 매니페스트 업데이트
- **트리거**:
  - Main CI/CD Pipeline 성공 시
  - 수동 실행 (workflow_dispatch)
- **주요 기능**:
  - GitOps 저장소 업데이트
  - Kustomization 파일 수정
  - ArgoCD 애플리케이션 동기화

### 3. **emergency-deploy.yml** - 비상 배포
- **목적**: 긴급 상황 시 빠른 배포
- **트리거**: 수동 실행만 가능
- **주요 기능**:
  - 최소한의 테스트
  - 빠른 Docker 빌드
  - 즉시 배포
  - 배포 이유 기록

## 🔧 환경 변수 설정

### Repository Variables
```yaml
DOCKER_REGISTRY: registry.jclee.me
DOCKER_IMAGE_NAME: fortinet
DEPLOY_METHOD: watchtower  # Options: watchtower, k8s-direct, argocd
ARGOCD_SERVER: argocd.jclee.me
```

### Repository Secrets
```yaml
REGISTRY_USERNAME: Docker 레지스트리 사용자명
REGISTRY_PASSWORD: Docker 레지스트리 비밀번호
ARGOCD_PASSWORD: ArgoCD admin 비밀번호
KUBECONFIG: Kubernetes 설정 (base64 인코딩)
```

## 🚀 배포 방식

### 1. Watchtower (기본)
- 이미지가 레지스트리에 푸시되면 자동으로 감지하여 업데이트
- 가장 간단한 방식
- 설정 불필요

### 2. K8s Direct
- kubectl을 사용하여 직접 deployment 업데이트
- 빠른 배포 가능
- KUBECONFIG secret 필요

### 3. ArgoCD
- GitOps 방식으로 선언적 배포
- 변경 사항 추적 가능
- 롤백 용이

## 📝 사용 예시

### 일반 배포
```bash
git add .
git commit -m "feat: 새로운 기능 추가"
git push origin main
# 자동으로 CI/CD 파이프라인 실행
```

### 긴급 배포
1. GitHub Actions 탭으로 이동
2. "Emergency Deploy" 워크플로우 선택
3. "Run workflow" 클릭
4. 배포 이유 입력
5. 실행

### 배포 방식 변경
1. Settings → Secrets and variables → Actions
2. Variables 탭에서 DEPLOY_METHOD 수정
3. 옵션: watchtower, k8s-direct, argocd

## 🔍 트러블슈팅

### 빌드 실패
- requirements.txt 확인
- Dockerfile.production 문법 검사
- 레지스트리 인증 정보 확인

### 배포 실패
- 배포 방식에 따른 설정 확인
- 헬스 체크 URL 접근 가능 여부
- 로그 확인: `kubectl logs -n fortinet`

### ArgoCD 동기화 실패
- ArgoCD 서버 접근 가능 여부
- GitOps 저장소 권한 확인
- ArgoCD 애플리케이션 상태 확인

## 📊 모니터링

### GitHub Actions 대시보드
- 각 워크플로우 실행 상태
- 실행 시간 및 로그
- 실패 원인 분석

### 애플리케이션 헬스
- https://fortinet.jclee.me/api/health
- 배포 후 자동 체크
- 5회 재시도 로직

## 🔒 보안 고려사항

1. **Secrets 관리**
   - 모든 인증 정보는 GitHub Secrets 사용
   - 로그에 secrets 노출 방지
   - 정기적인 토큰 갱신

2. **이미지 서명**
   - 프로덕션 이미지는 서명 권장
   - 레지스트리 접근 제한

3. **최소 권한 원칙**
   - 각 워크플로우는 필요한 최소 권한만 부여
   - Self-hosted runner 보안 강화