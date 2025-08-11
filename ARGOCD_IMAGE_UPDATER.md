# ArgoCD Image Updater 기반 CI/CD 파이프라인

## 개요

이 문서는 ArgoCD Image Updater를 사용한 자동화된 CI/CD 파이프라인 및 오프라인 TAR 생성 프로세스를 설명합니다.

## 아키텍처

```
GitHub Push → GitHub Actions (빌드/테스트) → Registry Push 
    ↓
ArgoCD Image Updater (자동 감지)
    ↓
Kubernetes 배포 (자동)
    ↓
배포 완료 감지 → 오프라인 TAR 생성
```

## 1. ArgoCD Image Updater 설정

### Image Updater 설치
```bash
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj-labs/argocd-image-updater/stable/manifests/install.yaml
```

### Registry 설정 적용
```bash
kubectl apply -f argocd/image-updater-config.yaml
```

### Application 생성/업데이트
```bash
# 기존 앱이 있다면 삭제
argocd app delete fortinet --cascade

# Image Updater 어노테이션이 포함된 새 앱 생성
kubectl apply -f argocd/fortinet-app.yaml
```

## 2. 워크플로우 프로세스

### 2.1 코드 푸시 및 빌드
1. 개발자가 코드를 push
2. GitHub Actions가 자동으로 실행
3. 테스트 실행 및 Docker 이미지 빌드
4. registry.jclee.me에 이미지 푸시 (SHA 태그)

### 2.2 자동 배포 (Image Updater)
1. ArgoCD Image Updater가 주기적으로 레지스트리 스캔
2. 새 이미지 태그 발견 시 자동으로 git에 커밋
3. ArgoCD가 변경사항 감지하고 자동 배포

### 2.3 오프라인 TAR 생성
1. 배포 완료 후 webhook 트리거
2. offline-tar.yml 워크플로우 실행
3. 배포된 이미지를 기반으로 오프라인 패키지 생성
4. GitHub Releases에 업로드

## 3. 사용 방법

### 일반 배포 (온라인)
```bash
# 코드 변경 후
git add .
git commit -m "feat: new feature"
git push origin master

# 이후 모든 과정은 자동화됨
```

### 배포 상태 확인
```bash
# ArgoCD CLI
argocd app get fortinet

# 웹 UI
https://argo.jclee.me/applications/fortinet

# Image Updater 로그 확인
kubectl -n argocd logs -l app.kubernetes.io/name=argocd-image-updater -f
```

### 오프라인 패키지 다운로드
```bash
# GitHub Releases에서 다운로드
# https://github.com/JCLEE94/fortinet/releases

# 또는 Actions 아티팩트에서 다운로드
# https://github.com/JCLEE94/fortinet/actions
```

## 4. 오프라인 배포

### 패키지 구조
```
fortinet-offline-YYYYMMDD-HHMMSS.tar.gz
├── fortinet-offline.tar     # Docker 이미지
├── k8s/                      # Kubernetes 매니페스트
├── deploy-offline.sh         # 배포 스크립트
└── README.md                 # 사용 설명서
```

### 배포 방법
```bash
# 패키지 압축 해제
tar -xzf fortinet-offline-*.tar.gz
cd offline-package

# 자동 배포 (Kubernetes 또는 Docker)
./deploy-offline.sh

# 수동 Docker 배포
docker load < fortinet-offline.tar
docker run -d -p 7777:7777 fortinet:offline

# 수동 Kubernetes 배포
docker load < fortinet-offline.tar
kubectl apply -k k8s/
```

## 5. 모니터링

### 배포 완료 감지 스크립트
```bash
# 수동으로 배포 상태 모니터링 및 오프라인 빌드 트리거
export GITHUB_TOKEN=your-token
./scripts/argocd-webhook-handler.sh
```

### Image Updater 상태
```bash
# Image Updater 앱 목록
kubectl -n argocd get applications.argoproj.io -o json | \
  jq '.items[] | select(.metadata.annotations | has("argocd-image-updater.argoproj.io/image-list")) | .metadata.name'

# 특정 앱의 이미지 업데이트 상태
kubectl -n argocd get applications.argoproj.io fortinet -o json | \
  jq '.metadata.annotations'
```

## 6. 트러블슈팅

### Image Updater가 이미지를 감지하지 못하는 경우
```bash
# 1. Registry 접근 확인
curl https://registry.jclee.me/v2/fortinet/tags/list

# 2. Image Updater 로그 확인
kubectl -n argocd logs -l app.kubernetes.io/name=argocd-image-updater

# 3. 수동으로 이미지 업데이트 트리거
argocd app sync fortinet
```

### 오프라인 빌드가 실패하는 경우
```bash
# 1. ArgoCD 배포 상태 확인
argocd app get fortinet

# 2. GitHub Actions 로그 확인
# https://github.com/JCLEE94/fortinet/actions

# 3. 수동으로 오프라인 빌드 트리거
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/JCLEE94/fortinet/actions/workflows/offline-tar.yml/dispatches \
  -d '{"ref":"master","inputs":{"image_tag":"latest"}}'
```

## 7. 설정 변경

### Image Update 전략 변경
```yaml
# argocd/fortinet-app.yaml
annotations:
  # semver 전략으로 변경 (v1.2.x 형식)
  argocd-image-updater.argoproj.io/fortinet.update-strategy: semver
  argocd-image-updater.argoproj.io/fortinet.allow-tags: regexp:^v[0-9]+\.[0-9]+\.[0-9]+$
  
  # digest 전략 (가장 안정적)
  argocd-image-updater.argoproj.io/fortinet.update-strategy: digest
```

### 업데이트 주기 변경
```bash
# Image Updater ConfigMap 수정
kubectl -n argocd edit configmap argocd-image-updater-config

# interval 설정 추가 (기본: 2m)
data:
  interval: "5m"
```

## 8. 보안 고려사항

### GitHub Token
- Repository dispatch 권한 필요
- ArgoCD Secret에 저장 권장
```bash
kubectl -n argocd create secret generic github-token \
  --from-literal=token=$GITHUB_TOKEN
```

### Registry 인증
- 현재 no-auth 설정 (폐쇄망 환경)
- 필요시 credentials 추가 가능

## 9. 성능 최적화

### Image Updater 최적화
- 불필요한 이미지 태그 제외
- 적절한 스캔 주기 설정
- Registry 미러링 고려

### 오프라인 패키지 최적화
- 멀티스테이지 빌드로 이미지 크기 축소
- 필요한 매니페스트만 포함
- 압축 알고리즘 최적화