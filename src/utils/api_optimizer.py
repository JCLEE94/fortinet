#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 응답 최적화 시스템 - 압축, 페이지네이션, 응답 시간 최적화
"""

import gzip
import json
import time
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union
from functools import wraps
from flask import request, jsonify, Response, g
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class APIOptimizer:
    """API 응답 최적화 관리자"""
    
    def __init__(self):
        self.compression_threshold = 1024  # 1KB 이상일 때 압축
        self.default_page_size = 20
        self.max_page_size = 100
        self.response_cache = {}
        
        # 성능 메트릭
        self.metrics = {
            'total_requests': 0,
            'compressed_responses': 0,
            'paginated_responses': 0,
            'cache_hits': 0,
            'avg_response_time': 0,
            'response_times': []
        }
    
    def _json_serializer(self, obj):
        """JSON 직렬화를 위한 커스텀 시리얼라이저"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, timedelta):
            return str(obj)
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)
    
    def compress_response(self, data: Union[str, Dict, List]) -> Tuple[bytes, bool]:
        """응답 데이터 압축"""
        try:
            # JSON 직렬화 (datetime 객체 처리 포함)
            if isinstance(data, (dict, list)):
                json_data = json.dumps(data, ensure_ascii=False, separators=(',', ':'), default=self._json_serializer)
            else:
                json_data = str(data)
            
            # 크기 확인
            original_size = len(json_data.encode('utf-8'))
            
            if original_size < self.compression_threshold:
                return json_data.encode('utf-8'), False
            
            # gzip 압축
            compressed_data = gzip.compress(json_data.encode('utf-8'))
            compression_ratio = len(compressed_data) / original_size
            
            # 압축 효과가 있는 경우만 압축 데이터 사용
            if compression_ratio < 0.9:  # 10% 이상 압축된 경우
                self.metrics['compressed_responses'] += 1
                logger.debug(f"응답 압축: {original_size} -> {len(compressed_data)} bytes "
                           f"({compression_ratio:.2%})")
                return compressed_data, True
            else:
                return json_data.encode('utf-8'), False
                
        except Exception as e:
            logger.error(f"응답 압축 실패: {e}")
            # 압축 실패 시 원본 반환
            if isinstance(data, (dict, list)):
                return json.dumps(data, default=self._json_serializer).encode('utf-8'), False
            return str(data).encode('utf-8'), False
    
    def paginate_data(self, data: List[Any], page: int = 1, page_size: Optional[int] = None) -> Dict[str, Any]:
        """데이터 페이지네이션"""
        if not isinstance(data, list):
            return {
                'data': data,
                'pagination': None
            }
        
        page_size = min(page_size or self.default_page_size, self.max_page_size)
        total_items = len(data)
        total_pages = (total_items + page_size - 1) // page_size
        
        # 페이지 범위 검증
        page = max(1, min(page, total_pages)) if total_pages > 0 else 1
        
        # 데이터 슬라이싱
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_data = data[start_idx:end_idx]
        
        # 페이지네이션 메타데이터
        pagination_info = {
            'current_page': page,
            'page_size': page_size,
            'total_items': total_items,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1,
            'next_page': page + 1 if page < total_pages else None,
            'prev_page': page - 1 if page > 1 else None
        }
        
        self.metrics['paginated_responses'] += 1
        
        return {
            'data': paginated_data,
            'pagination': pagination_info
        }
    
    def create_optimized_response(self, data: Any, status_code: int = 200) -> Response:
        """최적화된 응답 생성"""
        start_time = time.time()
        
        try:
            # Flask 애플리케이션 컨텍스트 확인
            try:
                from flask import has_request_context
                if not has_request_context():
                    # 요청 컨텍스트가 없는 경우 단순 JSON 응답 반환
                    if isinstance(data, (dict, list)):
                        response = Response(
                            json.dumps(data, ensure_ascii=False),
                            status=status_code,
                            content_type='application/json; charset=utf-8'
                        )
                    else:
                        response = Response(
                            str(data),
                            status=status_code,
                            content_type='application/json; charset=utf-8'
                        )
                    return response
            except ImportError:
                pass
            
            # 요청 헤더에서 압축 지원 확인
            accept_encoding = request.headers.get('Accept-Encoding', '') if request else ''
            supports_gzip = 'gzip' in accept_encoding.lower()
            
            # 응답 데이터 압축
            response_data, is_compressed = self.compress_response(data)
            
            # 응답 생성
            if is_compressed and supports_gzip:
                response = Response(
                    response_data,
                    status=status_code,
                    content_type='application/json; charset=utf-8'
                )
                response.headers['Content-Encoding'] = 'gzip'
                response.headers['Vary'] = 'Accept-Encoding'
            else:
                # 모든 경우에 Response 객체 직접 생성
                if isinstance(data, (dict, list)):
                    json_data = json.dumps(data, ensure_ascii=False, separators=(',', ':'), default=self._json_serializer)
                    response = Response(
                        json_data,
                        status=status_code,
                        content_type='application/json; charset=utf-8'
                    )
                else:
                    # 문자열 데이터의 경우 JSON으로 감싸기
                    if isinstance(data, str):
                        try:
                            # JSON 문자열인지 확인
                            json.loads(data)
                            response = Response(
                                data,
                                status=status_code,
                                content_type='application/json; charset=utf-8'
                            )
                        except (json.JSONDecodeError, TypeError):
                            # 일반 문자열인 경우 JSON 객체로 감싸기
                            wrapped_data = json.dumps({'data': data, 'message': data}, ensure_ascii=False, default=self._json_serializer)
                            response = Response(
                                wrapped_data,
                                status=status_code,
                                content_type='application/json; charset=utf-8'
                            )
                    else:
                        response = Response(
                            json.dumps({'data': str(data)}, ensure_ascii=False, default=self._json_serializer),
                            status=status_code,
                            content_type='application/json; charset=utf-8'
                        )
            
            # 캐시 헤더 설정
            response.headers['Cache-Control'] = 'public, max-age=300'  # 5분 캐시
            response.headers['ETag'] = f'"{hash(str(data))}"'
            
            # 응답 시간 측정
            response_time = time.time() - start_time
            self._update_metrics(response_time)
            
            # 성능 헤더 추가
            response.headers['X-Response-Time'] = f"{response_time:.3f}s"
            response.headers['X-Compressed'] = str(is_compressed and supports_gzip).lower()
            
            return response
            
        except Exception as e:
            logger.error(f"최적화된 응답 생성 실패: {e}")
            # 폴백: 기본 응답 (jsonify 사용하지 않음)
            error_data = json.dumps({'error': 'Response optimization failed', 'details': str(e)}, ensure_ascii=False, default=self._json_serializer)
            response = Response(
                error_data,
                status=500,
                content_type='application/json; charset=utf-8'
            )
            return response
    
    def _update_metrics(self, response_time: float):
        """성능 메트릭 업데이트"""
        self.metrics['total_requests'] += 1
        self.metrics['response_times'].append(response_time)
        
        # 최근 100개 응답 시간만 유지
        if len(self.metrics['response_times']) > 100:
            self.metrics['response_times'] = self.metrics['response_times'][-100:]
        
        # 평균 응답 시간 계산
        self.metrics['avg_response_time'] = sum(self.metrics['response_times']) / len(self.metrics['response_times'])
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 조회"""
        if not self.metrics['response_times']:
            return self.metrics
        
        response_times = self.metrics['response_times']
        
        return {
            **self.metrics,
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'p95_response_time': sorted(response_times)[int(len(response_times) * 0.95)],
            'compression_ratio': (self.metrics['compressed_responses'] / 
                                max(self.metrics['total_requests'], 1) * 100),
            'pagination_ratio': (self.metrics['paginated_responses'] / 
                               max(self.metrics['total_requests'], 1) * 100)
        }


# 전역 API 최적화 인스턴스
_api_optimizer: Optional[APIOptimizer] = None


def get_api_optimizer() -> APIOptimizer:
    """전역 API 최적화 인스턴스 반환"""
    global _api_optimizer
    if _api_optimizer is None:
        _api_optimizer = APIOptimizer()
    return _api_optimizer


def optimized_response(auto_paginate: bool = False, cache_key: Optional[str] = None):
    """
    API 응답 최적화 데코레이터
    
    Args:
        auto_paginate: 자동 페이지네이션 적용 여부
        cache_key: 캐시 키 (지정하면 응답 캐싱)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            optimizer = get_api_optimizer()
            
            # 캐시 확인
            if cache_key and cache_key in optimizer.response_cache:
                cached_response, cache_time = optimizer.response_cache[cache_key]
                # 캐시 만료 확인 (5분)
                if time.time() - cache_time < 300:
                    optimizer.metrics['cache_hits'] += 1
                    return optimizer.create_optimized_response(cached_response)
            
            # 함수 실행
            result = func(*args, **kwargs)
            
            # Flask Response 객체인 경우 그대로 반환
            if hasattr(result, 'status_code') and hasattr(result, 'headers'):
                logger.debug(f"Returning Flask Response object directly: {type(result)}")
                return result
            
            # Tuple 형태의 응답 (data, status_code) 처리
            response_data = result
            status_code = 200
            
            if isinstance(result, tuple) and len(result) == 2:
                response_data, status_code = result
            
            # 자동 페이지네이션 적용
            if auto_paginate and isinstance(response_data, (dict, list)):
                if isinstance(response_data, list):
                    # 페이지네이션 매개변수 추출
                    page = request.args.get('page', 1, type=int)
                    page_size = request.args.get('page_size', type=int)
                    
                    response_data = optimizer.paginate_data(response_data, page, page_size)
                elif isinstance(response_data, dict) and 'data' in response_data and isinstance(response_data['data'], list):
                    # 이미 구조화된 응답의 데이터 부분만 페이지네이션
                    page = request.args.get('page', 1, type=int)
                    page_size = request.args.get('page_size', type=int)
                    
                    paginated = optimizer.paginate_data(response_data['data'], page, page_size)
                    response_data.update(paginated)
            
            # 응답 캐싱
            if cache_key:
                optimizer.response_cache[cache_key] = (response_data, time.time())
                # 캐시 크기 제한 (최대 100개)
                if len(optimizer.response_cache) > 100:
                    oldest_key = min(optimizer.response_cache.keys(), 
                                   key=lambda k: optimizer.response_cache[k][1])
                    del optimizer.response_cache[oldest_key]
            
            return optimizer.create_optimized_response(response_data, status_code)
        
        return wrapper
    return decorator


def async_optimized_response(auto_paginate: bool = False):
    """비동기 API 응답 최적화 데코레이터"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            optimizer = get_api_optimizer()
            
            # 비동기 함수 실행
            result = await func(*args, **kwargs)
            
            # 자동 페이지네이션 적용
            if auto_paginate and isinstance(result, list):
                page = request.args.get('page', 1, type=int)
                page_size = request.args.get('page_size', type=int)
                result = optimizer.paginate_data(result, page, page_size)
            
            return optimizer.create_optimized_response(result)
        
        return wrapper
    return decorator


class ResponseBatcher:
    """응답 배치 처리 시스템"""
    
    def __init__(self, batch_size: int = 10, timeout: float = 0.1):
        self.batch_size = batch_size
        self.timeout = timeout
        self.pending_requests = []
        self.last_batch_time = time.time()
    
    async def add_request(self, request_func, *args, **kwargs):
        """요청을 배치에 추가"""
        self.pending_requests.append((request_func, args, kwargs))
        
        # 배치 크기에 도달하거나 타임아웃 시 배치 처리
        if (len(self.pending_requests) >= self.batch_size or 
            time.time() - self.last_batch_time > self.timeout):
            return await self._process_batch()
    
    async def _process_batch(self):
        """배치된 요청들을 병렬 처리"""
        if not self.pending_requests:
            return []
        
        # 병렬 실행
        tasks = []
        for request_func, args, kwargs in self.pending_requests:
            if asyncio.iscoroutinefunction(request_func):
                tasks.append(request_func(*args, **kwargs))
            else:
                # 동기 함수를 비동기로 실행
                tasks.append(asyncio.get_event_loop().run_in_executor(
                    None, lambda: request_func(*args, **kwargs)
                ))
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            self.pending_requests.clear()
            self.last_batch_time = time.time()
            return results
        except Exception as e:
            logger.error(f"배치 처리 실패: {e}")
            self.pending_requests.clear()
            return []


class StreamingResponse:
    """스트리밍 응답 처리"""
    
    @staticmethod
    def create_sse_response(data_generator):
        """Server-Sent Events 응답 생성"""
        def generate():
            try:
                for data in data_generator:
                    if isinstance(data, dict):
                        json_data = json.dumps(data, ensure_ascii=False)
                    else:
                        json_data = str(data)
                    
                    yield f"data: {json_data}\n\n"
            except Exception as e:
                error_data = json.dumps({'error': str(e)})
                yield f"data: {error_data}\n\n"
        
        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*'
            }
        )
    
    @staticmethod
    def create_chunked_response(data: List[Any], chunk_size: int = 100):
        """청크 단위 응답 생성"""
        def generate():
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i + chunk_size]
                chunk_data = {
                    'chunk_index': i // chunk_size,
                    'chunk_size': len(chunk),
                    'total_items': len(data),
                    'is_last_chunk': i + chunk_size >= len(data),
                    'data': chunk
                }
                yield json.dumps(chunk_data, ensure_ascii=False) + '\n'
        
        return Response(
            generate(),
            mimetype='application/x-ndjson',
            headers={
                'Content-Type': 'application/x-ndjson',
                'Transfer-Encoding': 'chunked'
            }
        )


# 사용 예시
if __name__ == "__main__":
    # API 최적화 데코레이터 사용 예시
    from flask import Flask, request
    
    app = Flask(__name__)
    
    @app.route('/api/devices')
    @optimized_response(auto_paginate=True, cache_key='devices_list')
    def get_devices():
        """최적화된 장치 목록 조회"""
        # 시뮬레이션 데이터
        devices = [f"Device-{i:03d}" for i in range(1, 501)]  # 500개 장치
        return devices
    
    @app.route('/api/performance')
    @optimized_response()
    def get_performance():
        """성능 메트릭 조회"""
        optimizer = get_api_optimizer()
        return optimizer.get_performance_metrics()
    
    if __name__ == '__main__':
        app.run(debug=True)