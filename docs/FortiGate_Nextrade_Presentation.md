# FortiGate Nextrade
## 네트워크 모니터링 & 분석 플랫폼

---

## 🎯 프로젝트 개요

**FortiGate Nextrade**는 FortiGate 방화벽과 FortiManager를 통합한 네트워크 모니터링 및 분석 플랫폼입니다.

### 핵심 가치
- **실시간 네트워크 모니터링**
- **정책 분석 및 자동화** 
- **오프라인 환경 최적화**
- **AI 기반 보안 관리**

---

## 🛠️ 기술 스택

### Backend
- **Python 3.11** - 메인 언어
- **Flask** - 웹 프레임워워크  
- **SQLite** - 로컬 데이터베이스
- **Redis** - 캐싱 (선택사항)

### Frontend
- **HTML5/CSS3/JavaScript**
- **Bootstrap** - UI 프레임워크
- **WebSocket** - 실시간 통신
- **Chart.js** - 데이터 시각화

### DevOps
- **Docker** - 컨테이너화
- **GitHub Actions** - CI/CD
- **Private Registry** - 이미지 저장소

---

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐
│   FortiGate     │────│  FortiManager   │
│   방화벽        │    │  중앙 관리      │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────────────────┘
                     │
         ┌─────────────────┐
         │ FortiGate       │
         │ Nextrade        │
         │ 플랫폼          │
         └─────────────────┘
                     │
         ┌─────────────────┐
         │ Web Dashboard   │
         │ 웹 인터페이스   │
         └─────────────────┘
```

---

## 🚀 주요 기능

### 1. 실시간 모니터링
- 네트워크 트래픽 분석
- 방화벽 정책 상태 확인
- 시스템 리소스 모니터링

### 2. FortiManager 통합
- 중앙화된 정책 관리
- 자동화된 정책 배포
- 컴플라이언스 체크

### 3. Mock 시스템
- 하드웨어 없는 개발/테스트
- 시뮬레이션 환경 제공
- 데모 및 교육용

### 4. 오프라인 지원
- 인터넷 연결 불필요
- 폐쇄망 환경 최적화
- 로컬 데이터 저장

---

## 🎨 사용자 인터페이스

### 대시보드
- **실시간 상태 표시**
- **트래픽 차트**
- **알림 및 경고**

### 정책 관리
- **정책 목록 및 편집**
- **일괄 적용**
- **백업/복원**

### 분석 도구
- **패킷 경로 추적**
- **성능 분석**
- **보안 이벤트 분석**

---

## 🔧 배포 및 운영

### Docker 기반 배포
```bash
# 간단한 배포
./scripts/deploy.sh

# 상태 확인
./scripts/deploy.sh status

# 문제 해결
./scripts/troubleshoot.sh
```

### CI/CD 파이프라인
- **자동 빌드** - GitHub push 시 자동 실행
- **테스트** - 코드 품질 및 보안 검사
- **배포** - Private Registry로 자동 배포

---

## 📊 성능 특징

### 최적화된 성능
- **CPU**: 최대 4코어 활용
- **메모리**: 4GB 제한
- **동시 연결**: 1,000+ 지원
- **응답 시간**: < 2초

### 확장성
- **컨테이너 기반** 배포
- **수평 확장** 가능
- **로드밸런싱** 지원

---

## 🔐 보안 기능

### 접근 제어
- 내부 네트워크 전용
- SSL/TLS 암호화
- 사용자 인증

### 데이터 보호
- 민감 정보 암호화
- 환경 변수 관리
- 감사 로그

---

## 🎯 사용 시나리오

### 1. 기업 네트워크 관리
- 중소기업 방화벽 관리
- 정책 자동화
- 컴플라이언스 모니터링

### 2. 교육 및 훈련
- 네트워크 보안 교육
- 실습 환경 제공
- 시뮬레이션 도구

### 3. 개발 및 테스트
- API 개발 환경
- 자동화 테스트
- 통합 검증

---

## 📈 향후 계획

### 단기 목표
- **모바일 앱** 개발
- **추가 FortiNet 제품** 연동
- **AI 기반 분석** 강화

### 장기 목표
- **클라우드 버전** 출시
- **오픈소스 공개**
- **커뮤니티 구축**

---

## 🙋‍♂️ Q&A

### 자주 묻는 질문

**Q: 실제 FortiGate 없이도 사용 가능한가요?**
A: 네, Mock 시스템으로 완전한 시뮬레이션 환경을 제공합니다.

**Q: 폐쇄망에서도 동작하나요?**
A: 네, 완전한 오프라인 환경을 지원합니다.

**Q: 설치가 복잡한가요?**
A: Docker를 이용한 원클릭 설치를 지원합니다.

---

## 📞 연락처

**프로젝트 저장소**: https://github.com/JCLEE94/fortinet

**데모 사이트**: http://localhost:7777

**기술 지원**: Docker 기반 완전 자동화 배포

---

# 감사합니다! 🎉

**FortiGate Nextrade**로 더 스마트한 네트워크 관리를 경험하세요.