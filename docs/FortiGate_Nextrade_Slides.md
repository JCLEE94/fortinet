# FortiGate Nextrade 발표자료

---

## 슬라이드 1: 타이틀
```
==============================================
            FortiGate Nextrade
      네트워크 모니터링 & 보안 관리 플랫폼
==============================================

🛡️ 실시간 모니터링  🤖 AI 기반 분석  🔒 보안 강화
```

---

## 슬라이드 2: 기술 스택
```
🛠️ 기술 스택

Backend                Frontend               DevOps
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Python 3.11         • HTML5 + Bootstrap    • Docker 컨테이너
• Flask Framework     • JavaScript           • GitHub Actions
• SQLite Database     • WebSocket            • Private Registry  
• Redis Cache         • Chart.js 시각화     • CI/CD 파이프라인
```

---

## 슬라이드 3: 시스템 아키텍처
```
🏗️ 시스템 아키텍처

    ┌─────────────────┐
    │   FortiGate     │ 🛡️ 방화벽
    │     방화벽      │
    └─────────────────┘
            │
            ▼
    ┌─────────────────┐
    │  FortiManager   │ ⚙️ 중앙관리
    │    중앙관리     │
    └─────────────────┘
            │
            ▼
    ┌─────────────────┐
    │ FortiGate       │ 🖥️ 분석플랫폼
    │ Nextrade 플랫폼 │
    └─────────────────┘
            │
            ▼
    ┌─────────────────┐
    │   웹 대시보드   │ 📊 인터페이스
    │   인터페이스    │
    └─────────────────┘
```

---

## 슬라이드 4: 주요 기능
```
🚀 주요 기능

📈 실시간 모니터링        ⚙️ 정책 자동화          🔬 Mock 시스템
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 네트워크 트래픽 분석    • 중앙화된 정책 관리     • 하드웨어 없는 테스트
• 방화벽 정책 상태       • 자동 배포 시스템       • 시뮬레이션 환경  
• 시스템 리소스 감시     • 컴플라이언스 체크      • 교육용 도구
```

---

## 슬라이드 5: 성능 지표
```
📊 성능 지표

⚡ 하드웨어 성능                    🚀 최적화 특징
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    4          4GB              • Docker 기반 컨테이너화
  CPU 코어    메모리              • 자동 스케일링 지원
                                 • 무중단 배포
  1,000+      < 2초              • 실시간 헬스체크
 동시 연결   응답 시간
```

---

## 슬라이드 6: 간편한 배포
```
🚀 간편한 배포

명령어                             CI/CD 파이프라인
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
./scripts/deploy.sh              Code Push → 자동 테스트 → 자동 배포
(원클릭 배포)                          │              │            │
                                   GitHub         Security      Docker
./scripts/deploy.sh status            Actions        Scan         Registry
(상태 확인)                                              

./scripts/troubleshoot.sh
(문제 해결)
```

---

## 슬라이드 7: 활용 분야
```
🎯 활용 분야

🏢 기업 네트워크          🎓 교육 & 훈련           ⚡ 개발 & 테스트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 중소기업 방화벽 관리    • 네트워크 보안 교육     • API 개발 환경
• 정책 자동화           • 실습 환경 제공         • 자동화 테스트
• 컴플라이언스 모니터링  • 시뮬레이션 도구        • 통합 검증
```

---

## 슬라이드 8: 마무리
```
🎉 감사합니다!

더 스마트한 네트워크 관리를 경험하세요

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📞 연락처

🔗 GitHub: github.com/JCLEE94/fortinet
🌐 Demo: http://localhost:7777  
🐳 Registry: registry.jclee.me/fortinet

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FortiGate Nextrade로 
네트워크 보안을 한 단계 업그레이드하세요!
```

---

## 💡 발표 팁

### 슬라이드별 발표 포인트:

1. **타이틀**: 프로젝트 소개 (30초)
2. **기술 스택**: 사용된 기술들 강조 (1분)  
3. **아키텍처**: 시스템 구조 설명 (1분)
4. **주요 기능**: 핵심 기능 3가지 (2분)
5. **성능 지표**: 수치로 성능 강조 (1분)
6. **배포**: 간편함 어필 (1분)
7. **활용 분야**: 다양한 사용처 (1분)
8. **마무리**: 연락처 및 감사 인사 (30초)

**총 발표 시간**: 약 8분

### 준비사항:
- 각 슬라이드를 별도 화면/페이지로 출력
- 데모 사이트 준비 (http://localhost:7777)
- 질문 답변 준비