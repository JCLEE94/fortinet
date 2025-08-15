# FortiGate Nextrade

**AI-Enhanced Network Security Management Platform**

FortiGate Nextrade는 FortiGate 방화벽, FortiManager, ITSM 시스템과 통합된 종합적인 네트워크 모니터링 및 분석 플랫폼입니다. 오프라인 환경을 위해 설계되었으며 AI 기반 보안 분석과 자동화 기능을 제공합니다.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3-green.svg)](https://flask.palletsprojects.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-brightgreen.svg)](https://docker.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-GitOps-orange.svg)](https://kubernetes.io)

## 🚀 주요 기능

### AI 기반 보안 분석
- **AI 정책 최적화**: 머신러닝 기반 방화벽 정책 자동 최적화
- **실시간 위협 탐지**: DDoS, 침입, 멀웨어, 데이터 유출 자동 탐지
- **지능형 컴플라이언스**: PCI DSS, HIPAA, GDPR 자동 준수 검사
- **예측 분석**: 트래픽 및 위협 패턴 예측

### 통합 관리
- **FortiGate 통합**: 실시간 방화벽 정책 및 상태 모니터링
- **FortiManager Advanced Hub**: 중앙집중식 보안 관리
- **ITSM 자동화**: ServiceNow 연동 티켓 자동화
- **실시간 패킷 분석**: 고급 패킷 캡처 및 분석

### 아키텍처
- **하이브리드 설계**: 모놀리식 + 마이크로서비스 지원
- **오프라인 우선**: 인터넷 연결 없이도 완전 동작
- **GitOps CI/CD**: GitHub Actions → ArgoCD 자동 배포
- **확장 가능**: Kubernetes 기반 수평 확장

## 🏗️ 기술 스택

| 구성 요소 | 기술 |
|-----------|------|
| **Backend** | Python 3.11, Flask, Blueprint |
| **Frontend** | Bootstrap 5, Vanilla JavaScript |
| **Database** | Redis (캐시), JSON (오프라인) |
| **AI/ML** | NumPy, 사용자 정의 AI 엔진 |
| **Container** | Docker, Multi-stage builds |
| **Orchestration** | Kubernetes, ArgoCD |
| **CI/CD** | GitHub Actions, Harbor Registry |
| **Gateway** | Kong (MSA), Traefik (Ingress) |

## 🚦 빠른 시작

### 로컬 개발
```bash
git clone <repository-url>
cd fortinet
pip install -r requirements.txt
cd src && python main.py --web
```

### Docker 실행
```bash
docker build -f Dockerfile.production -t fortigate-nextrade .
docker run -d -p 7777:7777 -e APP_MODE=production fortigate-nextrade
```

### MSA 개발
```bash
docker-compose -f docker-compose.msa.yml up -d
```

## 📊 AI 기능

### 정책 최적화
```bash
curl -X POST /api/fortimanager/ai/optimize-policies \
  -d '{"device_id": "FGT001"}'
```

### 위협 분석
```bash
curl -X POST /api/fortimanager/ai/threat-analysis \
  -d '{"fabric_id": "default"}'
```

## 🔧 환경 설정

```bash
APP_MODE=production
OFFLINE_MODE=true
ENABLE_THREAT_INTEL=true
ENABLE_POLICY_OPTIMIZATION=true
```

## 📦 배포

GitOps 파이프라인:
1. Code Push → GitHub
2. CI Tests → GitHub Actions  
3. Image Build → Harbor Registry
4. ArgoCD Sync → Kubernetes

## 🧪 테스트

```bash
pytest tests/ -v
python tests/test_ai_features.py
```

## 📋 API 엔드포인트

- `POST /api/fortimanager/ai/optimize-policies`
- `POST /api/fortimanager/ai/threat-analysis`
- `POST /api/fortimanager/ai/compliance-check`
- `GET /api/health`

## 🔍 문제 해결

Port 사용 중: `sudo lsof -ti:7777 | xargs kill -9`
Import 오류: `cd src && python main.py --web`

---
**버전**: v2.1.0 | **업데이트**: 2024년 8월