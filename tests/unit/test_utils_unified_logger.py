#!/usr/bin/env python3
"""
Unit tests for Unified Logger Module
Tests for utils/unified_logger.py
"""

import pytest
from unittest.mock import Mock, patch, mock_open
import logging
import sys
import os
import tempfile
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from utils.unified_logger import (
    SensitiveDataMasker, 
    StructuredLogger, 
    get_logger,
    setup_security_logging,
    LogConfigManager
)


class TestSensitiveDataMasker:
    """Test cases for SensitiveDataMasker class"""
    
    def test_mask_api_key(self):
        """Test API key masking"""
        test_cases = [
            "api_key=abc123def456ghi789",
            "apikey: xyz789abc123def456",
            'api-key="token123456789012345"',
            "API_KEY=Bearer_token_123456789012345"
        ]
        
        for test_input in test_cases:
            result = SensitiveDataMasker.mask_sensitive_data(test_input)
            assert "***API_KEY_MASKED***" in result
            assert "abc123" not in result
            assert "xyz789" not in result
            assert "token123" not in result
    
    def test_mask_password(self):
        """Test password masking"""
        test_cases = [
            "password=secretpassword123",
            "passwd: myverysecretpassword",
            'pwd="password123456"',
            "PASSWORD=SuperSecret123!"
        ]
        
        for test_input in test_cases:
            result = SensitiveDataMasker.mask_sensitive_data(test_input)
            assert "***PASSWORD_MASKED***" in result
            assert "secret" not in result.lower()
    
    def test_mask_bearer_token(self):
        """Test Bearer token masking"""
        test_input = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        result = SensitiveDataMasker.mask_sensitive_data(test_input)
        assert "***BEARER_TOKEN_MASKED***" in result
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in result
    
    def test_mask_jwt_token(self):
        """Test JWT token masking"""
        jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        result = SensitiveDataMasker.mask_sensitive_data(jwt_token)
        assert "***JWT_TOKEN_MASKED***" in result
        assert jwt_token not in result
    
    def test_mask_credit_card(self):
        """Test credit card masking"""
        test_cases = [
            "4532123456789012",
            "4532 1234 5678 9012",
            "4532-1234-5678-9012"
        ]
        
        for test_input in test_cases:
            result = SensitiveDataMasker.mask_sensitive_data(test_input)
            assert "***CREDIT_CARD_MASKED***" in result
            assert "4532" not in result
    
    def test_mask_private_ip(self):
        """Test private IP masking"""
        test_cases = [
            "Server IP: 192.168.1.100",
            "Database at 10.0.0.50",
            "Internal: 172.16.254.1"
        ]
        
        for test_input in test_cases:
            result = SensitiveDataMasker.mask_sensitive_data(test_input)
            assert "***PRIVATE_IP_MASKED***" in result
    
    def test_mask_email(self):
        """Test email masking"""
        test_input = "Contact: admin@example.com for support"
        result = SensitiveDataMasker.mask_sensitive_data(test_input)
        assert "***EMAIL_MASKED***" in result
        assert "admin@example.com" not in result
    
    def test_mask_non_string_input(self):
        """Test masking with non-string input"""
        test_inputs = [
            123,
            {"api_key": "secret123"},
            ["password", "secret"]
        ]
        
        for test_input in test_inputs:
            result = SensitiveDataMasker.mask_sensitive_data(test_input)
            assert isinstance(result, str)
    
    def test_no_sensitive_data(self):
        """Test masking with no sensitive data"""
        test_input = "This is a normal log message with no sensitive information"
        result = SensitiveDataMasker.mask_sensitive_data(test_input)
        assert result == test_input


class TestStructuredLogger:
    """Test cases for StructuredLogger class"""
    
    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger for testing"""
        return Mock(spec=logging.Logger)
    
    def test_initialization(self, mock_logger):
        """Test StructuredLogger initialization"""
        structured_logger = StructuredLogger(mock_logger)
        assert structured_logger.logger == mock_logger
        assert structured_logger.context == {}
    
    def test_set_context(self, mock_logger):
        """Test setting logger context"""
        structured_logger = StructuredLogger(mock_logger)
        context = {"user_id": "123", "session_id": "abc"}
        
        structured_logger.set_context(context)
        assert structured_logger.context == context
    
    def test_update_context(self, mock_logger):
        """Test updating logger context"""
        structured_logger = StructuredLogger(mock_logger)
        structured_logger.context = {"user_id": "123"}
        
        structured_logger.update_context({"session_id": "abc", "request_id": "xyz"})
        expected = {"user_id": "123", "session_id": "abc", "request_id": "xyz"}
        assert structured_logger.context == expected
    
    def test_clear_context(self, mock_logger):
        """Test clearing logger context"""
        structured_logger = StructuredLogger(mock_logger)
        structured_logger.context = {"user_id": "123"}
        
        structured_logger.clear_context()
        assert structured_logger.context == {}
    
    @patch('utils.unified_logger.SensitiveDataMasker.mask_sensitive_data')
    def test_log_with_masking(self, mock_mask, mock_logger):
        """Test logging with sensitive data masking"""
        mock_mask.return_value = "masked message"
        structured_logger = StructuredLogger(mock_logger)
        
        structured_logger._log(logging.INFO, "test message", extra={"key": "value"})
        
        mock_mask.assert_called_once_with("test message")
        mock_logger.log.assert_called_once()
    
    def test_info_logging(self, mock_logger):
        """Test info level logging"""
        structured_logger = StructuredLogger(mock_logger)
        
        with patch.object(structured_logger, '_log') as mock_log:
            structured_logger.info("test message", extra={"key": "value"})
            mock_log.assert_called_once_with(logging.INFO, "test message", extra={"key": "value"})
    
    def test_error_logging(self, mock_logger):
        """Test error level logging"""
        structured_logger = StructuredLogger(mock_logger)
        
        with patch.object(structured_logger, '_log') as mock_log:
            structured_logger.error("error message")
            mock_log.assert_called_once_with(logging.ERROR, "error message", extra={})
    
    def test_warning_logging(self, mock_logger):
        """Test warning level logging"""
        structured_logger = StructuredLogger(mock_logger)
        
        with patch.object(structured_logger, '_log') as mock_log:
            structured_logger.warning("warning message")
            mock_log.assert_called_once_with(logging.WARNING, "warning message", extra={})
    
    def test_debug_logging(self, mock_logger):
        """Test debug level logging"""
        structured_logger = StructuredLogger(mock_logger)
        
        with patch.object(structured_logger, '_log') as mock_log:
            structured_logger.debug("debug message")
            mock_log.assert_called_once_with(logging.DEBUG, "debug message", extra={})


class TestLogConfigManager:
    """Test cases for LogConfigManager class"""
    
    def test_get_log_level_from_env(self):
        """Test getting log level from environment"""
        with patch.dict(os.environ, {'LOG_LEVEL': 'DEBUG'}):
            config_manager = LogConfigManager()
            assert config_manager.get_log_level() == logging.DEBUG
        
        with patch.dict(os.environ, {'LOG_LEVEL': 'INFO'}):
            config_manager = LogConfigManager()
            assert config_manager.get_log_level() == logging.INFO
        
        with patch.dict(os.environ, {'LOG_LEVEL': 'ERROR'}):
            config_manager = LogConfigManager()
            assert config_manager.get_log_level() == logging.ERROR
    
    def test_get_log_level_default(self):
        """Test default log level when no environment variable"""
        with patch.dict(os.environ, {}, clear=True):
            config_manager = LogConfigManager()
            assert config_manager.get_log_level() == logging.INFO
    
    def test_get_log_level_invalid(self):
        """Test invalid log level in environment"""
        with patch.dict(os.environ, {'LOG_LEVEL': 'INVALID'}):
            config_manager = LogConfigManager()
            assert config_manager.get_log_level() == logging.INFO
    
    def test_get_log_format(self):
        """Test getting log format"""
        config_manager = LogConfigManager()
        log_format = config_manager.get_log_format()
        
        assert isinstance(log_format, str)
        assert "%(asctime)s" in log_format
        assert "%(name)s" in log_format
        assert "%(levelname)s" in log_format
        assert "%(message)s" in log_format
    
    def test_get_log_file_path_default(self):
        """Test getting default log file path"""
        config_manager = LogConfigManager()
        log_path = config_manager.get_log_file_path()
        
        assert isinstance(log_path, Path)
        assert log_path.name == "fortigate_analyzer.log"
    
    def test_get_log_file_path_from_env(self):
        """Test getting log file path from environment"""
        test_path = "/tmp/custom.log"
        with patch.dict(os.environ, {'LOG_FILE': test_path}):
            config_manager = LogConfigManager()
            log_path = config_manager.get_log_file_path()
            
            assert str(log_path) == test_path
    
    def test_should_enable_console_logging(self):
        """Test console logging enablement"""
        with patch.dict(os.environ, {'CONSOLE_LOGGING': 'true'}):
            config_manager = LogConfigManager()
            assert config_manager.should_enable_console_logging() is True
        
        with patch.dict(os.environ, {'CONSOLE_LOGGING': 'false'}):
            config_manager = LogConfigManager()
            assert config_manager.should_enable_console_logging() is False
        
        with patch.dict(os.environ, {}, clear=True):
            config_manager = LogConfigManager()
            assert config_manager.should_enable_console_logging() is True
    
    def test_should_enable_file_logging(self):
        """Test file logging enablement"""
        with patch.dict(os.environ, {'FILE_LOGGING': 'true'}):
            config_manager = LogConfigManager()
            assert config_manager.should_enable_file_logging() is True
        
        with patch.dict(os.environ, {'FILE_LOGGING': 'false'}):
            config_manager = LogConfigManager()
            assert config_manager.should_enable_file_logging() is False
        
        with patch.dict(os.environ, {}, clear=True):
            config_manager = LogConfigManager()
            assert config_manager.should_enable_file_logging() is True


class TestGetLogger:
    """Test cases for get_logger function"""
    
    @patch('utils.unified_logger.LogConfigManager')
    @patch('logging.getLogger')
    def test_get_logger_basic(self, mock_get_logger, mock_config_manager):
        """Test basic logger creation"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_config_manager.return_value.get_log_level.return_value = logging.INFO
        
        logger = get_logger("test_module")
        
        assert isinstance(logger, StructuredLogger)
        mock_get_logger.assert_called_once_with("test_module")
    
    @patch('utils.unified_logger.LogConfigManager')
    @patch('logging.getLogger')
    def test_get_logger_with_custom_level(self, mock_get_logger, mock_config_manager):
        """Test logger creation with custom level"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_config_manager.return_value.get_log_level.return_value = logging.DEBUG
        
        logger = get_logger("test_module", level=logging.ERROR)
        
        mock_logger.setLevel.assert_called_with(logging.ERROR)
    
    @patch('utils.unified_logger.LogConfigManager')
    @patch('logging.getLogger')
    def test_get_logger_caching(self, mock_get_logger, mock_config_manager):
        """Test logger caching mechanism"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_config_manager.return_value.get_log_level.return_value = logging.INFO
        
        # Get logger twice with same name
        logger1 = get_logger("test_module")
        logger2 = get_logger("test_module")
        
        # Should use cached logger
        assert logger1 is logger2


class TestSetupSecurityLogging:
    """Test cases for setup_security_logging function"""
    
    @patch('utils.unified_logger.logging.getLogger')
    def test_setup_security_logging(self, mock_get_logger):
        """Test security logging setup"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        result = setup_security_logging()
        
        mock_get_logger.assert_called_once_with("security_audit")
        mock_logger.setLevel.assert_called_once_with(logging.WARNING)
        assert isinstance(result, StructuredLogger)
    
    @patch('utils.unified_logger.logging.getLogger')
    def test_setup_security_logging_with_file_handler(self, mock_get_logger):
        """Test security logging with file handler"""
        mock_logger = Mock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger
        
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "security.log"
            
            with patch('utils.unified_logger.LogConfigManager') as mock_config:
                mock_config.return_value.get_log_file_path.return_value = log_file.parent / "security.log"
                mock_config.return_value.should_enable_file_logging.return_value = True
                
                result = setup_security_logging()
                
                # Verify handler was added
                mock_logger.addHandler.assert_called()


@pytest.mark.integration
class TestUnifiedLoggerIntegration:
    """Integration tests for the unified logger system"""
    
    def test_end_to_end_logging(self):
        """Test complete logging workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            with patch.dict(os.environ, {
                'LOG_FILE': str(log_file),
                'LOG_LEVEL': 'DEBUG',
                'FILE_LOGGING': 'true',
                'CONSOLE_LOGGING': 'false'
            }):
                logger = get_logger("integration_test")
                
                # Test various log levels
                logger.info("Test info message")
                logger.error("Test error message")
                logger.warning("Test warning message")
                logger.debug("Test debug message")
                
                # Test with sensitive data
                logger.info("API key: abc123def456ghi789jkl012")
                
                # Verify log file was created and contains expected content
                if log_file.exists():
                    content = log_file.read_text()
                    assert "Test info message" in content
                    assert "Test error message" in content
                    assert "***API_KEY_MASKED***" in content
                    assert "abc123def456ghi789jkl012" not in content
    
    def test_context_logging(self):
        """Test contextual logging functionality"""
        logger = get_logger("context_test")
        
        # Set context
        logger.set_context({"user_id": "12345", "session_id": "abcdef"})
        
        # Update context
        logger.update_context({"action": "login"})
        
        # Log with context
        logger.info("User action performed")
        
        # Verify context is maintained
        assert logger.context["user_id"] == "12345"
        assert logger.context["session_id"] == "abcdef"
        assert logger.context["action"] == "login"
        
        # Clear context
        logger.clear_context()
        assert logger.context == {}
    
    def test_security_logging_workflow(self):
        """Test security logging workflow"""
        security_logger = setup_security_logging()
        
        # Test security events
        security_logger.warning("Unauthorized access attempt", extra={
            "ip_address": "192.168.1.100",
            "user_agent": "suspicious_bot"
        })
        
        security_logger.error("Authentication failure", extra={
            "username": "admin",
            "password": "wrongpassword123"
        })
        
        # Verify logger is properly configured
        assert isinstance(security_logger, StructuredLogger)
        assert security_logger.logger.name == "security_audit"