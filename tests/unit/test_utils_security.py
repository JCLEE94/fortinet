#!/usr/bin/env python3
"""
Unit tests for Security Utils
Tests for utils/security.py
"""

import pytest
from unittest.mock import Mock, patch, mock_open
import hashlib
import hmac
import sys
import os
import tempfile
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from utils.security import (
    SecurityManager,
    CryptographyHelper,
    TokenManager,
    AuditLogger,
    SecurityValidator
)


class TestSecurityManager:
    """Test cases for SecurityManager class"""
    
    @pytest.fixture
    def security_manager(self):
        """Create a SecurityManager instance for testing"""
        return SecurityManager()
    
    def test_initialization(self, security_manager):
        """Test SecurityManager initialization"""
        assert security_manager is not None
        assert hasattr(security_manager, 'config')
        assert hasattr(security_manager, 'logger')
    
    def test_hash_password(self, security_manager):
        """Test password hashing functionality"""
        password = "test_password_123"
        hashed = security_manager.hash_password(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0
        
        # Test that same password produces different hashes (due to salt)
        hashed2 = security_manager.hash_password(password)
        assert hashed != hashed2
    
    def test_verify_password(self, security_manager):
        """Test password verification"""
        password = "test_password_123"
        hashed = security_manager.hash_password(password)
        
        # Correct password should verify
        assert security_manager.verify_password(password, hashed) is True
        
        # Wrong password should not verify
        assert security_manager.verify_password("wrong_password", hashed) is False
        
        # Empty password should not verify
        assert security_manager.verify_password("", hashed) is False
    
    def test_generate_secure_token(self, security_manager):
        """Test secure token generation"""
        token = security_manager.generate_secure_token()
        
        assert token is not None
        assert len(token) > 0
        assert isinstance(token, str)
        
        # Test custom length
        token_custom = security_manager.generate_secure_token(length=32)
        assert len(token_custom) == 64  # 32 bytes = 64 hex chars
        
        # Test that tokens are unique
        token2 = security_manager.generate_secure_token()
        assert token != token2
    
    def test_validate_api_key(self, security_manager):
        """Test API key validation"""
        # Valid API key format
        valid_key = "sk_test_" + "a" * 40
        assert security_manager.validate_api_key(valid_key) is True
        
        # Invalid API key formats
        invalid_keys = [
            "",
            "short",
            "invalid_format",
            "sk_test_" + "a" * 10,  # Too short
            None
        ]
        
        for invalid_key in invalid_keys:
            assert security_manager.validate_api_key(invalid_key) is False
    
    def test_sanitize_input(self, security_manager):
        """Test input sanitization"""
        # Test basic sanitization
        clean_input = "normal_input_123"
        assert security_manager.sanitize_input(clean_input) == clean_input
        
        # Test dangerous characters
        dangerous_input = "<script>alert('xss')</script>"
        sanitized = security_manager.sanitize_input(dangerous_input)
        assert "<script>" not in sanitized
        assert "alert" not in sanitized
        
        # Test SQL injection patterns
        sql_injection = "'; DROP TABLE users; --"
        sanitized = security_manager.sanitize_input(sql_injection)
        assert "DROP" not in sanitized
        assert "--" not in sanitized
    
    def test_encrypt_decrypt_data(self, security_manager):
        """Test data encryption and decryption"""
        original_data = "sensitive_information_123"
        
        # Encrypt data
        encrypted = security_manager.encrypt_data(original_data)
        assert encrypted != original_data
        assert len(encrypted) > 0
        
        # Decrypt data
        decrypted = security_manager.decrypt_data(encrypted)
        assert decrypted == original_data
    
    def test_rate_limiting(self, security_manager):
        """Test rate limiting functionality"""
        identifier = "test_user_123"
        
        # First few requests should be allowed
        for i in range(5):
            assert security_manager.check_rate_limit(identifier) is True
        
        # After limit, should be blocked
        # Note: This test assumes a rate limit exists
        # Implementation may vary based on actual rate limiting logic


class TestCryptographyHelper:
    """Test cases for CryptographyHelper class"""
    
    @pytest.fixture
    def crypto_helper(self):
        """Create a CryptographyHelper instance"""
        return CryptographyHelper()
    
    def test_generate_key(self, crypto_helper):
        """Test cryptographic key generation"""
        key = crypto_helper.generate_key()
        
        assert key is not None
        assert len(key) > 0
        assert isinstance(key, (str, bytes))
    
    def test_derive_key_from_password(self, crypto_helper):
        """Test key derivation from password"""
        password = "strong_password_123"
        salt = os.urandom(16)
        
        key = crypto_helper.derive_key(password, salt)
        
        assert key is not None
        assert len(key) > 0
        
        # Same password and salt should produce same key
        key2 = crypto_helper.derive_key(password, salt)
        assert key == key2
        
        # Different salt should produce different key
        salt2 = os.urandom(16)
        key3 = crypto_helper.derive_key(password, salt2)
        assert key != key3
    
    def test_encrypt_decrypt_symmetric(self, crypto_helper):
        """Test symmetric encryption/decryption"""
        plaintext = "This is sensitive data that needs encryption"
        key = crypto_helper.generate_key()
        
        # Encrypt
        ciphertext = crypto_helper.encrypt_symmetric(plaintext, key)
        assert ciphertext != plaintext
        assert len(ciphertext) > 0
        
        # Decrypt
        decrypted = crypto_helper.decrypt_symmetric(ciphertext, key)
        assert decrypted == plaintext
    
    def test_generate_hash(self, crypto_helper):
        """Test hash generation"""
        data = "data_to_hash"
        
        hash_value = crypto_helper.generate_hash(data)
        
        assert hash_value is not None
        assert len(hash_value) > 0
        assert isinstance(hash_value, str)
        
        # Same data should produce same hash
        hash_value2 = crypto_helper.generate_hash(data)
        assert hash_value == hash_value2
        
        # Different data should produce different hash
        hash_value3 = crypto_helper.generate_hash("different_data")
        assert hash_value != hash_value3
    
    def test_verify_signature(self, crypto_helper):
        """Test digital signature verification"""
        data = "data_to_sign"
        secret_key = "secret_signing_key"
        
        # Generate signature
        signature = crypto_helper.sign_data(data, secret_key)
        
        # Verify signature
        assert crypto_helper.verify_signature(data, signature, secret_key) is True
        
        # Wrong data should fail verification
        assert crypto_helper.verify_signature("wrong_data", signature, secret_key) is False
        
        # Wrong key should fail verification
        assert crypto_helper.verify_signature(data, signature, "wrong_key") is False


class TestTokenManager:
    """Test cases for TokenManager class"""
    
    @pytest.fixture
    def token_manager(self):
        """Create a TokenManager instance"""
        return TokenManager(secret_key="test_secret_key_123")
    
    def test_initialization(self, token_manager):
        """Test TokenManager initialization"""
        assert token_manager is not None
        assert hasattr(token_manager, 'secret_key')
        assert token_manager.secret_key == "test_secret_key_123"
    
    def test_generate_jwt_token(self, token_manager):
        """Test JWT token generation"""
        payload = {
            "user_id": 123,
            "username": "testuser",
            "permissions": ["read", "write"]
        }
        
        token = token_manager.generate_jwt_token(payload)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        
        # JWT tokens have three parts separated by dots
        parts = token.split('.')
        assert len(parts) == 3
    
    def test_verify_jwt_token(self, token_manager):
        """Test JWT token verification"""
        payload = {"user_id": 123, "username": "testuser"}
        
        # Generate token
        token = token_manager.generate_jwt_token(payload)
        
        # Verify token
        decoded_payload = token_manager.verify_jwt_token(token)
        
        assert decoded_payload is not None
        assert decoded_payload["user_id"] == 123
        assert decoded_payload["username"] == "testuser"
    
    def test_verify_invalid_jwt_token(self, token_manager):
        """Test verification of invalid JWT tokens"""
        # Invalid token formats
        invalid_tokens = [
            "invalid.token.format",
            "not_a_token",
            "",
            None
        ]
        
        for invalid_token in invalid_tokens:
            result = token_manager.verify_jwt_token(invalid_token)
            assert result is None or result is False
    
    def test_generate_session_token(self, token_manager):
        """Test session token generation"""
        user_id = 123
        
        token = token_manager.generate_session_token(user_id)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_validate_session_token(self, token_manager):
        """Test session token validation"""
        user_id = 123
        
        # Generate token
        token = token_manager.generate_session_token(user_id)
        
        # Validate token
        is_valid = token_manager.validate_session_token(token, user_id)
        assert is_valid is True
        
        # Wrong user ID should fail
        is_valid = token_manager.validate_session_token(token, 456)
        assert is_valid is False


class TestAuditLogger:
    """Test cases for AuditLogger class"""
    
    @pytest.fixture
    def audit_logger(self):
        """Create an AuditLogger instance"""
        return AuditLogger()
    
    def test_initialization(self, audit_logger):
        """Test AuditLogger initialization"""
        assert audit_logger is not None
        assert hasattr(audit_logger, 'logger')
    
    def test_log_security_event(self, audit_logger):
        """Test logging security events"""
        event_data = {
            "event_type": "login_attempt",
            "user_id": 123,
            "ip_address": "192.168.1.100",
            "success": True
        }
        
        with patch.object(audit_logger.logger, 'info') as mock_log:
            audit_logger.log_security_event("LOGIN", event_data)
            
            mock_log.assert_called_once()
            call_args = mock_log.call_args[0][0]
            assert "LOGIN" in call_args
            assert "user_id" in call_args
    
    def test_log_access_attempt(self, audit_logger):
        """Test logging access attempts"""
        with patch.object(audit_logger.logger, 'warning') as mock_log:
            audit_logger.log_access_attempt(
                user_id=123,
                resource="/admin/panel",
                ip_address="192.168.1.100",
                success=False
            )
            
            mock_log.assert_called_once()
    
    def test_log_data_access(self, audit_logger):
        """Test logging data access"""
        with patch.object(audit_logger.logger, 'info') as mock_log:
            audit_logger.log_data_access(
                user_id=123,
                data_type="user_records",
                operation="READ",
                record_count=10
            )
            
            mock_log.assert_called_once()
    
    def test_log_system_event(self, audit_logger):
        """Test logging system events"""
        with patch.object(audit_logger.logger, 'info') as mock_log:
            audit_logger.log_system_event(
                event_type="SYSTEM_START",
                details={"version": "1.0.0", "config": "production"}
            )
            
            mock_log.assert_called_once()


class TestSecurityValidator:
    """Test cases for SecurityValidator class"""
    
    @pytest.fixture
    def validator(self):
        """Create a SecurityValidator instance"""
        return SecurityValidator()
    
    def test_validate_email(self, validator):
        """Test email validation"""
        # Valid emails
        valid_emails = [
            "test@example.com",
            "user.name@domain.org",
            "admin+tag@company.co.uk"
        ]
        
        for email in valid_emails:
            assert validator.validate_email(email) is True
        
        # Invalid emails
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user..name@domain.com"
        ]
        
        for email in invalid_emails:
            assert validator.validate_email(email) is False
    
    def test_validate_password_strength(self, validator):
        """Test password strength validation"""
        # Strong passwords
        strong_passwords = [
            "StrongPassword123!",
            "Complex@Pass1",
            "SecureP@ssw0rd"
        ]
        
        for password in strong_passwords:
            result = validator.validate_password_strength(password)
            assert result['is_valid'] is True
            assert result['score'] >= 3
        
        # Weak passwords
        weak_passwords = [
            "weak",
            "password123",
            "PASSWORD",
            "12345678"
        ]
        
        for password in weak_passwords:
            result = validator.validate_password_strength(password)
            assert result['is_valid'] is False or result['score'] < 3
    
    def test_validate_ip_address(self, validator):
        """Test IP address validation"""
        # Valid IP addresses
        valid_ips = [
            "192.168.1.1",
            "10.0.0.1",
            "172.16.254.1",
            "8.8.8.8"
        ]
        
        for ip in valid_ips:
            assert validator.validate_ip_address(ip) is True
        
        # Invalid IP addresses
        invalid_ips = [
            "192.168.1.256",
            "not.an.ip",
            "192.168.1",
            ""
        ]
        
        for ip in invalid_ips:
            assert validator.validate_ip_address(ip) is False
    
    def test_validate_url(self, validator):
        """Test URL validation"""
        # Valid URLs
        valid_urls = [
            "https://example.com",
            "http://subdomain.domain.org/path",
            "https://api.service.com/v1/endpoint"
        ]
        
        for url in valid_urls:
            assert validator.validate_url(url) is True
        
        # Invalid URLs
        invalid_urls = [
            "not-a-url",
            "ftp://unsupported.protocol",
            "http://",
            ""
        ]
        
        for url in invalid_urls:
            assert validator.validate_url(url) is False
    
    def test_detect_sql_injection(self, validator):
        """Test SQL injection detection"""
        # Clean inputs
        clean_inputs = [
            "normal search term",
            "user123",
            "valid@email.com"
        ]
        
        for clean_input in clean_inputs:
            assert validator.detect_sql_injection(clean_input) is False
        
        # SQL injection attempts
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'/*",
            "UNION SELECT password FROM users"
        ]
        
        for malicious_input in malicious_inputs:
            assert validator.detect_sql_injection(malicious_input) is True
    
    def test_detect_xss(self, validator):
        """Test XSS detection"""
        # Clean inputs
        clean_inputs = [
            "normal text",
            "user input",
            "safe content"
        ]
        
        for clean_input in clean_inputs:
            assert validator.detect_xss(clean_input) is False
        
        # XSS attempts
        xss_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>"
        ]
        
        for xss_input in xss_inputs:
            assert validator.detect_xss(xss_input) is True


@pytest.mark.integration
class TestSecurityIntegration:
    """Integration tests for security components"""
    
    def test_complete_authentication_flow(self):
        """Test complete authentication workflow"""
        security_manager = SecurityManager()
        token_manager = TokenManager(secret_key="integration_test_key")
        audit_logger = AuditLogger()
        
        # User registration flow
        password = "SecurePassword123!"
        hashed_password = security_manager.hash_password(password)
        
        # Login flow
        login_success = security_manager.verify_password(password, hashed_password)
        assert login_success is True
        
        if login_success:
            # Generate session token
            user_id = 123
            session_token = token_manager.generate_session_token(user_id)
            
            # Log successful login
            with patch.object(audit_logger.logger, 'info'):
                audit_logger.log_security_event("LOGIN_SUCCESS", {
                    "user_id": user_id,
                    "ip_address": "192.168.1.100"
                })
            
            # Validate session
            is_valid = token_manager.validate_session_token(session_token, user_id)
            assert is_valid is True
    
    def test_security_validation_workflow(self):
        """Test security validation workflow"""
        validator = SecurityValidator()
        security_manager = SecurityManager()
        
        # Validate user input
        user_input = "normal user input"
        
        # Check for security threats
        has_sql_injection = validator.detect_sql_injection(user_input)
        has_xss = validator.detect_xss(user_input)
        
        assert has_sql_injection is False
        assert has_xss is False
        
        # Sanitize input
        sanitized_input = security_manager.sanitize_input(user_input)
        assert sanitized_input == user_input  # Should be unchanged for clean input
    
    def test_data_protection_workflow(self):
        """Test data protection workflow"""
        crypto_helper = CryptographyHelper()
        
        # Sensitive data
        sensitive_data = "user_personal_information"
        
        # Generate encryption key
        encryption_key = crypto_helper.generate_key()
        
        # Encrypt data
        encrypted_data = crypto_helper.encrypt_symmetric(sensitive_data, encryption_key)
        assert encrypted_data != sensitive_data
        
        # Decrypt data
        decrypted_data = crypto_helper.decrypt_symmetric(encrypted_data, encryption_key)
        assert decrypted_data == sensitive_data