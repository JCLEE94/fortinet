"""
Integration tests for ArgoCD Deployment Automation

Tests ArgoCD authentication, application sync, and monitoring
using the refactored ArgoCDClient module.
"""

import pytest
import os
import json
import time
from unittest.mock import patch, MagicMock, call
from src.cicd import ArgoCDClient
from src.cicd.argocd_client import SyncStatus, HealthStatus, AuthMethod


class TestArgoCDIntegration:
    """Test ArgoCD deployment automation"""
    
    @pytest.fixture
    def argocd_client(self):
        """Create configured ArgoCD client"""
        return ArgoCDClient(server="argo.jclee.me", insecure=True)
    
    @pytest.fixture
    def mock_subprocess(self):
        """Mock subprocess for ArgoCD CLI commands"""
        with patch('subprocess.run') as mock_run:
            with patch('subprocess.Popen') as mock_popen:
                yield mock_run, mock_popen
    
    @pytest.fixture
    def auth_environments(self):
        """Different authentication environment setups"""
        return {
            "password": {"ARGOCD_PASSWORD": "bingogo1"},
            "token": {"ARGOCD_AUTH_TOKEN": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."},
            "both": {
                "ARGOCD_PASSWORD": "bingogo1",
                "ARGOCD_AUTH_TOKEN": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            },
            "none": {}
        }
    
    def test_argocd_authentication_methods(self, argocd_client, mock_subprocess, auth_environments):
        """Test multiple auth methods (password, token, existing)"""
        mock_run, mock_popen = mock_subprocess
        
        # Test 1: Password authentication
        with patch.dict(os.environ, auth_environments["password"], clear=True):
            # Mock successful password auth
            mock_process = MagicMock()
            mock_process.communicate.return_value = ("Login successful", "")
            mock_process.returncode = 0
            mock_popen.return_value = mock_process
            
            success, method = argocd_client.authenticate([AuthMethod.PASSWORD])
            
            assert success is True
            assert method == AuthMethod.PASSWORD
            assert argocd_client.authenticated is True
            
            # Verify login command
            popen_args = mock_popen.call_args[0][0]
            assert "argocd" in popen_args
            assert "login" in popen_args
            assert "argo.jclee.me" in popen_args
            assert "--password" in popen_args
            assert "--insecure" in popen_args
        
        # Reset client state
        argocd_client.authenticated = False
        mock_popen.reset_mock()
        mock_run.reset_mock()
        
        # Test 2: Token authentication
        with patch.dict(os.environ, auth_environments["token"], clear=True):
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            
            success, method = argocd_client.authenticate([AuthMethod.TOKEN])
            
            assert success is True
            assert method == AuthMethod.TOKEN
            assert os.getenv("ARGOCD_AUTH_TOKEN") is not None
            
            # Verify list command used for validation
            run_args = mock_run.call_args[0][0]
            assert "argocd" in run_args
            assert "app" in run_args
            assert "list" in run_args
        
        # Reset
        argocd_client.authenticated = False
        mock_run.reset_mock()
        
        # Test 3: Existing authentication (self-hosted runner)
        with patch.dict(os.environ, auth_environments["none"], clear=True):
            mock_run.return_value = MagicMock(returncode=0)
            
            success, method = argocd_client.authenticate([AuthMethod.EXISTING])
            
            assert success is True
            assert method == AuthMethod.EXISTING
    
    def test_authentication_fallback_sequence(self, argocd_client, mock_subprocess, auth_environments):
        """Test authentication fallback through multiple methods"""
        mock_run, mock_popen = mock_subprocess
        
        with patch.dict(os.environ, auth_environments["both"], clear=True):
            # Mock: password fails, token fails, existing succeeds
            mock_process = MagicMock()
            mock_process.communicate.return_value = ("", "Login failed")
            mock_process.returncode = 1
            mock_popen.return_value = mock_process
            
            mock_run.side_effect = [
                MagicMock(returncode=1),  # Token check fails
                MagicMock(returncode=0),  # Existing auth succeeds
            ]
            
            success, method = argocd_client.authenticate()
            
            assert success is True
            assert method == AuthMethod.EXISTING
            assert mock_popen.call_count == 1  # Password attempt
            assert mock_run.call_count == 2  # Token + existing attempts
    
    def test_application_sync_status(self, argocd_client, mock_subprocess):
        """Verify application sync completes successfully"""
        mock_run, _ = mock_subprocess
        argocd_client.authenticated = True
        
        # Mock sync command
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="application 'fortinet' synced",
            stderr=""
        )
        
        result = argocd_client.sync_application(
            app_name="fortinet",
            prune=True,
            force=True,
            retry_limit=3
        )
        
        assert result["success"] is True
        assert "synced" in result["stdout"]
        
        # Verify sync command structure
        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "argocd"
        assert cmd[1] == "app"
        assert cmd[2] == "sync"
        assert cmd[3] == "fortinet"
        assert "--prune" in cmd
        assert "--force" in cmd
        assert "--retry-limit" in cmd
        assert "3" in cmd
    
    def test_sync_retry_on_failure(self, argocd_client, mock_subprocess):
        """Test retry logic for failed syncs"""
        mock_run, _ = mock_subprocess
        argocd_client.authenticated = True
        
        # Mock timeout
        mock_run.side_effect = subprocess.TimeoutExpired("argocd", 120)
        
        result = argocd_client.sync_application("fortinet", retry_limit=2)
        
        assert result["success"] is False
        assert result.get("timeout") is True
    
    def test_get_application_status_parsing(self, argocd_client, mock_subprocess):
        """Test parsing of application status"""
        mock_run, _ = mock_subprocess
        argocd_client.authenticated = True
        
        # Mock ArgoCD app get response
        mock_app_status = {
            "metadata": {"name": "fortinet"},
            "status": {
                "sync": {
                    "status": "Synced",
                    "revision": "abc123def456"
                },
                "health": {
                    "status": "Healthy"
                },
                "conditions": [{
                    "type": "Synced",
                    "message": "Application is synced"
                }]
            }
        }
        
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(mock_app_status),
            stderr=""
        )
        
        status = argocd_client.get_application_status("fortinet")
        
        assert status["sync_status"] == "Synced"
        assert status["health_status"] == "Healthy"
        assert status["revision"] == "abc123def456"
        assert "Application is synced" in status["message"]
    
    def test_wait_for_sync_success(self, argocd_client, mock_subprocess):
        """Test waiting for sync completion"""
        mock_run, _ = mock_subprocess
        argocd_client.authenticated = True
        
        # Mock progression: OutOfSync -> Progressing -> Synced
        responses = [
            MagicMock(
                returncode=0,
                stdout=json.dumps({
                    "status": {
                        "sync": {"status": "OutOfSync"},
                        "health": {"status": "Progressing"}
                    }
                })
            ),
            MagicMock(
                returncode=0,
                stdout=json.dumps({
                    "status": {
                        "sync": {"status": "OutOfSync"},
                        "health": {"status": "Progressing"}
                    }
                })
            ),
            MagicMock(
                returncode=0,
                stdout=json.dumps({
                    "status": {
                        "sync": {"status": "Synced"},
                        "health": {"status": "Healthy"}
                    }
                })
            )
        ]
        
        mock_run.side_effect = responses
        
        # Use short intervals for testing
        success, final_status = argocd_client.wait_for_sync(
            "fortinet",
            timeout=5,
            interval=0.1
        )
        
        assert success is True
        assert final_status["sync_status"] == "Synced"
        assert final_status["health_status"] == "Healthy"
        assert mock_run.call_count == 3
    
    def test_wait_for_sync_timeout(self, argocd_client, mock_subprocess):
        """Test sync wait timeout handling"""
        mock_run, _ = mock_subprocess
        argocd_client.authenticated = True
        
        # Always return OutOfSync
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "status": {
                    "sync": {"status": "OutOfSync"},
                    "health": {"status": "Progressing"}
                }
            })
        )
        
        success, final_status = argocd_client.wait_for_sync(
            "fortinet",
            timeout=1,
            interval=0.2
        )
        
        assert success is False
        assert final_status["sync_status"] == "OutOfSync"
    
    def test_wait_for_sync_degraded_abort(self, argocd_client, mock_subprocess):
        """Test aborting wait when app becomes degraded"""
        mock_run, _ = mock_subprocess
        argocd_client.authenticated = True
        
        # Return degraded status
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "status": {
                    "sync": {"status": "OutOfSync"},
                    "health": {"status": "Degraded"}
                }
            })
        )
        
        success, final_status = argocd_client.wait_for_sync("fortinet")
        
        assert success is False
        assert final_status["health_status"] == "Degraded"
    
    def test_list_applications(self, argocd_client, mock_subprocess):
        """Test listing all ArgoCD applications"""
        mock_run, _ = mock_subprocess
        argocd_client.authenticated = True
        
        # Mock app list response
        mock_apps = [
            {
                "metadata": {"name": "fortinet"},
                "spec": {
                    "destination": {
                        "namespace": "fortinet",
                        "server": "https://kubernetes.default.svc"
                    }
                },
                "status": {
                    "sync": {"status": "Synced"},
                    "health": {"status": "Healthy"}
                }
            },
            {
                "metadata": {"name": "blacklist"},
                "spec": {
                    "destination": {
                        "namespace": "blacklist",
                        "server": "https://kubernetes.default.svc"
                    }
                },
                "status": {
                    "sync": {"status": "OutOfSync"},
                    "health": {"status": "Progressing"}
                }
            }
        ]
        
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(mock_apps),
            stderr=""
        )
        
        apps = argocd_client.list_applications()
        
        assert len(apps) == 2
        assert apps[0]["name"] == "fortinet"
        assert apps[0]["sync_status"] == "Synced"
        assert apps[0]["namespace"] == "fortinet"
        assert apps[1]["name"] == "blacklist"
        assert apps[1]["health_status"] == "Progressing"
    
    def test_refresh_application(self, argocd_client, mock_subprocess):
        """Test refreshing application to detect changes"""
        mock_run, _ = mock_subprocess
        argocd_client.authenticated = True
        
        mock_run.return_value = MagicMock(returncode=0)
        
        success = argocd_client.refresh_application("fortinet")
        
        assert success is True
        
        # Verify refresh command
        cmd = mock_run.call_args[0][0]
        assert "argocd" in cmd
        assert "app" in cmd
        assert "get" in cmd
        assert "fortinet" in cmd
        assert "--refresh" in cmd
    
    def test_sync_requires_authentication(self, argocd_client):
        """Test that sync operations require authentication"""
        with pytest.raises(RuntimeError, match="Not authenticated"):
            argocd_client.sync_application("fortinet")
        
        with pytest.raises(RuntimeError, match="Not authenticated"):
            argocd_client.get_application_status("fortinet")
        
        with pytest.raises(RuntimeError, match="Not authenticated"):
            argocd_client.list_applications()
    
    def test_multi_cluster_sync(self, argocd_client, mock_subprocess):
        """Test syncing to multiple clusters"""
        mock_run, _ = mock_subprocess
        argocd_client.authenticated = True
        
        # Mock listing apps across clusters
        mock_apps = [
            {
                "metadata": {"name": "fortinet-primary"},
                "spec": {
                    "destination": {
                        "namespace": "fortinet",
                        "server": "https://cluster1.k8s.local"
                    }
                },
                "status": {
                    "sync": {"status": "Synced"},
                    "health": {"status": "Healthy"}
                }
            },
            {
                "metadata": {"name": "fortinet-secondary"},
                "spec": {
                    "destination": {
                        "namespace": "fortinet",
                        "server": "https://cluster2.k8s.local"
                    }
                },
                "status": {
                    "sync": {"status": "OutOfSync"},
                    "health": {"status": "Progressing"}
                }
            }
        ]
        
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(mock_apps)
        )
        
        apps = argocd_client.list_applications()
        
        # Verify multi-cluster apps detected
        clusters = set(app["cluster"] for app in apps)
        assert len(clusters) == 2
        assert "https://cluster1.k8s.local" in clusters
        assert "https://cluster2.k8s.local" in clusters