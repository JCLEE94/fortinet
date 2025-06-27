# FortiGate Nextrade 배포 가이드

## 🎯 배포 개요

FortiGate Nextrade는 Docker 컨테이너로 배포되며, private registry인 `registry.jclee.me`에서 이미지를 가져와서 실행합니다.

## 🏗️ CI/CD 파이프라인

### 자동 빌드 프로세스
1. **코드 푸시** → GitHub master 브랜치
2. **GitHub Actions 트리거** → `.github/workflows/ci-cd.yml`
3. **멀티아키텍처 빌드** → linux/amd64, linux/arm64
4. **Registry 푸시** → registry.jclee.me/fortinet:latest

### 빌드 상태 확인
```bash
# GitHub CLI로 빌드 상태 확인
gh run list --limit 5

# 특정 워크플로우 상세 보기
gh run view [RUN_ID]
```

## 📦 배포 방법

### 1. 자동 배포 스크립트 사용 (권장)

#### 기본 배포
```bash
# 기본 설정으로 배포
./deploy.sh

# 커스텀 포트로 배포
APP_PORT=8080 ./deploy.sh

# 특정 태그로 배포
TAG=v1.0.0 ./deploy.sh
```

#### 환경 변수와 함께 배포
```bash
# 모든 설정과 함께 배포
export REGISTRY_USERNAME="your_username"
export REGISTRY_PASSWORD="your_password"
export APP_PORT=7777
export FORTIGATE_HOST="192.168.1.1"
export FORTIGATE_TOKEN="your_api_token"
export FORTIMANAGER_HOST="192.168.1.2"
export FORTIMANAGER_USERNAME="admin"
export FORTIMANAGER_PASSWORD="your_password"

./deploy.sh
```

### 2. 수동 배포

#### Docker 명령어로 직접 배포
```bash
# 1. Registry 로그인
docker login registry.jclee.me -u [USERNAME] -p [PASSWORD]

# 2. 이미지 가져오기
docker pull registry.jclee.me/fortinet:latest

# 3. 기존 컨테이너 정리
docker stop fortinet-app 2>/dev/null || true
docker rm fortinet-app 2>/dev/null || true

# 4. 새 컨테이너 실행
docker run -d \
  --name fortinet-app \
  --restart unless-stopped \
  -p 7777:7777 \
  -e APP_MODE=production \
  -e FLASK_ENV=production \
  -e LOG_LEVEL=INFO \
  -e TZ=Asia/Seoul \
  registry.jclee.me/fortinet:latest
```

### 3. Docker Compose 배포 (선택사항)

#### docker-compose.yml 생성
```yaml
version: '3.8'

services:
  fortinet-app:
    image: registry.jclee.me/fortinet:latest
    container_name: fortinet-app
    restart: unless-stopped
    ports:
      - "7777:7777"
    environment:
      - APP_MODE=production
      - FLASK_ENV=production
      - LOG_LEVEL=INFO
      - TZ=Asia/Seoul
      - WEB_APP_PORT=7777
      # FortiGate 설정 (선택사항)
      - FORTIGATE_HOST=${FORTIGATE_HOST}
      - FORTIGATE_TOKEN=${FORTIGATE_TOKEN}
      - FORTIMANAGER_HOST=${FORTIMANAGER_HOST}
      - FORTIMANAGER_USERNAME=${FORTIMANAGER_USERNAME}
      - FORTIMANAGER_PASSWORD=${FORTIMANAGER_PASSWORD}
    volumes:
      - fortinet_data:/app/data
      - fortinet_logs:/app/logs

volumes:
  fortinet_data:
  fortinet_logs:
```

#### 실행
```bash
# 백그라운드에서 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 정지
docker-compose down
```

## ⚙️ 환경 변수 설정

### 필수 환경 변수
| 변수명 | 기본값 | 설명 |
|--------|--------|------|
| `APP_MODE` | `production` | 애플리케이션 모드 |
| `FLASK_ENV` | `production` | Flask 환경 |
| `WEB_APP_PORT` | `7777` | 웹 애플리케이션 포트 |

### FortiGate 연동 (선택사항)
| 변수명 | 설명 |
|--------|------|
| `FORTIGATE_HOST` | FortiGate 방화벽 IP/호스트명 |
| `FORTIGATE_TOKEN` | FortiGate API 토큰 |
| `FORTIMANAGER_HOST` | FortiManager IP/호스트명 |
| `FORTIMANAGER_USERNAME` | FortiManager 사용자명 |
| `FORTIMANAGER_PASSWORD` | FortiManager 비밀번호 |

### 기타 설정
| 변수명 | 기본값 | 설명 |
|--------|--------|------|
| `LOG_LEVEL` | `INFO` | 로그 레벨 (DEBUG, INFO, WARNING, ERROR) |
| `TZ` | `Asia/Seoul` | 시간대 |
| `OFFLINE_MODE` | `false` | 오프라인 모드 활성화 |
| `ENABLE_MOCK_MODE` | `false` | Mock 모드 활성화 |

## 🔍 배포 확인

### 1. 컨테이너 상태 확인
```bash
# 실행 중인 컨테이너 확인
docker ps --filter "name=fortinet-app"

# 컨테이너 상세 정보
docker inspect fortinet-app

# 컨테이너 로그
docker logs fortinet-app --tail=100 -f
```

### 2. 서비스 접근 확인
```bash
# 헬스 체크
curl http://localhost:7777/health

# 메인 페이지
curl http://localhost:7777/

# API 상태
curl http://localhost:7777/api/health
```

### 3. 웹 브라우저 접근
- **메인 대시보드**: http://localhost:7777
- **헬스 체크**: http://localhost:7777/health
- **API 문서**: http://localhost:7777/api/docs (있는 경우)

## 🚨 문제 해결

### 포트 충돌
```bash
# 포트 사용 중인 프로세스 확인
lsof -ti:7777

# 프로세스 종료
kill -9 $(lsof -ti:7777)
```

### 컨테이너 문제
```bash
# 컨테이너 재시작
docker restart fortinet-app

# 컨테이너 재생성
docker stop fortinet-app
docker rm fortinet-app
./deploy.sh
```

### 이미지 문제
```bash
# 캐시된 이미지 제거
docker rmi registry.jclee.me/fortinet:latest

# 강제로 최신 이미지 가져오기
docker pull registry.jclee.me/fortinet:latest --no-cache
```

### 로그 분석
```bash
# 실시간 로그 모니터링
docker logs fortinet-app -f

# 에러 로그만 확인
docker logs fortinet-app 2>&1 | grep -i error

# 최근 100줄 로그
docker logs fortinet-app --tail=100
```

## 📊 모니터링

### 컨테이너 리소스 사용량
```bash
# 실시간 리소스 모니터링
docker stats fortinet-app

# 시스템 리소스 확인
docker system df
docker system events --filter container=fortinet-app
```

### 디스크 사용량
```bash
# 컨테이너 크기 확인
docker ps -s --filter "name=fortinet-app"

# 볼륨 사용량
docker volume ls
docker system df -v
```

## 🔄 업데이트 및 롤백

### 무중단 업데이트
```bash
# 1. 새 이미지 가져오기
docker pull registry.jclee.me/fortinet:latest

# 2. 새 컨테이너로 교체
./deploy.sh
```

### 특정 버전으로 롤백
```bash
# 특정 태그로 롤백
TAG=v1.0.0 ./deploy.sh

# 또는 커밋 해시로 롤백
TAG=38b11de ./deploy.sh
```

### 데이터 백업
```bash
# 데이터 볼륨 백업
docker run --rm -v fortinet_data:/data -v $(pwd):/backup ubuntu tar czf /backup/fortinet_data.tar.gz -C /data .

# 로그 백업
docker run --rm -v fortinet_logs:/logs -v $(pwd):/backup ubuntu tar czf /backup/fortinet_logs.tar.gz -C /logs .
```

## 🔧 개발 환경 배포

### 로컬 개발용
```bash
# 개발 모드로 실행
docker run -d \
  --name fortinet-dev \
  -p 7778:7777 \
  -e APP_MODE=development \
  -e FLASK_ENV=development \
  -e LOG_LEVEL=DEBUG \
  -e ENABLE_MOCK_MODE=true \
  registry.jclee.me/fortinet:latest
```

### 테스트 환경
```bash
# 테스트 모드로 실행
docker run -d \
  --name fortinet-test \
  -p 7779:7777 \
  -e APP_MODE=test \
  -e FLASK_ENV=testing \
  -e LOG_LEVEL=DEBUG \
  registry.jclee.me/fortinet:latest
```

## 📝 배포 체크리스트

### 배포 전 확인사항
- [ ] GitHub Actions 빌드 성공 확인
- [ ] Registry에 이미지 업로드 확인
- [ ] 환경 변수 설정 확인
- [ ] 포트 충돌 확인
- [ ] 기존 데이터 백업

### 배포 후 확인사항
- [ ] 컨테이너 정상 실행 확인
- [ ] 웹 서비스 접근 확인
- [ ] API 헬스 체크 통과
- [ ] 로그 에러 없음 확인
- [ ] FortiGate 연동 테스트 (설정한 경우)

## 🆘 지원 및 연락처

문제 발생 시:
1. 로그 파일 확인
2. 환경 변수 재확인
3. 컨테이너 재시작 시도
4. 이슈 등록: [GitHub Issues](https://github.com/JCLEE94/fortinet/issues)

---

**배포 완료**: FortiGate Nextrade가 성공적으로 배포되어 `http://localhost:7777`에서 접근 가능합니다.