# ArgoCD CI/CD 설정 가이드

## 📋 사전 준비사항

### 1. ArgoCD 서버 정보
- **Server URL**: argo.jclee.me
- **Username**: admin / jclee
- **Password**: bingogo1

### 2. Registry 정보
- **URL**: registry.jclee.me
- **Username**: qws9411
- **Password**: bingogo1

### 3. GitHub Token
- **Username**: JCLEE94
- **Token**: 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

## 🔐 GitHub Repository Secrets 설정

GitHub Repository에서 다음 Secrets를 설정해야 합니다:

1. **Repository 이동**: https://github.com/JCLEE94/fortinet
2. **Settings → Secrets and variables → Actions**
3. **New repository secret** 클릭

### 필수 Secrets:

```yaml
# Docker Registry
REGISTRY_USERNAME: qws9411
REGISTRY_PASSWORD: bingogo1

# ArgoCD
ARGOCD_AUTH_TOKEN: <ArgoCD에서 생성한 토큰>
ARGOCD_PASSWORD: bingogo1

# Kubernetes (옵션 - K8s 직접 배포 시)
KUBECONFIG: <base64로 인코딩된 kubeconfig 파일>
```

## 🚀 ArgoCD 초기 설정

### 1. 설정 스크립트 실행

```bash
cd /home/jclee/app/fortinet
./scripts/argocd-setup.sh
```

### 2. ArgoCD Token 생성

```bash
# ArgoCD 로그인
argocd login argo.jclee.me --username admin --password bingogo1 --insecure --grpc-web

# 토큰 생성
argocd account generate-token --account admin
```

생성된 토큰을 `ARGOCD_AUTH_TOKEN` Secret에 추가합니다.

### 3. Secrets 파일 업데이트

`k8s/manifests/secrets.yaml` 파일을 실제 값으로 업데이트:

```yaml
stringData:
  fortimanager-host: "실제_FORTIMANAGER_HOST"
  fortimanager-api-key: "실제_API_KEY"
  fortigate-host: "실제_FORTIGATE_HOST"
  fortigate-api-key: "실제_API_KEY"
```

**주의**: 이 파일은 git에 커밋하지 마세요! 대신 다음 방법을 사용하세요:

```bash
# Secret 직접 생성
kubectl create secret generic fortinet-secrets \
  --from-literal=fortimanager-host=YOUR_HOST \
  --from-literal=fortimanager-api-key=YOUR_KEY \
  -n fortinet
```

## 📦 배포 프로세스

### 1. 코드 푸시
```bash
git add .
git commit -m "feat: 새 기능 추가"
git push origin main
```

### 2. CI/CD 파이프라인
1. GitHub Actions가 자동으로 시작됨
2. 테스트 실행
3. Docker 이미지 빌드
4. Registry에 푸시
5. ArgoCD가 자동으로 새 이미지 감지 및 배포

### 3. 배포 확인
```bash
# ArgoCD CLI로 확인
argocd app get fortinet-app

# Kubernetes로 확인
kubectl get pods -n fortinet
kubectl logs -n fortinet -l app=fortinet
```

### 4. ArgoCD UI 확인
- https://argo.jclee.me 접속
- fortinet-app 애플리케이션 상태 확인

## 🔧 문제 해결

### ArgoCD 동기화 실패
```bash
# 수동 동기화
argocd app sync fortinet-app --force

# 상태 확인
argocd app get fortinet-app
```

### 이미지 Pull 실패
```bash
# Registry Secret 재생성
kubectl delete secret regcred -n fortinet
kubectl create secret docker-registry regcred \
  --docker-server=registry.jclee.me \
  --docker-username=qws9411 \
  --docker-password=bingogo1 \
  -n fortinet
```

### Pod 시작 실패
```bash
# Pod 상태 확인
kubectl describe pod -n fortinet -l app=fortinet

# 로그 확인
kubectl logs -n fortinet -l app=fortinet --previous
```

## 📊 모니터링

### ArgoCD 대시보드
- URL: https://argo.jclee.me
- 애플리케이션 상태
- 동기화 히스토리
- 리소스 트리 뷰

### Kubernetes 명령어
```bash
# 전체 상태
kubectl get all -n fortinet

# 실시간 로그
kubectl logs -f -n fortinet -l app=fortinet

# 리소스 사용량
kubectl top pods -n fortinet
```

## 🔄 업데이트 전략

### 1. Rolling Update (기본)
- 무중단 배포
- 점진적 업데이트

### 2. Blue-Green (옵션)
- 전체 교체 방식
- 빠른 롤백 가능

### 3. Canary (고급)
- 일부 트래픽만 새 버전으로
- 위험 최소화

## 📝 체크리스트

- [ ] ArgoCD 서버 접근 확인
- [ ] GitHub Secrets 설정 완료
- [ ] ArgoCD 토큰 생성 및 설정
- [ ] Registry 인증 확인
- [ ] 첫 배포 성공
- [ ] 헬스체크 통과
- [ ] 모니터링 설정

## 🎯 다음 단계

1. **Production 환경 분리**
   - k8s/overlays/production 설정
   - 환경별 설정 분리

2. **자동 롤백 설정**
   - 헬스체크 실패 시 자동 롤백
   - 메트릭 기반 롤백

3. **알림 설정**
   - Slack/Discord 통합
   - 배포 성공/실패 알림