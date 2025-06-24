#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
공통 API 유틸리티 - 중복 코드 제거를 위한 공통 함수 및 믹스인
"""

import time
import threading
from typing import Dict, Any, Optional, Callable, Tuple, List
from abc import ABC, abstractmethod
from src.config.constants import RATE_LIMITS

from .unified_logger import get_logger


class ConnectionTestMixin:
    """연결 테스트 공통 로직을 제공하는 믹스인"""
    
    def perform_token_auth_test(self, test_endpoint: str) -> Tuple[bool, str, Optional[int]]:
        """토큰 인증 테스트 수행"""
        test_url = f"{self.base_url}/{test_endpoint.lstrip('/')}"
        
        success, result, status_code = self._make_request(
            'GET', test_url, headers=self.headers
        )
        
        if success:
            return True, f"Token authentication successful. Version: {result.get('version', 'Unknown')}", status_code
        else:
            return False, f"Token authentication failed: {status_code} - {result}", status_code
    
    def perform_credential_auth_test(self, login_endpoint: str) -> Tuple[bool, str, int]:
        """사용자 인증 테스트 수행"""
        try:
            login_url = f"{self.base_url}/{login_endpoint.lstrip('/')}"
            
            login_data = {
                'username': self.username,
                'secretkey': self.password
            }
            
            response = self.session.post(login_url, data=login_data, timeout=10)
            
            if 'ccsrftoken' in response.cookies:
                csrf_token = response.cookies['ccsrftoken']
                self.session.headers['X-CSRFTOKEN'] = csrf_token
                
                # 상태 확인
                status_url = f"{self.base_url}/api/v2/cmdb/system/status"
                status_response = self.session.get(status_url, timeout=10)
                
                if status_response.status_code == 200:
                    data = status_response.json()
                    version = data.get('version', 'Unknown')
                    return True, f"Credential authentication successful. Version: {version}", 200
                else:
                    return False, f"Status check failed: HTTP {status_response.status_code}", status_response.status_code
            else:
                return False, "Credential authentication failed", 401
                
        except Exception as e:
            return False, f"Credential authentication error: {str(e)}", 500


class JsonRpcMixin:
    """JSON-RPC 공통 로직을 제공하는 믹스인"""
    
    def __init__(self):
        if not hasattr(self, 'request_id'):
            self.request_id = 1
    
    def get_next_request_id(self) -> int:
        """다음 요청 ID 반환"""
        current_id = self.request_id
        self.request_id += 1
        return current_id
    
    def build_json_rpc_request(self, method: str, url: str, data: Optional[Dict] = None, 
                              session: Optional[str] = None, verbose: int = 0) -> Dict[str, Any]:
        """JSON-RPC 요청 페이로드 생성"""
        payload = {
            "id": self.get_next_request_id(),
            "jsonrpc": "2.0",
            "method": method,
            "params": {
                "url": url,
                "verbose": verbose
            }
        }
        
        if session:
            payload["session"] = session
        
        if data:
            payload["params"]["data"] = data
            
        return payload
    
    def parse_json_rpc_response(self, response: Dict[str, Any]) -> Tuple[bool, Any]:
        """JSON-RPC 응답 파싱"""
        if not isinstance(response, dict):
            return False, "Invalid response format"
        
        # JSON-RPC 오류 확인
        if "error" in response:
            error = response["error"]
            return False, f"JSON-RPC Error: {error.get('message', 'Unknown error')}"
        
        # 결과 확인
        result = response.get("result")
        if not result:
            return False, "No result in response"
        
        # 배열 결과인 경우 첫 번째 요소의 상태 확인
        if isinstance(result, list) and len(result) > 0:
            status = result[0].get("status", {})
            if status.get("code") == 0:
                return True, result[0].get("data", result)
            else:
                return False, status.get("message", "Unknown error")
        
        return True, result
    
    def make_json_rpc_request(self, method: str, url: str, data: Optional[Dict] = None,
                             session: Optional[str] = None, max_retries: int = 3) -> Tuple[bool, Any]:
        """JSON-RPC 요청 수행 (재시도 로직 포함)"""
        for attempt in range(max_retries + 1):
            try:
                payload = self.build_json_rpc_request(method, url, data, session)
                
                success, response_data, status_code = self._make_request(
                    'POST', f"{self.base_url}/jsonrpc", data=payload
                )
                
                if success:
                    return self.parse_json_rpc_response(response_data)
                elif status_code not in [500, 502, 503, 504]:
                    # 재시도할 필요가 없는 상태 코드
                    return False, f"HTTP {status_code}: {response_data}"
                
                # 재시도 대기
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # 지수 백오프
                    time.sleep(wait_time)
                    
            except Exception as e:
                if attempt == max_retries:
                    return False, f"Request failed after {max_retries} retries: {str(e)}"
                time.sleep(2 ** attempt)
        
        return False, f"Request failed after {max_retries} retries"


class MonitoringMixin:
    """모니터링 공통 로직을 제공하는 믹스인"""
    
    def __init__(self):
        if not hasattr(self, 'monitoring_data'):
            self.monitoring_data = {}
        if not hasattr(self, 'last_monitoring_update'):
            self.last_monitoring_update = None
        if not hasattr(self, 'monitoring_lock'):
            self.monitoring_lock = threading.RLock()
    
    def collect_base_monitoring_data(self) -> Dict[str, Any]:
        """기본 모니터링 데이터 수집"""
        with self.monitoring_lock:
            base_data = {
                'client_type': self.__class__.__name__,
                'host': getattr(self, 'host', 'unknown'),
                'auth_method': getattr(self, 'auth_method', 'unknown'),
                'offline_mode': getattr(self, 'OFFLINE_MODE', False),
                'timestamp': time.time(),
                'last_update': self.last_monitoring_update
            }
            
            # 연결 상태 테스트
            try:
                if hasattr(self, 'test_connection'):
                    success, message, status_code = self.test_connection()
                    base_data.update({
                        'connection_status': 'connected' if success else 'disconnected',
                        'last_status_message': message,
                        'last_status_code': status_code
                    })
            except Exception as e:
                base_data.update({
                    'connection_status': 'error',
                    'last_error': str(e)
                })
            
            self.last_monitoring_update = time.time()
            return base_data
    
    def update_monitoring_data(self, additional_data: Dict[str, Any]):
        """모니터링 데이터 업데이트"""
        with self.monitoring_lock:
            self.monitoring_data.update(additional_data)
            self.monitoring_data['last_update'] = time.time()
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """모니터링 요약 정보 반환"""
        with self.monitoring_lock:
            base_data = self.collect_base_monitoring_data()
            base_data.update(self.monitoring_data)
            return base_data


class ErrorHandlingMixin:
    """오류 처리 공통 로직을 제공하는 믹스인"""
    
    def __init__(self):
        if not hasattr(self, 'error_count'):
            self.error_count = 0
        if not hasattr(self, 'last_error'):
            self.last_error = None
        if not hasattr(self, 'max_error_threshold'):
            self.max_error_threshold = RATE_LIMITS['ERROR_THRESHOLD']
    
    def handle_api_error(self, error: Exception, context: str = ""):
        """API 오류 처리"""
        self.error_count += 1
        self.last_error = {
            'error': str(error),
            'context': context,
            'timestamp': time.time(),
            'count': self.error_count
        }
        
        if hasattr(self, 'logger'):
            self.logger.error(f"API Error in {context}: {error}")
        
        # 오류 임계치 확인
        if self.error_count >= self.max_error_threshold:
            if hasattr(self, 'logger'):
                self.logger.warning(f"Error threshold reached ({self.error_count})")
            return True  # 임계치 도달
        
        return False
    
    def reset_error_count(self):
        """오류 카운트 리셋"""
        self.error_count = 0
        self.last_error = None
    
    def get_error_status(self) -> Dict[str, Any]:
        """오류 상태 정보 반환"""
        return {
            'error_count': self.error_count,
            'last_error': self.last_error,
            'threshold_reached': self.error_count >= self.max_error_threshold
        }


class RequestRetryMixin:
    """요청 재시도 공통 로직을 제공하는 믹스인"""
    
    def __init__(self):
        if not hasattr(self, 'max_retries'):
            self.max_retries = 3
        if not hasattr(self, 'retry_delay'):
            self.retry_delay = 1.0
        if not hasattr(self, 'backoff_factor'):
            self.backoff_factor = 2.0
    
    def make_request_with_retry(self, method: str, url: str, max_retries: Optional[int] = None,
                               **kwargs) -> Tuple[bool, Any, int]:
        """재시도 로직이 포함된 요청 수행"""
        max_retries = max_retries or self.max_retries
        
        for attempt in range(max_retries + 1):
            try:
                success, data, status_code = self._make_request(method, url, **kwargs)
                
                # 성공하거나 재시도할 필요가 없는 상태 코드
                if success or status_code not in [500, 502, 503, 504, 408]:
                    return success, data, status_code
                
                # 마지막 시도가 아니면 대기
                if attempt < max_retries:
                    delay = self.retry_delay * (self.backoff_factor ** attempt)
                    if hasattr(self, 'logger'):
                        self.logger.warning(f"요청 실패 (시도 {attempt + 1}/{max_retries + 1}), {delay}초 후 재시도")
                    time.sleep(delay)
                    
            except Exception as e:
                if attempt == max_retries:
                    if hasattr(self, 'logger'):
                        self.logger.error(f"모든 재시도 실패: {e}")
                    return False, f"Request failed after {max_retries} retries: {str(e)}", 500
                
                delay = self.retry_delay * (self.backoff_factor ** attempt)
                if hasattr(self, 'logger'):
                    self.logger.warning(f"요청 예외 발생 (시도 {attempt + 1}/{max_retries + 1}), {delay}초 후 재시도: {e}")
                time.sleep(delay)
        
        return False, f"Request failed after {max_retries} retries", 500


class CacheMixin:
    """캐시 공통 로직을 제공하는 믹스인"""
    
    def __init__(self):
        if not hasattr(self, '_cache'):
            self._cache = {}
        if not hasattr(self, '_cache_ttl'):
            self._cache_ttl = {}
        if not hasattr(self, 'default_cache_duration'):
            self.default_cache_duration = 300  # 5분
        if not hasattr(self, '_cache_lock'):
            self._cache_lock = threading.RLock()
    
    def get_cached_data(self, key: str) -> Optional[Any]:
        """캐시된 데이터 조회"""
        with self._cache_lock:
            if key not in self._cache:
                return None
            
            # TTL 확인
            if key in self._cache_ttl:
                if time.time() > self._cache_ttl[key]:
                    # 만료된 캐시 제거
                    del self._cache[key]
                    del self._cache_ttl[key]
                    return None
            
            return self._cache[key]
    
    def set_cached_data(self, key: str, data: Any, ttl: Optional[int] = None):
        """데이터 캐시 저장"""
        with self._cache_lock:
            self._cache[key] = data
            
            if ttl is None:
                ttl = self.default_cache_duration
            
            if ttl > 0:
                self._cache_ttl[key] = time.time() + ttl
    
    def clear_cache(self, pattern: Optional[str] = None):
        """캐시 지우기"""
        with self._cache_lock:
            if pattern is None:
                self._cache.clear()
                self._cache_ttl.clear()
            else:
                # 패턴 매칭으로 캐시 삭제
                keys_to_delete = [key for key in self._cache.keys() if pattern in key]
                for key in keys_to_delete:
                    del self._cache[key]
                    if key in self._cache_ttl:
                        del self._cache_ttl[key]
    
    def cache_cleanup(self):
        """만료된 캐시 정리"""
        with self._cache_lock:
            current_time = time.time()
            expired_keys = [
                key for key, expiry in self._cache_ttl.items()
                if current_time > expiry
            ]
            
            for key in expired_keys:
                del self._cache[key]
                del self._cache_ttl[key]


# 공통 유틸리티 함수들
def sanitize_sensitive_data(data: Dict[str, Any], 
                           sensitive_keys: List[str] = None) -> Dict[str, Any]:
    """민감한 데이터 마스킹"""
    if sensitive_keys is None:
        sensitive_keys = ['password', 'passwd', 'secret', 'key', 'token', 'api_token']
    
    if not isinstance(data, dict):
        return data
    
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, dict):
            sanitized[key] = sanitize_sensitive_data(value, sensitive_keys)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_sensitive_data(item, sensitive_keys) if isinstance(item, dict) else item
                for item in value
            ]
        elif any(sk.lower() in key.lower() for sk in sensitive_keys):
            sanitized[key] = '********'
        else:
            sanitized[key] = value
    
    return sanitized


def create_timeout_context(timeout: int, operation_name: str = "operation"):
    """타임아웃 컨텍스트 생성"""
    import signal
    import contextlib
    
    class TimeoutError(Exception):
        pass
    
    def timeout_handler(signum, frame):
        raise TimeoutError(f"{operation_name} timed out after {timeout} seconds")
    
    @contextlib.contextmanager
    def timeout_context():
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        try:
            yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
    
    return timeout_context


def format_api_response(success: bool, data: Any, status_code: int, 
                       message: str = None) -> Dict[str, Any]:
    """API 응답 표준 포맷"""
    response = {
        'success': success,
        'status_code': status_code,
        'timestamp': time.time()
    }
    
    if success:
        response['data'] = data
    else:
        response['error'] = data
    
    if message:
        response['message'] = message
    
    return response


def validate_config(config: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, List[str]]:
    """설정 유효성 검사"""
    missing_fields = []
    
    for field in required_fields:
        if field not in config or not config[field]:
            missing_fields.append(field)
    
    return len(missing_fields) == 0, missing_fields


def merge_monitoring_data(base_data: Dict[str, Any], 
                         additional_data: Dict[str, Any]) -> Dict[str, Any]:
    """모니터링 데이터 병합"""
    merged = base_data.copy()
    merged.update(additional_data)
    merged['merge_timestamp'] = time.time()
    return merged