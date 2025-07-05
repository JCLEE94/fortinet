# GitHub Secrets 설정 가이드

## 필수 GitHub Secrets

### 1. ArgoCD 관련 Secrets

#### ARGOCD_AUTH_TOKEN
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhcmdvY2QiLCJzdWIiOiJhZG1pbjphcGlLZXkiLCJuYmYiOjE3NTE2OTYzNzEsImlhdCI6MTc1MTY5NjM3MSwianRpIjoiZmQyY2E2NGEtNTYzYi00NDNkLWIzYzYtYjJhZGYwYzZmMjczIn0.D8MOf5lQ0GNuIXy--0mcsR6iAukUXnlnM_yRbdaWWDw
```

#### ARGOCD_PASSWORD
```
bingogo1
```

### 2. Docker Registry Secrets

#### REGISTRY_USERNAME
```
qws9411
```

#### REGISTRY_PASSWORD
```
bingogo1
```

## 설정 방법

### 방법 1: GitHub UI를 통한 설정

1. GitHub 저장소로 이동: https://github.com/JCLEE94/fortinet
2. Settings → Secrets and variables → Actions 클릭
3. "New repository secret" 버튼 클릭
4. 각 Secret 추가:
   - Name: `ARGOCD_AUTH_TOKEN`
   - Secret: 위의 토큰 값 붙여넣기
   - "Add secret" 클릭

### 방법 2: GitHub CLI를 통한 설정

```bash
# GitHub CLI 설치 확인
gh --version

# 저장소에서 실행
cd /home/jclee/app/fortinet

# Secrets 추가
gh secret set ARGOCD_AUTH_TOKEN --body="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhcmdvY2QiLCJzdWIiOiJhZG1pbjphcGlLZXkiLCJuYmYiOjE3NTE2OTYzNzEsImlhdCI6MTc1MTY5NjM3MSwianRpIjoiZmQyY2E2NGEtNTYzYi00NDNkLWIzYzYtYjJhZGYwYzZmMjczIn0.D8MOf5lQ0GNuIXy--0mcsR6iAukUXnlnM_yRbdaWWDw"

gh secret set ARGOCD_PASSWORD --body="bingogo1"

# Registry secrets
gh secret set REGISTRY_USERNAME --body="qws9411"
gh secret set REGISTRY_PASSWORD --body="bingogo1"
```

## 토큰 재생성이 필요한 경우

```bash
# 1. ArgoCD 로그인
argocd login argo.jclee.me --username admin --password bingogo1 --insecure --grpc-web

# 2. 새 토큰 생성
argocd account generate-token --account admin --grpc-web

# 3. 새 토큰으로 GitHub Secret 업데이트
```

## 검증

### Secrets 확인
```bash
# GitHub CLI로 확인
gh secret list

# 출력 예시:
# ARGOCD_AUTH_TOKEN     Updated 2025-01-05
# ARGOCD_PASSWORD       Updated 2025-01-05
# REGISTRY_USERNAME     Updated 2025-01-05
# REGISTRY_PASSWORD     Updated 2025-01-05
```

### 파이프라인 테스트
```bash
# 변경사항 커밋 및 푸시
git add .
git commit -m "fix: ArgoCD authentication setup"
git push

# GitHub Actions 확인
# https://github.com/JCLEE94/fortinet/actions
```

## 문제 해결

### Self-hosted Runner에서 인증 실패
1. Runner 머신에서 실행:
   ```bash
   ./scripts/setup-self-hosted-runner.sh
   ```

2. ArgoCD 수동 로그인:
   ```bash
   argocd login argo.jclee.me --username admin --password bingogo1 --insecure --grpc-web
   ```

### 토큰 만료
- ArgoCD 토큰은 기본적으로 만료되지 않음
- 만약 만료된 경우 위의 "토큰 재생성" 절차 수행

## 참고 링크

- [GitHub Secrets 관리](https://github.com/JCLEE94/fortinet/settings/secrets/actions)
- [ArgoCD Dashboard](https://argo.jclee.me)
- [GitHub Actions](https://github.com/JCLEE94/fortinet/actions)