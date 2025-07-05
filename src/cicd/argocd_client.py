"""
ArgoCD Client Wrapper - Manages ArgoCD operations for deployments

This module provides a testable interface for ArgoCD operations including
authentication, application sync, and status monitoring.
"""

import os
import subprocess
import json
import time
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
import logging


class SyncStatus(Enum):
    """ArgoCD Sync Status"""
    SYNCED = "Synced"
    OUT_OF_SYNC = "OutOfSync"
    UNKNOWN = "Unknown"


class HealthStatus(Enum):
    """ArgoCD Health Status"""
    HEALTHY = "Healthy"
    PROGRESSING = "Progressing"
    DEGRADED = "Degraded"
    SUSPENDED = "Suspended"
    MISSING = "Missing"
    UNKNOWN = "Unknown"


class AuthMethod(Enum):
    """ArgoCD Authentication Methods"""
    PASSWORD = "password"
    TOKEN = "token"
    EXISTING = "existing"


class ArgoCDClient:
    """Wrapper for ArgoCD CLI operations with testable methods"""
    
    def __init__(self, server: Optional[str] = None, insecure: bool = True):
        """
        Initialize ArgoCD client
        
        Args:
            server: ArgoCD server URL
            insecure: Skip TLS verification
        """
        self.server = server or os.getenv("ARGOCD_SERVER", "argo.jclee.me")
        self.insecure = insecure
        self.logger = logging.getLogger(__name__)
        self.authenticated = False
        self.auth_method = None
        
    def authenticate(self, methods: Optional[List[AuthMethod]] = None) -> Tuple[bool, Optional[AuthMethod]]:
        """
        Try multiple authentication methods in order
        
        Args:
            methods: List of auth methods to try (defaults to all)
            
        Returns:
            Tuple of (success, method_used)
        """
        if methods is None:
            methods = [AuthMethod.PASSWORD, AuthMethod.TOKEN, AuthMethod.EXISTING]
            
        for method in methods:
            self.logger.info(f"Trying ArgoCD authentication with {method.value}")
            
            if method == AuthMethod.PASSWORD and self._try_password_auth():
                self.authenticated = True
                self.auth_method = method
                return True, method
                
            elif method == AuthMethod.TOKEN and self._try_token_auth():
                self.authenticated = True
                self.auth_method = method
                return True, method
                
            elif method == AuthMethod.EXISTING and self._try_existing_auth():
                self.authenticated = True
                self.auth_method = method
                return True, method
                
        return False, None
    
    def _try_password_auth(self) -> bool:
        """Try password-based authentication"""
        password = os.getenv("ARGOCD_PASSWORD")
        if not password:
            return False
            
        cmd = [
            "argocd", "login", self.server,
            "--username", "admin",
            "--password", password,
            "--grpc-web"
        ]
        
        if self.insecure:
            cmd.append("--insecure")
            
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Password auth failed: {e}")
            return False
    
    def _try_token_auth(self) -> bool:
        """Try token-based authentication"""
        token = os.getenv("ARGOCD_AUTH_TOKEN")
        if not token:
            return False
            
        # Set token in environment for ArgoCD CLI
        os.environ["ARGOCD_AUTH_TOKEN"] = token
        
        # Test with a simple command
        cmd = ["argocd", "app", "list", "--server", self.server, "--grpc-web"]
        
        if self.insecure:
            cmd.append("--insecure")
            
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Token auth failed: {e}")
            return False
    
    def _try_existing_auth(self) -> bool:
        """Try using existing authentication (self-hosted runner)"""
        cmd = ["argocd", "app", "list", "--grpc-web"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Existing auth check failed: {e}")
            return False
    
    def sync_application(self, app_name: str, prune: bool = True, 
                        force: bool = True, retry_limit: int = 3) -> Dict[str, Any]:
        """
        Trigger application sync
        
        Args:
            app_name: Application name
            prune: Remove resources not in Git
            force: Force sync even if no changes
            retry_limit: Number of retry attempts
            
        Returns:
            Sync result dictionary
        """
        if not self.authenticated:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
            
        cmd = ["argocd", "app", "sync", app_name]
        
        if prune:
            cmd.append("--prune")
        if force:
            cmd.append("--force")
        if retry_limit > 0:
            cmd.extend(["--retry-limit", str(retry_limit)])
            cmd.extend(["--retry-backoff-duration", "10s"])
            
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Sync operation timed out",
                "timeout": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_application_status(self, app_name: str) -> Dict[str, Any]:
        """
        Get current application status
        
        Args:
            app_name: Application name
            
        Returns:
            Application status dictionary
        """
        if not self.authenticated:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
            
        cmd = ["argocd", "app", "get", app_name, "-o", "json"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return {
                    "error": result.stderr,
                    "sync_status": SyncStatus.UNKNOWN.value,
                    "health_status": HealthStatus.UNKNOWN.value
                }
                
            app_data = json.loads(result.stdout)
            
            return {
                "sync_status": app_data.get("status", {}).get("sync", {}).get("status", SyncStatus.UNKNOWN.value),
                "health_status": app_data.get("status", {}).get("health", {}).get("status", HealthStatus.UNKNOWN.value),
                "revision": app_data.get("status", {}).get("sync", {}).get("revision", ""),
                "message": app_data.get("status", {}).get("conditions", [{}])[0].get("message", ""),
                "raw": app_data
            }
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse ArgoCD response",
                "sync_status": SyncStatus.UNKNOWN.value,
                "health_status": HealthStatus.UNKNOWN.value
            }
        except Exception as e:
            return {
                "error": str(e),
                "sync_status": SyncStatus.UNKNOWN.value,
                "health_status": HealthStatus.UNKNOWN.value
            }
    
    def wait_for_sync(self, app_name: str, timeout: int = 300, interval: int = 10) -> Tuple[bool, Dict[str, Any]]:
        """
        Wait for application to reach synced state
        
        Args:
            app_name: Application name
            timeout: Maximum wait time in seconds
            interval: Check interval in seconds
            
        Returns:
            Tuple of (success, final_status)
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_application_status(app_name)
            
            if status.get("sync_status") == SyncStatus.SYNCED.value:
                return True, status
                
            if status.get("health_status") == HealthStatus.DEGRADED.value:
                # Don't wait if app is degraded
                return False, status
                
            self.logger.info(f"Waiting for sync... Current: {status.get('sync_status')}, Health: {status.get('health_status')}")
            time.sleep(interval)
            
        # Timeout reached
        final_status = self.get_application_status(app_name)
        return False, final_status
    
    def list_applications(self) -> List[Dict[str, Any]]:
        """
        List all ArgoCD applications
        
        Returns:
            List of application summaries
        """
        if not self.authenticated:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
            
        cmd = ["argocd", "app", "list", "-o", "json"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return []
                
            apps_data = json.loads(result.stdout)
            
            return [
                {
                    "name": app.get("metadata", {}).get("name", ""),
                    "namespace": app.get("spec", {}).get("destination", {}).get("namespace", ""),
                    "sync_status": app.get("status", {}).get("sync", {}).get("status", ""),
                    "health_status": app.get("status", {}).get("health", {}).get("status", ""),
                    "cluster": app.get("spec", {}).get("destination", {}).get("server", "")
                }
                for app in apps_data
            ]
        except Exception as e:
            self.logger.error(f"Failed to list applications: {e}")
            return []
    
    def refresh_application(self, app_name: str) -> bool:
        """
        Refresh application to detect changes
        
        Args:
            app_name: Application name
            
        Returns:
            Success boolean
        """
        if not self.authenticated:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
            
        cmd = ["argocd", "app", "get", app_name, "--refresh"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception:
            return False


# Inline tests
if __name__ == "__main__":
    import pytest
    from unittest.mock import patch, MagicMock
    
    class TestArgoCDClient:
        """Inline integration tests for ArgoCDClient"""
        
        @pytest.fixture
        def client(self):
            """Create test client"""
            return ArgoCDClient(server="test.argo.local")
        
        @pytest.fixture
        def mock_subprocess(self):
            """Mock subprocess for CLI commands"""
            with patch('subprocess.run') as mock:
                yield mock
        
        def test_password_authentication(self, client, mock_subprocess, monkeypatch):
            """Test password-based authentication"""
            monkeypatch.setenv("ARGOCD_PASSWORD", "test-password")
            mock_subprocess.return_value.returncode = 0
            
            success, method = client.authenticate([AuthMethod.PASSWORD])
            
            assert success is True
            assert method == AuthMethod.PASSWORD
            assert client.authenticated is True
            
            # Verify command
            cmd = mock_subprocess.call_args[0][0]
            assert "argocd" in cmd
            assert "login" in cmd
            assert "--password" in cmd
            assert "test-password" in cmd
            
        def test_token_authentication(self, client, mock_subprocess, monkeypatch):
            """Test token-based authentication"""
            monkeypatch.setenv("ARGOCD_AUTH_TOKEN", "test-token")
            mock_subprocess.return_value.returncode = 0
            
            success, method = client.authenticate([AuthMethod.TOKEN])
            
            assert success is True
            assert method == AuthMethod.TOKEN
            assert os.getenv("ARGOCD_AUTH_TOKEN") == "test-token"
            
        def test_authentication_fallback(self, client, mock_subprocess):
            """Test authentication fallback through methods"""
            # First two methods fail, third succeeds
            mock_subprocess.return_value.returncode = 1  # Fail
            
            # Set up to succeed on third call (existing auth)
            mock_subprocess.side_effect = [
                MagicMock(returncode=1),  # Password fails
                MagicMock(returncode=1),  # Token fails  
                MagicMock(returncode=0),  # Existing succeeds
            ]
            
            success, method = client.authenticate()
            
            assert success is True
            assert method == AuthMethod.EXISTING
            assert mock_subprocess.call_count == 3
            
        def test_sync_application(self, client, mock_subprocess):
            """Test application sync operation"""
            client.authenticated = True
            mock_subprocess.return_value = MagicMock(
                returncode=0,
                stdout="Sync successful",
                stderr=""
            )
            
            result = client.sync_application("test-app")
            
            assert result["success"] is True
            assert "Sync successful" in result["stdout"]
            
            # Verify command
            cmd = mock_subprocess.call_args[0][0]
            assert "sync" in cmd
            assert "test-app" in cmd
            assert "--prune" in cmd
            assert "--force" in cmd
            
        def test_sync_requires_auth(self, client):
            """Test sync fails without authentication"""
            with pytest.raises(RuntimeError, match="Not authenticated"):
                client.sync_application("test-app")
                
        def test_get_application_status(self, client, mock_subprocess):
            """Test getting application status"""
            client.authenticated = True
            
            mock_app_data = {
                "status": {
                    "sync": {"status": "Synced", "revision": "abc123"},
                    "health": {"status": "Healthy"},
                    "conditions": [{"message": "App is healthy"}]
                }
            }
            
            mock_subprocess.return_value = MagicMock(
                returncode=0,
                stdout=json.dumps(mock_app_data)
            )
            
            status = client.get_application_status("test-app")
            
            assert status["sync_status"] == "Synced"
            assert status["health_status"] == "Healthy"
            assert status["revision"] == "abc123"
            assert "App is healthy" in status["message"]
            
        def test_wait_for_sync_success(self, client, mock_subprocess):
            """Test waiting for sync to complete"""
            client.authenticated = True
            
            # First call: OutOfSync, Second call: Synced
            mock_subprocess.side_effect = [
                MagicMock(returncode=0, stdout=json.dumps({
                    "status": {
                        "sync": {"status": "OutOfSync"},
                        "health": {"status": "Progressing"}
                    }
                })),
                MagicMock(returncode=0, stdout=json.dumps({
                    "status": {
                        "sync": {"status": "Synced"},
                        "health": {"status": "Healthy"}
                    }
                }))
            ]
            
            success, final_status = client.wait_for_sync("test-app", timeout=30, interval=1)
            
            assert success is True
            assert final_status["sync_status"] == "Synced"
            assert mock_subprocess.call_count == 2
            
        def test_wait_for_sync_timeout(self, client, mock_subprocess):
            """Test sync wait timeout"""
            client.authenticated = True
            
            # Always return OutOfSync
            mock_subprocess.return_value = MagicMock(
                returncode=0,
                stdout=json.dumps({
                    "status": {
                        "sync": {"status": "OutOfSync"},
                        "health": {"status": "Progressing"}
                    }
                })
            )
            
            success, final_status = client.wait_for_sync("test-app", timeout=2, interval=1)
            
            assert success is False
            assert final_status["sync_status"] == "OutOfSync"
            
        def test_list_applications(self, client, mock_subprocess):
            """Test listing ArgoCD applications"""
            client.authenticated = True
            
            mock_apps = [
                {
                    "metadata": {"name": "app1"},
                    "spec": {"destination": {"namespace": "default", "server": "https://kubernetes.default.svc"}},
                    "status": {"sync": {"status": "Synced"}, "health": {"status": "Healthy"}}
                },
                {
                    "metadata": {"name": "app2"},
                    "spec": {"destination": {"namespace": "prod", "server": "https://kubernetes.default.svc"}},
                    "status": {"sync": {"status": "OutOfSync"}, "health": {"status": "Degraded"}}
                }
            ]
            
            mock_subprocess.return_value = MagicMock(
                returncode=0,
                stdout=json.dumps(mock_apps)
            )
            
            apps = client.list_applications()
            
            assert len(apps) == 2
            assert apps[0]["name"] == "app1"
            assert apps[0]["sync_status"] == "Synced"
            assert apps[1]["name"] == "app2"
            assert apps[1]["health_status"] == "Degraded"
    
    # Run inline tests
    pytest.main([__file__, "-v"])