# FortiGate Nextrade

[![CI/CD Pipeline](https://github.com/JCLEE94/fortinet/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/JCLEE94/fortinet/actions/workflows/ci-cd.yml)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://hub.docker.com/)
[![License](https://img.shields.io/badge/license-proprietary-red.svg)](LICENSE)

FortiGate 방화벽과 FortiManager를 위한 종합적인 네트워크 모니터링 및 분석 플랫폼입니다. 폐쇄망(오프라인) 환경에서 완전히 동작하도록 설계되었습니다.

## 🚀 주요 기능

- **실시간 모니터링**: 네트워크 트래픽, CPU, 메모리 사용률 모니터링
- **정책 분석**: 방화벽 정책 분석 및 패킷 경로 추적  
- **토폴로지 시각화**: 네트워크 구조 시각화
- **ITSM 연동**: 방화벽 정책 요청 및 티켓 관리
- **FortiManager Hub**: AI 기반 정책 오케스트레이션 및 컴플라이언스 자동화
- **Docker 지원**: 컨테이너 오케스트레이션을 통한 간편한 배포
- **CI/CD 파이프라인**: GitHub Actions를 통한 자동화된 배포
- **로그 관리**: 실시간 로그 스트리밍 및 분석

## 📋 시스템 요구사항

### 최소 요구사항
- **OS**: Linux (Ubuntu 18.04+, CentOS 7+) 또는 Windows 10+
- **RAM**: 4GB 이상
- **Storage**: 20GB 이상 여유 공간  
- **Docker**: 20.10+ 또는 Podman 3.0+
- **Python**: 3.11+

### 권장 사양
- **OS**: Ubuntu 20.04 LTS 또는 CentOS 8
- **RAM**: 8GB 이상
- **Storage**: 50GB 이상 SSD
- **CPU**: 4 Core 이상

## 🚀 빠른 시작

### Docker를 사용한 배포 (권장)
```bash
# 1. 레포지토리 클론
git clone https://github.com/JCLEE94/fortinet.git
cd fortinet

# 2. Docker Compose로 실행
docker-compose up -d

# 3. 접속
# http://localhost:7777
```

### 수동 설치
```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 환경 변수 설정
export APP_MODE=production
export WEB_APP_PORT=7777

# 3. 애플리케이션 실행
cd src
python main.py --web
```

## 🔧 환경 설정

### 환경 변수
- `APP_MODE`: `production` | `test` | `development`
- `OFFLINE_MODE`: `true` | `false` (폐쇄망 환경용)
- `WEB_APP_PORT`: 웹 서버 포트 (기본값: 7777)
- `FORTIMANAGER_HOST`: FortiManager 서버 주소
- `FORTIGATE_HOST`: FortiGate 장비 주소

### 설정 파일
설정은 `data/config.json`에서 관리됩니다:
```json
{
  "fortimanager": {
    "host": "your-fortimanager-host",
    "api_key": "your-api-key"
  },
  "app_settings": {
    "port": 7777,
    "mode": "production"
  }
}
```

## 📁 프로젝트 구조

```
fortinet/
├── src/                    # 소스 코드
│   ├── main.py            # 진입점
│   ├── web_app.py         # Flask 애플리케이션
│   ├── routes/            # API 라우트
│   ├── api/clients/       # API 클라이언트
│   ├── modules/           # 비즈니스 로직
│   └── templates/         # HTML 템플릿
├── tests/                 # 테스트 코드
├── docs/                  # 문서
│   ├── guides/           # 사용자 가이드
│   ├── api/              # API 문서
│   └── reports/          # 분석 리포트
├── scripts/              # 유틸리티 스크립트
├── docker-compose.yml    # Docker 구성
└── .github/workflows/    # CI/CD 파이프라인
```

## 🔌 API 엔드포인트

### 핵심 API
- `GET /api/health` - 헬스 체크
- `GET /api/settings` - 현재 설정 조회
- `POST /api/settings` - 설정 업데이트

### FortiManager API
- `POST /api/fortimanager/analyze-packet-path` - 패킷 경로 분석
- `GET /api/fortimanager/devices` - 관리 장비 목록
- `POST /api/fortimanager/policies` - 방화벽 정책 조회

### 로그 관리 API
- `GET /api/logs/container` - Docker 컨테이너 로그
- `GET /api/logs/stream` - 실시간 로그 스트리밍 (SSE)

## 🛠️ 개발 가이드

### 로컬 개발 환경
```bash
# 개발 서버 실행
APP_MODE=development python src/main.py --web

# 테스트 실행
pytest tests/ -v

# 코드 품질 검사
black src/
flake8 src/
mypy src/
```

### Mock 모드
FortiGate 하드웨어 없이 개발/테스트:
```bash
APP_MODE=test python src/main.py --web
```

## 🚢 배포

### GitHub Actions CI/CD
마스터 브랜치에 푸시하면 자동으로:
1. 테스트 실행
2. Docker 이미지 빌드
3. Private Registry 푸시
4. Production 서버 배포

### 수동 배포
```bash
# Docker 이미지 빌드
docker build -f Dockerfile.production -t fortigate-nextrade:latest .

# Registry에 푸시
docker tag fortigate-nextrade:latest registry.jclee.me/fortinet:latest
docker push registry.jclee.me/fortinet:latest
```

## 📊 모니터링

- **애플리케이션 로그**: `/logs/web_app.log`
- **Docker 로그**: `docker logs fortinet`
- **실시간 모니터링**: http://localhost:7777/dashboard

## 🔒 보안

- CSRF 보호
- Rate Limiting
- XSS 방지 헤더
- 입력 검증
- 민감 정보 환경 변수 관리

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

© 2025 Nextrade. All rights reserved.

## 📞 지원

- **이슈 트래커**: [GitHub Issues](https://github.com/JCLEE94/fortinet/issues)
- **문서**: [docs/](docs/)
- **이메일**: support@nextrade.comCI/CD 테스트용 변경사항
