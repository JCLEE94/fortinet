#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Settings Compatibility Layer - FortiGate Nextrade
하위 호환성을 위한 기존 Settings 클래스 래퍼
"""

import warnings
from .unified_settings import unified_settings

class Settings:
    """
    하위 호환성을 위한 Settings 클래스 래퍼
    기존 코드가 깨지지 않도록 레거시 API를 유지합니다.
    """
    
    def __init__(self):
        warnings.warn(
            "Settings 클래스는 더 이상 권장되지 않습니다. "
            "대신 unified_settings를 사용하세요.",
            DeprecationWarning,
            stacklevel=2
        )
        self._unified = unified_settings
        
        # 레거시 호환성을 위한 속성들
        self.base_dir = self._unified.base_dir
        self.config_dir = self._unified.data_dir
        self.config_file = self._unified.config_file
        
        # 기존 속성들을 통합 설정에서 가져오기
        self._sync_from_unified()
    
    def _sync_from_unified(self):
        """통합 설정에서 레거시 속성 동기화"""
        self.fortimanager = self._unified.get_service_config('fortimanager')
        self.fortigate = self._unified.get_service_config('fortigate')
        self.fortianalyzer = self._unified.get_service_config('fortianalyzer')
        self.app_mode = self._unified.app_mode
        self.test_mode = self._unified.is_test_mode()
        
        # data 속성 (API 호환성을 위해)
        self.data = {
            'fortimanager': self.fortimanager,
            'fortigate': self.fortigate,
            'fortianalyzer': self.fortianalyzer,
            'app_mode': self.app_mode
        }
    
    def load_from_file(self):
        """설정 파일에서 설정 로드 (더 이상 필요 없음)"""
        warnings.warn(
            "load_from_file은 더 이상 필요하지 않습니다. "
            "통합 설정이 자동으로 로드됩니다.",
            DeprecationWarning
        )
        self._sync_from_unified()
    
    def save_to_file(self):
        """설정을 파일에 저장"""
        self._unified.save_to_json()
        self._sync_from_unified()
    
    def save(self):
        """설정 저장 (save_to_file의 별칭)"""
        self.save_to_file()
    
    def update_fortimanager(self, host=None, username=None, password=None, port=None):
        """FortiManager 설정 업데이트"""
        kwargs = {}
        if host is not None:
            kwargs['host'] = host
        if username is not None:
            kwargs['username'] = username
        if password is not None:
            kwargs['password'] = password
        if port is not None:
            kwargs['port'] = port
        
        if kwargs:
            self._unified.update_api_config('fortimanager', **kwargs)
            self._sync_from_unified()
    
    def update_fortigate(self, host=None, api_key=None, port=None):
        """FortiGate 설정 업데이트"""
        kwargs = {}
        if host is not None:
            kwargs['host'] = host
        if api_key is not None:
            kwargs['api_token'] = api_key  # api_key -> api_token 변환
        if port is not None:
            kwargs['port'] = port
        
        if kwargs:
            self._unified.update_api_config('fortigate', **kwargs)
            self._sync_from_unified()
    
    def update_fortianalyzer(self, host=None, username=None, password=None, port=None):
        """FortiAnalyzer 설정 업데이트"""
        kwargs = {}
        if host is not None:
            kwargs['host'] = host
        if username is not None:
            kwargs['username'] = username
        if password is not None:
            kwargs['password'] = password
        if port is not None:
            kwargs['port'] = port
        
        if kwargs:
            self._unified.update_api_config('fortianalyzer', **kwargs)
            self._sync_from_unified()
    
    def get_fortimanager_config(self):
        """FortiManager 설정 반환"""
        return self._unified.get_service_config('fortimanager')
    
    def update_fortimanager_config(self, config):
        """FortiManager 설정 업데이트"""
        # api_key -> api_token 변환
        if 'api_key' in config:
            config['api_token'] = config.pop('api_key')
        
        # use_https -> verify_ssl 변환
        if 'use_https' in config:
            config['verify_ssl'] = config.pop('use_https')
        
        self._unified.update_api_config('fortimanager', **config)
        self._sync_from_unified()
    
    def get_all_settings(self):
        """모든 설정 반환"""
        return {
            'fortimanager': self.fortimanager,
            'fortigate': self.fortigate,
            'fortianalyzer': self.fortianalyzer,
            'app_mode': self.app_mode,
            'test_mode': self.test_mode
        }
    
    def set_test_mode(self, enabled=True):
        """테스트 모드 설정"""
        mode = 'test' if enabled else 'production'
        self._unified.switch_mode(mode)
        self._sync_from_unified()

# 싱글톤 인스턴스 (하위 호환성을 위해)
settings = Settings()