# CI/CD Integration Testing Guide

## Overview

This guide documents the comprehensive CI/CD integration testing framework implemented for the FortiGate Nextrade project. The framework provides testable modules and integration tests following Rust-style inline testing patterns.

## Architecture

### Testable CI/CD Modules

The CI/CD pipeline has been refactored into four main testable modules located in `src/cicd/`:

#### 1. PipelineCoordinator (`pipeline_coordinator.py`)
Manages CI/CD pipeline decisions and flow control.

**Key Features:**
- Deployment trigger logic based on branch and event type
- Docker image tag generation
- Deployment metadata creation for Kubernetes annotations
- Branch name extraction from Git refs
- Cache key generation for build artifacts

**Usage Example:**
```python
from src.cicd import PipelineCoordinator

# Initialize with GitHub context
context = {
    "sha": "abc123def456789",
    "ref": "refs/heads/main",
    "event_name": "push",
    "actor": "developer"
}
pc = PipelineCoordinator(context)

# Check deployment decisions
if pc.should_deploy():
    tag = pc.generate_image_tag()
    metadata = pc.get_deployment_metadata()
```

#### 2. ArgoCDClient (`argocd_client.py`)
Wrapper for ArgoCD operations with multiple authentication methods.

**Key Features:**
- Three authentication methods: password, token, existing
- Application sync with retry logic
- Status monitoring and health checks
- Wait for sync completion with timeout
- Application listing and refresh

**Usage Example:**
```python
from src.cicd import ArgoCDClient

client = ArgoCDClient(server="argo.jclee.me")

# Authenticate with fallback
success, method = client.authenticate()

if success:
    # Sync application
    result = client.sync_application("fortinet", prune=True, force=True)
    
    # Wait for sync
    synced, status = client.wait_for_sync("fortinet", timeout=300)
```

#### 3. GitOpsManager (`gitops_manager.py`)
Manages Git operations for GitOps workflow.

**Key Features:**
- Kustomization.yaml updates (YAML and regex methods)
- Deployment annotation management
- Git configuration and operations
- Commit message formatting
- Push with retry on conflicts

**Usage Example:**
```python
from src.cicd import GitOpsManager

manager = GitOpsManager()
manager.configure_git()

# Update kustomization with new image tag
manager.update_kustomization("v1.2.3")

# Add deployment annotations
annotations = {
    "app.kubernetes.io/version": "v1.2.3",
    "deployed-by": "github-actions"
}
manager.add_deployment_annotations(annotations)

# Commit and push
manager.stage_changes()
manager.commit_changes("🚀 Update image tag to v1.2.3")
manager.push_changes("main")
```

#### 4. DockerRegistryClient (`docker_registry.py`)
Handles Docker registry operations for private registries.

**Key Features:**
- Secure registry authentication
- Image building with multi-tag support
- Push/pull operations
- Image metadata retrieval
- Offline package support (save/load)
- Metadata tag generation

**Usage Example:**
```python
from src.cicd import DockerRegistryClient

client = DockerRegistryClient(
    registry="registry.jclee.me",
    username="user",
    password="pass"
)

# Login to registry
if client.login():
    # Build image
    success, image_id = client.build_image(
        context_path=".",
        dockerfile="Dockerfile.production",
        tags=["v1.0.0", "latest"]
    )
    
    # Push to registry
    if success:
        pushed, digest = client.push_image("registry.jclee.me/fortinet:v1.0.0")
```

## Integration Tests

### Test Structure

Integration tests are located in `tests/integration/` with comprehensive coverage:

1. **test_pipeline_triggers.py** - Tests GitHub Actions trigger scenarios
2. **test_docker_registry.py** - Tests Docker operations
3. **test_gitops_integration.py** - Tests GitOps workflow
4. **test_argocd_integration.py** - Tests ArgoCD deployment
5. **test_health_check.py** - Tests post-deployment validation

### Running Tests

```bash
# Run all CI/CD integration tests
pytest tests/integration/ -v

# Run specific test file
pytest tests/integration/test_pipeline_triggers.py -v

# Run with coverage
pytest tests/integration/ -v --cov=src/cicd --cov-report=html

# Run inline tests in modules
python src/cicd/pipeline_coordinator.py -v
python src/cicd/argocd_client.py -v
```

### Test Fixtures

Common fixtures are provided in `tests/fixtures/cicd_fixtures.py`:

- `mock_github_context` - GitHub Actions context
- `mock_argocd_client` - Pre-configured ArgoCD client
- `mock_docker_registry` - Docker registry operations
- `temp_k8s_manifests` - Temporary Kubernetes manifest structure
- `deployment_metadata` - Common deployment metadata

## Best Practices

### 1. Mock External Dependencies
Always mock subprocess calls and network requests:
```python
@patch('subprocess.run')
def test_docker_build(mock_run):
    mock_run.return_value = MagicMock(returncode=0)
    # Test logic here
```

### 2. Test Authentication Fallbacks
Ensure all authentication methods are tested:
```python
def test_authentication_fallback(client, mock_subprocess):
    # Mock: password fails, token fails, existing succeeds
    mock_subprocess.side_effect = [
        MagicMock(returncode=1),  # Password fails
        MagicMock(returncode=1),  # Token fails  
        MagicMock(returncode=0),  # Existing succeeds
    ]
    
    success, method = client.authenticate()
    assert method == AuthMethod.EXISTING
```

### 3. Verify Retry Logic
Test retry mechanisms for transient failures:
```python
def test_push_with_retry(manager, mock_run):
    # First push fails, pull succeeds, second push succeeds
    mock_run.side_effect = [
        subprocess.CalledProcessError(1, "git push"),
        MagicMock(returncode=0),  # Pull succeeds
        MagicMock(returncode=0),  # Push succeeds
    ]
    
    success = manager.push_changes("main", max_retries=2)
    assert success is True
```

### 4. Test Success and Failure Paths
Always test both scenarios:
```python
def test_health_check_success_and_failure():
    # Test successful health check
    mock_response = MagicMock(status_code=200)
    # ... assertions
    
    # Test failed health check
    mock_response = MagicMock(status_code=503)
    # ... assertions
```

### 5. Use Realistic Test Data
Create fixtures that mirror production data:
```python
@pytest.fixture
def github_push_main_context():
    return {
        "sha": "abc123def456789012345",
        "ref": "refs/heads/main",
        "event_name": "push",
        "actor": "developer",
        "repository": "JCLEE94/fortinet"
    }
```

## Inline Testing Pattern

Following Rust's inline testing pattern, each module includes its own tests:

```python
# At the end of the module file
if __name__ == "__main__":
    import pytest
    
    class TestModuleName:
        """Inline tests for ModuleName"""
        
        def test_functionality(self):
            # Test implementation
            pass
    
    # Run inline tests
    pytest.main([__file__, "-v"])
```

This allows running tests directly:
```bash
python src/cicd/pipeline_coordinator.py -v
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   export PYTHONPATH=$PYTHONPATH:$(pwd)
   ```

2. **Missing Dependencies**
   ```bash
   pip install pytest pytest-mock pytest-cov
   ```

3. **Test Discovery Issues**
   Ensure test files follow naming convention: `test_*.py`

4. **Mock Subprocess Failures**
   Always specify return values for subprocess mocks

## Future Enhancements

1. **Performance Testing**
   - Add benchmarks for CI/CD operations
   - Test with large repositories

2. **Security Testing**
   - Test credential handling
   - Verify secure communication

3. **Multi-Cluster Testing**
   - Test deployment to multiple clusters
   - Verify cluster-specific configurations

4. **Chaos Testing**
   - Test recovery from failures
   - Simulate network issues

## Conclusion

The CI/CD integration testing framework provides comprehensive coverage for the FortiGate Nextrade deployment pipeline. By following these patterns and best practices, you can ensure reliable and maintainable CI/CD operations.