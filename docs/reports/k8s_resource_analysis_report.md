# K8s 클러스터 미사용 리소스 현황 분석 리포트

## 📊 종합 분석 결과

**분석 일시**: 2025-08-12  
**클러스터**: 192.168.50.110 (jclee-ops)  
**분석 범위**: 전체 네임스페이스 (8개)

---

## 🚨 긴급 정리 필요 항목

### 1. **중단된 Deployment (0 replica)**
- `blacklist/blacklist` - 98분 전 생성, 0/0 replica
- `fortinet-prod/fortinet` - 91분 전 생성, 0/0 replica  
- `fortinet-v2/fortinet` - 85분 전 생성, 0/0 replica

### 2. **비정상 상태 Pod**
- `kube-system/coredns-5688667fd4-qnl6l` - 0/1 Ready, 44회 재시작
- `kube-system/metrics-server-6f4c6675d5-lphhj` - 0/1 Ready, 47회 재시작
- `kube-system/traefik-7bc4b4b46d-l7qwj` - 0/1 Ready, 39회 재시작
- `default/postgres-7465fcfb44-9jhld` - 0/1 Ready, 8회 재시작

### 3. **Endpoint 연결 실패 Service**
- `fortinet-prod/fortinet-metrics` - 연결된 Pod 없음
- `fortinet-v2/fortinet` - 연결된 Pod 없음
- `kube-system/metrics-server` - 연결된 Pod 없음
- `kube-system/traefik` - 연결된 Pod 없음

---

## 📈 리소스별 상세 분석

### **1. Pod 상태 분석**

#### ✅ 정상 운영 Pod (24개)
- **argocd**: 8개 Pod 모두 정상 (1/1 Ready)
- **blacklist**: 2개 Pod 정상 운영
- **safework**: 6개 Pod 정상 운영 (최근 롤링 업데이트 완료)

#### ⚠️ 문제 Pod (4개)
| Pod | 네임스페이스 | 상태 | 재시작 횟수 | 문제점 |
|-----|-------------|------|-------------|--------|
| coredns | kube-system | 0/1 | 44회 | DNS 서비스 불안정 |
| metrics-server | kube-system | 0/1 | 47회 | 메트릭 수집 장애 |
| traefik | kube-system | 0/1 | 39회 | 인그레스 컨트롤러 장애 |
| postgres | default | 0/1 | 8회 | 데이터베이스 연결 실패 |

### **2. Deployment 및 ReplicaSet 분석**

#### 🗑️ 정리 대상 Deployment (3개)
- `blacklist/blacklist`: 0 replica로 설정, 실제 서비스 미사용
- `fortinet-prod/fortinet`: 0 replica, 프로덕션 환경 미사용  
- `fortinet-v2/fortinet`: 0 replica, v2 테스트 환경 종료

#### 📦 과도한 ReplicaSet (대량 정리 필요)
- **argocd-image-updater**: 11개 이전 버전 ReplicaSet (0 desired)
- **argocd-repo-server**: 10개 이전 버전 ReplicaSet (0 desired)
- **argocd-server**: 5개 이전 버전 ReplicaSet (0 desired)
- **blacklist**: 6개 이전 버전 ReplicaSet (0 desired)
- **fortinet-prod**: 3개 이전 버전 ReplicaSet (0 desired)

**예상 정리 효과**: 35개 미사용 ReplicaSet 제거로 etcd 부하 감소

### **3. Service 및 Ingress 분석**

#### 🔌 연결 끊긴 Service (4개)
- `fortinet-prod/fortinet-metrics`: Endpoint 없음
- `fortinet-v2/fortinet`: Endpoint 없음  
- `kube-system/metrics-server`: 메트릭 수집 장애로 연결 없음
- `kube-system/traefik`: 로드밸런서 Pod 장애로 연결 불안정

#### 🌐 중복 Ingress 설정
- `fortinet.jclee.me` 도메인이 2개 Ingress에서 중복 사용:
  - `fortinet-prod/fortinet-ingress` (traefik)
  - `fortinet-v2/fortinet` (traefik)
- `safework.jclee.me` 도메인이 2개 Ingress에서 중복 사용:
  - `default/safework-ingress`
  - `safework/safework`

### **4. ConfigMap 및 Secret 분석**

#### 💾 미사용 ConfigMap (정리 권장)
- `fortinet-prod/fortinet-scripts`: 연결된 Pod 없음
- `blacklist/blacklist-config`: 이전 버전, 미사용
- `argocd/argocd-tls-certs-cm`: 빈 ConfigMap (0 data)
- `argocd/argocd-gpg-keys-cm`: 빈 ConfigMap (0 data)

#### 🔐 과도한 Registry Secret (중복 제거 필요)
같은 registry.jclee.me 인증정보가 여러 네임스페이스에 중복:
- `harbor-registry`: 4개 네임스페이스
- `registry-secret`: 4개 네임스페이스  
- `jclee-registry-secret`: 4개 네임스페이스

**중복도**: 총 25개 Secret 중 12개가 Docker registry 인증 (48%)

### **5. PVC 및 Storage 분석**

#### ⏸️ Pending 상태 PVC (즉시 정리)
- `blacklist/blacklist-data`: 96분간 Pending
- `blacklist/blacklist-logs`: 96분간 Pending

#### 💽 활성 Storage 사용량
- **총 PV**: 7개 (용량: 55.25GB)
- **Redis 클러스터**: 6개 PV (50GB) - blacklist 서비스용
- **사용률**: 모든 PV가 Bound 상태로 정상 사용 중

---

## ⚡ 리소스 사용량 분석

### **CPU 및 메모리 사용 현황**

#### 🔥 고사용량 Pod (Top 5)
1. **safework Pods**: CPU 349-401m, Memory 153-237Mi (6개 Pod)
2. **argocd-application-controller**: CPU 43m, Memory 188Mi
3. **blacklist-helm**: CPU 23m, Memory 66Mi
4. **argocd-server**: CPU 9m, Memory 54Mi
5. **coredns**: CPU 9m, Memory 51Mi

#### 📊 네임스페이스별 리소스 집중도
- **safework**: 전체 클러스터 CPU의 ~60% 사용
- **argocd**: 메모리 집약적 워크로드 (평균 50Mi/Pod)
- **시스템 Pod**: 안정적인 리소스 사용 패턴

---

## 🎯 최적화 권장사항

### **즉시 실행 (High Priority)**

1. **중단된 Deployment 제거**
   ```bash
   kubectl delete deployment blacklist -n blacklist
   kubectl delete deployment fortinet -n fortinet-prod
   kubectl delete deployment fortinet -n fortinet-v2
   ```

2. **Pending PVC 정리**
   ```bash
   kubectl delete pvc blacklist-data blacklist-logs -n blacklist
   ```

3. **시스템 Pod 복구**
   ```bash
   kubectl rollout restart deployment/coredns -n kube-system
   kubectl rollout restart deployment/metrics-server -n kube-system
   kubectl rollout restart deployment/traefik -n kube-system
   ```

### **중기 실행 (Medium Priority)**

4. **이전 ReplicaSet 정리**
   ```bash
   # 보존 기간을 1개로 설정
   kubectl patch deployment argocd-image-updater -n argocd -p '{"spec":{"revisionHistoryLimit":1}}'
   kubectl patch deployment argocd-repo-server -n argocd -p '{"spec":{"revisionHistoryLimit":1}}'
   ```

5. **중복 Registry Secret 통합**
   - Namespace별 개별 Secret → 공통 Secret으로 통합
   - ServiceAccount imagePullSecrets 설정으로 자동 인증

6. **Ingress 중복 해결**
   - fortinet.jclee.me 도메인 단일 Ingress로 통합
   - safework.jclee.me 도메인 정리

### **장기 실행 (Low Priority)**

7. **모니터링 시스템 구축**
   - 미사용 리소스 자동 탐지
   - 정기적인 정리 작업 자동화
   - 리소스 사용량 임계치 설정

8. **네임스페이스 정책 수립**
   - 개발/스테이징/프로덕션 환경 분리
   - 리소스 쿼터 및 LimitRange 설정

---

## 💰 예상 절약 효과

### **즉시 절약 가능**
- **Pod 수**: 4개 문제 Pod 복구 → 안정성 향상
- **ReplicaSet**: 35개 제거 → etcd 용량 ~15% 절약
- **Secret**: 12개 중복 제거 → 보안 관리 단순화
- **PVC**: 2개 Pending 제거 → 스토리지 할당 정리

### **운영 효율성 향상**
- **배포 속도**: ReplicaSet 정리로 배포 시간 단축
- **모니터링**: 불필요한 알람 제거로 운영 집중도 향상  
- **보안**: 중복 Secret 정리로 인증 관리 단순화
- **안정성**: 시스템 Pod 복구로 클러스터 안정성 확보

---

## 📋 정리 작업 체크리스트

### Phase 1: 긴급 정리 (1-2시간)
- [ ] 중단된 Deployment 3개 제거
- [ ] Pending PVC 2개 정리  
- [ ] 시스템 Pod 재시작으로 복구
- [ ] Endpoint 연결 상태 확인

### Phase 2: 최적화 (1주일)
- [ ] 이전 ReplicaSet 35개 정리
- [ ] 중복 Secret 12개 통합
- [ ] Ingress 중복 설정 해결
- [ ] 미사용 ConfigMap 정리

### Phase 3: 거버넌스 (1개월)
- [ ] 리소스 모니터링 시스템 구축
- [ ] 자동 정리 스크립트 개발
- [ ] 네임스페이스 정책 수립
- [ ] 정기 점검 프로세스 확립

---

**📝 리포트 생성**: 2025-08-12  
**🔍 분석 도구**: kubectl + bash scripting  
**⏱️ 총 분석 시간**: ~30분  
**📊 발견된 최적화 기회**: 50+ 항목