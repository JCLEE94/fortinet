#!/bin/bash

# External-DNS 설치 스크립트

set -e

echo "🌐 External-DNS 설치"
echo "===================="

# Helm repo 추가
echo "1️⃣ Helm repository 추가..."
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Namespace 생성
echo "2️⃣ Namespace 생성..."
kubectl create namespace external-dns --dry-run=client -o yaml | kubectl apply -f -

# Cloudflare API 토큰 설정
echo "3️⃣ Cloudflare 설정..."
read -p "Cloudflare API Token: " CF_API_TOKEN

# Secret 생성 (API 토큰 저장)
kubectl create secret generic cloudflare-api-token \
  --from-literal=apiToken="$CF_API_TOKEN" \
  --namespace external-dns \
  --dry-run=client -o yaml | kubectl apply -f -

# External-DNS 설치
echo "4️⃣ External-DNS 설치..."
helm upgrade --install external-dns bitnami/external-dns \
  --namespace external-dns \
  --values values.yaml \
  --set cloudflare.secretName=cloudflare-api-token \
  --wait

echo "✅ 설치 완료!"
echo ""
echo "📊 상태 확인:"
kubectl get pods -n external-dns
kubectl logs -n external-dns -l app.kubernetes.io/name=external-dns --tail=20