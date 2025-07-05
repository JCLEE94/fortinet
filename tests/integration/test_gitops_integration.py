"""
Integration tests for GitOps Workflow

Tests GitOps operations including kustomization updates, Git commits,
and ArgoCD synchronization using the refactored modules.
"""

import pytest
import os
import yaml
import tempfile
import shutil
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from datetime import datetime
from src.cicd import GitOpsManager, PipelineCoordinator


class TestGitOpsIntegration:
    """Test GitOps workflow with ArgoCD"""
    
    @pytest.fixture
    def temp_git_repo(self):
        """Create temporary Git repository with k8s manifests"""
        temp_dir = tempfile.mkdtemp()
        
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=temp_dir)
        
        # Create k8s directory structure
        k8s_dir = Path(temp_dir) / "k8s" / "manifests"
        k8s_dir.mkdir(parents=True)
        
        # Create initial kustomization.yaml
        kustomization = {
            "apiVersion": "kustomize.config.k8s.io/v1beta1",
            "kind": "Kustomization",
            "namespace": "fortinet",
            "resources": [
                "deployment.yaml",
                "service.yaml",
                "ingress.yaml"
            ],
            "images": [{
                "name": "registry.jclee.me/fortinet",
                "newTag": "main-old123"
            }],
            "commonLabels": {
                "app": "fortinet",
                "version": "1.0.0"
            }
        }
        
        kustomization_path = k8s_dir / "kustomization.yaml"
        with open(kustomization_path, 'w') as f:
            yaml.dump(kustomization, f, default_flow_style=False)
        
        # Create sample deployment.yaml
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "fortinet-app"},
            "spec": {
                "replicas": 3,
                "selector": {"matchLabels": {"app": "fortinet"}},
                "template": {
                    "metadata": {"labels": {"app": "fortinet"}},
                    "spec": {
                        "containers": [{
                            "name": "fortinet",
                            "image": "registry.jclee.me/fortinet:latest"
                        }]
                    }
                }
            }
        }
        
        with open(k8s_dir / "deployment.yaml", 'w') as f:
            yaml.dump(deployment, f)
        
        # Initial commit
        subprocess.run(["git", "add", "-A"], cwd=temp_dir)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=temp_dir)
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def gitops_manager(self, temp_git_repo):
        """Create GitOpsManager with temp repo"""
        return GitOpsManager(temp_git_repo)
    
    def test_kustomization_update_on_build(self, gitops_manager):
        """Verify kustomization.yaml is updated with new image tag"""
        # Update with new tag
        success = gitops_manager.update_kustomization("main-new456")
        assert success is True
        
        # Read and verify update
        with open(gitops_manager.kustomization_path, 'r') as f:
            kustomization = yaml.safe_load(f)
        
        assert kustomization["images"][0]["newTag"] == "main-new456"
        assert kustomization["images"][0]["name"] == "registry.jclee.me/fortinet"
        
        # Verify other sections unchanged
        assert kustomization["namespace"] == "fortinet"
        assert len(kustomization["resources"]) == 3
    
    def test_kustomization_update_with_new_image(self, gitops_manager):
        """Test adding new image to kustomization"""
        # Add a second image
        success = gitops_manager.update_kustomization(
            image_tag="v1.0.0",
            image_name="registry.jclee.me/fortinet-sidecar"
        )
        assert success is True
        
        # Verify both images exist
        with open(gitops_manager.kustomization_path, 'r') as f:
            kustomization = yaml.safe_load(f)
        
        assert len(kustomization["images"]) == 2
        image_names = [img["name"] for img in kustomization["images"]]
        assert "registry.jclee.me/fortinet" in image_names
        assert "registry.jclee.me/fortinet-sidecar" in image_names
    
    def test_deployment_annotations_addition(self, gitops_manager):
        """Test adding deployment annotations"""
        annotations = {
            "app.kubernetes.io/version": "v1.2.3",
            "deployed-by": "github-actions",
            "deployed-at": "2024-01-01T12:00:00Z",
            "git-sha": "abc123def456",
            "git-branch": "main"
        }
        
        success = gitops_manager.add_deployment_annotations(annotations)
        assert success is True
        
        # Verify annotations added
        with open(gitops_manager.kustomization_path, 'r') as f:
            kustomization = yaml.safe_load(f)
        
        assert "commonAnnotations" in kustomization
        for key, value in annotations.items():
            assert kustomization["commonAnnotations"][key] == value
    
    def test_git_commit_and_push(self, gitops_manager):
        """Verify automated git commit/push for GitOps"""
        # Configure git
        success = gitops_manager.configure_git(
            name="GitHub Actions Bot",
            email="actions@github.com"
        )
        assert success is True
        
        # Make changes
        gitops_manager.update_kustomization("test-commit-tag")
        
        # Get diff before commit
        diff = gitops_manager.get_git_diff()
        assert "newTag:" in diff
        assert "test-commit-tag" in diff
        
        # Stage changes
        success = gitops_manager.stage_changes()
        assert success is True
        
        # Commit changes
        commit_msg = "🚀 Update image tag to test-commit-tag"
        success = gitops_manager.commit_changes(commit_msg)
        assert success is True
        
        # Verify commit
        result = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd=gitops_manager.repo_path,
            capture_output=True,
            text=True
        )
        assert "Update image tag to test-commit-tag" in result.stdout
    
    def test_complete_gitops_flow(self, gitops_manager):
        """Test complete GitOps update flow"""
        gitops_manager.configure_git()
        
        # Create metadata for deployment
        metadata = {
            "event_name": "push",
            "branch": "main",
            "actor": "developer",
            "registry": "registry.jclee.me",
            "image_name": "fortinet",
            "deployed-at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        # Execute complete flow
        success = gitops_manager.create_gitops_commit("v2.0.0", metadata)
        assert success is True
        
        # Verify all changes
        with open(gitops_manager.kustomization_path, 'r') as f:
            kustomization = yaml.safe_load(f)
        
        # Check image tag
        assert kustomization["images"][0]["newTag"] == "v2.0.0"
        
        # Check annotations
        assert kustomization["commonAnnotations"]["app.kubernetes.io/version"] == "v2.0.0"
        assert kustomization["commonAnnotations"]["deployed-by"] == "github-actions"
        
        # Verify commit exists
        result = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd=gitops_manager.repo_path,
            capture_output=True,
            text=True
        )
        assert "Update image tag to v2.0.0" in result.stdout
    
    @patch('subprocess.run')
    def test_push_with_retry_logic(self, mock_run, gitops_manager):
        """Test Git push retry on conflicts"""
        # Configure responses: first push fails, pull succeeds, second push succeeds
        responses = [
            # First push fails
            subprocess.CompletedProcess(
                args=["git", "push"],
                returncode=1,
                stdout="",
                stderr="error: failed to push"
            ),
            # Pull rebase succeeds
            subprocess.CompletedProcess(
                args=["git", "pull"],
                returncode=0,
                stdout="Successfully rebased",
                stderr=""
            ),
            # Second push succeeds
            subprocess.CompletedProcess(
                args=["git", "push"],
                returncode=0,
                stdout="Everything up-to-date",
                stderr=""
            )
        ]
        
        mock_run.side_effect = responses
        
        # Attempt push with retry
        success = gitops_manager.push_changes("main", max_retries=2)
        assert success is True
        
        # Verify retry sequence
        assert mock_run.call_count == 3
        push_calls = [call for call in mock_run.call_args_list if "push" in call[0][0]]
        pull_calls = [call for call in mock_run.call_args_list if "pull" in call[0][0]]
        assert len(push_calls) == 2
        assert len(pull_calls) == 1
    
    def test_no_changes_scenario(self, gitops_manager):
        """Test handling when no changes to commit"""
        gitops_manager.configure_git()
        
        # Try to commit without changes
        success = gitops_manager.commit_changes("Empty commit attempt")
        assert success is True  # Should succeed but not create commit
        
        # Verify no new commit created
        result = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd=gitops_manager.repo_path,
            capture_output=True,
            text=True
        )
        assert "Empty commit attempt" not in result.stdout
    
    def test_branch_detection(self, gitops_manager):
        """Test current branch detection"""
        # Default branch (master or main)
        branch = gitops_manager.get_current_branch()
        assert branch in ["master", "main"]
        
        # Create and checkout new branch
        subprocess.run(
            ["git", "checkout", "-b", "feature/test-branch"],
            cwd=gitops_manager.repo_path,
            capture_output=True
        )
        
        branch = gitops_manager.get_current_branch()
        assert branch == "feature/test-branch"
    
    def test_regex_fallback_update(self, gitops_manager):
        """Test regex-based kustomization update (fallback)"""
        # Use regex method
        success = gitops_manager.update_kustomization_regex("regex-tag-789")
        assert success is True
        
        # Verify update
        with open(gitops_manager.kustomization_path, 'r') as f:
            content = f.read()
        
        assert "newTag: regex-tag-789" in content
    
    def test_multi_cluster_annotations(self, gitops_manager):
        """Test annotations for multi-cluster deployments"""
        # Add cluster-specific annotations
        cluster_annotations = {
            "app.kubernetes.io/version": "v1.0.0",
            "deployed-by": "github-actions",
            "target-cluster": "production-primary",
            "cluster-region": "us-east-1",
            "deployment-strategy": "blue-green"
        }
        
        success = gitops_manager.add_deployment_annotations(cluster_annotations)
        assert success is True
        
        # Verify all annotations present
        with open(gitops_manager.kustomization_path, 'r') as f:
            kustomization = yaml.safe_load(f)
        
        for key, value in cluster_annotations.items():
            assert kustomization["commonAnnotations"][key] == value
    
    def test_integration_with_pipeline_coordinator(self, gitops_manager):
        """Test integration between PipelineCoordinator and GitOpsManager"""
        # Create pipeline coordinator
        context = {
            "sha": "abc123def456789",
            "ref": "refs/heads/main",
            "event_name": "push",
            "actor": "developer",
            "repository": "JCLEE94/fortinet",
            "run_id": "12345"
        }
        
        pc = PipelineCoordinator(context)
        
        # Generate image tag from coordinator
        image_tag = pc.generate_image_tag()
        
        # Get deployment metadata
        metadata = pc.get_deployment_metadata()
        
        # Use in GitOps flow
        gitops_manager.configure_git()
        success = gitops_manager.create_gitops_commit(image_tag, metadata)
        assert success is True
        
        # Verify integration
        with open(gitops_manager.kustomization_path, 'r') as f:
            kustomization = yaml.safe_load(f)
        
        assert kustomization["images"][0]["newTag"] == image_tag
        assert kustomization["commonAnnotations"]["github-run-id"] == "12345"