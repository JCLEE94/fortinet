#!/bin/bash
# GitLab Runner 문제 해결 스크립트

echo "=== GitLab Runner 문제 해결 도구 ==="
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. GitLab Runner 설치 확인
echo "1. GitLab Runner 설치 확인..."
if command -v gitlab-runner &> /dev/null; then
    echo -e "${GREEN}✓ GitLab Runner가 설치되어 있습니다.${NC}"
    gitlab-runner --version
else
    echo -e "${RED}✗ GitLab Runner가 설치되어 있지 않습니다.${NC}"
    echo ""
    echo "설치 방법:"
    echo "# Ubuntu/Debian"
    echo "curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh | sudo bash"
    echo "sudo apt-get install gitlab-runner"
    echo ""
    echo "# RHEL/CentOS"
    echo "curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.rpm.sh | sudo bash"
    echo "sudo yum install gitlab-runner"
    exit 1
fi

echo ""

# 2. Docker 설치 확인
echo "2. Docker 설치 확인..."
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Docker가 설치되어 있습니다.${NC}"
    docker --version
else
    echo -e "${YELLOW}⚠ Docker가 설치되어 있지 않습니다.${NC}"
    echo "Podman을 사용하시려면 docker 별칭을 설정하세요:"
    echo "alias docker=podman"
fi

echo ""

# 3. GitLab Runner 상태 확인
echo "3. GitLab Runner 서비스 상태..."
if systemctl is-active --quiet gitlab-runner; then
    echo -e "${GREEN}✓ GitLab Runner 서비스가 실행 중입니다.${NC}"
else
    echo -e "${RED}✗ GitLab Runner 서비스가 중지되어 있습니다.${NC}"
    echo "시작하려면: sudo systemctl start gitlab-runner"
fi

echo ""

# 4. 등록된 Runner 확인
echo "4. 등록된 Runner 확인..."
sudo gitlab-runner list 2>/dev/null || gitlab-runner list 2>/dev/null

echo ""

# 5. Runner 등록
echo "5. 새 Runner 등록하기"
echo -e "${YELLOW}Runner를 등록하시겠습니까? (y/n)${NC}"
read -r response

if [[ "$response" == "y" ]]; then
    echo ""
    echo "GitLab URL: http://192.168.50.215:22080/"
    echo "프로젝트 Settings → CI/CD → Runners에서 토큰을 확인하세요."
    echo ""
    echo "다음 명령어로 등록:"
    echo "sudo gitlab-runner register \\"
    echo "  --non-interactive \\"
    echo "  --url 'http://192.168.50.215:22080/' \\"
    echo "  --registration-token 'YOUR_TOKEN' \\"
    echo "  --executor 'docker' \\"
    echo "  --docker-image 'python:3.9-slim' \\"
    echo "  --description 'fortinet-runner' \\"
    echo "  --tag-list 'docker,fortinet' \\"
    echo "  --run-untagged='true' \\"
    echo "  --locked='false' \\"
    echo "  --docker-privileged"
fi

echo ""

# 6. 네트워크 연결 확인
echo "6. GitLab 서버 연결 확인..."
if ping -c 1 192.168.50.215 &> /dev/null; then
    echo -e "${GREEN}✓ GitLab 서버에 ping이 가능합니다.${NC}"
    
    if curl -s -o /dev/null -w "%{http_code}" http://192.168.50.215:22080/api/v4/projects | grep -q "200\|401"; then
        echo -e "${GREEN}✓ GitLab API에 접근 가능합니다.${NC}"
    else
        echo -e "${RED}✗ GitLab API에 접근할 수 없습니다.${NC}"
    fi
else
    echo -e "${RED}✗ GitLab 서버에 연결할 수 없습니다.${NC}"
fi

echo ""

# 7. 일반적인 문제 해결
echo "7. 일반적인 문제 해결 방법:"
echo ""
echo "• Runner가 offline 상태인 경우:"
echo "  - sudo gitlab-runner restart"
echo "  - sudo gitlab-runner verify"
echo ""
echo "• Docker 권한 문제:"
echo "  - sudo usermod -aG docker gitlab-runner"
echo "  - sudo systemctl restart gitlab-runner"
echo ""
echo "• 네트워크 문제:"
echo "  - 방화벽 확인: sudo iptables -L"
echo "  - DNS 확인: nslookup 192.168.50.215"
echo ""
echo "• 로그 확인:"
echo "  - sudo gitlab-runner --debug run"
echo "  - sudo journalctl -u gitlab-runner -f"

echo ""
echo "=== 진단 완료 ==="