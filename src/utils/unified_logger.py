#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Logger Module for FortiGate Analyzer
Provides a consistent, configurable logging interface with multiple logging strategies
"""

import atexit
import json
import logging
import logging.handlers
import os
import sys
import traceback
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from config.constants import FILE_LIMITS


# Logger strategies
class LoggerStrategy:
    """Base class for logger strategies"""

    def __init__(self, name: str, log_dir: str = None):
        self.name = name
        self.log_dir = self._get_log_dir(log_dir)
        os.makedirs(self.log_dir, exist_ok=True)

    def _get_log_dir(self, log_dir: str = None) -> str:
        """Determine log directory based on environment"""
        if log_dir:
            return log_dir
        elif os.path.exists("/app/fortigate/logs"):
            return "/app/fortigate/logs"
        else:
            return os.path.join(os.getcwd(), "logs")

    def setup(self, logger: logging.Logger) -> None:
        """Setup the logger with appropriate handlers"""
        raise NotImplementedError("Subclasses must implement setup method")


class BasicLoggerStrategy(LoggerStrategy):
    """Basic logging strategy with console and file output"""

    def setup(self, logger: logging.Logger) -> None:
        """Setup basic logger with console and file handlers"""
        # Clear existing handlers to prevent duplicates
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Create formatters
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File handler with rotation
        log_file = os.path.join(self.log_dir, f"{self.name}.log")
        try:
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=FILE_LIMITS["LOG_MAX_SIZE"],
                backupCount=FILE_LIMITS["LOG_BACKUP_COUNT"],
                encoding="utf-8",
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

            # Fix permissions if needed
            if os.path.exists(log_file):
                os.chmod(log_file, 0o666)

        except Exception as e:
            # If file logging fails, log to console
            logger.warning(
                f"Log file setup failed (console logging still active): {str(e)}"
            )


class AdvancedLoggerStrategy(LoggerStrategy):
    """Advanced logging strategy with structured logs and troubleshooting features"""

    def setup(self, logger: logging.Logger) -> None:
        """Setup advanced logger with structured logging and troubleshooting support"""
        # Clear existing handlers to prevent duplicates
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Create formatters
        standard_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        json_formatter = StructuredFormatter()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(standard_formatter)
        logger.addHandler(console_handler)

        # Standard log file with rotation
        log_file = os.path.join(self.log_dir, f"{self.name}.log")
        try:
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=FILE_LIMITS["LOG_MAX_SIZE"],
                backupCount=FILE_LIMITS["LOG_BACKUP_COUNT"],
                encoding="utf-8",
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(standard_formatter)
            logger.addHandler(file_handler)

            # JSON structured log file
            json_log_file = os.path.join(self.log_dir, f"{self.name}_structured.json")
            json_handler = logging.handlers.RotatingFileHandler(
                json_log_file,
                maxBytes=10 * 1024 * 1024,
                backupCount=5,
                encoding="utf-8",
            )
            json_handler.setLevel(logging.DEBUG)
            json_handler.setFormatter(json_formatter)
            logger.addHandler(json_handler)

            # Error-only log file
            error_log_file = os.path.join(self.log_dir, f"{self.name}_errors.log")
            error_handler = logging.handlers.RotatingFileHandler(
                error_log_file,
                maxBytes=FILE_LIMITS["ERROR_LOG_MAX_SIZE"],
                backupCount=FILE_LIMITS["LOG_BACKUP_COUNT"],
                encoding="utf-8",
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(standard_formatter)
            logger.addHandler(error_handler)

            # Troubleshooting log - shared across all loggers
            troubleshoot_file = os.path.join(self.log_dir, "troubleshooting.log")
            troubleshoot_handler = logging.handlers.RotatingFileHandler(
                troubleshoot_file,
                maxBytes=20 * 1024 * 1024,
                backupCount=2,
                encoding="utf-8",
            )
            troubleshoot_handler.setLevel(logging.INFO)
            troubleshoot_handler.setFormatter(json_formatter)
            logger.addHandler(troubleshoot_handler)

            # Fix permissions if needed
            for file_path in [
                log_file,
                json_log_file,
                error_log_file,
                troubleshoot_file,
            ]:
                if os.path.exists(file_path):
                    os.chmod(file_path, 0o666)

        except Exception as e:
            # If file logging fails, log to console
            logger.warning(
                f"Advanced log file setup failed (console logging still active): {str(e)}"
            )


class StructuredFormatter(logging.Formatter):
    """Formatter for structured JSON logs"""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as a JSON string"""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if available
        if record.exc_info and record.exc_info[0] is not None:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]) if record.exc_info[1] else "",
                "traceback": traceback.format_exception(*record.exc_info),
            }
        elif record.exc_info:
            # Handle case where exc_info is provided but empty
            log_data["exception"] = {"type": "None", "message": "", "traceback": ""}

        # Add context information if available
        for attr in [
            "context",
            "fortimanager",
            "fortigate",
            "api_request",
            "api_response",
        ]:
            if hasattr(record, attr):
                log_data[attr] = getattr(record, attr)

        return json.dumps(log_data, ensure_ascii=False, default=str)


# Singleton registry to manage logger instances
class LoggerRegistry:
    """Singleton registry for managing logger instances"""

    _instance = None
    _loggers = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerRegistry, cls).__new__(cls)
            # Register cleanup on exit
            atexit.register(cls._instance.cleanup)
        return cls._instance

    def get_logger(
        self,
        name: str,
        strategy: str = "basic",
        log_dir: str = None,
        log_level: str = None,
    ) -> "UnifiedLogger":
        """Get or create a logger instance"""
        if name not in self._loggers:
            self._loggers[name] = UnifiedLogger(name, strategy, log_dir, log_level)
        return self._loggers[name]

    def cleanup(self):
        """Clean up resources on exit"""
        for logger in self._loggers.values():
            # Flush any pending logs
            for handler in logger.logger.handlers:
                handler.flush()


# Main logger class
class UnifiedLogger:
    """Unified logger with support for multiple logging strategies"""

    def __init__(
        self,
        name: str,
        strategy: str = "basic",
        log_dir: str = None,
        log_level: str = None,
    ):
        """
        Initialize a new logger instance

        Args:
            name (str): Logger name
            strategy (str): Logging strategy ('basic' or 'advanced')
            log_dir (str, optional): Directory to store log files
            log_level (str, optional): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.name = name

        # Setup Python logger
        self.logger = logging.getLogger(name)

        # Set log level
        if log_level is None:
            log_level = os.environ.get("LOG_LEVEL", "DEBUG")
        level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger.setLevel(level)

        # Apply strategy
        self._setup_strategy(strategy, log_dir)

        # Bind standard logging methods
        self.debug = self.logger.debug
        self.info = self.logger.info
        self.warning = self.logger.warning
        self.error = self.logger.error
        self.critical = self.logger.critical

    def _setup_strategy(self, strategy: str, log_dir: str = None):
        """Setup the logger with the specified strategy"""
        if strategy.lower() == "advanced":
            self.strategy = AdvancedLoggerStrategy(self.name, log_dir)
        else:
            self.strategy = BasicLoggerStrategy(self.name, log_dir)

        self.strategy.setup(self.logger)

    def log_with_context(
        self, level: int, msg: str, context: Dict[str, Any] = None, **kwargs
    ):
        """Log a message with additional context"""
        extra = kwargs.get("extra", {})
        if context:
            extra["context"] = context
        self.logger.log(level, msg, extra=extra, **kwargs)

    # Specialized logging methods for API clients
    def log_api_request(
        self, method: str, url: str, data: Any = None, headers: Dict = None
    ):
        """Log an API request"""
        extra = {
            "api_request": {
                "method": method,
                "url": url,
                "data": data,
                "headers": self._sanitize_headers(headers),
            }
        }
        self.logger.info(f"API Request: {method} {url}", extra=extra)

    def log_api_response(
        self, status_code: int, response_data: Any = None, error: Any = None
    ):
        """Log an API response"""
        extra = {
            "api_response": {
                "status_code": status_code,
                "data": response_data,
                "error": str(error) if error else None,
            }
        }

        if error or (status_code >= 400):
            self.logger.error(f"API Response Error: {status_code}", extra=extra)
        else:
            self.logger.info(f"API Response: {status_code}", extra=extra)

    def log_fortigate_connection(
        self,
        host: str,
        status: str,
        error: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Log FortiGate connection status"""
        extra = {
            "fortigate": {
                "host": host,
                "status": status,
                "error": error,
                "context": context,
            }
        }

        if status == "connected":
            self.logger.info(f"FortiGate connected: {host}", extra=extra)
        else:
            self.logger.error(
                f"FortiGate connection failed: {host} - {error}", extra=extra
            )

    def log_fortimanager_connection(
        self,
        host: str,
        status: str,
        error: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Log FortiManager connection status"""
        extra = {
            "fortimanager": {
                "host": host,
                "status": status,
                "error": error,
                "context": context,
            }
        }

        if status == "connected":
            self.logger.info(f"FortiManager connected: {host}", extra=extra)
        else:
            self.logger.error(
                f"FortiManager connection failed: {host} - {error}", extra=extra
            )

    def log_troubleshooting(
        self, issue: str, context: Dict[str, Any], resolution: Optional[str] = None
    ):
        """Log troubleshooting information"""
        extra = {
            "context": {"issue": issue, "details": context, "resolution": resolution}
        }
        self.logger.info(f"Troubleshooting: {issue}", extra=extra)

    def log_environment_check(self):
        """Log environment information"""
        env_info = {
            "python_version": sys.version,
            "platform": sys.platform,
            "cwd": os.getcwd(),
            "env_vars": {
                "DOCKER": os.environ.get("DOCKER", "false"),
                "TZ": os.environ.get("TZ", "UTC"),
                "LANG": os.environ.get("LANG", "en_US.UTF-8"),
            },
            "paths": {
                "app": os.path.exists("/app"),
                "data": os.path.exists("/app/data"),
                "logs": os.path.exists("/app/logs"),
            },
        }

        extra = {"context": env_info}
        self.logger.info("Environment check completed", extra=extra)

    def collect_logs_for_support(self, output_dir: str = None) -> str:
        """Collect logs for support"""
        if output_dir is None:
            output_dir = os.path.join(self.strategy.log_dir, "support")

        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        support_file = os.path.join(output_dir, f"support_logs_{timestamp}.tar.gz")

        try:
            # Get log files
            log_files = []
            for handler in self.logger.handlers:
                if hasattr(handler, "baseFilename"):
                    log_files.append(handler.baseFilename)

            # Add all logs from the directory
            log_dir = self.strategy.log_dir
            for filename in os.listdir(log_dir):
                if filename.endswith(".log") or filename.endswith(".json"):
                    filepath = os.path.join(log_dir, filename)
                    if filepath not in log_files:
                        log_files.append(filepath)

            # Compress log files
            import tarfile

            with tarfile.open(support_file, "w:gz") as tar:
                for log_file in log_files:
                    if os.path.exists(log_file):
                        tar.add(log_file, arcname=os.path.basename(log_file))

            self.logger.info(f"Support logs collected: {support_file}")
            return support_file
        except Exception as e:
            self.logger.error(f"Failed to collect support logs: {str(e)}")
            return None

    def _sanitize_headers(self, headers: Dict) -> Dict:
        """Sanitize headers to remove sensitive information"""
        if not headers:
            return {}

        sanitized = headers.copy()
        sensitive_keys = ["Authorization", "api-key", "token", "password", "secret"]

        for key in sanitized:
            for sensitive_key in sensitive_keys:
                if sensitive_key.lower() in key.lower():
                    sanitized[key] = "********"

        return sanitized


# Global functions for backward compatibility
def get_logger(
    name: str, strategy: str = "basic", log_dir: str = None, log_level: str = None
) -> UnifiedLogger:
    """Get a logger instance (compatible with existing code)"""
    return LoggerRegistry().get_logger(name, strategy, log_dir, log_level)


def setup_logger(name: str, log_level: str = None) -> UnifiedLogger:
    """Setup a logger (compatible with existing code)"""
    return get_logger(name, "basic", None, log_level)


def get_advanced_logger(
    name: str, log_dir: str = None, log_level: str = None
) -> UnifiedLogger:
    """Get an advanced logger (compatible with existing code)"""
    return get_logger(name, "advanced", log_dir, log_level)


# Pre-configure a global troubleshooting logger for direct import
troubleshooting_logger = get_logger("nextrade.fortigate", "advanced")
