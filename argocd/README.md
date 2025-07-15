# ArgoCD Application Configuration

이 디렉토리에는 다양한 환경과 용도에 맞는 ArgoCD 애플리케이션 구성 파일들이 포함되어 있습니다.

## 파일 설명

### application.yaml (기본)
- 프로덕션 환경용 기본 구성
- 최소한의 하드코딩으로 Helm 차트의 기본값 활용
- 레지스트리 인증 정보만 파라미터로 오버라이드

### application-simple.yaml
- 환경별 values 파일을 사용하는 예제
- values-prod.yaml과 함께 사용

### application-with-secret.yaml
- Helm Secrets를 사용한 민감한 정보 관리 예제
- 프로덕션 환경에서 권장

## 사용 방법

### 1. 기본 배포 (application.yaml)
```bash
kubectl apply -f application.yaml
```

### 2. 환경별 배포
개발 환경:
```bash
# application.yaml 복사 후 수정
cp application.yaml application-dev.yaml
# valueFiles에 values-dev.yaml 추가
# 또는 parameters로 환경별 값 오버라이드
```

### 3. 민감한 정보 관리

#### 옵션 1: ArgoCD 파라미터 사용 (현재 방식)
```yaml
parameters:
  - name: registryCredentials.username
    value: admin
  - name: registryCredentials.password
    value: bingogo1
```

#### 옵션 2: Kubernetes Secret 참조
```bash
# Secret 생성
kubectl create secret generic fortinet-helm-values \
  --from-file=values-secret.yaml \
  -n argocd
```

#### 옵션 3: ArgoCD Secret Management
ArgoCD UI 또는 CLI를 통해 애플리케이션별 시크릿 설정

## 하드코딩 제거 가이드

### 이전 (하드코딩됨)
```yaml
parameters:
  - name: fortinet.appMode
    value: production
  - name: image.tag
    value: latest
  - name: ingress.hosts[0].host
    value: fortinet.jclee.me
  # ... 많은 파라미터들
```

### 현재 (최소화됨)
```yaml
parameters:
  # 필수 인증 정보만
  - name: registryCredentials.username
    value: admin
  - name: registryCredentials.password
    value: bingogo1
```

나머지 값들은 Helm 차트의 values.yaml에서 관리됩니다.

## 환경 변수로 관리하기

ArgoCD CLI를 사용한 파라미터 설정:
```bash
argocd app set fortinet \
  --parameter registryCredentials.username=$REGISTRY_USER \
  --parameter registryCredentials.password=$REGISTRY_PASS
```

## 모범 사례

1. **기본값은 Helm Chart에**: 대부분의 설정은 values.yaml에 정의
2. **환경별 분리**: values-dev.yaml, values-prod.yaml 등으로 환경 분리
3. **민감한 정보**: Secret이나 환경 변수로 관리
4. **자동화**: ArgoCD Image Updater로 이미지 업데이트 자동화
5. **버전 관리**: targetRevision: "*"로 최신 차트 자동 사용