"""
File path configuration to replace hardcoded paths.
"""
import os
from pathlib import Path

# Base directory configuration
BASE_DIR = Path(os.getenv('APP_BASE_DIR', '/app'))
PROJECT_ROOT = Path(os.getenv('PROJECT_ROOT', os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

# Application paths
PATHS = {
    # Data paths
    'data_dir': BASE_DIR / 'data',
    'config': BASE_DIR / 'data' / 'config.json',
    'default_config': BASE_DIR / 'data' / 'default_config.json',
    'cache_dir': BASE_DIR / 'data' / 'cache',
    
    # Log paths
    'log_dir': BASE_DIR / 'logs',
    'app_log': BASE_DIR / 'logs' / 'app.log',
    'error_log': BASE_DIR / 'logs' / 'error.log',
    'access_log': BASE_DIR / 'logs' / 'access.log',
    'performance_log': BASE_DIR / 'logs' / 'performance.json',
    'security_log': BASE_DIR / 'logs' / 'security.log',
    
    # Source paths
    'src_dir': BASE_DIR / 'src',
    'static_dir': BASE_DIR / 'src' / 'static',
    'templates_dir': BASE_DIR / 'src' / 'templates',
    'modules_dir': BASE_DIR / 'src' / 'modules',
    
    # Service paths
    'service_dir': BASE_DIR / 'service',
    'fortigate_service': BASE_DIR / 'service' / 'fortigate',
    'fortigate_logs': BASE_DIR / 'service' / 'fortigate' / 'logs',
    
    # Temporary paths
    'temp_dir': Path(os.getenv('TEMP_DIR', '/tmp')),
    'upload_dir': Path(os.getenv('UPLOAD_DIR', '/tmp/uploads')),
    'download_dir': Path(os.getenv('DOWNLOAD_DIR', '/tmp/downloads')),
    
    # System paths
    'docker_socket': Path('/var/run/docker.sock'),
    'system_logs': {
        'auth': Path('/var/log/auth.log'),
        'syslog': Path('/var/log/syslog'),
    },
    
    # Development paths (should not be used in production)
    'dev_env': PROJECT_ROOT / '.env',
    'dev_config': PROJECT_ROOT / 'data' / 'config.json',
}

# Report paths
REPORT_PATHS = {
    'diagnostics': PATHS['log_dir'] / 'diagnostics',
    'monitoring': PATHS['temp_dir'] / 'monitoring_reports',
    'deployment': PATHS['temp_dir'] / 'deployment_reports',
    'api_test': PROJECT_ROOT / 'api_test_report.json',
}

def get_path(path_name: str, create_dirs: bool = False) -> Path:
    """
    Get a path by name, optionally creating parent directories.
    
    Args:
        path_name: Name of the path to retrieve
        create_dirs: Whether to create parent directories if they don't exist
        
    Returns:
        Path object
    """
    # Check main paths
    path = PATHS.get(path_name)
    
    # Check report paths if not found
    if path is None:
        path = REPORT_PATHS.get(path_name)
    
    # Check system logs
    if path is None and path_name in PATHS.get('system_logs', {}):
        path = PATHS['system_logs'][path_name]
    
    if path is None:
        raise ValueError(f"Unknown path: {path_name}")
    
    # Create parent directories if requested
    if create_dirs and not path.exists():
        if path.is_file() or '.' in path.name:
            path.parent.mkdir(parents=True, exist_ok=True)
        else:
            path.mkdir(parents=True, exist_ok=True)
    
    return path

def ensure_directory(path: Path) -> Path:
    """Ensure a directory exists, creating it if necessary."""
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_log_path(log_type: str) -> Path:
    """Get path for a specific log type."""
    log_paths = {
        'app': PATHS['app_log'],
        'error': PATHS['error_log'],
        'access': PATHS['access_log'],
        'performance': PATHS['performance_log'],
        'security': PATHS['security_log'],
    }
    
    path = log_paths.get(log_type)
    if path is None:
        # Default to creating a new log file in log directory
        path = PATHS['log_dir'] / f"{log_type}.log"
    
    # Ensure log directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

# Environment-specific path overrides
if os.getenv('ENVIRONMENT') == 'development':
    # Use local paths in development
    PATHS['config'] = PROJECT_ROOT / 'data' / 'config.json'
    PATHS['log_dir'] = PROJECT_ROOT / 'logs'
    PATHS['data_dir'] = PROJECT_ROOT / 'data'