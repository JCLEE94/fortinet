"""
GitOps Manager - Manages Git operations for GitOps workflow

This module provides testable Git operations for updating manifests,
committing changes, and managing the GitOps deployment flow.
"""

import os
import subprocess
import re
import yaml
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import logging
from datetime import datetime


class GitOpsManager:
    """Manage GitOps operations for Kubernetes deployments"""
    
    def __init__(self, repo_path: Optional[str] = None):
        """
        Initialize GitOps manager
        
        Args:
            repo_path: Repository root path (defaults to cwd)
        """
        self.repo_path = Path(repo_path or os.getcwd())
        self.logger = logging.getLogger(__name__)
        self.kustomization_path = self.repo_path / "k8s" / "manifests" / "kustomization.yaml"
        
    def update_kustomization(self, image_tag: str, image_name: Optional[str] = None) -> bool:
        """
        Update kustomization.yaml with new image tag
        
        Args:
            image_tag: New image tag
            image_name: Image name (defaults to reading from file)
            
        Returns:
            Success boolean
        """
        try:
            # Read current kustomization
            with open(self.kustomization_path, 'r') as f:
                content = f.read()
                kustomization = yaml.safe_load(content)
            
            # Update images section
            if 'images' not in kustomization:
                kustomization['images'] = []
                
            # Find or create image entry
            image_found = False
            for image in kustomization['images']:
                if image_name and image.get('name') == image_name:
                    image['newTag'] = image_tag
                    image_found = True
                    break
                elif not image_name and 'newTag' in image:
                    # Update first image with newTag if no name specified
                    image['newTag'] = image_tag
                    image_found = True
                    break
                    
            if not image_found and image_name:
                # Add new image entry
                kustomization['images'].append({
                    'name': image_name,
                    'newTag': image_tag
                })
                
            # Write updated kustomization
            with open(self.kustomization_path, 'w') as f:
                yaml.dump(kustomization, f, default_flow_style=False, sort_keys=False)
                
            self.logger.info(f"Updated kustomization.yaml with tag: {image_tag}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update kustomization: {e}")
            return False
    
    def update_kustomization_regex(self, image_tag: str) -> bool:
        """
        Update kustomization.yaml using regex (fallback method)
        
        Args:
            image_tag: New image tag
            
        Returns:
            Success boolean
        """
        try:
            with open(self.kustomization_path, 'r') as f:
                content = f.read()
                
            # Update newTag using regex
            updated_content = re.sub(
                r'newTag:\s*\S+',
                f'newTag: {image_tag}',
                content
            )
            
            if content == updated_content:
                self.logger.warning("No changes made to kustomization.yaml")
                return False
                
            with open(self.kustomization_path, 'w') as f:
                f.write(updated_content)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update kustomization with regex: {e}")
            return False
    
    def add_deployment_annotations(self, annotations: Dict[str, str]) -> bool:
        """
        Add deployment annotations to kustomization.yaml
        
        Args:
            annotations: Dictionary of annotations to add
            
        Returns:
            Success boolean
        """
        try:
            with open(self.kustomization_path, 'r') as f:
                kustomization = yaml.safe_load(f)
                
            # Add or update commonAnnotations
            if 'commonAnnotations' not in kustomization:
                kustomization['commonAnnotations'] = {}
                
            kustomization['commonAnnotations'].update(annotations)
            
            with open(self.kustomization_path, 'w') as f:
                yaml.dump(kustomization, f, default_flow_style=False, sort_keys=False)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add annotations: {e}")
            return False
    
    def configure_git(self, name: str = "GitHub Actions Bot", 
                     email: str = "actions@github.com") -> bool:
        """
        Configure Git user for commits
        
        Args:
            name: Git user name
            email: Git user email
            
        Returns:
            Success boolean
        """
        try:
            subprocess.run(
                ["git", "config", "user.name", name],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            
            subprocess.run(
                ["git", "config", "user.email", email],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to configure git: {e}")
            return False
    
    def get_git_diff(self, file_path: Optional[str] = None) -> str:
        """
        Get git diff for specified file or all files
        
        Args:
            file_path: Specific file to diff
            
        Returns:
            Diff output
        """
        cmd = ["git", "diff"]
        if file_path:
            cmd.append(file_path)
            
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            return result.stdout
        except Exception as e:
            self.logger.error(f"Failed to get diff: {e}")
            return ""
    
    def stage_changes(self, files: Optional[List[str]] = None) -> bool:
        """
        Stage files for commit
        
        Args:
            files: List of files to stage (None for all)
            
        Returns:
            Success boolean
        """
        cmd = ["git", "add"]
        
        if files:
            cmd.extend(files)
        else:
            # Stage only kustomization.yaml by default
            cmd.append(str(self.kustomization_path.relative_to(self.repo_path)))
            
        try:
            subprocess.run(
                cmd,
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to stage changes: {e}")
            return False
    
    def commit_changes(self, message: str) -> bool:
        """
        Commit staged changes
        
        Args:
            message: Commit message
            
        Returns:
            Success boolean
        """
        try:
            # Check if there are changes to commit
            result = subprocess.run(
                ["git", "diff", "--cached", "--quiet"],
                cwd=self.repo_path,
                capture_output=True
            )
            
            if result.returncode == 0:
                self.logger.info("No changes to commit")
                return True
                
            # Commit changes
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            
            self.logger.info("Changes committed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to commit: {e}")
            return False
    
    def push_changes(self, branch: Optional[str] = None, max_retries: int = 3) -> bool:
        """
        Push changes to remote with retry logic
        
        Args:
            branch: Branch name (defaults to current)
            max_retries: Maximum push attempts
            
        Returns:
            Success boolean
        """
        if not branch:
            branch = self.get_current_branch()
            
        for attempt in range(max_retries):
            try:
                subprocess.run(
                    ["git", "push", "origin", f"HEAD:{branch}"],
                    cwd=self.repo_path,
                    check=True,
                    capture_output=True
                )
                
                self.logger.info(f"Successfully pushed to {branch}")
                return True
                
            except subprocess.CalledProcessError as e:
                self.logger.warning(f"Push attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    # Try to pull and rebase
                    try:
                        subprocess.run(
                            ["git", "pull", "--rebase", "origin", branch],
                            cwd=self.repo_path,
                            check=True,
                            capture_output=True
                        )
                        self.logger.info("Rebased with remote changes")
                    except subprocess.CalledProcessError:
                        self.logger.error("Failed to rebase")
                        return False
                        
        return False
    
    def get_current_branch(self) -> str:
        """
        Get current Git branch name
        
        Returns:
            Branch name
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except Exception:
            return "main"
    
    def create_gitops_commit(self, image_tag: str, metadata: Dict[str, Any]) -> bool:
        """
        Complete GitOps flow: update, stage, commit
        
        Args:
            image_tag: New image tag
            metadata: Deployment metadata
            
        Returns:
            Success boolean
        """
        # Update kustomization
        if not self.update_kustomization(image_tag):
            return False
            
        # Add annotations
        annotations = {
            "app.kubernetes.io/version": image_tag,
            "deployed-by": metadata.get("deployed-by", "github-actions"),
            "deployed-at": metadata.get("deployed-at", datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
        }
        
        if not self.add_deployment_annotations(annotations):
            self.logger.warning("Failed to add annotations, continuing anyway")
            
        # Show diff
        diff = self.get_git_diff()
        if diff:
            self.logger.info(f"Git diff:\n{diff}")
            
        # Stage changes
        if not self.stage_changes():
            return False
            
        # Create commit message
        commit_message = self._format_commit_message(image_tag, metadata)
        
        # Commit
        return self.commit_changes(commit_message)
    
    def _format_commit_message(self, image_tag: str, metadata: Dict[str, Any]) -> str:
        """Format standardized commit message"""
        return f"""🚀 Update image tag to {image_tag}

📋 Deployment Info:
- Triggered by: {metadata.get('event_name', 'unknown')}
- Branch: {metadata.get('branch', 'unknown')}
- Actor: {metadata.get('actor', 'unknown')}
- Image: {metadata.get('registry', '')}/{metadata.get('image_name', '')}:{image_tag}
- Timestamp: {metadata.get('deployed-at', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'))}

🤖 Auto-generated by GitHub Actions"""


# Inline tests
if __name__ == "__main__":
    import pytest
    import tempfile
    import shutil
    from unittest.mock import patch, MagicMock
    
    class TestGitOpsManager:
        """Inline integration tests for GitOpsManager"""
        
        @pytest.fixture
        def temp_repo(self):
            """Create temporary Git repository"""
            temp_dir = tempfile.mkdtemp()
            
            # Initialize git repo
            subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)
            
            # Create directory structure
            k8s_dir = Path(temp_dir) / "k8s" / "manifests"
            k8s_dir.mkdir(parents=True)
            
            # Create sample kustomization.yaml
            kustomization = {
                "apiVersion": "kustomize.config.k8s.io/v1beta1",
                "kind": "Kustomization",
                "resources": ["deployment.yaml", "service.yaml"],
                "images": [{
                    "name": "registry.jclee.me/fortinet",
                    "newTag": "main-abc123"
                }]
            }
            
            with open(k8s_dir / "kustomization.yaml", 'w') as f:
                yaml.dump(kustomization, f)
                
            yield temp_dir
            
            # Cleanup
            shutil.rmtree(temp_dir)
            
        @pytest.fixture
        def manager(self, temp_repo):
            """Create GitOpsManager with temp repo"""
            return GitOpsManager(temp_repo)
            
        def test_update_kustomization_yaml(self, manager):
            """Test updating kustomization.yaml with new tag"""
            success = manager.update_kustomization("main-def456")
            assert success is True
            
            # Verify update
            with open(manager.kustomization_path, 'r') as f:
                kustomization = yaml.safe_load(f)
                
            assert kustomization["images"][0]["newTag"] == "main-def456"
            
        def test_update_kustomization_regex_fallback(self, manager):
            """Test regex-based kustomization update"""
            success = manager.update_kustomization_regex("main-ghi789")
            assert success is True
            
            # Verify update
            with open(manager.kustomization_path, 'r') as f:
                content = f.read()
                
            assert "newTag: main-ghi789" in content
            
        def test_add_deployment_annotations(self, manager):
            """Test adding deployment annotations"""
            annotations = {
                "app.kubernetes.io/version": "v1.2.3",
                "deployed-by": "test-user",
                "deployed-at": "2024-01-01T00:00:00Z"
            }
            
            success = manager.add_deployment_annotations(annotations)
            assert success is True
            
            # Verify annotations
            with open(manager.kustomization_path, 'r') as f:
                kustomization = yaml.safe_load(f)
                
            assert "commonAnnotations" in kustomization
            assert kustomization["commonAnnotations"]["deployed-by"] == "test-user"
            
        def test_git_configuration(self, manager):
            """Test Git user configuration"""
            success = manager.configure_git("Test Bot", "test@example.com")
            assert success is True
            
            # Verify config
            result = subprocess.run(
                ["git", "config", "user.name"],
                cwd=manager.repo_path,
                capture_output=True,
                text=True
            )
            assert result.stdout.strip() == "Test Bot"
            
        def test_stage_and_commit_changes(self, manager):
            """Test staging and committing changes"""
            # Configure git first
            manager.configure_git()
            
            # Make a change
            manager.update_kustomization("test-tag-123")
            
            # Stage changes
            success = manager.stage_changes()
            assert success is True
            
            # Commit changes
            success = manager.commit_changes("Test commit")
            assert success is True
            
            # Verify commit
            result = subprocess.run(
                ["git", "log", "--oneline", "-1"],
                cwd=manager.repo_path,
                capture_output=True,
                text=True
            )
            assert "Test commit" in result.stdout
            
        def test_no_changes_to_commit(self, manager):
            """Test handling when no changes to commit"""
            manager.configure_git()
            
            # Try to commit without changes
            success = manager.commit_changes("Empty commit")
            assert success is True  # Should succeed but not create commit
            
        def test_get_current_branch(self, manager):
            """Test getting current branch name"""
            # Create and checkout a branch
            subprocess.run(
                ["git", "checkout", "-b", "test-branch"],
                cwd=manager.repo_path,
                capture_output=True
            )
            
            branch = manager.get_current_branch()
            assert branch == "test-branch"
            
        def test_complete_gitops_flow(self, manager):
            """Test complete GitOps workflow"""
            manager.configure_git()
            
            metadata = {
                "event_name": "push",
                "branch": "main",
                "actor": "test-user",
                "registry": "registry.jclee.me",
                "image_name": "fortinet",
                "deployed-at": "2024-01-01T12:00:00Z"
            }
            
            success = manager.create_gitops_commit("v1.0.0", metadata)
            assert success is True
            
            # Verify kustomization was updated
            with open(manager.kustomization_path, 'r') as f:
                kustomization = yaml.safe_load(f)
                
            assert kustomization["images"][0]["newTag"] == "v1.0.0"
            assert kustomization["commonAnnotations"]["app.kubernetes.io/version"] == "v1.0.0"
            
            # Verify commit was created
            result = subprocess.run(
                ["git", "log", "--oneline", "-1"],
                cwd=manager.repo_path,
                capture_output=True,
                text=True
            )
            assert "Update image tag to v1.0.0" in result.stdout
            
        @patch('subprocess.run')
        def test_push_with_retry(self, mock_run, manager):
            """Test push with retry on failure"""
            # First push fails, pull succeeds, second push succeeds
            mock_run.side_effect = [
                subprocess.CalledProcessError(1, "git push"),  # First push fails
                MagicMock(returncode=0),  # Pull rebase succeeds
                MagicMock(returncode=0),  # Second push succeeds
            ]
            
            success = manager.push_changes("main", max_retries=2)
            assert success is True
            assert mock_run.call_count == 3
            
        def test_get_git_diff(self, manager):
            """Test getting git diff"""
            # Make a change
            manager.update_kustomization("diff-test")
            
            diff = manager.get_git_diff()
            assert "newTag:" in diff
            assert "diff-test" in diff
    
    # Run inline tests
    pytest.main([__file__, "-v"])