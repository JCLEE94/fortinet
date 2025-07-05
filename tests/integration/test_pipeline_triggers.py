"""
Integration tests for CI/CD Pipeline Triggers

Tests GitHub Actions pipeline trigger conditions and decision logic
using the refactored PipelineCoordinator module.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from src.cicd import PipelineCoordinator


class TestPipelineTriggers:
    """Test GitHub Actions pipeline trigger conditions"""
    
    @pytest.fixture
    def github_contexts(self):
        """Collection of different GitHub contexts"""
        return {
            "push_main": {
                "sha": "abc123def456789012345",
                "ref": "refs/heads/main",
                "event_name": "push",
                "actor": "developer",
                "repository": "JCLEE94/fortinet",
                "run_id": "12345",
                "run_number": "42"
            },
            "push_master": {
                "sha": "def456abc789012345678",
                "ref": "refs/heads/master",
                "event_name": "push",
                "actor": "developer",
                "repository": "JCLEE94/fortinet",
                "run_id": "23456",
                "run_number": "43"
            },
            "push_feature": {
                "sha": "789012def345abc678901",
                "ref": "refs/heads/feature/new-feature",
                "event_name": "push",
                "actor": "contributor",
                "repository": "JCLEE94/fortinet",
                "run_id": "34567",
                "run_number": "44"
            },
            "pr_open": {
                "sha": "012345abc678def901234",
                "ref": "refs/pull/123/merge",
                "event_name": "pull_request",
                "actor": "contributor",
                "repository": "JCLEE94/fortinet",
                "run_id": "45678",
                "run_number": "45"
            },
            "tag_version": {
                "sha": "345678def901abc234567",
                "ref": "refs/tags/v1.2.3",
                "event_name": "push",
                "actor": "release-bot",
                "repository": "JCLEE94/fortinet",
                "run_id": "56789",
                "run_number": "46"
            },
            "tag_non_version": {
                "sha": "678901abc234def567890",
                "ref": "refs/tags/release-candidate",
                "event_name": "push",
                "actor": "developer",
                "repository": "JCLEE94/fortinet",
                "run_id": "67890",
                "run_number": "47"
            }
        }
    
    def test_push_to_main_triggers_full_pipeline(self, github_contexts):
        """Verify push to main/master branches triggers all jobs"""
        # Test main branch
        pc_main = PipelineCoordinator(github_contexts["push_main"])
        
        assert pc_main.should_run_tests() is True
        assert pc_main.should_build() is True
        assert pc_main.should_deploy() is True
        assert pc_main.should_create_offline_package() is True
        
        # Test master branch
        pc_master = PipelineCoordinator(github_contexts["push_master"])
        
        assert pc_master.should_run_tests() is True
        assert pc_master.should_build() is True
        assert pc_master.should_deploy() is True
        assert pc_master.should_create_offline_package() is True
    
    def test_push_to_feature_branch_skips_deploy(self, github_contexts):
        """Verify feature branches only run test/build, not deploy"""
        pc = PipelineCoordinator(github_contexts["push_feature"])
        
        assert pc.should_run_tests() is True
        assert pc.should_build() is True
        assert pc.should_deploy() is False  # No deployment
        assert pc.should_create_offline_package() is False  # No offline package
    
    def test_pr_event_triggers_limited_pipeline(self, github_contexts):
        """Verify PR events run tests but skip deployment"""
        pc = PipelineCoordinator(github_contexts["pr_open"])
        
        assert pc.should_run_tests() is True
        assert pc.should_build() is True  # Build for validation
        assert pc.should_deploy() is False  # No deployment
        assert pc.should_create_offline_package() is False  # No offline package
    
    def test_version_tag_triggers_deployment(self, github_contexts):
        """Verify version tags trigger full deployment"""
        pc = PipelineCoordinator(github_contexts["tag_version"])
        
        assert pc.is_version_tag() is True
        assert pc.should_run_tests() is True
        assert pc.should_build() is True
        assert pc.should_deploy() is True
        assert pc.should_create_offline_package() is True
    
    def test_non_version_tag_behavior(self, github_contexts):
        """Verify non-version tags don't trigger deployment"""
        pc = PipelineCoordinator(github_contexts["tag_non_version"])
        
        assert pc.is_version_tag() is False
        assert pc.should_deploy() is False
    
    @patch.dict(os.environ, {
        "GITHUB_SHA": "env123abc456def789012",
        "GITHUB_REF": "refs/heads/develop",
        "GITHUB_EVENT_NAME": "push",
        "GITHUB_ACTOR": "env-user",
        "GITHUB_REPOSITORY": "JCLEE94/fortinet"
    })
    def test_load_from_environment(self):
        """Test loading context from environment variables"""
        pc = PipelineCoordinator()  # No context provided
        
        assert pc.context["sha"] == "env123abc456def789012"
        assert pc.context["ref"] == "refs/heads/develop"
        assert pc.context["event_name"] == "push"
        assert pc.get_branch_name() == "develop"
    
    def test_branch_name_extraction(self, github_contexts):
        """Test branch name extraction from various refs"""
        # Branch ref
        pc_branch = PipelineCoordinator(github_contexts["push_main"])
        assert pc_branch.get_branch_name() == "main"
        
        # Tag ref
        pc_tag = PipelineCoordinator(github_contexts["tag_version"])
        assert pc_tag.get_branch_name() == "v1.2.3"
        
        # PR ref
        pc_pr = PipelineCoordinator(github_contexts["pr_open"])
        assert pc_pr.get_branch_name() == "refs/pull/123/merge"
    
    def test_image_tag_generation(self, github_contexts):
        """Test Docker image tag generation logic"""
        # Branch push
        pc_branch = PipelineCoordinator(github_contexts["push_main"])
        tag = pc_branch.generate_image_tag()
        assert tag == "main-abc123d"
        
        # Version tag
        pc_tag = PipelineCoordinator(github_contexts["tag_version"])
        tag = pc_tag.generate_image_tag()
        assert tag == "v1.2.3"
        
        # Custom inputs
        pc = PipelineCoordinator()
        tag = pc.generate_image_tag(sha="custom123456789", branch="feature/test")
        assert tag == "feature/test-custom1"
    
    def test_deployment_metadata_generation(self, github_contexts):
        """Test deployment metadata for Kubernetes annotations"""
        pc = PipelineCoordinator(github_contexts["push_main"])
        metadata = pc.get_deployment_metadata()
        
        assert metadata["app.kubernetes.io/version"] == "main-abc123d"
        assert metadata["deployed-by"] == "github-actions"
        assert metadata["git-sha"] == "abc123def456789012345"
        assert metadata["git-branch"] == "main"
        assert metadata["github-actor"] == "developer"
        assert metadata["github-run-id"] == "12345"
        assert "deployed-at" in metadata
        
        # Verify timestamp format
        import re
        timestamp_pattern = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z')
        assert timestamp_pattern.match(metadata["deployed-at"])
    
    def test_commit_message_generation(self, github_contexts):
        """Test GitOps commit message formatting"""
        pc = PipelineCoordinator(github_contexts["push_main"])
        msg = pc.generate_commit_message("main-abc123d")
        
        # Verify message structure
        assert "🚀 Update image tag to main-abc123d" in msg
        assert "📋 Deployment Info:" in msg
        assert "Triggered by: push" in msg
        assert "Branch: main" in msg
        assert "Actor: developer" in msg
        assert "🤖 Auto-generated by GitHub Actions" in msg
    
    def test_cache_key_generation(self):
        """Test cache key generation for build artifacts"""
        pc = PipelineCoordinator()
        
        # Test consistency
        key1 = pc.calculate_cache_key("docker", "v1", "linux", "amd64")
        key2 = pc.calculate_cache_key("docker", "v1", "linux", "amd64")
        assert key1 == key2
        
        # Test uniqueness
        key3 = pc.calculate_cache_key("docker", "v2", "linux", "amd64")
        assert key1 != key3
        
        # Test format
        assert len(key1) == 16
        assert key1.isalnum()
    
    @pytest.mark.parametrize("event_name,branch,should_deploy", [
        ("push", "main", True),
        ("push", "master", True),
        ("push", "develop", False),
        ("push", "feature/test", False),
        ("pull_request", "main", False),
        ("pull_request", "feature/test", False),
        ("workflow_dispatch", "main", False),
        ("schedule", "main", False),
    ])
    def test_deployment_decision_matrix(self, event_name, branch, should_deploy):
        """Test deployment decisions across various scenarios"""
        pc = PipelineCoordinator()
        assert pc.should_deploy(branch, event_name) == should_deploy
    
    def test_concurrent_pipeline_handling(self, github_contexts):
        """Test handling of concurrent pipeline runs"""
        # Simulate multiple coordinators for concurrent runs
        coordinators = [
            PipelineCoordinator(context) 
            for context in github_contexts.values()
        ]
        
        # Each should maintain independent state
        tags = [pc.generate_image_tag() for pc in coordinators]
        assert len(set(tags)) == len(tags)  # All unique
    
    def test_pipeline_failure_scenarios(self):
        """Test handling of various failure scenarios"""
        # Missing context
        pc_empty = PipelineCoordinator({})
        assert pc_empty.should_deploy() is False  # Safe default
        
        # Invalid ref format
        pc_invalid = PipelineCoordinator({
            "ref": "invalid-ref-format",
            "event_name": "push"
        })
        assert pc_invalid.get_branch_name() == "invalid-ref-format"
        assert pc_invalid.should_deploy() is False