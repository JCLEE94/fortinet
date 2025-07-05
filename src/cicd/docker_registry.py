"""
Docker Registry Client - Manages Docker registry operations

This module provides testable interface for Docker image operations
including building, tagging, and pushing to private registries.
"""

import os
import subprocess
import json
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import logging
from datetime import datetime


class DockerRegistryClient:
    """Client for Docker registry operations"""
    
    def __init__(self, registry: Optional[str] = None, 
                 username: Optional[str] = None,
                 password: Optional[str] = None):
        """
        Initialize Docker registry client
        
        Args:
            registry: Registry URL
            username: Registry username
            password: Registry password
        """
        self.registry = registry or os.getenv("DOCKER_REGISTRY", "registry.jclee.me")
        self.username = username or os.getenv("REGISTRY_USERNAME", "")
        self.password = password or os.getenv("REGISTRY_PASSWORD", "")
        self.logger = logging.getLogger(__name__)
        self.authenticated = False
        
    def login(self) -> bool:
        """
        Login to Docker registry
        
        Returns:
            Success boolean
        """
        if not self.username or not self.password:
            self.logger.error("Registry credentials not provided")
            return False
            
        try:
            # Use stdin to avoid password in command line
            process = subprocess.Popen(
                ["docker", "login", self.registry, "-u", self.username, "--password-stdin"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=self.password)
            
            if process.returncode == 0:
                self.authenticated = True
                self.logger.info(f"Successfully logged in to {self.registry}")
                return True
            else:
                self.logger.error(f"Login failed: {stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Docker login error: {e}")
            return False
    
    def build_image(self, context_path: str, dockerfile: str = "Dockerfile",
                   image_name: str = None, tags: List[str] = None,
                   build_args: Dict[str, str] = None,
                   no_cache: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Build Docker image
        
        Args:
            context_path: Build context directory
            dockerfile: Dockerfile path
            image_name: Image name (without tag)
            tags: List of tags to apply
            build_args: Build arguments
            no_cache: Disable build cache
            
        Returns:
            Tuple of (success, image_id)
        """
        if not image_name:
            image_name = "fortinet"
            
        cmd = ["docker", "build", "-f", dockerfile]
        
        # Add tags
        if tags:
            for tag in tags:
                full_tag = f"{self.registry}/{image_name}:{tag}"
                cmd.extend(["-t", full_tag])
        else:
            # Default tag
            cmd.extend(["-t", f"{self.registry}/{image_name}:latest"])
            
        # Add build args
        if build_args:
            for key, value in build_args.items():
                cmd.extend(["--build-arg", f"{key}={value}"])
                
        # No cache option
        if no_cache:
            cmd.append("--no-cache")
            
        # Add context
        cmd.append(context_path)
        
        try:
            self.logger.info(f"Building image with command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Extract image ID from output
                image_id = self._extract_image_id(result.stdout)
                self.logger.info(f"Successfully built image: {image_id}")
                return True, image_id
            else:
                self.logger.error(f"Build failed: {result.stderr}")
                return False, None
                
        except Exception as e:
            self.logger.error(f"Docker build error: {e}")
            return False, None
    
    def tag_image(self, source: str, target: str) -> bool:
        """
        Tag Docker image
        
        Args:
            source: Source image reference
            target: Target image reference
            
        Returns:
            Success boolean
        """
        try:
            result = subprocess.run(
                ["docker", "tag", source, target],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.logger.info(f"Tagged {source} as {target}")
                return True
            else:
                self.logger.error(f"Tag failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Docker tag error: {e}")
            return False
    
    def push_image(self, image_ref: str) -> Tuple[bool, Optional[str]]:
        """
        Push image to registry
        
        Args:
            image_ref: Full image reference
            
        Returns:
            Tuple of (success, digest)
        """
        if not self.authenticated:
            self.logger.error("Not authenticated. Call login() first.")
            return False, None
            
        try:
            result = subprocess.run(
                ["docker", "push", image_ref],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Extract digest from output
                digest = self._extract_digest(result.stdout)
                self.logger.info(f"Successfully pushed {image_ref} with digest: {digest}")
                return True, digest
            else:
                self.logger.error(f"Push failed: {result.stderr}")
                return False, None
                
        except Exception as e:
            self.logger.error(f"Docker push error: {e}")
            return False, None
    
    def pull_image(self, image_ref: str) -> bool:
        """
        Pull image from registry
        
        Args:
            image_ref: Full image reference
            
        Returns:
            Success boolean
        """
        try:
            result = subprocess.run(
                ["docker", "pull", image_ref],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.logger.info(f"Successfully pulled {image_ref}")
                return True
            else:
                self.logger.error(f"Pull failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Docker pull error: {e}")
            return False
    
    def image_exists_locally(self, image_ref: str) -> bool:
        """
        Check if image exists locally
        
        Args:
            image_ref: Image reference
            
        Returns:
            True if exists
        """
        try:
            result = subprocess.run(
                ["docker", "image", "inspect", image_ref],
                capture_output=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def save_image(self, image_ref: str, output_path: str) -> bool:
        """
        Save image to tar file
        
        Args:
            image_ref: Image reference
            output_path: Output tar file path
            
        Returns:
            Success boolean
        """
        try:
            with open(output_path, 'wb') as f:
                result = subprocess.run(
                    ["docker", "save", image_ref],
                    stdout=f,
                    stderr=subprocess.PIPE
                )
                
            if result.returncode == 0:
                self.logger.info(f"Saved image to {output_path}")
                return True
            else:
                self.logger.error(f"Save failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Docker save error: {e}")
            return False
    
    def load_image(self, input_path: str) -> bool:
        """
        Load image from tar file
        
        Args:
            input_path: Input tar file path
            
        Returns:
            Success boolean
        """
        try:
            with open(input_path, 'rb') as f:
                result = subprocess.run(
                    ["docker", "load"],
                    stdin=f,
                    capture_output=True,
                    text=True
                )
                
            if result.returncode == 0:
                self.logger.info(f"Loaded image from {input_path}")
                return True
            else:
                self.logger.error(f"Load failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Docker load error: {e}")
            return False
    
    def get_image_metadata(self, image_ref: str) -> Optional[Dict[str, Any]]:
        """
        Get image metadata
        
        Args:
            image_ref: Image reference
            
        Returns:
            Image metadata dict or None
        """
        try:
            result = subprocess.run(
                ["docker", "image", "inspect", image_ref],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                metadata = json.loads(result.stdout)
                if metadata:
                    return metadata[0]
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get image metadata: {e}")
            return None
    
    def generate_metadata_tags(self, base_tag: str, branch: str, 
                              sha: str, timestamp: Optional[str] = None) -> List[str]:
        """
        Generate Docker metadata tags
        
        Args:
            base_tag: Base tag name
            branch: Git branch
            sha: Git SHA
            timestamp: Optional timestamp
            
        Returns:
            List of tags
        """
        tags = []
        
        # Branch-based tags
        if branch in ["main", "master"]:
            tags.append("latest")
            
        tags.append(branch)
        
        # SHA-based tags
        tags.append(f"{branch}-{sha[:7]}")
        tags.append(f"sha-{sha[:7]}")
        
        # Timestamp tag
        if timestamp:
            tags.append(f"{branch}-{timestamp}")
            
        # Version tag if provided
        if base_tag.startswith("v"):
            tags.append(base_tag)
            # Extract semantic version
            parts = base_tag[1:].split(".")
            if len(parts) >= 2:
                tags.append(f"v{parts[0]}.{parts[1]}")
                
        return list(set(tags))  # Remove duplicates
    
    def _extract_image_id(self, build_output: str) -> Optional[str]:
        """Extract image ID from build output"""
        import re
        match = re.search(r'Successfully built ([a-f0-9]+)', build_output)
        if match:
            return match.group(1)
        return None
    
    def _extract_digest(self, push_output: str) -> Optional[str]:
        """Extract digest from push output"""
        import re
        match = re.search(r'digest: (sha256:[a-f0-9]+)', push_output)
        if match:
            return match.group(1)
        return None


# Inline tests
if __name__ == "__main__":
    import pytest
    from unittest.mock import patch, MagicMock, mock_open
    
    class TestDockerRegistryClient:
        """Inline integration tests for DockerRegistryClient"""
        
        @pytest.fixture
        def client(self):
            """Create test client"""
            return DockerRegistryClient(
                registry="test.registry.local",
                username="testuser",
                password="testpass"
            )
            
        @pytest.fixture
        def mock_subprocess(self):
            """Mock subprocess for Docker commands"""
            with patch('subprocess.run') as mock_run:
                with patch('subprocess.Popen') as mock_popen:
                    yield mock_run, mock_popen
                    
        def test_docker_login(self, client, mock_subprocess):
            """Test Docker registry login"""
            mock_run, mock_popen = mock_subprocess
            
            # Mock successful login
            mock_process = MagicMock()
            mock_process.communicate.return_value = ("Login Succeeded", "")
            mock_process.returncode = 0
            mock_popen.return_value = mock_process
            
            success = client.login()
            
            assert success is True
            assert client.authenticated is True
            
            # Verify command
            mock_popen.assert_called_once()
            args = mock_popen.call_args[0][0]
            assert "docker" in args
            assert "login" in args
            assert "test.registry.local" in args
            assert "--password-stdin" in args
            
        def test_build_image(self, client, mock_subprocess):
            """Test Docker image build"""
            mock_run, _ = mock_subprocess
            
            # Mock successful build
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Successfully built abc123def",
                stderr=""
            )
            
            success, image_id = client.build_image(
                context_path=".",
                dockerfile="Dockerfile.production",
                image_name="fortinet",
                tags=["v1.0.0", "latest"],
                build_args={"BUILD_DATE": "2024-01-01"}
            )
            
            assert success is True
            assert image_id == "abc123def"
            
            # Verify command
            cmd = mock_run.call_args[0][0]
            assert "docker" in cmd
            assert "build" in cmd
            assert "-f" in cmd
            assert "Dockerfile.production" in cmd
            assert "-t" in cmd
            assert "test.registry.local/fortinet:v1.0.0" in cmd
            assert "test.registry.local/fortinet:latest" in cmd
            assert "--build-arg" in cmd
            assert "BUILD_DATE=2024-01-01" in cmd
            
        def test_push_image(self, client, mock_subprocess):
            """Test Docker image push"""
            mock_run, _ = mock_subprocess
            client.authenticated = True
            
            # Mock successful push
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="digest: sha256:abc123def456789",
                stderr=""
            )
            
            success, digest = client.push_image("test.registry.local/fortinet:v1.0.0")
            
            assert success is True
            assert digest == "sha256:abc123def456789"
            
            # Verify command
            cmd = mock_run.call_args[0][0]
            assert cmd == ["docker", "push", "test.registry.local/fortinet:v1.0.0"]
            
        def test_push_requires_auth(self, client):
            """Test push fails without authentication"""
            success, digest = client.push_image("test.registry.local/fortinet:v1.0.0")
            
            assert success is False
            assert digest is None
            
        def test_tag_image(self, client, mock_subprocess):
            """Test Docker image tagging"""
            mock_run, _ = mock_subprocess
            
            mock_run.return_value = MagicMock(returncode=0)
            
            success = client.tag_image(
                source="fortinet:latest",
                target="test.registry.local/fortinet:v1.0.0"
            )
            
            assert success is True
            
            # Verify command
            cmd = mock_run.call_args[0][0]
            assert cmd == ["docker", "tag", "fortinet:latest", "test.registry.local/fortinet:v1.0.0"]
            
        def test_image_exists_locally(self, client, mock_subprocess):
            """Test checking if image exists"""
            mock_run, _ = mock_subprocess
            
            # Image exists
            mock_run.return_value = MagicMock(returncode=0)
            assert client.image_exists_locally("fortinet:latest") is True
            
            # Image doesn't exist
            mock_run.return_value = MagicMock(returncode=1)
            assert client.image_exists_locally("fortinet:nonexistent") is False
            
        def test_save_and_load_image(self, client, mock_subprocess):
            """Test saving and loading Docker images"""
            mock_run, _ = mock_subprocess
            
            # Test save
            mock_run.return_value = MagicMock(returncode=0)
            
            with patch('builtins.open', mock_open()) as mock_file:
                success = client.save_image("fortinet:latest", "/tmp/fortinet.tar")
                assert success is True
                mock_file.assert_called_once_with("/tmp/fortinet.tar", 'wb')
                
            # Test load
            with patch('builtins.open', mock_open(read_data=b"fake tar data")) as mock_file:
                success = client.load_image("/tmp/fortinet.tar")
                assert success is True
                mock_file.assert_called_once_with("/tmp/fortinet.tar", 'rb')
                
        def test_get_image_metadata(self, client, mock_subprocess):
            """Test getting image metadata"""
            mock_run, _ = mock_subprocess
            
            mock_metadata = [{
                "Id": "sha256:abc123",
                "RepoTags": ["fortinet:latest"],
                "Created": "2024-01-01T00:00:00Z",
                "Size": 123456789
            }]
            
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=json.dumps(mock_metadata)
            )
            
            metadata = client.get_image_metadata("fortinet:latest")
            
            assert metadata is not None
            assert metadata["Id"] == "sha256:abc123"
            assert "fortinet:latest" in metadata["RepoTags"]
            
        def test_generate_metadata_tags(self, client):
            """Test metadata tag generation"""
            tags = client.generate_metadata_tags(
                base_tag="v1.2.3",
                branch="main",
                sha="abc123def456789",
                timestamp="20240101120000"
            )
            
            assert "latest" in tags
            assert "main" in tags
            assert "main-abc123d" in tags
            assert "sha-abc123d" in tags
            assert "main-20240101120000" in tags
            assert "v1.2.3" in tags
            assert "v1.2" in tags
            
            # Test feature branch
            feature_tags = client.generate_metadata_tags(
                base_tag="feature",
                branch="feature/new-feature",
                sha="def456abc789012",
                timestamp=None
            )
            
            assert "latest" not in feature_tags
            assert "feature/new-feature" in feature_tags
            assert "feature/new-feature-def456a" in feature_tags
    
    # Run inline tests
    pytest.main([__file__, "-v"])