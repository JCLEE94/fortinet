# 클러스터 등록 절차 요약

## 🎯 한 번에 이해하기

**목표**: 192.168.50.110 서버를 ArgoCD에 등록해서 하나의 Git push로 두 서버에 동시 배포

## 📋 3단계 절차

### 1단계: 192.168.50.110에 Kubernetes 설치
```bash
# SSH로 192.168.50.110 접속
ssh jclee@192.168.50.110

# Kubernetes 설치 스크립트 실행
curl -s https://raw.githubusercontent.com/kubernetes/kubernetes/master/cluster/get-kube.sh | bash
```

### 2단계: ArgoCD에 클러스터 등록
```bash
# 자동 등록 스크립트 실행
./scripts/register-cluster.sh 192.168.50.110 jclee bingogo1

# 또는 수동 등록
argocd cluster add prod-192-168-50-110 --name secondary-cluster
```

### 3단계: ApplicationSet으로 다중 클러스터 배포 활성화
```bash
# ApplicationSet 적용
kubectl apply -f argocd/applicationset.yaml

# 이제 git push 한 번으로 두 서버에 자동 배포됨!
git push origin master
```

## ⚡ 빠른 실행

```bash
# 1. 클러스터 등록 (한 번만)
./scripts/register-cluster.sh

# 2. 다중 클러스터 배포 설정 (한 번만)
kubectl apply -f argocd/applicationset.yaml

# 3. 앞으로는 이것만!
git push origin master  # → 모든 클러스터에 자동 배포
```

## 📊 현재 vs 목표

### 현재 상황
```
git push → GitHub Actions → registry.jclee.me → ArgoCD → 1개 클러스터
```

### 목표 상황
```
git push → GitHub Actions → registry.jclee.me → ArgoCD → 2개 클러스터 (동시)
                                                    ├── Primary (kubernetes.default.svc)
                                                    └── Secondary (192.168.50.110:6443)
```

## 🔧 등록 후 확인 방법

```bash
# 등록된 클러스터 확인
argocd cluster list

# 애플리케이션 상태 확인
argocd app list

# 배포 테스트
git add . && git commit -m "test multi-cluster" && git push origin master
```

## 📞 문제 해결

### Q: 클러스터 등록이 안 돼요
```bash
# 1. 네트워크 연결 확인
curl -k https://192.168.50.110:6443/version

# 2. 인증 정보 확인
kubectl --context=prod-192.168.50.110 get nodes

# 3. ArgoCD 로그 확인
argocd cluster get https://192.168.50.110:6443
```

### Q: ApplicationSet이 작동 안 해요
```bash
# ApplicationSet 상태 확인
kubectl get applicationset -n argocd

# ArgoCD Application Controller 로그 확인
kubectl logs -n argocd deployment/argocd-applicationset-controller
```

### Q: 한 클러스터에만 배포돼요
```bash
# 모든 클러스터 상태 확인
argocd cluster list

# 특정 클러스터 상태 확인
argocd cluster get <cluster-url>
```

## 📚 관련 문서

- **상세 가이드**: [cluster-registration-guide.md](cluster-registration-guide.md)
- **다중 클러스터 설정**: [multi-cluster-setup.md](multi-cluster-setup.md)
- **ApplicationSet 설정**: [../argocd/applicationset.yaml](../argocd/applicationset.yaml)

## ✨ 완료 후 혜택

1. **하나의 Git push로 모든 서버에 배포**
2. **자동 동기화** (3분마다 체크)
3. **개별 클러스터 관리** 가능
4. **롤백도 한 번에** 가능
5. **ArgoCD 대시보드에서 모든 클러스터 모니터링**