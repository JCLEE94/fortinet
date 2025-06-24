#!/usr/bin/env python3
"""
커버리지 향상을 위한 기본 모듈 테스트
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestCoverageBoost(unittest.TestCase):
    """커버리지 향상을 위한 기본 테스트"""
    
    def test_import_api_common(self):
        """API 공통 모듈 임포트 테스트"""
        from src.utils.api_common import (
            ConnectionTestMixin, JsonRpcMixin, MonitoringMixin,
            ErrorHandlingMixin, RequestRetryMixin, CacheMixin,
            sanitize_sensitive_data, format_api_response
        )
        
        # 기본 함수 테스트
        data = {"password": "secret123", "normal": "data"}
        sanitized = sanitize_sensitive_data(data)
        self.assertEqual(sanitized["password"], "********")
        self.assertEqual(sanitized["normal"], "data")
        
        # API 응답 포맷 테스트
        response = format_api_response(True, {"result": "success"}, 200)
        self.assertTrue(response["success"])
        self.assertEqual(response["status_code"], 200)
        
    def test_import_api_clients(self):
        """API 클라이언트 임포트 테스트"""
        from src.api.clients.base_api_client import BaseApiClient, RealtimeMonitoringMixin
        from src.api.clients.fortigate_api_client import FortiGateAPIClient
        from src.api.clients.fortimanager_api_client import FortiManagerAPIClient
        from src.api.clients.faz_client import FAZClient
        
        # 오프라인 모드 테스트를 위한 환경 설정
        os.environ['OFFLINE_MODE'] = 'true'
        
        # 클라이언트 생성 테스트 (오프라인 모드)
        fortigate_client = FortiGateAPIClient(host="localhost")
        self.assertIsNotNone(fortigate_client)
        self.assertTrue(hasattr(fortigate_client, 'OFFLINE_MODE'))
        
        fortimanager_client = FortiManagerAPIClient(host="localhost")
        self.assertIsNotNone(fortimanager_client)
        
        faz_client = FAZClient(host="localhost")
        self.assertIsNotNone(faz_client)
        
    def test_import_monitoring(self):
        """모니터링 모듈 임포트 테스트"""
        from src.monitoring.base import MonitoringBase, ThresholdMixin, HealthCheckMixin
        from src.monitoring.config import get_config, MonitoringConfig
        from src.monitoring.manager import UnifiedMonitoringManager
        from src.monitoring.collectors.system_metrics import SystemMetricsCollector
        
        # 설정 테스트
        config = get_config()
        self.assertIsInstance(config, MonitoringConfig)
        
        # 모니터링 관리자 테스트
        manager = UnifiedMonitoringManager()
        self.assertIsNotNone(manager)
        
    def test_import_utils(self):
        """유틸리티 모듈 임포트 테스트"""
        from src.utils.unified_logger import get_logger
        from src.utils.api_optimization import CacheManager
        from src.utils.batch_operations import BatchProcessor
        from src.utils.route_helpers import standard_api_response, handle_api_exceptions
        
        # 로거 테스트
        logger = get_logger("test")
        self.assertIsNotNone(logger)
        
        # 캐시 매니저 테스트
        cache_manager = CacheManager()
        self.assertIsNotNone(cache_manager)
        
        # 배치 프로세서 테스트
        batch_processor = BatchProcessor()
        self.assertIsNotNone(batch_processor)
        
    def test_import_core(self):
        """코어 모듈 임포트 테스트"""
        from src.core.config_manager import ConfigManager
        from src.core.connection_pool import ConnectionPoolManager
        from src.core.cache_manager import CacheManager as CoreCacheManager
        
        # 설정 관리자 테스트
        config_manager = ConfigManager()
        self.assertIsNotNone(config_manager)
        
        # 연결 풀 매니저 테스트
        pool_manager = ConnectionPoolManager()
        self.assertIsNotNone(pool_manager)
        
    def test_import_mock(self):
        """Mock 모듈 임포트 테스트"""
        from src.mock.data_generator import DummyDataGenerator
        from src.mock.fortigate import MockFortiGate
        
        # Mock 데이터 생성기 테스트
        data_generator = DummyDataGenerator()
        self.assertIsNotNone(data_generator)
        
        # Mock FortiGate 테스트
        mock_fortigate = MockFortiGate()
        self.assertIsNotNone(mock_fortigate)
        
        # Mock 데이터 생성 테스트
        policies = data_generator.generate_policies(5)
        self.assertEqual(len(policies), 5)
        
    def test_import_security(self):
        """보안 모듈 임포트 테스트"""
        from src.utils.security import hash_api_key, verify_api_key, add_security_headers
        
        # API 키 해싱 테스트
        api_key = "test123"
        hashed = hash_api_key(api_key)
        self.assertIsNotNone(hashed)
        self.assertNotEqual(hashed, api_key)
        self.assertTrue(verify_api_key(api_key, hashed))
        
    def test_import_fortimanager_advanced(self):
        """FortiManager 고급 모듈 임포트 테스트"""
        from src.fortimanager.advanced_hub import FortiManagerAdvancedHub
        from src.fortimanager.fortimanager_analytics_engine import AdvancedAnalyticsEngine
        
        # 고급 허브 테스트
        hub = FortiManagerAdvancedHub(None)
        self.assertIsNotNone(hub)
        
    def test_import_itsm(self):
        """ITSM 모듈 임포트 테스트"""
        from src.itsm.automation_service import ITSMAutomationService
        from src.itsm.external_connector import ExternalITSMConnector
        
        # ITSM 자동화 서비스 테스트
        automation_service = ITSMAutomationService()
        self.assertIsNotNone(automation_service)
        
    def test_coverage_helper_functions(self):
        """커버리지 향상을 위한 헬퍼 함수들 테스트"""
        from src.utils.api_common import create_timeout_context, validate_config, merge_monitoring_data
        
        # 설정 검증 테스트
        valid, missing = validate_config({"key1": "value1"}, ["key1"])
        self.assertTrue(valid)
        self.assertEqual(len(missing), 0)
        
        valid, missing = validate_config({"key1": "value1"}, ["key1", "key2"])
        self.assertFalse(valid)
        self.assertEqual(len(missing), 1)
        
        # 모니터링 데이터 병합 테스트
        base_data = {"metric1": 100}
        additional_data = {"metric2": 200}
        merged = merge_monitoring_data(base_data, additional_data)
        self.assertEqual(merged["metric1"], 100)
        self.assertEqual(merged["metric2"], 200)
        self.assertIn("merge_timestamp", merged)

if __name__ == '__main__':
    unittest.main()