#!/bin/bash
# Quick setup script for GitHub Actions self-hosted runner

set -e

RUNNER_VERSION="2.311.0"
REPO_URL="https://github.com/JCLEE94/fortinet"
RUNNER_NAME="self-hosted-$(hostname)"

echo "🚀 GitHub Actions Self-Hosted Runner Quick Setup"
echo "================================================"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "❌ Please don't run this script as root"
   echo "   Run as a regular user with sudo access"
   exit 1
fi

# Create runner directory
RUNNER_DIR="$HOME/github-runner"
mkdir -p "$RUNNER_DIR"
cd "$RUNNER_DIR"

echo "📥 Downloading GitHub Actions Runner v${RUNNER_VERSION}..."
curl -o actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz -L \
  https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

echo "📦 Extracting runner..."
tar xzf ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz
rm actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

echo ""
echo "🔑 Getting runner registration token..."
echo "   Please go to: ${REPO_URL}/settings/actions/runners/new"
echo "   And copy the token from the configuration page"
echo ""
read -p "Enter registration token: " RUNNER_TOKEN

echo ""
echo "🔧 Configuring runner..."
./config.sh --url "$REPO_URL" \
  --token "$RUNNER_TOKEN" \
  --name "$RUNNER_NAME" \
  --labels "self-hosted,linux,x64,docker" \
  --work "_work" \
  --unattended \
  --replace

echo ""
echo "🎯 Installing as systemd service..."
sudo ./svc.sh install
sudo ./svc.sh start

echo ""
echo "✅ Runner setup complete!"
echo ""
echo "📊 Runner Status:"
sudo ./svc.sh status

echo ""
echo "📝 Useful commands:"
echo "   View logs:    journalctl -u actions.runner.JCLEE94-fortinet.${RUNNER_NAME} -f"
echo "   Stop runner:  sudo ./svc.sh stop"
echo "   Start runner: sudo ./svc.sh start"
echo "   Uninstall:    sudo ./svc.sh uninstall"
echo ""
echo "🎉 Your self-hosted runner is ready!"
echo "   It should appear in: ${REPO_URL}/settings/actions/runners"