# 다중 클러스터 배포 가이드

## 📋 현재 상태

### ✅ 완료된 작업
- **Primary 클러스터**: kubernetes.default.svc (배포 완료)
- **ArgoCD 애플리케이션**: fortinet-primary (정상 동작)
- **다중 클러스터 스크립트**: 준비 완료

### ⚠️ 대기 중인 작업
- **Secondary 클러스터**: 192.168.50.110 (클러스터 미설치)
- **ArgoCD 등록**: 클러스터 설치 후 진행 필요

## 🚀 Secondary 클러스터 설정 방법

### 1. 192.168.50.110에 Kubernetes 설치

```bash
# Ubuntu/Debian에서 Kubernetes 설치
# 1. Docker 설치
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable docker
sudo systemctl start docker

# 2. Kubernetes 설치 (kubeadm 방식)
sudo apt install -y apt-transport-https ca-certificates curl
sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt update
sudo apt install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

# 3. 클러스터 초기화
sudo kubeadm init --pod-network-cidr=10.244.0.0/16

# 4. kubectl 설정
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# 5. CNI 플러그인 설치 (Flannel)
kubectl apply -f https://raw.githubusercontent.com/flannel-io/flannel/master/Documentation/kube-flannel.yml

# 6. 단일 노드 클러스터로 설정 (taint 제거)
kubectl taint nodes --all node-role.kubernetes.io/control-plane-
```

### 2. ArgoCD에 새 클러스터 등록

192.168.50.110 클러스터가 준비되면 다음 스크립트를 실행:

```bash
# ArgoCD 클러스터 추가 스크립트 실행
./scripts/add-cluster.sh

# 또는 수동으로:
# 1. kubectl 컨텍스트 생성
kubectl config set-cluster production-secondary \
    --server=https://192.168.50.110:6443 \
    --certificate-authority=/path/to/ca.crt

kubectl config set-credentials jclee@production-secondary \
    --client-certificate=/path/to/client.crt \
    --client-key=/path/to/client.key

kubectl config set-context production-secondary \
    --cluster=production-secondary \
    --user=jclee@production-secondary

# 2. ArgoCD에 클러스터 추가
argocd login argo.jclee.me --username admin --password bingogo1 --insecure --grpc-web
argocd cluster add production-secondary --name production-secondary
```

### 3. Secondary 애플리케이션 생성

```bash
# Secondary 클러스터용 애플리케이션 생성
argocd app create fortinet-secondary \
    --repo https://github.com/JCLEE94/fortinet.git \
    --path k8s/manifests \
    --dest-server https://192.168.50.110:6443 \
    --dest-namespace fortinet \
    --sync-policy auto \
    --auto-prune \
    --self-heal \
    --revision HEAD

# 동기화 실행
argocd app sync fortinet-secondary --prune
```

## 📊 현재 배포 상태

### Primary 클러스터 (활성)
- **서버**: kubernetes.default.svc
- **네임스페이스**: fortinet
- **상태**: ✅ Synced & Healthy
- **애플리케이션**: fortinet-primary
- **접속**: https://fortinet.jclee.me

### Secondary 클러스터 (대기)
- **서버**: 192.168.50.110:6443
- **네임스페이스**: fortinet
- **상태**: ⚠️ 클러스터 미설치
- **애플리케이션**: 생성 대기 중

## 🔄 자동 배포 플로우

클러스터가 모두 준비되면:

1. **코드 푸시**
   ```bash
   git push origin master
   ```

2. **GitHub Actions**
   - 테스트 실행
   - Docker 이미지 빌드
   - Registry 푸시 (registry.jclee.me/fortinet:latest)

3. **ArgoCD 자동 감지**
   - fortinet-primary: 즉시 배포
   - fortinet-secondary: 즉시 배포 (클러스터 준비 시)

4. **결과 확인**
   ```bash
   # Primary 확인
   argocd app get fortinet-primary
   
   # Secondary 확인
   argocd app get fortinet-secondary
   ```

## 🛠️ 유틸리티 스크립트

### 전체 다중 클러스터 설정
```bash
./scripts/multi-cluster-deploy.sh
```

### 클러스터 추가만
```bash
./scripts/add-cluster.sh
```

### 간단한 다중 클러스터 설정 (현재 완료)
```bash
./scripts/setup-multi-cluster-simple.sh
```

## 📈 스케일링 고려사항

### Primary 클러스터 (메인)
- **Replicas**: 3개
- **리소스**: High (1Gi RAM, 500m CPU)
- **용도**: 메인 트래픽 처리

### Secondary 클러스터 (보조)
- **Replicas**: 2개
- **리소스**: Medium (512Mi RAM, 250m CPU)
- **용도**: 로드 분산, 백업

## 🔍 모니터링

### ArgoCD 대시보드
- https://argo.jclee.me/applications/fortinet-primary ✅
- https://argo.jclee.me/applications/fortinet-secondary ⚠️

### 클러스터 상태 확인
```bash
# Primary
kubectl get pods -n fortinet

# Secondary (클러스터 준비 시)
kubectl --context=production-secondary get pods -n fortinet
```

## 📝 체크리스트

- [x] Primary 클러스터 배포 완료
- [x] ArgoCD 애플리케이션 생성
- [x] 다중 클러스터 스크립트 준비
- [ ] 192.168.50.110 Kubernetes 설치
- [ ] Secondary 클러스터 ArgoCD 등록
- [ ] Secondary 애플리케이션 생성 및 동기화
- [ ] 다중 클러스터 테스트

## 📞 문제 해결

### Secondary 클러스터 연결 실패
```bash
# 1. 클러스터 상태 확인
kubectl --context=production-secondary cluster-info

# 2. 네트워크 연결 확인
ping 192.168.50.110
curl -k https://192.168.50.110:6443/version

# 3. ArgoCD 클러스터 목록 확인
argocd cluster list
```

### 애플리케이션 동기화 실패
```bash
# 강제 동기화
argocd app sync fortinet-secondary --force --prune

# 상태 확인
argocd app get fortinet-secondary
```