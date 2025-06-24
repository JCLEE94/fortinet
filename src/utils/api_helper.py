"""
API Helper utilities to reduce code duplication
"""
from typing import Optional, Tuple
from src.config.unified_settings import unified_settings
from src.api.integration.api_integration import APIIntegrationManager
from src.mock.data_generator import DummyDataGenerator
import os

def get_api_manager() -> APIIntegrationManager:
    """
    Get initialized API manager instance
    
    Returns:
        APIIntegrationManager instance
    """
    # 통합 설정에서 데이터 구성
    settings_data = {
        'fortimanager': unified_settings.get_service_config('fortimanager'),
        'fortigate': unified_settings.get_service_config('fortigate'),
        'fortianalyzer': unified_settings.get_service_config('fortianalyzer'),
        'app_mode': unified_settings.app_mode
    }
    api_manager = APIIntegrationManager(settings_data)
    api_manager.initialize_connections()
    return api_manager

def get_dummy_generator() -> DummyDataGenerator:
    """
    Get dummy data generator instance
    
    Returns:
        DummyDataGenerator instance
    """
    return DummyDataGenerator()

def is_test_mode() -> bool:
    """
    Check if application is in test mode
    
    Returns:
        True if in test mode, False otherwise
    """
    return unified_settings.is_test_mode()

def get_data_source() -> Tuple[Optional[APIIntegrationManager], DummyDataGenerator, bool]:
    """
    Get appropriate data source based on mode
    
    Returns:
        Tuple of (api_manager, dummy_generator, is_test)
        - In test mode: (None, dummy_generator, True)
        - In production mode: (api_manager, dummy_generator, False)
        Note: dummy_generator is always available for fallback
    """
    dummy_generator = get_dummy_generator()
    if is_test_mode():
        return None, dummy_generator, True
    else:
        return get_api_manager(), dummy_generator, False