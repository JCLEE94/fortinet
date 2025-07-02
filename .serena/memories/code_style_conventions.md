# Code Style and Conventions for FortiGate Nextrade

## Python Code Style

### General Guidelines
- Python 3.11+ syntax and features
- UTF-8 encoding with `# -*- coding: utf-8 -*-` header
- Module-level docstrings for all Python files
- Follow PEP 8 with 120 character line limit

### Imports
```python
# Standard library imports
import os
import sys
from pathlib import Path

# Third-party imports  
from flask import Flask, jsonify
import requests

# Project imports (use absolute imports)
from src.utils.unified_logger import get_logger
from src.api.clients.base_api_client import BaseAPIClient
```

### Naming Conventions
- **Classes**: PascalCase (e.g., `FortiManagerAPIClient`)
- **Functions/Methods**: snake_case (e.g., `get_device_list()`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_TIMEOUT`)
- **Private methods**: Leading underscore (e.g., `_internal_method()`)
- **Module names**: snake_case (e.g., `api_client.py`)

### Type Hints
Always use type hints for function parameters and return values:
```python
from typing import Dict, List, Optional, Any

def process_data(data: Dict[str, Any], timeout: Optional[int] = None) -> List[str]:
    """Process data and return results."""
    pass
```

### Docstrings
Use Google-style docstrings:
```python
def analyze_packet_path(self, src_ip: str, dst_ip: str, port: int) -> Dict[str, Any]:
    """
    Analyze packet path through firewall.
    
    Args:
        src_ip: Source IP address
        dst_ip: Destination IP address  
        port: Destination port number
        
    Returns:
        Dictionary containing analysis results
        
    Raises:
        FortiManagerAPIException: If API call fails
    """
```

### Error Handling
```python
try:
    result = api_client.method()
except FortiManagerAPIException as e:
    logger.error(f"FortiManager error: {e}")
    return jsonify({"error": str(e)}), 500
```

### Logging Pattern
```python
from src.utils.unified_logger import get_logger

logger = get_logger(__name__)
logger.info("Operation started")
logger.error(f"Operation failed: {error}")
```

## Flask Blueprint Structure

### Blueprint Registration
```python
# In web_app.py
from src.routes.main_routes import main_bp
from src.routes.api_routes import api_bp

app.register_blueprint(main_bp)
app.register_blueprint(api_bp, url_prefix='/api')
```

### Route Definition
```python
# In routes file
from flask import Blueprint

api_bp = Blueprint('api', __name__)

@api_bp.route('/health')
def health_check():
    return jsonify({"status": "healthy"})
```

### Template URL Generation
Always use blueprint namespaces:
```jinja2
{{ url_for('main.dashboard') }}     <!-- Correct -->
{{ url_for('dashboard') }}          <!-- Wrong -->
```

## API Client Pattern

### Session Management (CRITICAL)
```python
class SomeAPIClient(BaseAPIClient):
    def __init__(self):
        super().__init__()  # MUST call parent init
        self.session = requests.Session()  # REQUIRED!
        self.session.verify = self.verify_ssl
```

## Configuration Management

### Priority Order
1. `data/config.json` (runtime configuration)
2. Environment variables
3. `src/config/unified_settings.py` (defaults)

### Environment Variables
- Use uppercase with underscores
- Prefix with service name (e.g., `FORTIMANAGER_HOST`)
- Always provide defaults

## Security Patterns

### Decorators
```python
@rate_limit(max_requests=30, window=60)
@csrf_protect
@admin_required
def protected_endpoint():
    pass
```

### Input Validation
Always validate and sanitize user input:
```python
if not isinstance(port, int) or port < 1 or port > 65535:
    raise ValueError("Invalid port number")
```

## Testing Conventions

### Test File Naming
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Test Structure
```python
import pytest
from unittest.mock import Mock, patch

class TestFortiManagerClient:
    def setup_method(self):
        """Setup before each test."""
        self.client = FortiManagerAPIClient()
        
    def test_successful_connection(self):
        """Test successful API connection."""
        # Arrange
        expected = {"status": "success"}
        
        # Act
        result = self.client.connect()
        
        # Assert
        assert result == expected
```

## Comments and Documentation

### When to Comment
- Complex algorithms or business logic
- Non-obvious code decisions
- TODO/FIXME items with ticket numbers
- API endpoint documentation

### Comment Style
```python
# Single line comment for simple explanations

"""
Multi-line comment for longer explanations
that need more detail or context.
"""

# TODO(JIRA-123): Implement rate limiting
# FIXME: Handle edge case when response is None
```

## File Organization

### Module Structure
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module description goes here.
"""

# Imports (grouped and sorted)
import os
import sys

from flask import Flask

from src.utils import logger

# Constants
DEFAULT_TIMEOUT = 30

# Classes
class MyClass:
    pass

# Functions
def main():
    pass

# Entry point
if __name__ == "__main__":
    main()
```