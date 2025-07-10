# 파이프라인 안정화 가이드

## 개선 사항

### 1. 빌드 안정성 강화
- **타임아웃 설정**: 각 작업에 적절한 타임아웃 설정
- **Dockerfile 자동 생성**: 없을 경우 자동으로 기본 Dockerfile 생성
- **의존성 체크**: requirements.txt 존재 여부 확인
- **테스트 Fallback**: 테스트가 없을 경우 placeholder 테스트 생성

### 2. 에러 핸들링 개선
- **Registry 연결 테스트**: 빌드 전 레지스트리 접근성 확인
- **이미지 푸시 검증**: 빌드 후 실제 푸시 성공 여부 확인
- **매니페스트 검증**: 파일 존재 여부 및 구조 확인
- **상세한 로깅**: 각 단계별 상세 로그 출력

### 3. 재시도 로직 강화
- **Git Push 재시도**: 최대 5회 재시도 with exponential backoff
- **Conflict 해결**: Rebase 실패 시 merge로 fallback
- **Network 재시도**: 네트워크 오류 시 자동 재시도

### 4. 모니터링 및 알림
- **배포 상태 알림**: 성공/실패 상태를 명확히 표시
- **상세한 출력**: 이미지 태그, 레지스트리 링크 등 정보 제공
- **헬스체크 스크립트**: 파이프라인 전체 상태 점검 도구

## 헬스체크 사용법

```bash
# 파이프라인 전체 상태 확인
./scripts/pipeline-health-check.sh
```

## 트러블슈팅

### 자주 발생하는 문제

#### 1. Dockerfile 없음
**증상**: "Dockerfile.production not found" 에러
**해결**: 워크플로우가 자동으로 기본 Dockerfile 생성

#### 2. Registry 연결 실패
**증상**: "Registry not accessible" 에러
**해결**: 
```bash
curl -f https://registry.jclee.me/v2/
```

#### 3. Git Push 실패
**증상**: "Push failed after 5 attempts" 에러
**해결**: Manual 해결 후 재시도
```bash
git pull --rebase origin master
git push origin master
```

#### 4. 이미지 푸시 검증 실패
**증상**: "Failed to verify image push" 에러
**해결**: Registry 상태 확인
```bash
curl https://registry.jclee.me/v2/fortinet/tags/list
```

## 안정성 메트릭

### 성공률 목표
- **빌드 성공률**: > 95%
- **배포 성공률**: > 98%
- **평균 빌드 시간**: < 5분
- **평균 배포 시간**: < 3분

### 모니터링 포인트
1. **GitHub Actions 성공률**
2. **Registry 가용성**
3. **ArgoCD 동기화 상태**
4. **애플리케이션 헬스체크**

## 긴급 대응

### 파이프라인 완전 실패 시
```bash
# 1. 헬스체크 실행
./scripts/pipeline-health-check.sh

# 2. 수동 배포
./scripts/deploy-simple.sh

# 3. ArgoCD 강제 동기화
argocd app sync fortinet --prune
```

### Registry 장애 시
1. Registry 상태 확인: https://registry.jclee.me/
2. ArgoCD에서 이전 이미지로 롤백
3. 장애 복구 후 재배포

## 성능 최적화

### 빌드 캐시 활용
- GitHub Actions 캐시 사용
- Docker layer 캐시 최적화
- 의존성 캐시 활용

### 병렬 처리
- 테스트와 빌드 단계 최적화
- 독립적인 작업 병렬 실행

## 보안 강화

### 시크릿 관리
- GitHub secrets 최소 권한 원칙
- Registry 무인증 설정 (폐쇄망)
- ArgoCD 토큰 로테이션

### 이미지 보안
- 최신 base image 사용
- 취약점 스캔 (선택적)
- 멀티스테이지 빌드 활용