# Task Completion Checklist for FortiGate Nextrade

## When You Complete a Coding Task

### 1. Run Tests (MANDATORY)
```bash
# Always run tests after code changes
pytest tests/ -v

# If specific area was changed, run related tests
pytest tests/test_api_clients.py -v  # For API client changes
pytest tests/test_routes.py -v       # For route changes

# Ensure all tests pass before considering task complete
```

### 2. Code Quality Checks
```bash
# Format code
black src/

# Sort imports  
isort src/

# Lint code
flake8 src/ --max-line-length=120

# Type checking
mypy src/ --ignore-missing-imports

# Run all checks in sequence
black src/ && isort src/ && flake8 src/ --max-line-length=120 && mypy src/ --ignore-missing-imports
```

### 3. Verify No Hardcoded Values
- Check for hardcoded URLs, paths, passwords, API keys
- All configurable values should be in:
  - Environment variables (highest priority)
  - `data/config.json` (runtime config)
  - `src/config/unified_settings.py` (defaults only)

### 4. Update Documentation
- Update docstrings for new/modified functions
- Update README.md if adding new features
- Update API documentation if changing endpoints

### 5. Test in Different Modes
```bash
# Test in mock mode (no hardware required)
APP_MODE=test python src/main.py --web

# Test in production mode
APP_MODE=production python src/main.py --web
```

### 6. Check Blueprint Namespacing
- Ensure all template URLs use blueprint namespaces
- Example: `{{ url_for('api.health') }}` not `{{ url_for('health') }}`

### 7. Verify Session Management
- All API clients must initialize requests.Session()
- Always call `super().__init__()` in API client constructors

### 8. Security Review
- No hardcoded secrets or credentials
- Input validation on all user inputs
- Proper error handling without exposing internals
- CSRF protection on state-changing endpoints

### 9. Commit with Conventional Messages
```bash
# Examples of good commit messages
git commit -m "feat: add packet path analysis endpoint"
git commit -m "fix: resolve session timeout in FortiManager client"
git commit -m "test: add unit tests for firewall analyzer"
git commit -m "refactor: extract common API logic to base client"
git commit -m "docs: update API documentation for new endpoints"
```

### 10. Final Verification
Before pushing:
1. ✅ All tests pass
2. ✅ Code is formatted and linted
3. ✅ No hardcoded values
4. ✅ Documentation updated if needed
5. ✅ Works in both test and production modes
6. ✅ Security considerations addressed
7. ✅ Commit message follows conventions

### Push to Trigger CI/CD
```bash
git push origin master  # or main
```

The GitHub Actions pipeline will:
1. Run tests and coverage
2. Perform security scans
3. Build Docker image
4. Push to registry.jclee.me
5. Auto-deploy via Watchtower

Monitor deployment:
```bash
gh run list --limit 5 --repo JCLEE94/fortinet
```