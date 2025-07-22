# FortiGate Nextrade - Parallel CI/CD Pipeline

[![CI/CD Pipeline](https://github.com/JCLEE94/fortinet/actions/workflows/ci-parallel.yml/badge.svg)](https://github.com/JCLEE94/fortinet/actions/workflows/ci-parallel.yml)
[![Manual Deploy](https://img.shields.io/badge/deploy-manual-blue.svg)](https://github.com/JCLEE94/fortinet/actions/workflows/deploy-manual.yml)
[![Registry](https://img.shields.io/badge/registry.jclee.me-ready-green.svg)](https://registry.jclee.me)
[![Version](https://img.shields.io/badge/version-2.0.0-brightgreen.svg)](https://github.com/JCLEE94/fortinet/releases/tag/v2.0.0)
[![License](https://img.shields.io/badge/license-proprietary-red.svg)](LICENSE)

FortiGate 방화벽과 FortiManager를 위한 종합적인 네트워크 모니터링 및 분석 플랫폼입니다. **병렬 CI/CD 파이프라인**으로 업그레이드되어 다중 환경 배포와 향상된 자동화를 지원합니다.

## ✨ 새로운 병렬 파이프라인 기능

### 🔄 병렬 처리
- **테스트 & 린트**: 동시 실행으로 빠른 피드백
- **다중 환경**: 개발, 스테이징, 프로덕션 병렬 배포
- **빌드 최적화**: 캐싱을 활용한 병렬 Docker 빌드

### 🎯 환경 지원
- **Production**: `https://fortinet.jclee.me` (Port: 30777)
- **Staging**: `https://fortinet-staging.jclee.me` (Port: 30779)  
- **Development**: `https://fortinet-development.jclee.me` (Port: 30778)

### 🛠 향상된 기능
- **자동 이미지 업데이트**: ArgoCD Image Updater with 환경별 태그
- **보안 스캔**: Trivy 이미지 취약점 검사, Bandit 코드 보안
- **헬스 체크**: 배포 후 자동 검증
- **수동 배포**: 커스텀 파라미터로 온디맨드 배포

## 🚀 주요 기능

- **실시간 모니터링**: 네트워크 트래픽, CPU, 메모리 사용률 모니터링
- **정책 분석**: 방화벽 정책 분석 및 패킷 경로 추적  
- **토폴로지 시각화**: 네트워크 구조 시각화
- **ITSM 연동**: 방화벽 정책 요청 및 티켓 관리
- **FortiManager Hub**: AI 기반 정책 오케스트레이션 및 컴플라이언스 자동화
- **병렬 CI/CD**: GitHub Actions 병렬 파이프라인
- **GitOps 배포**: ArgoCD 다중 환경 자동 배포
- **보안 강화**: 이미지 스캔, 코드 보안 검사
- **오프라인 배포**: 배포 완료 시 자동으로 오프라인 TAR 패키지 생성
- **로그 관리**: 실시간 로그 스트리밍 및 분석

## 📋 시스템 요구사항

### 프로덕션 환경
- **Kubernetes**: 1.20+ 클러스터
- **ArgoCD**: 2.8+ 설치됨
- **ArgoCD Image Updater**: 0.12+ (자동 배포용)
- **Docker Registry**: registry.jclee.me (인증 불필요)

### 로컬 개발 환경
- **OS**: Linux (Ubuntu 18.04+, CentOS 7+) 또는 Windows 10+
- **RAM**: 4GB 이상 (권장: 8GB)
- **Storage**: 20GB 이상 여유 공간
- **Docker**: 20.10+ 또는 Podman 3.0+
- **Python**: 3.11+

## 🚀 빠른 시작

### 1. 다중 환경 설정
```bash
# 모든 환경 설정 (development, staging, production)
./scripts/setup-multi-env.sh

# 파이프라인 구성 검증
./scripts/validate-pipeline.sh
```

### 2. 애플리케이션 배포

#### 자동 배포 (GitOps)
```bash
# master/main 푸시 → 프로덕션 배포
git push origin master

# develop 푸시 → 개발 환경 배포
git push origin develop

# staging 푸시 → 스테이징 배포
git push origin staging
```

#### 수동 배포
```bash
# 특정 환경에 배포
./scripts/deploy-parallel.sh production

# 여러 환경에 병렬 배포
./scripts/deploy-parallel.sh staging development

# 모든 환경에 헬스 체크와 함께 배포
./scripts/deploy-parallel.sh all --check --wait

# 특정 이미지 태그로 배포
./scripts/deploy-parallel.sh production --tag v2.0.20240722 --force
```

#### GitHub Actions 수동 배포
```bash
# GitHub CLI 사용
gh workflow run deploy-manual.yml \
  -f environment=production \
  -f image_tag=latest \
  -f skip_build=false

# GitHub 웹 UI: Actions → Manual Deployment → Run workflow
```

### 로컬 개발 환경
```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 개발 서버 실행 (Mock 모드)
APP_MODE=test python src/main.py --web

# 3. 접속
# http://localhost:7777
```

### Docker 로컬 테스트
```bash
# Docker로 로컬 테스트
docker build -f Dockerfile.production -t fortinet-test .
docker run -p 7777:7777 -e APP_MODE=test fortinet-test
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
├── k8s/manifests/         # Kubernetes 배포 매니페스트
├── argocd/                # ArgoCD 애플리케이션 설정
├── tests/                 # 테스트 코드
├── docs/                  # 문서
│   ├── guides/           # 사용자 가이드
│   ├── deployment/       # 배포 가이드
│   └── reports/          # 분석 리포트
├── scripts/              # 유틸리티 스크립트
│   └── initial-deploy.sh # 최초 배포 스크립트
├── Dockerfile.production # 프로덕션 Docker 이미지
└── .github/workflows/    # GitHub Actions CI/CD
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

### ArgoCD Image Updater 자동 배포
마스터 브랜치에 푸시하면 자동으로:
1. **테스트 실행**: pytest, 코드 품질 검사
2. **Docker 빌드**: Multi-stage 프로덕션 이미지  
3. **Registry 푸시**: registry.jclee.me/fortinet
4. **ArgoCD Image Updater**: 새 이미지 자동 감지 및 배포
5. **오프라인 TAR 생성**: 배포 완료 후 자동으로 오프라인 패키지 생성

### 수동 배포 및 관리
```bash
# ArgoCD 로그인
argocd login argo.jclee.me --username admin --password bingogo1 --insecure --grpc-web

# 애플리케이션 상태 확인
argocd app get fortinet

# 수동 동기화 (긴급 배포)
argocd app sync fortinet --prune

# 웹 대시보드
open https://argo.jclee.me/applications/fortinet
```

### 직접 배포 (비상시)
```bash
# Kubernetes에 직접 배포
kubectl apply -k k8s/manifests/

# 이미지 직접 업데이트
kubectl set image deployment/fortinet-app fortinet=registry.jclee.me/fortinet:new-tag -n fortinet
```

## 📊 모니터링

### ArgoCD 모니터링
- **ArgoCD 대시보드**: https://argo.jclee.me/applications/fortinet
- **애플리케이션 헬스체크**: https://fortinet.jclee.me/api/health
- **실시간 동기화 상태**: `argocd app get fortinet`

### Kubernetes 모니터링
```bash
# Pod 상태 확인
kubectl get pods -n fortinet

# 애플리케이션 로그
kubectl logs -f -n fortinet -l app=fortinet

# 리소스 사용량
kubectl top pods -n fortinet
```

### 로컬 개발 모니터링
- **개발 서버**: http://localhost:7777/dashboard
- **애플리케이션 로그**: `/logs/web_app.log`

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
- **이메일**: support@nextrade.com
# CI/CD trigger - 2025. 07. 04. (금) 14:09:25 KST
# Webhook test - 2025. 07. 07. (월) 20:44:44 KST
