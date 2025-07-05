"""
CI/CD Pipeline Components for FortiGate Nextrade

This module provides testable components for CI/CD operations including:
- Pipeline coordination and decision logic
- ArgoCD integration and deployment automation
- GitOps workflow management
- Docker registry operations
"""

from .pipeline_coordinator import PipelineCoordinator
from .argocd_client import ArgoCDClient
from .gitops_manager import GitOpsManager
from .docker_registry import DockerRegistryClient

__all__ = [
    'PipelineCoordinator',
    'ArgoCDClient', 
    'GitOpsManager',
    'DockerRegistryClient'
]