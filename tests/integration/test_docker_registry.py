"""
Integration tests for Docker Registry Operations

Tests Docker build, tag, and push operations to private registry
using the refactored DockerRegistryClient module.
"""

import pytest
import os
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, call, mock_open
from src.cicd import DockerRegistryClient


class TestDockerRegistryIntegration:
    """Test Docker build and push to private registry"""
    
    @pytest.fixture
    def registry_client(self):
        """Create configured registry client"""
        return DockerRegistryClient(
            registry="registry.jclee.me",
            username="testuser",
            password="testpass"
        )
    
    @pytest.fixture
    def temp_build_context(self):
        """Create temporary build context with Dockerfile"""
        temp_dir = tempfile.mkdtemp()
        
        # Create sample Dockerfile
        dockerfile_content = """
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
"""
        
        dockerfile_path = Path(temp_dir) / "Dockerfile.production"
        dockerfile_path.write_text(dockerfile_content)
        
        # Create sample requirements.txt
        requirements_path = Path(temp_dir) / "requirements.txt"
        requirements_path.write_text("flask==2.3.0\nrequests==2.31.0\n")
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @patch('subprocess.run')
    @patch('subprocess.Popen')
    def test_docker_image_build_and_tag(self, mock_popen, mock_run, 
                                       registry_client, temp_build_context):
        """Verify Docker image is built with correct tags"""
        # Mock successful build
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Successfully built abc123def456\nSuccessfully tagged registry.jclee.me/fortinet:main-abc123d",
            stderr=""
        )
        
        # Build image with multiple tags
        success, image_id = registry_client.build_image(
            context_path=temp_build_context,
            dockerfile="Dockerfile.production",
            image_name="fortinet",
            tags=["main-abc123d", "latest", "v1.0.0"],
            build_args={
                "BUILD_DATE": "2024-01-01T12:00:00Z",
                "VCS_REF": "abc123def456",
                "VERSION": "1.0.0"
            }
        )
        
        # Verify success
        assert success is True
        assert image_id == "abc123def456"
        
        # Verify Docker command
        docker_cmd = mock_run.call_args[0][0]
        assert docker_cmd[0] == "docker"
        assert docker_cmd[1] == "build"
        assert "-f" in docker_cmd
        assert "Dockerfile.production" in docker_cmd
        
        # Verify all tags are present
        cmd_str = " ".join(docker_cmd)
        assert "-t registry.jclee.me/fortinet:main-abc123d" in cmd_str
        assert "-t registry.jclee.me/fortinet:latest" in cmd_str
        assert "-t registry.jclee.me/fortinet:v1.0.0" in cmd_str
        
        # Verify build args
        assert "--build-arg BUILD_DATE=2024-01-01T12:00:00Z" in cmd_str
        assert "--build-arg VCS_REF=abc123def456" in cmd_str
        assert "--build-arg VERSION=1.0.0" in cmd_str
    
    @patch('subprocess.run')
    @patch('subprocess.Popen')
    def test_registry_authentication(self, mock_popen, mock_run, registry_client):
        """Verify registry login with credentials"""
        # Mock successful login
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("Login Succeeded\n", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        # Attempt login
        success = registry_client.login()
        
        assert success is True
        assert registry_client.authenticated is True
        
        # Verify login command
        popen_args = mock_popen.call_args[0][0]
        assert popen_args == [
            "docker", "login", "registry.jclee.me", 
            "-u", "testuser", "--password-stdin"
        ]
        
        # Verify password was sent via stdin
        mock_process.communicate.assert_called_once_with(input="testpass")
    
    @patch('subprocess.run')
    def test_image_push_and_manifest(self, mock_run, registry_client):
        """Verify image push creates proper manifest"""
        registry_client.authenticated = True
        
        # Mock successful push with digest
        push_output = """
The push refers to repository [registry.jclee.me/fortinet]
abc123: Pushed
def456: Pushed
latest: digest: sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef size: 2206
"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=push_output,
            stderr=""
        )
        
        # Push image
        success, digest = registry_client.push_image("registry.jclee.me/fortinet:latest")
        
        assert success is True
        assert digest == "sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        
        # Verify push command
        docker_cmd = mock_run.call_args[0][0]
        assert docker_cmd == ["docker", "push", "registry.jclee.me/fortinet:latest"]
    
    @patch('subprocess.run')
    def test_multi_stage_build_optimization(self, mock_run, registry_client):
        """Verify production Dockerfile builds efficiently"""
        # Test build with no-cache option
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Successfully built xyz789abc123",
            stderr=""
        )
        
        success, image_id = registry_client.build_image(
            context_path=".",
            dockerfile="Dockerfile.production",
            image_name="fortinet",
            tags=["optimized"],
            no_cache=True
        )
        
        assert success is True
        
        # Verify no-cache flag
        docker_cmd = mock_run.call_args[0][0]
        assert "--no-cache" in docker_cmd
    
    def test_registry_authentication_failure_handling(self, registry_client):
        """Test handling of authentication failures"""
        # Test with missing credentials
        client_no_creds = DockerRegistryClient(registry="registry.jclee.me")
        success = client_no_creds.login()
        assert success is False
        assert client_no_creds.authenticated is False
    
    @patch('subprocess.run')
    def test_push_without_authentication(self, mock_run, registry_client):
        """Test that push fails without authentication"""
        # Attempt push without login
        success, digest = registry_client.push_image("registry.jclee.me/fortinet:latest")
        
        assert success is False
        assert digest is None
        assert mock_run.call_count == 0  # No subprocess call made
    
    @patch('subprocess.run')
    def test_image_tagging_operations(self, mock_run, registry_client):
        """Test various image tagging scenarios"""
        mock_run.return_value = MagicMock(returncode=0)
        
        # Tag with different registry
        success = registry_client.tag_image(
            source="fortinet:latest",
            target="registry.jclee.me/fortinet:v1.0.0"
        )
        assert success is True
        
        # Tag with same registry
        success = registry_client.tag_image(
            source="registry.jclee.me/fortinet:latest",
            target="registry.jclee.me/fortinet:stable"
        )
        assert success is True
        
        # Verify commands
        calls = mock_run.call_args_list
        assert len(calls) == 2
        assert calls[0][0][0] == ["docker", "tag", "fortinet:latest", "registry.jclee.me/fortinet:v1.0.0"]
        assert calls[1][0][0] == ["docker", "tag", "registry.jclee.me/fortinet:latest", "registry.jclee.me/fortinet:stable"]
    
    @patch('subprocess.run')
    def test_image_existence_check(self, mock_run, registry_client):
        """Test checking if images exist locally"""
        # Image exists
        mock_run.return_value = MagicMock(returncode=0)
        assert registry_client.image_exists_locally("fortinet:latest") is True
        
        # Image doesn't exist
        mock_run.return_value = MagicMock(returncode=1)
        assert registry_client.image_exists_locally("fortinet:nonexistent") is False
    
    @patch('subprocess.run')
    @patch('builtins.open', new_callable=mock_open)
    def test_offline_package_image_operations(self, mock_file, mock_run, registry_client):
        """Test save/load operations for offline packages"""
        mock_run.return_value = MagicMock(returncode=0, stderr=b"")
        
        # Test saving image
        success = registry_client.save_image(
            "registry.jclee.me/fortinet:latest",
            "/tmp/fortinet-offline.tar"
        )
        assert success is True
        
        # Verify file was opened for writing
        mock_file.assert_called_with("/tmp/fortinet-offline.tar", 'wb')
        
        # Reset mock
        mock_file.reset_mock()
        
        # Test loading image
        success = registry_client.load_image("/tmp/fortinet-offline.tar")
        assert success is True
        
        # Verify file was opened for reading
        mock_file.assert_called_with("/tmp/fortinet-offline.tar", 'rb')
    
    @patch('subprocess.run')
    def test_image_metadata_retrieval(self, mock_run, registry_client):
        """Test getting image metadata/inspect data"""
        mock_metadata = [{
            "Id": "sha256:abc123def456789",
            "RepoTags": ["registry.jclee.me/fortinet:latest", "registry.jclee.me/fortinet:v1.0.0"],
            "RepoDigests": ["registry.jclee.me/fortinet@sha256:1234567890abcdef"],
            "Created": "2024-01-01T12:00:00.000000000Z",
            "Size": 234567890,
            "VirtualSize": 234567890,
            "Config": {
                "Env": ["PATH=/usr/local/bin:/usr/bin"],
                "Cmd": ["python", "main.py"],
                "WorkingDir": "/app"
            }
        }]
        
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(mock_metadata),
            stderr=""
        )
        
        metadata = registry_client.get_image_metadata("registry.jclee.me/fortinet:latest")
        
        assert metadata is not None
        assert metadata["Id"] == "sha256:abc123def456789"
        assert "registry.jclee.me/fortinet:latest" in metadata["RepoTags"]
        assert metadata["Size"] == 234567890
        assert metadata["Config"]["WorkingDir"] == "/app"
    
    def test_metadata_tag_generation(self, registry_client):
        """Test Docker metadata tag generation patterns"""
        # Test main branch tags
        tags = registry_client.generate_metadata_tags(
            base_tag="",
            branch="main",
            sha="abc123def456789",
            timestamp="20240101120000"
        )
        
        expected_tags = {
            "latest", "main", "main-abc123d", "sha-abc123d", "main-20240101120000"
        }
        assert set(tags) == expected_tags
        
        # Test version tags
        version_tags = registry_client.generate_metadata_tags(
            base_tag="v1.2.3",
            branch="main",
            sha="def456abc789012",
            timestamp=None
        )
        
        assert "v1.2.3" in version_tags
        assert "v1.2" in version_tags
        assert "latest" in version_tags
        
        # Test feature branch (no latest tag)
        feature_tags = registry_client.generate_metadata_tags(
            base_tag="",
            branch="feature/new-feature",
            sha="789012def345abc",
            timestamp="20240102180000"
        )
        
        assert "latest" not in feature_tags
        assert "feature/new-feature" in feature_tags
        assert "feature/new-feature-789012d" in feature_tags
    
    @patch('subprocess.run')
    def test_build_failure_handling(self, mock_run, registry_client):
        """Test handling of Docker build failures"""
        # Mock build failure
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Error: failed to solve: dockerfile parse error"
        )
        
        success, image_id = registry_client.build_image(
            context_path=".",
            dockerfile="Dockerfile.invalid"
        )
        
        assert success is False
        assert image_id is None
    
    @patch('subprocess.run')
    def test_push_retry_mechanism(self, mock_run, registry_client):
        """Test push retry logic for transient failures"""
        registry_client.authenticated = True
        
        # Mock network timeout
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Error: timeout exceeded while awaiting headers"
        )
        
        success, digest = registry_client.push_image("registry.jclee.me/fortinet:latest")
        
        assert success is False
        assert digest is None