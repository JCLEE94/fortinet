#!/bin/bash

# ArgoCD 배포 테스트 스크립트

set -e

echo "🧪 ArgoCD 배포 테스트 시작..."

# 1. ArgoCD 로그인
echo "1️⃣ ArgoCD 로그인..."
argocd login argo.jclee.me \
    --username admin \
    --password bingogo1 \
    --insecure \
    --grpc-web

# 2. 애플리케이션 상태 확인
echo -e "\n2️⃣ 애플리케이션 상태 확인..."
argocd app get fortinet-app || {
    echo "❌ fortinet-app을 찾을 수 없습니다. 애플리케이션을 생성합니다..."
    kubectl apply -f argocd/application.yaml
    sleep 5
}

# 3. Repository 확인
echo -e "\n3️⃣ Repository 연결 확인..."
argocd repo list | grep fortinet || {
    echo "❌ Repository가 등록되지 않았습니다. 등록을 진행합니다..."
    argocd repo add https://github.com/JCLEE94/fortinet.git \
        --username JCLEE94 \
        --password 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
}

# 4. 수동 동기화 테스트
echo -e "\n4️⃣ 수동 동기화 테스트..."
argocd app sync fortinet-app --prune

# 5. 동기화 대기
echo -e "\n5️⃣ 동기화 완료 대기 (최대 5분)..."
argocd app wait fortinet-app \
    --timeout 300 \
    --health \
    --sync

# 6. 배포 상태 확인
echo -e "\n6️⃣ Kubernetes 리소스 확인..."
kubectl get all -n fortinet

# 7. Pod 상태 확인
echo -e "\n7️⃣ Pod 상태 상세 확인..."
kubectl get pods -n fortinet -o wide

# 8. 최신 로그 확인
echo -e "\n8️⃣ 애플리케이션 로그 (최근 50줄)..."
kubectl logs -n fortinet -l app=fortinet --tail=50 || echo "로그를 가져올 수 없습니다."

# 9. 헬스체크
echo -e "\n9️⃣ 애플리케이션 헬스체크..."
POD_NAME=$(kubectl get pods -n fortinet -l app=fortinet -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$POD_NAME" ]; then
    kubectl exec -n fortinet $POD_NAME -- curl -s http://localhost:7777/api/health || echo "내부 헬스체크 실패"
fi

# 외부 헬스체크
echo -e "\n🌐 외부 헬스체크..."
curl -s -k https://fortinet.jclee.me/api/health | jq . || echo "외부 접근 실패"

# 10. ArgoCD UI 정보
echo -e "\n📊 ArgoCD 대시보드 정보:"
echo "URL: https://argo.jclee.me"
echo "Username: admin / jclee"
echo "Password: bingogo1"

echo -e "\n✅ ArgoCD 배포 테스트 완료!"