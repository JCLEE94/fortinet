"""
Shared fixtures for CI/CD integration tests

Provides mock objects and test data for pipeline testing.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, Mock
from datetime import datetime


@pytest.fixture
def mock_github_context():
    """Mock GitHub Actions context with common scenarios"""
    return {
        "sha": "abc123def4567890123456789abcdef01234567",
        "ref": "refs/heads/main",
        "event_name": "push",
        "actor": "test-developer",
        "repository": "JCLEE94/fortinet",
        "run_id": "123456789",
        "run_number": "42",
        "workflow": "Main CI/CD Pipeline",
        "job": "deploy"
    }


@pytest.fixture
def mock_github_pr_context():
    """Mock GitHub PR context"""
    return {
        "sha": "def456abc7890123456789abcdef01234567890",
        "ref": "refs/pull/123/merge",
        "event_name": "pull_request",
        "actor": "contributor",
        "repository": "JCLEE94/fortinet",
        "run_id": "987654321",
        "run_number": "43",
        "workflow": "Main CI/CD Pipeline",
        "job": "test",
        "pr_number": "123",
        "pr_title": "Feature: Add new functionality",
        "pr_body": "This PR adds..."
    }


@pytest.fixture
def mock_argocd_client(mocker):
    """Mock ArgoCD client with common operations"""
    client = mocker.Mock()
    
    # Default behaviors
    client.authenticated = True
    client.server = "argo.jclee.me"
    
    # Mock methods
    client.authenticate.return_value = (True, "password")
    client.sync_application.return_value = {
        "success": True,
        "stdout": "Application synced successfully",
        "stderr": "",
        "return_code": 0
    }
    client.get_application_status.return_value = {
        "sync_status": "Synced",
        "health_status": "Healthy",
        "revision": "abc123def",
        "message": "Application is healthy"
    }
    client.wait_for_sync.return_value = (True, {
        "sync_status": "Synced",
        "health_status": "Healthy"
    })
    client.list_applications.return_value = [
        {
            "name": "fortinet",
            "namespace": "fortinet",
            "sync_status": "Synced",
            "health_status": "Healthy",
            "cluster": "https://kubernetes.default.svc"
        }
    ]
    
    return client


@pytest.fixture
def mock_docker_registry(mocker):
    """Mock Docker registry operations"""
    registry = mocker.Mock()
    
    # Default behaviors
    registry.registry = "registry.jclee.me"
    registry.authenticated = True
    
    # Mock methods
    registry.login.return_value = True
    registry.build_image.return_value = (True, "sha256:abc123def456")
    registry.push_image.return_value = (True, "sha256:1234567890abcdef")
    registry.tag_image.return_value = True
    registry.image_exists_locally.return_value = True
    registry.save_image.return_value = True
    registry.get_image_metadata.return_value = {
        "Id": "sha256:abc123def456",
        "RepoTags": ["registry.jclee.me/fortinet:latest"],
        "Size": 123456789,
        "Created": "2024-01-01T12:00:00Z"
    }
    
    return registry


@pytest.fixture
def temp_k8s_manifests():
    """Create temporary k8s manifest structure"""
    temp_dir = tempfile.mkdtemp()
    
    # Create directory structure
    k8s_dir = Path(temp_dir) / "k8s" / "manifests"
    k8s_dir.mkdir(parents=True)
    
    # Sample kustomization.yaml
    kustomization = """apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: fortinet

resources:
  - deployment.yaml
  - service.yaml
  - ingress.yaml
  - configmap.yaml

images:
  - name: registry.jclee.me/fortinet
    newTag: main-abc123d

commonLabels:
  app: fortinet
  component: web
"""
    
    (k8s_dir / "kustomization.yaml").write_text(kustomization)
    
    # Sample deployment.yaml
    deployment = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: fortinet-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fortinet
  template:
    metadata:
      labels:
        app: fortinet
    spec:
      containers:
      - name: fortinet
        image: registry.jclee.me/fortinet:latest
        ports:
        - containerPort: 7777
"""
    
    (k8s_dir / "deployment.yaml").write_text(deployment)
    
    # Sample service.yaml
    service = """apiVersion: v1
kind: Service
metadata:
  name: fortinet-service
spec:
  selector:
    app: fortinet
  ports:
  - port: 80
    targetPort: 7777
"""
    
    (k8s_dir / "service.yaml").write_text(service)
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_subprocess_success(mocker):
    """Mock subprocess for successful commands"""
    mock_run = mocker.patch('subprocess.run')
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="Command executed successfully",
        stderr=""
    )
    return mock_run


@pytest.fixture
def mock_subprocess_failure(mocker):
    """Mock subprocess for failed commands"""
    mock_run = mocker.patch('subprocess.run')
    mock_run.return_value = MagicMock(
        returncode=1,
        stdout="",
        stderr="Command failed with error"
    )
    return mock_run


@pytest.fixture
def deployment_metadata():
    """Common deployment metadata"""
    return {
        "event_name": "push",
        "branch": "main",
        "actor": "github-actions",
        "registry": "registry.jclee.me",
        "image_name": "fortinet",
        "deployed-at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git-sha": "abc123def4567890123456789abcdef01234567",
        "github-run-id": "123456789"
    }


@pytest.fixture
def offline_package_structure():
    """Create offline package directory structure"""
    temp_dir = tempfile.mkdtemp()
    
    # Create package directories
    package_dir = Path(temp_dir) / "fortinet-offline-deploy"
    (package_dir / "images").mkdir(parents=True)
    (package_dir / "manifests").mkdir(parents=True)
    (package_dir / "scripts").mkdir(parents=True)
    (package_dir / "config").mkdir(parents=True)
    
    # Create sample files
    (package_dir / "README.md").write_text("# Offline Deployment Package")
    (package_dir / "deploy.sh").write_text("#!/bin/bash\necho 'Deploying...'")
    (package_dir / "config" / "config.json").write_text('{"offline_mode": true}')
    
    yield package_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_health_check_responses():
    """Mock health check endpoint responses"""
    return [
        # Initial failure
        {"status_code": 503, "json": {"status": "starting"}},
        # Still starting
        {"status_code": 503, "json": {"status": "starting"}},
        # Healthy
        {"status_code": 200, "json": {"status": "healthy", "version": "1.0.0"}},
    ]


@pytest.fixture
def github_issue_template():
    """Template for GitHub issue creation"""
    return {
        "title": "🚨 CI/CD Pipeline Failed - {failed_jobs} - {branch}",
        "body": """## CI/CD Pipeline Failure Report

### 📋 Summary
The CI/CD pipeline has failed for commit `{sha}`.

### 🔴 Failed Jobs
- **Failed Jobs**: {failed_jobs}
- **Workflow Run ID**: {run_id}
- **Triggered by**: @{actor}
- **Branch**: `{branch}`

### 📝 Commit Information
- **SHA**: `{sha}`
- **Message**: {commit_message}

### 🔗 Links
- [View Workflow Run]({workflow_url})
- [View Commit]({commit_url})

### 📊 Job Results
{job_results}

### 🔧 Suggested Actions
1. Check the workflow logs for detailed error messages
2. Review the commit changes that triggered this failure
3. Fix the issues and push a new commit
4. Close this issue once the pipeline is green

---
*This issue was automatically created by GitHub Actions*""",
        "labels": ["ci-failure", "automated", "bug"],
        "assignees": []
    }


@pytest.fixture
def environment_configs():
    """Different environment configurations"""
    return {
        "production": {
            "APP_MODE": "production",
            "OFFLINE_MODE": "false",
            "WEB_APP_PORT": "7777",
            "WEB_APP_HOST": "0.0.0.0",
            "REDIS_ENABLED": "true",
            "FORTIMANAGER_HOST": "fortimanager.prod.local",
            "FORTIGATE_HOST": "fortigate.prod.local"
        },
        "test": {
            "APP_MODE": "test",
            "OFFLINE_MODE": "true",
            "WEB_APP_PORT": "7777",
            "WEB_APP_HOST": "127.0.0.1",
            "REDIS_ENABLED": "false",
            "DISABLE_EXTERNAL_CALLS": "true"
        },
        "development": {
            "APP_MODE": "development",
            "OFFLINE_MODE": "false",
            "WEB_APP_PORT": "7777",
            "WEB_APP_HOST": "127.0.0.1",
            "REDIS_ENABLED": "true",
            "DEBUG": "true"
        }
    }