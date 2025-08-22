# FortiGate Nextrade - Standalone Container Guide

## Overview
완전히 독립적이고 자체 포함된 Docker 이미지로, 외부 의존성이나 볼륨 마운트가 필요 없습니다.

## 주요 특징

### ✅ 자체 포함 (Self-Contained)
- **No Volume Mounts**: 모든 데이터가 컨테이너 내부에 저장
- **No External Dependencies**: Redis, 외부 DB 불필요
- **Embedded Configuration**: 모든 설정이 이미지에 포함
- **Built-in Mock Data**: 테스트 데이터 내장

### ✅ 독립 실행 (Standalone Operation)
- **In-Memory Cache**: Redis 대신 메모리 캐시 사용
- **Embedded Mock Server**: 외부 API 의존성 제거
- **Offline Mode**: 인터넷 연결 불필요
- **Auto-Configuration**: 자동 설정 생성

## 빠른 시작

### 1. 자동 빌드 및 실행
```bash
# 빌드 스크립트 실행
./scripts/build-standalone.sh

# 커스텀 포트로 실행
./scripts/build-standalone.sh latest 8080
```

### 2. 수동 Docker 빌드
```bash
# 이미지 빌드
docker build -f Dockerfile.standalone -t fortinet-standalone:latest .

# 컨테이너 실행
docker run -d \
  --name fortinet-standalone \
  -p 7777:7777 \
  fortinet-standalone:latest
```

### 3. Docker Compose 사용
```bash
# 빌드 및 실행
docker-compose -f docker-compose.standalone.yml up -d

# 로그 확인
docker-compose -f docker-compose.standalone.yml logs -f

# 중지
docker-compose -f docker-compose.standalone.yml down
```

## 구성 요소

### Dockerfile.standalone
- 모든 의존성 내장
- 설정 파일 자동 생성
- Mock 데이터 포함
- 최적화된 크기

### docker-compose.standalone.yml
- 단일 서비스 구성
- 볼륨 마운트 없음
- 외부 서비스 의존성 없음
- 메모리 제한 설정

## 환경 변수

최소한의 환경 변수만 필요:

```bash
APP_MODE=production      # 운영 모드
LOG_LEVEL=INFO          # 로그 레벨
WEB_APP_PORT=7777       # 웹 포트
STANDALONE_MODE=true    # 독립 모드
OFFLINE_MODE=true       # 오프라인 모드
```

## 데이터 관리

### 데이터 백업
```bash
# 컨테이너 내부 데이터 백업
docker cp fortinet-standalone:/app/data ./backup-data

# 전체 컨테이너 백업
docker export fortinet-standalone > fortinet-backup.tar
```

### 데이터 복원
```bash
# 데이터 복원
docker cp ./backup-data fortinet-standalone:/app/data

# 컨테이너 복원
docker import fortinet-backup.tar fortinet-standalone:backup
```

## 모니터링

### 헬스 체크
```bash
# 헬스 상태 확인
curl http://localhost:7777/api/health

# 컨테이너 상태
docker inspect fortinet-standalone --format='{{.State.Health.Status}}'
```

### 로그 확인
```bash
# 실시간 로그
docker logs -f fortinet-standalone

# 최근 100줄
docker logs --tail 100 fortinet-standalone
```

## 성능 최적화

### 메모리 설정
```yaml
deploy:
  resources:
    limits:
      memory: 1G      # 최대 메모리
    reservations:
      memory: 512M    # 예약 메모리
```

### 캐시 설정
- In-memory 캐시 사용
- TTL: 300초 (5분)
- 자동 가비지 컬렉션

## 보안

### 비root 사용자
- 사용자: fortinet
- 그룹: fortinet
- UID/GID: 자동 할당

### 보안 옵션
```yaml
security_opt:
  - no-new-privileges:true
```

### Secret Key
- 자동 생성 (미제공시)
- 환경 변수로 제공 가능
- 런타임시 생성

## 문제 해결

### 컨테이너가 시작되지 않을 때
```bash
# 로그 확인
docker logs fortinet-standalone

# 대화형 모드로 실행
docker run -it --rm fortinet-standalone:latest /bin/bash
```

### 포트 충돌
```bash
# 다른 포트 사용
docker run -d -p 8080:7777 fortinet-standalone:latest
```

### 메모리 부족
```bash
# 메모리 제한 증가
docker run -d --memory="2g" fortinet-standalone:latest
```

## 장점

1. **완전한 독립성**: 외부 서비스 불필요
2. **간단한 배포**: 단일 이미지로 실행
3. **이식성**: 어디서나 동일하게 동작
4. **보안**: 최소 권한, 비root 실행
5. **경량화**: 필요한 구성요소만 포함

## 제한 사항

1. **데이터 영속성**: 컨테이너 삭제시 데이터 손실
2. **스케일링**: 단일 인스턴스만 지원
3. **캐시**: Redis 대신 메모리 캐시 사용
4. **백업**: 수동 백업 필요

## 프로덕션 사용

프로덕션 환경에서는 다음을 권장:

1. **정기 백업**: 크론잡으로 자동 백업
2. **모니터링**: Prometheus/Grafana 연동
3. **로그 수집**: ELK Stack 연동
4. **리버스 프록시**: Nginx/Traefik 사용

## 라이선스
MIT License