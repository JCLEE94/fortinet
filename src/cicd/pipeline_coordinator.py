"""
Pipeline Coordinator - Manages CI/CD pipeline decisions and flow control

This module provides testable logic for pipeline execution decisions,
branch strategies, and deployment triggers.
"""

import os
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import hashlib


class PipelineCoordinator:
    """Coordinate CI/CD pipeline operations with testable decision logic"""
    
    DEPLOY_BRANCHES = ["main", "master"]
    TAG_PATTERN = re.compile(r'^v\d+\.\d+\.\d+')
    SKIP_PATHS = [
        r'\.md$',
        r'^docs/',
        r'^\.gitignore$',
        r'^\.github/(?!workflows)'
    ]
    
    def __init__(self, context: Optional[Dict[str, Any]] = None):
        """
        Initialize with GitHub context or environment variables
        
        Args:
            context: GitHub Actions context dictionary
        """
        self.context = context or self._load_from_env()
        
    def _load_from_env(self) -> Dict[str, Any]:
        """Load context from environment variables"""
        return {
            "sha": os.getenv("GITHUB_SHA", ""),
            "ref": os.getenv("GITHUB_REF", ""),
            "event_name": os.getenv("GITHUB_EVENT_NAME", ""),
            "actor": os.getenv("GITHUB_ACTOR", ""),
            "repository": os.getenv("GITHUB_REPOSITORY", ""),
            "run_id": os.getenv("GITHUB_RUN_ID", ""),
            "run_number": os.getenv("GITHUB_RUN_NUMBER", ""),
        }
    
    def should_deploy(self, branch: Optional[str] = None, event_type: Optional[str] = None) -> bool:
        """
        Determine if deployment should occur based on branch and event
        
        Args:
            branch: Override branch name (defaults to context)
            event_type: Override event type (defaults to context)
            
        Returns:
            True if deployment should proceed
        """
        branch = branch or self.get_branch_name()
        event_type = event_type or self.context.get("event_name", "")
        
        # Deploy on push to main branches
        if event_type == "push" and branch in self.DEPLOY_BRANCHES:
            return True
            
        # Deploy on version tags
        if event_type == "push" and self.is_version_tag():
            return True
            
        return False
    
    def should_build(self, event_type: Optional[str] = None) -> bool:
        """
        Determine if build should occur
        
        Args:
            event_type: Override event type
            
        Returns:
            True if build should proceed
        """
        event_type = event_type or self.context.get("event_name", "")
        
        # Build on push events
        if event_type == "push":
            return True
            
        # Skip builds for draft PRs
        if event_type == "pull_request" and not self._is_draft_pr():
            return True
            
        return False
    
    def should_run_tests(self) -> bool:
        """
        Determine if tests should run
        
        Returns:
            True if tests should run (almost always)
        """
        # Always run tests except for docs-only changes
        return not self._is_docs_only_change()
    
    def should_create_offline_package(self) -> bool:
        """
        Determine if offline package should be created
        
        Returns:
            True if offline package should be created
        """
        branch = self.get_branch_name()
        event_type = self.context.get("event_name", "")
        
        # Create package for main branches or tags
        return (
            event_type == "push" and 
            (branch in self.DEPLOY_BRANCHES or self.is_version_tag())
        )
    
    def get_branch_name(self) -> str:
        """Extract branch name from ref"""
        ref = self.context.get("ref", "")
        if ref.startswith("refs/heads/"):
            return ref.replace("refs/heads/", "")
        elif ref.startswith("refs/tags/"):
            return ref.replace("refs/tags/", "")
        return ref
    
    def is_version_tag(self) -> bool:
        """Check if current ref is a version tag"""
        ref = self.context.get("ref", "")
        if ref.startswith("refs/tags/"):
            tag = ref.replace("refs/tags/", "")
            return bool(self.TAG_PATTERN.match(tag))
        return False
    
    def generate_image_tag(self, sha: Optional[str] = None, branch: Optional[str] = None) -> str:
        """
        Generate consistent image tag for Docker
        
        Args:
            sha: Git SHA (defaults to context)
            branch: Branch name (defaults to context)
            
        Returns:
            Image tag string
        """
        sha = sha or self.context.get("sha", "")
        branch = branch or self.get_branch_name()
        
        # Use short SHA
        short_sha = sha[:7] if sha else "unknown"
        
        # For version tags, use the tag itself
        if self.is_version_tag():
            return self.get_branch_name()
            
        # For main branches, use branch-sha format
        return f"{branch}-{short_sha}"
    
    def get_deployment_metadata(self) -> Dict[str, str]:
        """
        Generate metadata for deployment annotations
        
        Returns:
            Dictionary of deployment metadata
        """
        return {
            "app.kubernetes.io/version": self.generate_image_tag(),
            "deployed-by": "github-actions",
            "deployed-at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "git-sha": self.context.get("sha", ""),
            "git-branch": self.get_branch_name(),
            "github-actor": self.context.get("actor", ""),
            "github-run-id": self.context.get("run_id", ""),
        }
    
    def generate_commit_message(self, image_tag: str) -> str:
        """
        Generate standardized commit message for GitOps
        
        Args:
            image_tag: The Docker image tag being deployed
            
        Returns:
            Formatted commit message
        """
        metadata = self.get_deployment_metadata()
        return f"""🚀 Update image tag to {image_tag}

📋 Deployment Info:
- Triggered by: {self.context.get('event_name', 'unknown')}
- Branch: {metadata['git-branch']}
- Actor: {metadata['github-actor']}
- Image: {image_tag}
- Timestamp: {metadata['deployed-at']}

🤖 Auto-generated by GitHub Actions"""
    
    def _is_draft_pr(self) -> bool:
        """Check if PR is draft (would need PR context)"""
        # This would need additional PR context from GitHub API
        return False
    
    def _is_docs_only_change(self) -> bool:
        """Check if only documentation files changed"""
        # This would need the list of changed files
        # For now, return False to ensure tests run
        return False
    
    def calculate_cache_key(self, prefix: str, *args) -> str:
        """
        Generate cache key for build artifacts
        
        Args:
            prefix: Cache key prefix
            *args: Additional key components
            
        Returns:
            Cache key string
        """
        components = [prefix] + list(args)
        key_string = "-".join(str(c) for c in components)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]


# Inline tests in Rust fashion
if __name__ == "__main__":
    import pytest
    
    class TestPipelineCoordinator:
        """Inline integration tests for PipelineCoordinator"""
        
        @pytest.fixture
        def github_push_main_context(self):
            """Mock GitHub context for push to main"""
            return {
                "sha": "abc123def456789012345",
                "ref": "refs/heads/main",
                "event_name": "push",
                "actor": "test-user",
                "repository": "JCLEE94/fortinet",
                "run_id": "12345",
                "run_number": "42"
            }
        
        @pytest.fixture
        def github_pr_context(self):
            """Mock GitHub context for pull request"""
            return {
                "sha": "def456abc789012345678",
                "ref": "refs/pull/123/merge",
                "event_name": "pull_request",
                "actor": "contributor",
                "repository": "JCLEE94/fortinet",
                "run_id": "67890",
                "run_number": "43"
            }
        
        @pytest.fixture
        def github_tag_context(self):
            """Mock GitHub context for version tag"""
            return {
                "sha": "789012def345abc678901",
                "ref": "refs/tags/v1.2.3",
                "event_name": "push",
                "actor": "release-bot",
                "repository": "JCLEE94/fortinet",
                "run_id": "11111",
                "run_number": "44"
            }
        
        def test_should_deploy_main_branch(self, github_push_main_context):
            """Test deployment triggers for main branch"""
            pc = PipelineCoordinator(github_push_main_context)
            assert pc.should_deploy() is True
            
        def test_should_deploy_master_branch(self):
            """Test deployment triggers for master branch"""
            pc = PipelineCoordinator()
            assert pc.should_deploy("master", "push") is True
            
        def test_should_not_deploy_feature_branch(self):
            """Test feature branches don't trigger deploy"""
            pc = PipelineCoordinator()
            assert pc.should_deploy("feature/new-feature", "push") is False
            assert pc.should_deploy("develop", "push") is False
            
        def test_should_not_deploy_on_pr(self, github_pr_context):
            """Test PRs don't trigger deployment"""
            pc = PipelineCoordinator(github_pr_context)
            assert pc.should_deploy() is False
            
        def test_should_deploy_version_tag(self, github_tag_context):
            """Test version tags trigger deployment"""
            pc = PipelineCoordinator(github_tag_context)
            assert pc.should_deploy() is True
            assert pc.is_version_tag() is True
            
        def test_image_tag_generation(self, github_push_main_context):
            """Test Docker image tag generation"""
            pc = PipelineCoordinator(github_push_main_context)
            tag = pc.generate_image_tag()
            assert tag == "main-abc123d"
            
        def test_image_tag_for_version(self, github_tag_context):
            """Test image tag for version tags"""
            pc = PipelineCoordinator(github_tag_context)
            tag = pc.generate_image_tag()
            assert tag == "v1.2.3"
            
        def test_deployment_metadata(self, github_push_main_context):
            """Test deployment metadata generation"""
            pc = PipelineCoordinator(github_push_main_context)
            metadata = pc.get_deployment_metadata()
            
            assert metadata["app.kubernetes.io/version"] == "main-abc123d"
            assert metadata["deployed-by"] == "github-actions"
            assert metadata["git-branch"] == "main"
            assert metadata["github-actor"] == "test-user"
            assert "deployed-at" in metadata
            
        def test_commit_message_generation(self, github_push_main_context):
            """Test GitOps commit message"""
            pc = PipelineCoordinator(github_push_main_context)
            msg = pc.generate_commit_message("main-abc123d")
            
            assert "🚀 Update image tag to main-abc123d" in msg
            assert "Triggered by: push" in msg
            assert "Branch: main" in msg
            assert "Actor: test-user" in msg
            
        def test_should_build_logic(self, github_push_main_context, github_pr_context):
            """Test build decision logic"""
            # Push events should build
            pc_push = PipelineCoordinator(github_push_main_context)
            assert pc_push.should_build() is True
            
            # PR events should build
            pc_pr = PipelineCoordinator(github_pr_context)
            assert pc_pr.should_build() is True
            
        def test_offline_package_creation(self, github_push_main_context, github_tag_context):
            """Test offline package creation logic"""
            # Main branch should create package
            pc_main = PipelineCoordinator(github_push_main_context)
            assert pc_main.should_create_offline_package() is True
            
            # Version tags should create package
            pc_tag = PipelineCoordinator(github_tag_context)
            assert pc_tag.should_create_offline_package() is True
            
            # Feature branches should not
            pc_feature = PipelineCoordinator()
            pc_feature.context["ref"] = "refs/heads/feature/test"
            pc_feature.context["event_name"] = "push"
            assert pc_feature.should_create_offline_package() is False
            
        def test_cache_key_generation(self):
            """Test cache key generation for builds"""
            pc = PipelineCoordinator()
            key1 = pc.calculate_cache_key("docker", "v1", "linux")
            key2 = pc.calculate_cache_key("docker", "v1", "linux")
            key3 = pc.calculate_cache_key("docker", "v2", "linux")
            
            assert key1 == key2  # Same inputs = same key
            assert key1 != key3  # Different inputs = different key
            assert len(key1) == 16  # Consistent length
    
    # Run the inline tests
    pytest.main([__file__, "-v"])