"""
Numeric limits and thresholds to replace magic numbers.
"""
import os

# Display limits
DISPLAY_LIMITS = {
    'top_items': int(os.getenv('DISPLAY_TOP_ITEMS', '10')),
    'max_table_rows': int(os.getenv('MAX_TABLE_ROWS', '100')),
    'preview_length': int(os.getenv('PREVIEW_LENGTH', '200')),
    'truncate_length': int(os.getenv('TRUNCATE_LENGTH', '50')),
    'max_log_entries': int(os.getenv('MAX_LOG_ENTRIES', '1000')),
    'pagination_size': int(os.getenv('PAGINATION_SIZE', '20')),
    'max_search_results': int(os.getenv('MAX_SEARCH_RESULTS', '500')),
}

# Timeout limits (in seconds)
TIMEOUT_LIMITS = {
    'default': int(os.getenv('DEFAULT_TIMEOUT', '30')),
    'api_request': int(os.getenv('API_REQUEST_TIMEOUT', '60')),
    'health_check': int(os.getenv('HEALTH_CHECK_TIMEOUT', '5')),
    'internet_check': int(os.getenv('INTERNET_CHECK_TIMEOUT', '5')),
    'long_operation': int(os.getenv('LONG_OPERATION_TIMEOUT', '300')),
    'session': int(os.getenv('SESSION_TIMEOUT', '3600')),
    'cache_ttl': int(os.getenv('CACHE_TTL', '300')),
}

# Size limits
SIZE_LIMITS = {
    'max_file_size': int(os.getenv('MAX_FILE_SIZE', '104857600')),  # 100MB
    'max_upload_size': int(os.getenv('MAX_UPLOAD_SIZE', '52428800')),  # 50MB
    'max_payload_size': int(os.getenv('MAX_PAYLOAD_SIZE', '10485760')),  # 10MB
    'max_log_file_size': int(os.getenv('MAX_LOG_FILE_SIZE', '1073741824')),  # 1GB
    'buffer_size': int(os.getenv('BUFFER_SIZE', '8192')),  # 8KB
    'chunk_size': int(os.getenv('CHUNK_SIZE', '4096')),  # 4KB
}

# Hash and cryptography limits
CRYPTO_LIMITS = {
    'hash_truncate_length': int(os.getenv('HASH_TRUNCATE_LENGTH', '16')),
    'token_length': int(os.getenv('TOKEN_LENGTH', '32')),
    'session_id_length': int(os.getenv('SESSION_ID_LENGTH', '8')),
    'password_min_length': int(os.getenv('PASSWORD_MIN_LENGTH', '8')),
    'salt_length': int(os.getenv('SALT_LENGTH', '16')),
}

# Performance limits
PERFORMANCE_LIMITS = {
    'max_concurrent_connections': int(os.getenv('MAX_CONCURRENT_CONNECTIONS', '1000')),
    'max_queue_size': int(os.getenv('MAX_QUEUE_SIZE', '10000')),
    'batch_size': int(os.getenv('BATCH_SIZE', '100')),
    'worker_threads': int(os.getenv('WORKER_THREADS', '4')),
    'connection_pool_size': int(os.getenv('CONNECTION_POOL_SIZE', '10')),
}

# Monitoring and metrics limits
MONITORING_LIMITS = {
    'metrics_retention_days': int(os.getenv('METRICS_RETENTION_DAYS', '30')),
    'alert_threshold_cpu': float(os.getenv('ALERT_THRESHOLD_CPU', '80.0')),
    'alert_threshold_memory': float(os.getenv('ALERT_THRESHOLD_MEMORY', '85.0')),
    'alert_threshold_disk': float(os.getenv('ALERT_THRESHOLD_DISK', '90.0')),
    'max_metrics_per_request': int(os.getenv('MAX_METRICS_PER_REQUEST', '1000')),
}

# Business hours (for ITSM integration)
BUSINESS_HOURS = {
    'start': os.getenv('BUSINESS_HOURS_START', '09:00'),
    'end': os.getenv('BUSINESS_HOURS_END', '18:00'),
    'timezone': os.getenv('BUSINESS_TIMEZONE', 'Asia/Seoul'),
}

# Retry limits
RETRY_LIMITS = {
    'max_retries': int(os.getenv('MAX_RETRIES', '3')),
    'retry_delay': int(os.getenv('RETRY_DELAY', '1')),
    'retry_backoff_factor': float(os.getenv('RETRY_BACKOFF_FACTOR', '2.0')),
    'max_retry_delay': int(os.getenv('MAX_RETRY_DELAY', '60')),
}

# Array slicing limits
SLICE_LIMITS = {
    'recent_items': int(os.getenv('RECENT_ITEMS_LIMIT', '5')),
    'summary_items': int(os.getenv('SUMMARY_ITEMS_LIMIT', '10')),
    'detail_items': int(os.getenv('DETAIL_ITEMS_LIMIT', '20')),
    'max_array_display': int(os.getenv('MAX_ARRAY_DISPLAY', '100')),
}

def get_limit(category: str, limit_name: str, default=None):
    """Get a limit value by category and name."""
    limits_map = {
        'display': DISPLAY_LIMITS,
        'timeout': TIMEOUT_LIMITS,
        'size': SIZE_LIMITS,
        'crypto': CRYPTO_LIMITS,
        'performance': PERFORMANCE_LIMITS,
        'monitoring': MONITORING_LIMITS,
        'retry': RETRY_LIMITS,
        'slice': SLICE_LIMITS,
    }
    
    if category in limits_map:
        return limits_map[category].get(limit_name, default)
    
    raise ValueError(f"Unknown limit category: {category}")