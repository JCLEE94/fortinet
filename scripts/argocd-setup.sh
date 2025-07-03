#!/bin/bash

# ArgoCD Initial Setup Script
# FortiGate Nextrade 프로젝트를 위한 ArgoCD 설정

set -e

# Configuration
ARGOCD_SERVER="argo.jclee.me"
ADMIN_USER="admin"
ADMIN_PASS="bingogo1"
NEW_USER="jclee"
NEW_USER_PASS="bingogo1"
GITHUB_USER="JCLEE94"
GITHUB_TOKEN="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"
REGISTRY_URL="registry.jclee.me"
REGISTRY_USER="qws9411"
REGISTRY_PASS="bingogo1"
NAMESPACE="argocd"
APP_NAMESPACE="fortinet"

echo "🎯 ArgoCD 초기 설정 시작..."

# 1. ArgoCD CLI 설치 확인
if ! command -v argocd &> /dev/null; then
    echo "📦 ArgoCD CLI 설치..."
    ARGOCD_VERSION="v2.9.3"
    curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/download/${ARGOCD_VERSION}/argocd-linux-amd64
    chmod +x /usr/local/bin/argocd
fi

# 2. ArgoCD 로그인
echo "🔐 ArgoCD 서버 로그인..."
argocd login $ARGOCD_SERVER \
    --username $ADMIN_USER \
    --password $ADMIN_PASS \
    --insecure \
    --grpc-web

# 3. 새로운 사용자 계정 생성 (옵션)
echo "👤 사용자 계정 설정..."
argocd account update-password \
    --account $NEW_USER \
    --current-password $ADMIN_PASS \
    --new-password $NEW_USER_PASS || echo "사용자 계정이 이미 존재하거나 권한이 없습니다."

# 4. GitHub Repository 추가
echo "🔗 GitHub Repository 연결..."
argocd repo add https://github.com/$GITHUB_USER/fortinet.git \
    --username $GITHUB_USER \
    --password $GITHUB_TOKEN \
    --name fortinet-repo || echo "Repository가 이미 추가되어 있습니다."

# 5. Docker Registry Secret 생성
echo "🔑 Docker Registry Secret 생성..."
kubectl create namespace $APP_NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret docker-registry regcred \
    --docker-server=$REGISTRY_URL \
    --docker-username=$REGISTRY_USER \
    --docker-password=$REGISTRY_PASS \
    -n $APP_NAMESPACE \
    --dry-run=client -o yaml | kubectl apply -f -

# 6. ArgoCD Project 생성
echo "📁 ArgoCD Project 생성..."
cat <<EOF | kubectl apply -f -
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: fortinet-project
  namespace: $NAMESPACE
spec:
  description: FortiGate Nextrade Project
  sourceRepos:
  - https://github.com/$GITHUB_USER/fortinet.git
  - https://github.com/$GITHUB_USER/fortinet-gitops.git
  destinations:
  - namespace: $APP_NAMESPACE
    server: https://kubernetes.default.svc
  - namespace: $NAMESPACE
    server: https://kubernetes.default.svc
  clusterResourceWhitelist:
  - group: ''
    kind: Namespace
  namespaceResourceWhitelist:
  - group: '*'
    kind: '*'
EOF

# 7. ArgoCD Application 생성
echo "📱 ArgoCD Application 생성..."
cat <<EOF | kubectl apply -f -
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: fortinet-app
  namespace: $NAMESPACE
  finalizers:
  - resources-finalizer.argocd.argoproj.io
spec:
  project: fortinet-project
  source:
    repoURL: https://github.com/$GITHUB_USER/fortinet.git
    targetRevision: HEAD
    path: k8s/manifests
  destination:
    server: https://kubernetes.default.svc
    namespace: $APP_NAMESPACE
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
      allowEmpty: false
    syncOptions:
    - CreateNamespace=true
    - PrunePropagationPolicy=foreground
    - PruneLast=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
EOF

# 8. RBAC 설정
echo "🔒 RBAC 정책 설정..."
cat <<EOF > /tmp/argocd-rbac-cm.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-rbac-cm
  namespace: $NAMESPACE
data:
  policy.default: role:readonly
  policy.csv: |
    p, role:admin, applications, *, */*, allow
    p, role:admin, clusters, *, *, allow
    p, role:admin, repositories, *, *, allow
    p, role:admin, certificates, *, *, allow
    p, role:admin, projects, *, *, allow
    
    g, $NEW_USER, role:admin
    g, $ADMIN_USER, role:admin
EOF

kubectl apply -f /tmp/argocd-rbac-cm.yaml

# 9. 초기 동기화
echo "🔄 애플리케이션 동기화..."
argocd app sync fortinet-app --force || echo "애플리케이션이 아직 준비되지 않았습니다."

# 10. 상태 확인
echo "📊 ArgoCD 설정 상태:"
echo "========================"
argocd app list
echo "========================"
argocd repo list
echo "========================"

echo "✅ ArgoCD 초기 설정 완료!"
echo ""
echo "🌐 ArgoCD UI: https://$ARGOCD_SERVER"
echo "👤 사용자: $NEW_USER"
echo "🔑 비밀번호: $NEW_USER_PASS"
echo ""
echo "📌 다음 단계:"
echo "1. k8s/manifests 디렉토리에 Kubernetes 매니페스트 생성"
echo "2. git push 시 자동 배포 확인"
echo "3. ArgoCD UI에서 애플리케이션 상태 모니터링"