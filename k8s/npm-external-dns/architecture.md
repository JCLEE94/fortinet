# External-DNS + Nginx Proxy Manager 통합 아키텍처

## 현재 네트워크 구조

```
인터넷 사용자
    ↓
[Cloudflare DNS]
  - *.jclee.me → 221.140.234.75 (공인 IP)
    ↓
[공유기/라우터]
  - WAN: 221.140.234.75
  - LAN: 192.168.50.1
  - Port Forward: 80, 443 → 192.168.50.215
    ↓
[Synology NAS: 192.168.50.215]
  - Nginx Proxy Manager Container
  - Ports: 80, 443
    ↓
[Kubernetes Cluster]
  - Node1: 192.168.50.110
  - Node2: 192.168.50.100
  - Services: NodePort or LoadBalancer

```

## 통합 솔루션 설계

### 옵션 1: External-DNS Webhook Provider (권장)
External-DNS가 NPM API를 호출하여 Proxy Host를 자동 관리

### 옵션 2: CRD Controller
Kubernetes Controller가 NPM API와 직접 통신

### 옵션 3: ConfigMap + CronJob
주기적으로 NPM을 업데이트하는 간단한 방식

## 구현 계획

1. **NPM API 클라이언트 구축**
   - Authentication
   - Proxy Host CRUD 작업
   - Health Check

2. **External-DNS Webhook Provider**
   - NPM과 통신하는 Webhook 서버
   - External-DNS가 호출할 수 있는 인터페이스

3. **자동화 및 모니터링**
   - 변경사항 감지
   - 자동 업데이트
   - 실패 시 알림