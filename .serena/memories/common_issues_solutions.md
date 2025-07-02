# Common Issues and Solutions for FortiGate Nextrade

## Port 7777 Already in Use

### Linux/Mac
```bash
# Find process using port
sudo lsof -ti:7777

# Kill process
sudo lsof -ti:7777 | xargs kill -9

# Check Docker containers
docker ps --filter "publish=7777" -q | xargs docker stop
docker ps -a --filter "publish=7777" -q | xargs docker rm
```

### Windows PowerShell
```powershell
# Find and kill process
Get-Process -Id (Get-NetTCPConnection -LocalPort 7777).OwningProcess | Stop-Process -Force
```

## Flask Development Server Warning
- The app uses Flask dev server in production (known issue)
- This is tracked for resolution but doesn't affect functionality
- Gunicorn configuration issue is being investigated

## Redis Connection Failed
- This is a WARNING, not an error
- System automatically falls back to memory cache
- Redis is optional for the application

## Docker Build Failures

### BuildKit Issues
```bash
# Disable BuildKit if errors occur
export DOCKER_BUILDKIT=0
docker build -f Dockerfile.production -t fortigate-nextrade:latest .
```

### Permission Issues
```bash
# Fix Docker socket permissions
sudo chmod 666 /var/run/docker.sock

# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect
```

## API Connection Issues

### FortiManager Connection Failed
1. Check environment variables:
   ```bash
   echo $FORTIMANAGER_HOST
   echo $FORTIMANAGER_API_KEY
   ```

2. Test with mock mode:
   ```bash
   APP_MODE=test python src/main.py --web
   ```

3. Check logs for auth method:
   ```bash
   tail -f logs/web_app.log | grep "auth"
   ```

### Session Initialization Error
- Ensure all API clients call `super().__init__()` 
- Check that `self.session = requests.Session()` is present
- Verify `verify_ssl` setting in config

## Template Routing Errors (404)

### Common Cause
Using wrong URL generation in templates:
```jinja2
<!-- WRONG - causes 404 -->
{{ url_for('dashboard') }}

<!-- CORRECT - uses blueprint namespace -->
{{ url_for('main.dashboard') }}
```

### Fix All Templates
```bash
# Find all incorrect url_for usage
grep -r "url_for('[^.]*')" src/templates/

# Common replacements needed:
# 'dashboard' → 'main.dashboard'
# 'settings' → 'api.settings'
# 'logs' → 'logs.logs_management'
```

## Import Errors

### Module Not Found
```bash
# Ensure you're in the right directory
cd /path/to/fortinet

# Set PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Or run from src directory
cd src && python main.py --web
```

### Circular Import
- Check for imports at module level that create cycles
- Move imports inside functions if needed
- Use lazy imports for circular dependencies

## Test Failures

### Coverage Too Low
```bash
# Check current coverage
pytest --cov=src --cov-report=term-missing

# Focus on untested modules
pytest --cov=src.api.clients --cov-report=html
```

### Mock Mode Not Working
```bash
# Ensure APP_MODE is set correctly
export APP_MODE=test
python src/main.py --web

# Check in code
import os
print(f"APP_MODE: {os.getenv('APP_MODE')}")
```

## Deployment Issues

### GitHub Actions Failing
```bash
# Check workflow status
gh run list --limit 5 --repo JCLEE94/fortinet

# View logs
gh run view <run-id> --repo JCLEE94/fortinet --log

# Re-run failed job
gh run rerun <run-id> --repo JCLEE94/fortinet
```

### Watchtower Not Updating
1. Check webhook token:
   ```bash
   curl -X POST https://watchtower.jclee.me/v1/update \
     -H "Authorization: Bearer MySuperSecretToken12345"
   ```

2. Verify image in registry:
   ```bash
   docker pull registry.jclee.me/fortinet:latest
   ```

3. Manual update:
   ```bash
   docker stop fortinet && docker rm fortinet
   docker pull registry.jclee.me/fortinet:latest
   docker run -d --name fortinet [options] registry.jclee.me/fortinet:latest
   ```

## Performance Issues

### High Memory Usage
```bash
# Check memory usage
docker stats fortinet

# Limit container memory
docker run -d --memory="1g" --memory-swap="2g" fortinet
```

### Slow API Responses
1. Enable Redis cache:
   ```bash
   docker run -d --name redis redis:alpine
   export REDIS_URL=redis://localhost:6379
   ```

2. Check API timeouts in config
3. Use mock mode for development

## Logging Issues

### Logs Not Appearing
```bash
# Check log file permissions
ls -la logs/

# Create logs directory if missing
mkdir -p logs
chmod 755 logs

# Check Flask logging level
export FLASK_LOG_LEVEL=DEBUG
```

### Log Rotation
```bash
# Manual rotation
mv logs/web_app.log logs/web_app.log.$(date +%Y%m%d)
touch logs/web_app.log

# Setup logrotate (Linux)
sudo tee /etc/logrotate.d/fortinet << EOF
/path/to/fortinet/logs/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
EOF
```