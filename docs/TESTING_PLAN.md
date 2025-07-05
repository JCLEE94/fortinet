# FortiGate Nextrade Testing Plan

## Overview

This document outlines the comprehensive testing strategy for the FortiGate Nextrade project, including unit tests, integration tests, CI/CD tests, and end-to-end testing.

## Testing Philosophy

1. **Test-Driven Development (TDD)**: Write tests before implementation
2. **Inline Testing**: Following Rust patterns, modules include their own tests
3. **Mock-First**: External dependencies are mocked for fast, reliable tests
4. **Comprehensive Coverage**: Aim for 80%+ code coverage

## Test Categories

### 1. Unit Tests (`tests/unit/`)

**Purpose**: Test individual functions and methods in isolation

**Current Coverage**:
- ✅ API Clients (FortiGate, FortiManager, FortiAnalyzer)
- ✅ Utility functions (logging, caching, security)
- ✅ Mock system components
- ⚠️ Business logic modules (partial coverage)

**Running Unit Tests**:
```bash
pytest tests/unit/ -v
pytest tests/unit/test_api_clients.py -v  # Specific file
```

### 2. Integration Tests (`tests/integration/`)

**Purpose**: Test interactions between components

**Current Coverage**:
- ✅ CI/CD Pipeline Integration (NEW)
  - Pipeline triggers
  - Docker registry operations
  - GitOps workflow
  - ArgoCD deployment
  - Health checks
- ✅ API Integration
- ✅ Database/Cache Integration
- ⚠️ FortiManager Advanced Hub (partial)

**Running Integration Tests**:
```bash
pytest tests/integration/ -v
pytest tests/integration/test_pipeline_triggers.py -v  # CI/CD tests
```

### 3. End-to-End Tests (`tests/e2e/`)

**Purpose**: Test complete user workflows

**Planned Coverage**:
- ❌ User authentication flow
- ❌ Firewall policy analysis workflow
- ❌ Network topology visualization
- ❌ ITSM ticket creation

### 4. Performance Tests (`tests/performance/`)

**Purpose**: Ensure system meets performance requirements

**Planned Coverage**:
- ❌ API response times
- ❌ Concurrent user handling
- ❌ Large dataset processing
- ❌ Real-time monitoring load

## CI/CD Testing Architecture (NEW)

### Testable Modules

Located in `src/cicd/`, each module includes inline tests:

1. **PipelineCoordinator**
   - Tests: 16 inline test methods
   - Coverage: Deployment decisions, image tagging, metadata

2. **ArgoCDClient**
   - Tests: 14 inline test methods
   - Coverage: Authentication, sync, monitoring

3. **GitOpsManager**
   - Tests: 13 inline test methods
   - Coverage: Git operations, kustomization updates

4. **DockerRegistryClient**
   - Tests: 12 inline test methods
   - Coverage: Build, push, registry operations

### Running Inline Tests

```bash
# Run module's inline tests directly
python src/cicd/pipeline_coordinator.py -v
python src/cicd/argocd_client.py -v
python src/cicd/gitops_manager.py -v
python src/cicd/docker_registry.py -v
```

## Test Execution Strategy

### Local Development

```bash
# Quick test during development
pytest tests/unit/test_current_module.py -v

# Pre-commit tests
pytest tests/unit/ tests/integration/ -v --tb=short

# Full test suite with coverage
pytest --cov=src --cov-report=html --cov-report=term-missing
```

### CI/CD Pipeline

```yaml
# GitHub Actions workflow
test:
  steps:
    - name: Unit Tests
      run: pytest tests/unit/ -v --junit-xml=unit-results.xml
      
    - name: Integration Tests
      run: pytest tests/integration/ -v --junit-xml=integration-results.xml
      
    - name: Coverage Report
      run: pytest --cov=src --cov-report=xml
```

## Test Data Management

### Mock Data
- Location: `src/mock/mock_data.py`
- Usage: Activated with `APP_MODE=test`
- Purpose: Realistic test data without hardware dependencies

### Fixtures
- Location: `tests/fixtures/`
- Key fixtures:
  - `cicd_fixtures.py` - CI/CD test data
  - Common contexts and mock objects

## Coverage Goals

### Current Status
- Overall Coverage: ~65%
- CI/CD Modules: ~85%
- API Clients: ~75%
- Core Business Logic: ~50%

### Target Coverage
- Overall: 80%+
- Critical Paths: 90%+
- New Code: 100%

## Testing Best Practices

### 1. Test Naming
```python
def test_should_deploy_main_branch():
    """Test that main branch triggers deployment"""
    # Clear, descriptive test names
```

### 2. Arrange-Act-Assert
```python
def test_example():
    # Arrange
    client = create_test_client()
    
    # Act
    result = client.perform_action()
    
    # Assert
    assert result.status == "success"
```

### 3. Mock External Dependencies
```python
@patch('subprocess.run')
def test_with_mock(mock_run):
    mock_run.return_value = MagicMock(returncode=0)
    # Test without actual subprocess calls
```

### 4. Parameterized Tests
```python
@pytest.mark.parametrize("branch,event,expected", [
    ("main", "push", True),
    ("feature", "push", False),
    ("main", "pull_request", False),
])
def test_deployment_scenarios(branch, event, expected):
    assert should_deploy(branch, event) == expected
```

## Test Maintenance

### Regular Tasks
1. **Weekly**: Review and update failing tests
2. **Sprint**: Add tests for new features
3. **Monthly**: Coverage analysis and improvement
4. **Quarterly**: Performance test review

### Test Documentation
- Document complex test scenarios
- Update test plan with new patterns
- Share testing knowledge in team meetings

## Troubleshooting Tests

### Common Issues

1. **Import Errors**
   ```bash
   export PYTHONPATH=$PYTHONPATH:$(pwd)
   ```

2. **Mock Failures**
   - Ensure mock return values match expected types
   - Use `side_effect` for multiple calls

3. **Flaky Tests**
   - Add proper wait/retry logic
   - Mock time-dependent operations

4. **Coverage Gaps**
   ```bash
   # Find uncovered lines
   pytest --cov=src --cov-report=term-missing
   ```

## Future Testing Enhancements

### Phase 1 (Current)
- ✅ CI/CD integration tests
- ✅ Inline testing pattern
- ✅ Comprehensive fixtures

### Phase 2 (Next Sprint)
- ❌ E2E test framework setup
- ❌ Performance test baseline
- ❌ Security testing suite

### Phase 3 (Future)
- ❌ Chaos engineering tests
- ❌ Load testing automation
- ❌ Visual regression testing

## Conclusion

The testing strategy ensures code quality, reliability, and maintainability. With the addition of CI/CD integration tests, the project now has comprehensive coverage of deployment operations, significantly reducing the risk of production issues.