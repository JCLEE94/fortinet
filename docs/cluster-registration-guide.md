# ArgoCD 클러스터 등록 가이드

## 📋 목차
1. [사전 요구사항](#사전-요구사항)
2. [클러스터 등록 방법](#클러스터-등록-방법)
3. [인증 방식별 설정](#인증-방식별-설정)
4. [문제 해결](#문제-해결)
5. [보안 고려사항](#보안-고려사항)

## 🔧 사전 요구사항

### 1. ArgoCD CLI 설치
```bash
# Linux/Mac
curl -sSL -o argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
chmod +x argocd
sudo mv argocd /usr/local/bin/

# 설치 확인
argocd version
```

### 2. kubectl 설치 및 설정
```bash
# kubectl 설치
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# 설치 확인
kubectl version --client
```

### 3. 대상 클러스터 접근 권한
- kubeconfig 파일 또는
- 클러스터 인증 정보 (인증서, 토큰 등)

## 🚀 클러스터 등록 방법

### 방법 1: kubeconfig 기반 등록 (권장)

#### 1-1. kubeconfig 파일 준비
```bash
# 대상 클러스터의 kubeconfig 파일 확인
export KUBECONFIG=/path/to/target-cluster-kubeconfig.yaml
kubectl cluster-info

# 또는 기존 kubeconfig에 병합
kubectl config view --flatten > ~/.kube/config
```

#### 1-2. ArgoCD 로그인
```bash
# ArgoCD 서버 로그인
argocd login argo.jclee.me \
    --username admin \
    --password bingogo1 \
    --insecure \
    --grpc-web
```

#### 1-3. 클러스터 추가
```bash
# 현재 kubectl 컨텍스트의 클러스터 추가
argocd cluster add <context-name> \
    --name <display-name> \
    --kubeconfig /path/to/kubeconfig.yaml

# 예시: 192.168.50.110 클러스터 추가
argocd cluster add production-secondary \
    --name prod-secondary \
    --kubeconfig ~/.kube/config
```

### 방법 2: 수동 인증 정보 등록

#### 2-1. 서비스 계정 생성 (대상 클러스터에서)
```bash
# argocd-manager 서비스 계정 생성
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  name: argocd-manager
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: argocd-manager-role
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: argocd-manager-role-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: argocd-manager-role
subjects:
- kind: ServiceAccount
  name: argocd-manager
  namespace: kube-system
EOF
```

#### 2-2. 토큰 및 인증서 추출
```bash
# 시크릿 이름 찾기
SECRET_NAME=$(kubectl -n kube-system get sa argocd-manager -o jsonpath='{.secrets[0].name}')

# 토큰 추출
TOKEN=$(kubectl -n kube-system get secret $SECRET_NAME -o jsonpath='{.data.token}' | base64 -d)

# CA 인증서 추출
CA_CERT=$(kubectl -n kube-system get secret $SECRET_NAME -o jsonpath='{.data.ca\.crt}')

# 클러스터 API 서버 주소 확인
API_SERVER=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')

echo "API Server: $API_SERVER"
echo "Token: $TOKEN"
echo "CA Certificate: $CA_CERT"
```

#### 2-3. ArgoCD에 클러스터 등록
```bash
# 클러스터 추가 (Bearer Token 방식)
argocd cluster add <cluster-name> \
    --server $API_SERVER \
    --auth-token $TOKEN \
    --ca-data $CA_CERT \
    --name <display-name>
```

### 방법 3: 기본 인증 방식 (192.168.50.110 예시)

```bash
# 1. kubectl 컨텍스트 생성
kubectl config set-cluster production-secondary \
    --server=https://192.168.50.110:6443 \
    --insecure-skip-tls-verify=true

kubectl config set-credentials jclee@production-secondary \
    --username=jclee \
    --password=bingogo1

kubectl config set-context production-secondary \
    --cluster=production-secondary \
    --user=jclee@production-secondary

# 2. 컨텍스트 테스트
kubectl --context=production-secondary get nodes

# 3. ArgoCD에 추가
argocd cluster add production-secondary \
    --name prod-secondary-110
```

## 🔐 인증 방식별 설정

### 1. 인증서 기반 (권장)
```bash
# 클라이언트 인증서와 키 사용
kubectl config set-credentials user \
    --client-certificate=/path/to/client.crt \
    --client-key=/path/to/client.key
```

### 2. Bearer Token
```bash
# 서비스 계정 토큰 사용
kubectl config set-credentials user \
    --token=$TOKEN
```

### 3. Basic Auth (비권장)
```bash
# 사용자명/비밀번호 (보안상 권장하지 않음)
kubectl config set-credentials user \
    --username=admin \
    --password=password
```

### 4. OIDC (OAuth2)
```bash
# OIDC 프로바이더 설정
kubectl config set-credentials user \
    --auth-provider=oidc \
    --auth-provider-arg=idp-issuer-url=https://example.com \
    --auth-provider-arg=client-id=kubernetes \
    --auth-provider-arg=client-secret=secret
```

## 📋 등록된 클러스터 관리

### 클러스터 목록 확인
```bash
# 모든 등록된 클러스터 보기
argocd cluster list

# 출력 예시:
SERVER                          NAME               VERSION  STATUS      MESSAGE
https://kubernetes.default.svc  in-cluster         1.24     Successful  
https://192.168.50.110:6443     prod-secondary-110 1.24     Successful  
```

### 클러스터 상세 정보
```bash
# 특정 클러스터 정보 확인
argocd cluster get https://192.168.50.110:6443
```

### 클러스터 제거
```bash
# 클러스터 등록 해제
argocd cluster rm https://192.168.50.110:6443
```

## 🔍 문제 해결

### 1. 연결 실패
```bash
# 네트워크 연결 테스트
curl -k https://192.168.50.110:6443/version

# 방화벽 규칙 확인
sudo iptables -L -n | grep 6443
```

### 2. 인증 실패
```bash
# kubeconfig 유효성 검증
kubectl --kubeconfig=/path/to/config cluster-info

# 토큰 만료 확인
kubectl get secret -n kube-system <secret-name> -o yaml
```

### 3. 권한 부족
```bash
# ClusterRoleBinding 확인
kubectl get clusterrolebinding -o wide | grep argocd

# 권한 테스트
kubectl auth can-i '*' '*' --as=system:serviceaccount:kube-system:argocd-manager
```

### 4. TLS 인증서 문제
```bash
# 자체 서명 인증서 허용
argocd cluster add <context> --insecure

# CA 인증서 명시적 지정
argocd cluster add <context> --ca-data <base64-encoded-ca-cert>
```

## 🛡️ 보안 고려사항

### 1. 최소 권한 원칙
```yaml
# 읽기 전용 권한만 필요한 경우
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: argocd-read-only
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["get", "list", "watch"]
```

### 2. 네임스페이스 제한
```yaml
# 특정 네임스페이스만 관리
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: argocd-manager
  namespace: fortinet
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
```

### 3. 네트워크 정책
```yaml
# ArgoCD에서 클러스터로의 접근만 허용
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-argocd
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - ipBlock:
        cidr: <argocd-server-ip>/32
    ports:
    - protocol: TCP
      port: 6443
```

## 📝 체크리스트

- [ ] ArgoCD CLI 설치 완료
- [ ] kubectl 설치 및 설정 완료
- [ ] 대상 클러스터 접근 권한 확보
- [ ] kubeconfig 파일 준비 또는 인증 정보 수집
- [ ] ArgoCD 서버 로그인 완료
- [ ] 클러스터 추가 명령 실행
- [ ] 클러스터 목록에서 확인
- [ ] 테스트 애플리케이션 배포
- [ ] 모니터링 설정

## 🚀 Quick Start (192.168.50.110)

```bash
#!/bin/bash
# 192.168.50.110 클러스터 빠른 등록

# 1. ArgoCD 로그인
argocd login argo.jclee.me --username admin --password bingogo1 --insecure --grpc-web

# 2. kubectl 컨텍스트 설정
kubectl config set-cluster prod-110 --server=https://192.168.50.110:6443 --insecure-skip-tls-verify=true
kubectl config set-credentials jclee@prod-110 --username=jclee --password=bingogo1
kubectl config set-context prod-110 --cluster=prod-110 --user=jclee@prod-110

# 3. 클러스터 추가
argocd cluster add prod-110 --name production-secondary

# 4. 확인
argocd cluster list
```

## 📚 참고 자료

- [ArgoCD 공식 문서 - Cluster Management](https://argo-cd.readthedocs.io/en/stable/operator-manual/declarative-setup/#clusters)
- [Kubernetes 인증 방식](https://kubernetes.io/docs/reference/access-authn-authz/authentication/)
- [kubectl config 관리](https://kubernetes.io/docs/tasks/access-application-cluster/configure-access-multiple-clusters/)