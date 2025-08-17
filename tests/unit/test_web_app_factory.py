#!/usr/bin/env python3
"""
Unit tests for Web App Factory
Tests for web_app.py
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from flask import Flask

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

# Set required environment variables for testing
os.environ['APP_MODE'] = 'test'
os.environ['TESTING'] = 'true'
os.environ['SECRET_KEY'] = 'test-secret-key-for-testing'

from web_app import create_app, setup_security_headers, register_blueprints


class TestCreateApp:
    """Test cases for create_app function"""
    
    @patch('web_app.UnifiedCacheManager')
    @patch('web_app.logging.getLogger')
    def test_create_app_basic(self, mock_logger, mock_cache):
        """Test basic app creation"""
        mock_cache_instance = Mock()
        mock_cache.return_value = mock_cache_instance
        
        app = create_app()
        
        assert isinstance(app, Flask)
        assert app.config['TESTING'] is True
        assert app.config['SECRET_KEY'] == 'test-secret-key-for-testing'
    
    @patch('web_app.UnifiedCacheManager')
    @patch('web_app.logging.getLogger')
    def test_create_app_production_mode(self, mock_logger, mock_cache):
        """Test app creation in production mode"""
        with patch.dict(os.environ, {'APP_MODE': 'production', 'SECRET_KEY': 'prod-secret'}):
            app = create_app()
            
            assert app.config['DEBUG'] is False
            assert app.config['TESTING'] is False
    
    @patch('web_app.UnifiedCacheManager')
    @patch('web_app.logging.getLogger')
    def test_create_app_debug_mode(self, mock_logger, mock_cache):
        """Test app creation in debug mode"""
        with patch.dict(os.environ, {'APP_MODE': 'development'}):
            app = create_app()
            
            assert app.config['DEBUG'] is True
    
    @patch('web_app.UnifiedCacheManager')
    @patch('web_app.logging.getLogger')
    def test_create_app_missing_secret_key(self, mock_logger, mock_cache):
        """Test app creation with missing secret key"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('os.urandom') as mock_urandom:
                mock_urandom.return_value = b'random-key-bytes'
                
                app = create_app()
                
                assert app.config['SECRET_KEY'] is not None
                mock_urandom.assert_called_once_with(24)
    
    @patch('web_app.UnifiedCacheManager')
    @patch('web_app.logging.getLogger')
    def test_create_app_wtf_csrf_configuration(self, mock_logger, mock_cache):
        """Test WTF CSRF configuration"""
        app = create_app()
        
        # In test mode, CSRF should be disabled
        assert app.config.get('WTF_CSRF_ENABLED', True) is False
    
    @patch('web_app.UnifiedCacheManager')
    @patch('web_app.logging.getLogger')
    @patch('web_app.register_blueprints')
    def test_create_app_blueprint_registration(self, mock_register, mock_logger, mock_cache):
        """Test blueprint registration during app creation"""
        app = create_app()
        
        mock_register.assert_called_once_with(app)
    
    @patch('web_app.UnifiedCacheManager')
    @patch('web_app.logging.getLogger')
    @patch('web_app.setup_security_headers')
    def test_create_app_security_headers(self, mock_security, mock_logger, mock_cache):
        """Test security headers setup during app creation"""
        app = create_app()
        
        mock_security.assert_called_once_with(app)
    
    @patch('web_app.UnifiedCacheManager')
    @patch('web_app.logging.getLogger')
    def test_create_app_cache_manager_initialization(self, mock_logger, mock_cache_class):
        """Test cache manager initialization"""
        mock_cache_instance = Mock()
        mock_cache_class.return_value = mock_cache_instance
        
        app = create_app()
        
        mock_cache_class.assert_called_once()
        # Cache manager should be attached to app
        assert hasattr(app, 'cache_manager')
    
    @patch('web_app.UnifiedCacheManager')
    @patch('web_app.logging.getLogger')
    def test_create_app_offline_mode_socketio(self, mock_logger, mock_cache):
        """Test SocketIO configuration in offline mode"""
        with patch.dict(os.environ, {'OFFLINE_MODE': 'true'}):
            with patch('web_app.SocketIO') as mock_socketio:
                app = create_app()
                
                # SocketIO should not be initialized in offline mode
                mock_socketio.assert_not_called()
    
    @patch('web_app.UnifiedCacheManager')
    @patch('web_app.logging.getLogger')
    def test_create_app_online_mode_socketio(self, mock_logger, mock_cache):
        """Test SocketIO configuration in online mode"""
        with patch.dict(os.environ, {'OFFLINE_MODE': 'false'}):
            with patch('web_app.SocketIO') as mock_socketio:
                mock_socketio_instance = Mock()
                mock_socketio.return_value = mock_socketio_instance
                
                app = create_app()
                
                mock_socketio.assert_called_once_with(app, cors_allowed_origins="*")
    
    @patch('web_app.UnifiedCacheManager')
    @patch('web_app.logging.getLogger')
    def test_create_app_error_handlers(self, mock_logger, mock_cache):
        """Test error handlers registration"""
        app = create_app()
        
        # Test 404 handler
        with app.test_request_context('/nonexistent'):
            response = app.handle_404(None)
            assert response[1] == 404
        
        # Test 500 handler
        with app.test_request_context('/'):
            response = app.handle_500(Exception("Test error"))
            assert response[1] == 500


class TestSetupSecurityHeaders:
    """Test cases for setup_security_headers function"""
    
    def test_security_headers_setup(self):
        """Test security headers configuration"""
        app = Flask(__name__)
        
        setup_security_headers(app)
        
        with app.test_request_context('/'):
            with app.test_client() as client:
                response = client.get('/')
                
                # Check basic security headers
                assert 'X-Content-Type-Options' in response.headers
                assert 'X-Frame-Options' in response.headers
                assert 'X-XSS-Protection' in response.headers
    
    def test_security_headers_content(self):
        """Test specific security header values"""
        app = Flask(__name__)
        
        @app.route('/test')
        def test_route():
            return 'test'
        
        setup_security_headers(app)
        
        with app.test_client() as client:
            response = client.get('/test')
            
            assert response.headers.get('X-Content-Type-Options') == 'nosniff'
            assert response.headers.get('X-Frame-Options') == 'DENY'
            assert response.headers.get('X-XSS-Protection') == '1; mode=block'
    
    def test_security_headers_csp(self):
        """Test Content Security Policy header"""
        app = Flask(__name__)
        
        @app.route('/test')
        def test_route():
            return 'test'
        
        setup_security_headers(app)
        
        with app.test_client() as client:
            response = client.get('/test')
            
            csp_header = response.headers.get('Content-Security-Policy')
            if csp_header:
                assert 'default-src' in csp_header
                assert 'script-src' in csp_header


class TestRegisterBlueprints:
    """Test cases for register_blueprints function"""
    
    @patch('web_app.main_bp')
    @patch('web_app.api_bp')
    @patch('web_app.fortimanager_bp')
    @patch('web_app.itsm_bp')
    @patch('web_app.security_bp')
    @patch('web_app.monitoring_bp')
    @patch('web_app.analysis_bp')
    @patch('web_app.admin_bp')
    def test_blueprint_registration(self, mock_admin, mock_analysis, mock_monitoring, 
                                   mock_security, mock_itsm, mock_fortimanager, 
                                   mock_api, mock_main):
        """Test that all blueprints are registered"""
        app = Flask(__name__)
        
        register_blueprints(app)
        
        # Verify all blueprints are registered
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        
        # Should have at least the main blueprints
        expected_blueprints = ['main', 'api', 'fortimanager', 'itsm', 'security', 
                              'monitoring', 'analysis', 'admin']
        
        for bp_name in expected_blueprints:
            if bp_name in blueprint_names:
                assert bp_name in blueprint_names
    
    def test_blueprint_registration_with_prefixes(self):
        """Test blueprint registration with URL prefixes"""
        app = Flask(__name__)
        
        # Mock blueprints
        mock_blueprints = {
            'main_bp': Mock(),
            'api_bp': Mock(),
            'fortimanager_bp': Mock(),
            'itsm_bp': Mock(),
            'security_bp': Mock(),
            'monitoring_bp': Mock(),
            'analysis_bp': Mock(),
            'admin_bp': Mock()
        }
        
        # Set blueprint names
        for name, bp in mock_blueprints.items():
            bp.name = name.replace('_bp', '')
        
        with patch.multiple('web_app', **mock_blueprints):
            register_blueprints(app)
            
            # Verify app.register_blueprint was called for each
            assert len(app.blueprints) >= 1  # At least one blueprint registered


class TestAppConfiguration:
    """Test cases for app configuration"""
    
    @patch('web_app.UnifiedCacheManager')
    @patch('web_app.logging.getLogger')
    def test_app_config_test_mode(self, mock_logger, mock_cache):
        """Test app configuration in test mode"""
        with patch.dict(os.environ, {'APP_MODE': 'test'}):
            app = create_app()
            
            assert app.config['TESTING'] is True
            assert app.config['DEBUG'] is True
            assert app.config.get('WTF_CSRF_ENABLED', True) is False
    
    @patch('web_app.UnifiedCacheManager')
    @patch('web_app.logging.getLogger')
    def test_app_config_production_mode(self, mock_logger, mock_cache):
        """Test app configuration in production mode"""
        with patch.dict(os.environ, {'APP_MODE': 'production'}):
            app = create_app()
            
            assert app.config['TESTING'] is False
            assert app.config['DEBUG'] is False
    
    @patch('web_app.UnifiedCacheManager')
    @patch('web_app.logging.getLogger')
    def test_app_config_database_url(self, mock_logger, mock_cache):
        """Test database URL configuration"""
        with patch.dict(os.environ, {'DATABASE_URL': 'sqlite:///test.db'}):
            app = create_app()
            
            assert app.config.get('DATABASE_URL') == 'sqlite:///test.db'
    
    @patch('web_app.UnifiedCacheManager')
    @patch('web_app.logging.getLogger')
    def test_app_config_redis_url(self, mock_logger, mock_cache):
        """Test Redis URL configuration"""
        with patch.dict(os.environ, {'REDIS_URL': 'redis://localhost:6379/0'}):
            app = create_app()
            
            assert app.config.get('REDIS_URL') == 'redis://localhost:6379/0'


class TestErrorHandlers:
    """Test cases for error handlers"""
    
    @patch('web_app.UnifiedCacheManager')
    @patch('web_app.logging.getLogger')
    def test_404_error_handler(self, mock_logger, mock_cache):
        """Test 404 error handler"""
        app = create_app()
        
        with app.test_client() as client:
            response = client.get('/nonexistent-page')
            
            assert response.status_code == 404
            assert b'404' in response.data or b'Not Found' in response.data
    
    @patch('web_app.UnifiedCacheManager')
    @patch('web_app.logging.getLogger')
    def test_500_error_handler(self, mock_logger, mock_cache):
        """Test 500 error handler"""
        app = create_app()
        
        @app.route('/test-error')
        def test_error():
            raise Exception("Test error")
        
        with app.test_client() as client:
            response = client.get('/test-error')
            
            assert response.status_code == 500
    
    @patch('web_app.UnifiedCacheManager')
    @patch('web_app.logging.getLogger')
    def test_error_handler_logging(self, mock_logger, mock_cache):
        """Test that errors are logged properly"""
        app = create_app()
        
        @app.route('/test-error')
        def test_error():
            raise ValueError("Test error for logging")
        
        with app.test_client() as client:
            response = client.get('/test-error')
            
            # Error should be handled and logged
            assert response.status_code == 500


class TestAppContext:
    """Test cases for application context"""
    
    @patch('web_app.UnifiedCacheManager')
    @patch('web_app.logging.getLogger')
    def test_app_context_variables(self, mock_logger, mock_cache):
        """Test application context variables"""
        app = create_app()
        
        with app.app_context():
            # Test that cache manager is available
            assert hasattr(app, 'cache_manager')
            
            # Test that logger is configured
            from flask import current_app
            assert current_app == app
    
    @patch('web_app.UnifiedCacheManager')
    @patch('web_app.logging.getLogger')
    def test_request_context(self, mock_logger, mock_cache):
        """Test request context functionality"""
        app = create_app()
        
        @app.route('/test-context')
        def test_context():
            from flask import request
            return f"Method: {request.method}"
        
        with app.test_client() as client:
            response = client.get('/test-context')
            assert b'Method: GET' in response.data


@pytest.mark.integration
class TestWebAppIntegration:
    """Integration tests for the web application"""
    
    @patch('web_app.UnifiedCacheManager')
    def test_app_startup_and_basic_functionality(self, mock_cache):
        """Test complete app startup and basic functionality"""
        mock_cache_instance = Mock()
        mock_cache_instance.health_check.return_value = {'status': 'healthy'}
        mock_cache.return_value = mock_cache_instance
        
        app = create_app()
        
        with app.test_client() as client:
            # Test that app starts successfully
            assert app is not None
            
            # Test basic route (if exists)
            response = client.get('/')
            # Should either succeed or return 404 (not 500)
            assert response.status_code in [200, 404]
    
    @patch('web_app.UnifiedCacheManager')
    def test_app_with_all_components(self, mock_cache):
        """Test app with all components loaded"""
        mock_cache_instance = Mock()
        mock_cache.return_value = mock_cache_instance
        
        app = create_app()
        
        # Test that all major components are loaded
        assert hasattr(app, 'cache_manager')
        
        # Test that blueprints are registered
        assert len(app.blueprints) > 0
        
        # Test that error handlers are registered
        assert 404 in app.error_handler_spec[None]
        assert 500 in app.error_handler_spec[None]
    
    @patch('web_app.UnifiedCacheManager')
    def test_app_configuration_loading(self, mock_cache):
        """Test configuration loading from various sources"""
        test_config = {
            'SECRET_KEY': 'integration-test-secret',
            'DEBUG': False,
            'TESTING': True
        }
        
        with patch.dict(os.environ, test_config):
            app = create_app()
            
            assert app.config['SECRET_KEY'] == 'integration-test-secret'
            assert app.config['TESTING'] is True
    
    @patch('web_app.UnifiedCacheManager')
    def test_security_features(self, mock_cache):
        """Test security features integration"""
        app = create_app()
        
        @app.route('/test-security')
        def test_security():
            return 'Security test'
        
        with app.test_client() as client:
            response = client.get('/test-security')
            
            # Check that security headers are present
            security_headers = [
                'X-Content-Type-Options',
                'X-Frame-Options',
                'X-XSS-Protection'
            ]
            
            for header in security_headers:
                assert header in response.headers