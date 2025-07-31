# Secure Testing Guide for FortiManager Tests

This guide explains how to securely run FortiManager tests without exposing sensitive credentials in the code.

## Environment Variables Required

Set the following environment variables before running tests:

### Basic Test Configuration
```bash
export FORTIMANAGER_TEST_HOST="your.fortimanager.host"
export FORTIMANAGER_TEST_PORT="443"
export FORTIMANAGER_TEST_USERNAME="your_username"
export FORTIMANAGER_TEST_PASSWORD="your_password"
export FORTIMANAGER_TEST_API_KEY="your_api_key"
export FORTIMANAGER_TEST_TOKEN="your_token"
```

### Demo Environment Configuration
```bash
export FORTIMANAGER_DEMO_HOST="demo.fortimanager.host"
export FORTIMANAGER_DEMO_PORT="14005"
export FORTIMANAGER_DEMO_TOKEN="demo_api_token"
export FORTIMANAGER_VERIFY_SSL="false"  # For demo/test environments only
```

### New API Key Testing
```bash
export FORTIMANAGER_NEW_API_KEY="new_api_key_to_test"
```

## Running Tests Securely

### Option 1: Using Environment File (Recommended)
Create a `.env.test` file (add to .gitignore):
```bash
# .env.test
FORTIMANAGER_TEST_HOST=your.fortimanager.host
FORTIMANAGER_TEST_PORT=443
FORTIMANAGER_TEST_USERNAME=your_username
FORTIMANAGER_TEST_API_KEY=your_api_key
```

Then source it before running tests:
```bash
source .env.test
python test_fortimanager_demo.py
```

### Option 2: Inline Environment Variables
```bash
FORTIMANAGER_TEST_HOST=demo.host FORTIMANAGER_TEST_API_KEY=key python test_fortimanager_demo.py
```

### Option 3: Using pytest with Environment
```bash
# Run all manual tests with environment
FORTIMANAGER_TEST_HOST=demo.host pytest tests/manual/ -v
```

## Security Best Practices

1. **Never commit credentials**: Always use environment variables or secure vaults
2. **Use .gitignore**: Add any `.env*` files to .gitignore
3. **Mock data for CI/CD**: Use placeholder values for automated testing
4. **Rotate credentials regularly**: Change test credentials periodically
5. **Use read-only accounts**: For testing, use accounts with minimal permissions

## Mock Values for Testing

When environment variables are not set, tests will use safe mock values:
- Host: `test.fortimanager.local` or `mock.fortimanager.test`
- Port: `443`
- Username: `test_user`
- Password: `test_pass_mock`
- API Key: `test_api_key_placeholder`
- Token: `mock_api_token_for_testing`

## Example Test Execution

```bash
# Set up test environment
export FORTIMANAGER_TEST_HOST="demo.fortinet.com"
export FORTIMANAGER_TEST_PORT="14005"
export FORTIMANAGER_TEST_API_KEY="your_actual_key"
export FORTIMANAGER_TEST_USERNAME="testuser"

# Run specific test
cd tests/manual
python test_fortimanager_demo.py

# Run all manual tests
python -m pytest . -v
```

## Troubleshooting

### Missing Environment Variables
If you see "NOT SET" or placeholder values in test output, ensure environment variables are properly set:
```bash
echo $FORTIMANAGER_TEST_HOST  # Should show your host
```

### SSL Certificate Errors
For test environments with self-signed certificates:
```bash
export FORTIMANAGER_VERIFY_SSL="false"
```

### Permission Errors
Ensure your test account has appropriate permissions:
- Read access to system status
- Access to ADOM and device information
- Permission to query firewall policies

## CI/CD Integration

For GitHub Actions or other CI/CD systems, use secrets:
```yaml
env:
  FORTIMANAGER_TEST_HOST: ${{ secrets.FORTIMANAGER_HOST }}
  FORTIMANAGER_TEST_API_KEY: ${{ secrets.FORTIMANAGER_KEY }}
```

## Important Notes

- All hardcoded credentials have been removed from test files
- Tests will use mock/placeholder values when environment variables are not set
- This ensures tests can run safely in any environment without exposing secrets
- For production testing, always use proper credential management systems