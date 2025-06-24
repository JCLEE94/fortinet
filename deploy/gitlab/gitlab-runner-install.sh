#!/bin/bash
# GitLab Runner 간단한 설치 및 등록 스크립트

echo "=== GitLab Runner 간편 설정 ==="
echo ""

# GitLab 정보
GITLAB_URL="http://192.168.50.215:22080/"
RUNNER_TOKEN="glrt-t3_bwNkz4VMB9qEgrzxbudc"

# GitLab Runner 설치 확인
if ! command -v gitlab-runner &> /dev/null; then
    echo "GitLab Runner 설치 중..."
    curl -L --output /usr/local/bin/gitlab-runner https://gitlab-runner-downloads.s3.amazonaws.com/latest/binaries/gitlab-runner-linux-amd64
    chmod +x /usr/local/bin/gitlab-runner
    useradd --comment 'GitLab Runner' --create-home gitlab-runner --shell /bin/bash
    gitlab-runner install --user=gitlab-runner --working-directory=/home/gitlab-runner
fi

# 기존 Runner 정리
echo "기존 Runner 정리..."
gitlab-runner unregister --all-runners 2>/dev/null || true

# 새 Runner 등록 (간단한 설정)
echo "새 Runner 등록..."
gitlab-runner register \
  --non-interactive \
  --url "$GITLAB_URL" \
  --token "$RUNNER_TOKEN" \
  --executor "shell" \
  --description "fortinet-shell-runner" \
  --tag-list "deploy,fortinet" \
  --run-untagged \
  --locked="false"

# Runner 시작
echo "Runner 시작..."
gitlab-runner start

# 상태 확인
echo ""
echo "Runner 상태:"
gitlab-runner verify

echo ""
echo "✅ 설정 완료!"
echo "이제 GitLab에서 파이프라인이 실행될 수 있습니다."