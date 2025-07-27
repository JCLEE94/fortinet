# MSA 아키텍처 설계 문서

## 현재 시스템 분석

### 기존 모놀리식 구조
```
FortiGate Nextrade (단일 Flask 애플리케이션)
├── API Layer (8 blueprints)
├── Core Services (인증, 캐시, 설정)
├── Monitoring System
├── ITSM Integration
├── FortiManager Hub
├── Security Components
└── Analysis Engine
```

## MSA 분리 계획

### 1. 핵심 마이크로서비스 식별

#### 1.1 API Gateway Service (포트: 8080)
- **역할**: 모든 외부 요청의 단일 진입점
- **기능**: 라우팅, 로드밸런싱, 인증, 레이트 리미팅
- **기술**: Kong 또는 Ambassador

#### 1.2 Authentication Service (포트: 8081)
- **기존 모듈**: `src/core/auth_manager.py`
- **기능**: JWT 토큰 관리, API 키 검증, 사용자 인증
- **데이터베이스**: Redis (세션 저장)

#### 1.3 FortiManager Service (포트: 8082)
- **기존 모듈**: `src/fortimanager/`, `src/api/clients/fortimanager_api_client.py`
- **기능**: FortiManager 연동, 정책 관리, 컴플라이언스
- **데이터베이스**: PostgreSQL

#### 1.4 ITSM Service (포트: 8083)
- **기존 모듈**: `src/itsm/`
- **기능**: ITSM 티켓 처리, 정책 자동화, 승인 워크플로우
- **데이터베이스**: PostgreSQL

#### 1.5 Monitoring Service (포트: 8084)
- **기존 모듈**: `src/monitoring/`
- **기능**: 실시간 모니터링, 알림, 메트릭 수집
- **데이터베이스**: InfluxDB + Redis

#### 1.6 Security Service (포트: 8085)
- **기존 모듈**: `src/security/`
- **기능**: 패킷 분석, 보안 스캔, 위협 탐지
- **데이터베이스**: MongoDB (패킷 데이터)

#### 1.7 Analysis Service (포트: 8086)
- **기존 모듈**: `src/analysis/`
- **기능**: 정책 분석, 경로 추적, 시각화
- **데이터베이스**: PostgreSQL

#### 1.8 Configuration Service (포트: 8087)
- **기존 모듈**: `src/config/`
- **기능**: 중앙화된 설정 관리, 설정 동기화
- **데이터베이스**: etcd

### 2. 데이터베이스 분리 전략

```yaml
Services:
  auth-service: Redis
  fortimanager-service: PostgreSQL (fortimanager_db)
  itsm-service: PostgreSQL (itsm_db)
  monitoring-service: InfluxDB + Redis
  security-service: MongoDB
  analysis-service: PostgreSQL (analysis_db)
  config-service: etcd
```

### 3. 서비스 간 통신

#### 3.1 동기 통신 (HTTP/REST)
- API Gateway ↔ 모든 서비스
- 사용자 요청 처리용

#### 3.2 비동기 통신 (Message Queue)
- **Message Broker**: RabbitMQ
- **이벤트 기반**: 상태 변경, 알림, 로그

#### 3.3 서비스 디스커버리
- **도구**: Consul 또는 Kubernetes Service
- **기능**: 서비스 등록/발견, 헬스체크

### 4. 배포 전략

#### 4.1 Docker 컨테이너화
각 서비스별 독립적인 Docker 이미지

#### 4.2 Kubernetes 배포
- **Namespace**: fortinet-msa
- **Pod**: 각 서비스당 2-3개 replica
- **Service**: ClusterIP (내부), NodePort (외부)
- **ConfigMap**: 서비스별 설정
- **Secret**: 데이터베이스 연결 정보

### 5. 모니터링 및 로깅

#### 5.1 분산 추적
- **도구**: Jaeger 또는 Zipkin
- **기능**: 요청 추적, 성능 분석

#### 5.2 중앙화된 로깅
- **도구**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **기능**: 로그 수집, 분석, 시각화

#### 5.3 메트릭 수집
- **도구**: Prometheus + Grafana
- **기능**: 서비스 메트릭, 대시보드

### 6. 보안 고려사항

#### 6.1 서비스 간 인증
- **방식**: mTLS (Mutual TLS)
- **인증서 관리**: Cert-Manager

#### 6.2 API 보안
- **인증**: JWT 토큰
- **권한**: RBAC (Role-Based Access Control)

### 7. 개발 환경

#### 7.1 로컬 개발
- **도구**: Docker Compose
- **구성**: 모든 서비스 + 의존성 (DB, Message Queue)

#### 7.2 테스트 환경
- **통합 테스트**: 서비스 간 통신 테스트
- **계약 테스트**: API 계약 검증

## 구현 단계

### Phase 1: 기반 구조 구축 (1주)
1. API Gateway 설정
2. 서비스 디스커버리 구축
3. Message Queue 설정
4. 데이터베이스 분리

### Phase 2: 핵심 서비스 분리 (2주)
1. Authentication Service 분리
2. FortiManager Service 분리
3. ITSM Service 분리

### Phase 3: 지원 서비스 분리 (1주)
1. Monitoring Service 분리
2. Security Service 분리
3. Analysis Service 분리
4. Configuration Service 분리

### Phase 4: 최적화 및 테스트 (1주)
1. 성능 최적화
2. 통합 테스트
3. 부하 테스트
4. 장애 복구 테스트

## 예상 효과

### 장점
- **확장성**: 개별 서비스 독립적 확장
- **가용성**: 서비스 간 격리로 장애 영향 최소화
- **개발 효율성**: 팀별 독립적 개발 가능
- **기술 다양성**: 서비스별 최적 기술 선택

### 단점
- **복잡성 증가**: 분산 시스템 관리 복잡도
- **네트워크 지연**: 서비스 간 통신 오버헤드
- **데이터 일관성**: 분산 트랜잭션 처리 필요

## 마이그레이션 전략

### 1. Strangler Fig Pattern
- 기존 모놀리스를 점진적으로 대체
- 새로운 기능은 마이크로서비스로 구현
- 기존 기능은 단계적으로 이관

### 2. Database-per-Service
- 각 서비스가 독립된 데이터베이스 소유
- 데이터 동기화는 이벤트 기반으로 처리

### 3. API Versioning
- 기존 API 호환성 유지
- 새 버전 API를 마이크로서비스로 제공