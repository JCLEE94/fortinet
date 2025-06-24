#!/bin/bash
# GitLab Runner 자동 등록 스크립트

echo "=== GitLab Runner 등록 도구 ==="
echo ""
echo "이 스크립트는 GitLab Runner를 자동으로 등록합니다."
echo ""

# GitLab 정보
GITLAB_URL="http://192.168.50.215:22080/"
PROJECT_NAME="nextrade/fortinet"

echo "GitLab URL: $GITLAB_URL"
echo "프로젝트: $PROJECT_NAME"
echo ""

# 토큰 입력
echo "GitLab 프로젝트에서 Runner 토큰을 가져오세요:"
echo "1. $GITLAB_URL$PROJECT_NAME 접속"
echo "2. Settings → CI/CD → Runners → 'New project runner' 클릭"
echo "3. Registration token 복사"
echo ""
read -p "Registration Token 입력: " RUNNER_TOKEN

if [ -z "$RUNNER_TOKEN" ]; then
    echo "토큰이 입력되지 않았습니다."
    exit 1
fi

# Runner 등록
echo ""
echo "Runner 등록 중..."

sudo gitlab-runner register \
  --non-interactive \
  --url "$GITLAB_URL" \
  --registration-token "$RUNNER_TOKEN" \
  --executor "docker" \
  --docker-image "docker:24-dind" \
  --description "fortinet-auto-deploy" \
  --maintenance-note "Auto-deploy runner for FortiGate Nextrade" \
  --tag-list "docker,fortinet,deploy" \
  --run-untagged="true" \
  --locked="false" \
  --access-level="not_protected" \
  --docker-privileged \
  --docker-volumes "/var/run/docker.sock:/var/run/docker.sock" \
  --docker-volumes "/cache"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Runner 등록 성공!"
    echo ""
    
    # Runner 재시작
    sudo systemctl restart gitlab-runner
    
    # 상태 확인
    echo "Runner 상태 확인:"
    sudo gitlab-runner list
    
    echo ""
    echo "이제 커밋하면 자동으로 CI/CD가 실행됩니다!"
else
    echo ""
    echo "❌ Runner 등록 실패"
    echo ""
    echo "문제 해결 방법:"
    echo "1. 토큰이 정확한지 확인"
    echo "2. GitLab 서버가 접근 가능한지 확인"
    echo "3. sudo 권한이 있는지 확인"
fi