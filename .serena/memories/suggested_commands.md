# Suggested Commands for FortiGate Nextrade Development

## Running the Application

### Local Development
```bash
# Run Flask development server
cd src && python main.py --web

# Run with specific environment
APP_MODE=test python src/main.py --web        # Mock mode (no hardware needed)
APP_MODE=production python src/main.py --web   # Production mode
```

### Docker Development
```bash
# Build Docker image
docker build -f Dockerfile.production -t fortigate-nextrade:latest .

# Run container
docker run -d --name fortigate-nextrade \
  -p 7777:7777 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e APP_MODE=test \
  fortigate-nextrade:latest

# View logs
docker logs -f fortigate-nextrade

# Stop container
docker stop fortigate-nextrade && docker rm fortigate-nextrade
```

## Testing Commands

```bash
# Run all tests with coverage
pytest tests/ --cov=src --cov-report=html -v

# Run specific test file
pytest tests/test_api_clients.py -v

# Run specific test class
pytest tests/test_api_clients.py::TestBaseApiClient -v

# Run specific test method
pytest tests/test_api_clients.py::TestBaseApiClient::test_offline_mode_detection -v

# Run tests with specific markers
pytest -m "unit" -v         # Unit tests only
pytest -m "integration" -v  # Integration tests only
pytest -m "not slow" -v     # Skip slow tests
```

## Code Quality Commands

```bash
# Format code (auto-fix)
black src/

# Sort imports (auto-fix)
isort src/

# Lint code
flake8 src/ --max-line-length=120

# Type checking
mypy src/ --ignore-missing-imports

# Run all quality checks
black src/ && isort src/ && flake8 src/ --max-line-length=120 && mypy src/ --ignore-missing-imports
```

## Git Commands

```bash
# Check status
git status

# Add all changes
git add -A

# Commit with conventional message
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug"
git commit -m "docs: update documentation"
git commit -m "test: add unit tests"
git commit -m "refactor: improve code structure"

# Push to trigger CI/CD
git push origin master
```

## GitHub Actions Monitoring

```bash
# List recent workflow runs
gh run list --limit 5 --repo JCLEE94/fortinet

# Watch workflow progress
gh run watch --repo JCLEE94/fortinet

# View specific run details
gh run view <run-id> --repo JCLEE94/fortinet
```

## API Testing

```bash
# Health check
curl http://localhost:7777/api/health

# Test packet analysis (with mock data)
curl -X POST http://localhost:7777/api/fortimanager/analyze-packet-path \
  -H "Content-Type: application/json" \
  -d '{"src_ip": "192.168.1.100", "dst_ip": "172.16.10.100", "port": 80, "protocol": "tcp"}'
```

## Docker Registry Commands

```bash
# Login to private registry
docker login registry.jclee.me

# Tag image for registry
docker tag fortigate-nextrade:latest registry.jclee.me/fortinet:latest

# Push to registry
docker push registry.jclee.me/fortinet:latest

# Pull from registry
docker pull registry.jclee.me/fortinet:latest
```

## System Utilities (Linux)

```bash
# Find process using port 7777
sudo lsof -ti:7777

# Kill process on port
sudo lsof -ti:7777 | xargs kill -9

# Check disk usage
df -h

# Check memory usage
free -h

# Monitor system resources
htop

# View application logs
tail -f logs/web_app.log

# Search in files
grep -r "search_term" src/
rg "search_term" src/  # Using ripgrep (faster)
```