"""
API Helper utilities to reduce code duplication
"""
from typing import Optional, Tuple
from src.config.unified_settings import unified_settings
from src.api.integration.api_integration import APIIntegrationManager
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

def get_data_source() -> Tuple[APIIntegrationManager, None, bool]:
    """
    Get appropriate data source - 항상 운영 모드
    
    Returns:
        Tuple of (api_manager, dummy_generator, is_test)
        - Always returns: (api_manager, None, False)
    """
    return get_api_manager(), None, False