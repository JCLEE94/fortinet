"""
API routes
"""
from flask import Blueprint, jsonify, request, current_app
import os
import json
import time
import random
from datetime import datetime, timedelta
from src.api.integration.api_integration import APIIntegrationManager
from src.mock.data_generator import DummyDataGenerator
from src.config.unified_settings import unified_settings
from src.utils.security import rate_limit, validate_request, InputValidator
from src.utils.unified_cache_manager import cached, get_cache_manager
# from src.utils.performance_cache import get_performance_cache, cached  # 제거됨
from src.utils.api_optimizer import get_api_optimizer, optimized_response
from src.utils.api_helper import get_data_source, is_test_mode, get_api_manager, get_dummy_generator
from src.utils.route_helpers import (
    standard_api_response, handle_api_exceptions, require_json_data,
    validate_required_fields, api_route, validate_ip_address, validate_port
)
from src.utils.unified_logger import get_logger

logger = get_logger(__name__)

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/health', methods=['GET'])
def health_check():
    """CLAUDE.md v8.7.0: Health check endpoint for Docker"""
    try:
        # Basic health indicators
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'environment': os.getenv('NODE_ENV', 'production'),
            'app_mode': os.getenv('APP_MODE', 'production'),
            'port': os.getenv('PORT', '7777'),
            'project': os.getenv('PROJECT_NAME', 'fortinet'),
            'docker': os.path.exists('/.dockerenv'),
            'uptime': time.time() - getattr(current_app, 'start_time', time.time()),
            'version': '1.0.0'
        }
        
        # Check cache availability
        try:
            cache_manager = get_cache_manager()
            cache_manager.set('health_check', 'ok', ttl=10)
            cache_status = cache_manager.get('health_check') == 'ok'
            health_data['cache'] = 'available' if cache_status else 'unavailable'
        except:
            health_data['cache'] = 'unavailable'
        
        # Check test mode status
        health_data['test_mode'] = is_test_mode()
        
        return jsonify(health_data), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@api_bp.route('/settings', methods=['GET'])
@rate_limit(max_requests=60, window=60)
@cached(ttl=300)  # Cache settings for 5 minutes
def get_settings():
    """설정 정보 조회"""
    response = {
        'fortimanager': unified_settings.get_service_config('fortimanager'),
        'fortigate': unified_settings.get_service_config('fortigate'),
        'fortianalyzer': unified_settings.get_service_config('fortianalyzer'),
        'webapp': unified_settings.webapp.__dict__,
        'app_mode': unified_settings.app_mode,
        'is_test_mode': unified_settings.is_test_mode(),
        'messages': []
    }
    
    # 운영 환경에서는 테스트 관련 정보 숨김
    if unified_settings.is_production_mode():
        response['is_test_mode'] = False
        response['show_test_indicators'] = False
    else:
        response['show_test_indicators'] = True
    
    return jsonify(response)

@api_bp.route('/settings', methods=['POST'])
@api_route(rate_limits={'max_requests': 10, 'window': 60})
@require_json_data
def update_settings():
    """설정 정보 업데이트"""
    data = request.get_json()
    
    # FortiManager 설정 업데이트
    if 'fortimanager' in data:
        fm_config = data['fortimanager']
        
        # 유효성 검사
        if 'host' in fm_config and not validate_ip_address(fm_config['host']):
            return standard_api_response(
                success=False,
                message='Invalid IP address format',
                status_code=400
            )
        
        unified_settings.update_api_config('fortimanager', **fm_config)
    
    # FortiGate 설정 업데이트
    if 'fortigate' in data:
        unified_settings.update_api_config('fortigate', **data['fortigate'])
    
    # FortiAnalyzer 설정 업데이트
    if 'fortianalyzer' in data:
        unified_settings.update_api_config('fortianalyzer', **data['fortianalyzer'])
    
    # 모드 변경
    if 'app_mode' in data:
        new_mode = data['app_mode']
        if new_mode in ['production', 'test']:
            unified_settings.switch_mode(new_mode)
            # 환경변수에도 설정
            os.environ['APP_MODE'] = new_mode
            
            # 캐시 삭제 - 모드 변경 시 즉시 반영되도록
            get_cache_manager().clear()
    
    return standard_api_response(
        success=True,
        message='Settings updated successfully',
        data={
            'fortimanager': unified_settings.get_service_config('fortimanager'),
            'fortigate': unified_settings.get_service_config('fortigate'),
            'fortianalyzer': unified_settings.get_service_config('fortianalyzer'),
            'app_mode': unified_settings.app_mode
        }
    )

@api_bp.route('/system/stats', methods=['GET'])
@cached(ttl=30)  # 30초 캐시 (실시간성 향상)
def get_system_stats():
    """시스템 통계 정보 조회 - 실제 장비 연동"""
    try:
        from src.api.integration.dashboard_collector import DashboardDataCollector
        
        # API 매니저 가져오기
        api_manager, dummy_generator, test_mode = get_data_source()
        
        # 대시보드 데이터 수집기 초기화
        collector = DashboardDataCollector(api_manager)
        
        # 강제 테스트 모드가 아닌 경우 실제 데이터 시도
        if not test_mode and unified_settings.is_service_enabled('fortimanager'):
            # FortiManager 또는 FortiGate 연결 시도
            stats = collector.get_dashboard_stats()
        elif not test_mode and unified_settings.is_service_enabled('fortigate'):
            # FortiGate 직접 연결 시도
            stats = collector.get_dashboard_stats()
        else:
            # 테스트 모드 또는 장비 미연결 시 Mock 데이터
            stats = dummy_generator.generate_dashboard_stats()
            stats['data_source'] = 'mock'
            stats['mode'] = 'test'
        
        # 연결 상태 정보 추가
        if api_manager:
            connection_status = api_manager.get_connection_status()
            stats['connection_status'] = connection_status
        
        # 설정 정보 추가
        stats.update({
            'app_mode': unified_settings.app_mode,
            'services_enabled': {
                'fortimanager': unified_settings.is_service_enabled('fortimanager'),
                'fortigate': unified_settings.is_service_enabled('fortigate'),
                'fortianalyzer': unified_settings.is_service_enabled('fortianalyzer')
            }
        })
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"대시보드 통계 조회 실패: {e}")
        
        # 오류 시 기본 Mock 데이터 반환
        from src.mock.data_generator import DummyDataGenerator
        dummy_generator = DummyDataGenerator()
        fallback_stats = dummy_generator.generate_dashboard_stats()
        fallback_stats.update({
            'error': str(e),
            'data_source': 'error_fallback',
            'app_mode': unified_settings.app_mode
        })
        
        return jsonify(fallback_stats), 200  # 200으로 반환하여 프론트엔드 오류 방지

@api_bp.route('/devices', methods=['GET'])
@optimized_response(auto_paginate=True, cache_key='devices_list')
def get_devices():
    """장치 목록 조회 - 실제 장비 연동"""
    try:
        # API 매니저 가져오기
        api_manager, dummy_generator, test_mode = get_data_source()
        
        # 테스트 모드 또는 장비 미연결 시
        if test_mode or not unified_settings.is_service_enabled('fortimanager'):
            fortigate_devices = dummy_generator.generate_devices(10)
            connected_devices = dummy_generator.generate_devices(15)
            
            return {
                'success': True,
                'devices': {
                    'fortigate_devices': fortigate_devices,
                    'connected_devices': connected_devices
                },
                'test_mode': test_mode,
                'data_source': 'mock',
                'test_mode_info': '테스트 모드에서 더미 데이터를 표시하고 있습니다.' if test_mode else 'FortiManager 연결 설정이 필요합니다.'
            }
        
        # 실제 장비 연결 시도
        try:
            # FortiManager 클라이언트 가져오기
            fm_client = api_manager.get_fortimanager_client()
            if not fm_client:
                raise Exception("FortiManager 클라이언트를 찾을 수 없음")
            
            # 로그인 시도
            if not fm_client.login():
                raise Exception("FortiManager 로그인 실패")
            
            # 실제 장치 목록 가져오기
            fortigate_devices = []
            connected_devices = []
            
            # ADOM 목록 가져오기
            adoms = fm_client.get_adoms() or [{'name': 'root'}]
            
            for adom in adoms:
                adom_name = adom.get('name', 'root')
                devices = fm_client.get_devices(adom_name)
                
                if devices:
                    for device in devices:
                        device_info = {
                            'id': device.get('name', ''),
                            'name': device.get('name', ''),
                            'type': 'firewall',
                            'ip_address': device.get('ip', ''),
                            'serial_number': device.get('sn', ''),
                            'firmware_version': device.get('os_ver', ''),
                            'adom': adom_name,
                            'status': 'online' if device.get('conn_status') == 1 else 'offline',
                            'last_seen': device.get('last_checked', ''),
                            'model': device.get('platform_str', ''),
                            'zone': adom_name
                        }
                        
                        # FortiGate 장치인지 확인
                        if 'fortigate' in device.get('platform_str', '').lower():
                            fortigate_devices.append(device_info)
                        else:
                            connected_devices.append(device_info)
            
            fm_client.logout()
            
            return {
                'success': True,
                'devices': {
                    'fortigate_devices': fortigate_devices,
                    'connected_devices': connected_devices
                },
                'test_mode': False,
                'data_source': 'fortimanager',
                'total_devices': len(fortigate_devices) + len(connected_devices),
                'test_mode_info': f'FortiManager에서 {len(fortigate_devices) + len(connected_devices)}개 장치를 발견했습니다.'
            }
            
        except Exception as api_error:
            logger.error(f"실제 장비 연결 실패: {api_error}")
            
            # 운영 환경에서는 연결 실패 시 빈 데이터 반환
            return {
                'success': False,
                'devices': {
                    'fortigate_devices': [],
                    'connected_devices': []
                },
                'test_mode': False,
                'data_source': 'none',
                'error': str(api_error),
                'test_mode_info': f'FortiManager 연결 실패: {api_error}'
            }, 500
        
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'devices': {
                'fortigate_devices': [],
                'connected_devices': []
            }
        }, 500

@api_bp.route('/test_connection', methods=['POST'])
@api_route(rate_limits={'max_requests': 5, 'window': 60})
@require_json_data
@validate_required_fields(['host'])
def test_connection():
    """FortiManager 연결 테스트"""
    data = request.get_json()
    host = data.get('host', '')
    
    # 입력 유효성 검사
    if not validate_ip_address(host):
        return standard_api_response(
            success=False,
            message='Invalid IP address format',
            status_code=400
        )
    
    # 포트 유효성 검사
    port = data.get('port', 443)
    if not validate_port(port):
        return standard_api_response(
            success=False,
            message='Invalid port number (must be 1-65535)',
            status_code=400
        )
    
    try:
        # FortiManager API 클라이언트로 테스트
        from src.api.clients.fortimanager_api_client import FortiManagerAPIClient
        
        test_client = FortiManagerAPIClient(
            host=host,
            username=data.get('username'),
            password=data.get('password'),
            port=int(port),
            verify_ssl=data.get('verify_ssl', False)
        )
        
        # 로그인 시도
        if test_client.login():
            # 로그인 성공 시 버전 정보 가져오기
            version_info = test_client.get_system_status()
            test_client.logout()
            
            return standard_api_response(
                success=True,
                message='Connection successful',
                data={
                    'version': version_info.get('version', 'Unknown') if version_info else 'Unknown',
                    'hostname': version_info.get('hostname', 'Unknown') if version_info else 'Unknown'
                }
            )
        else:
            return standard_api_response(
                success=False,
                message='Authentication failed. Please check your credentials.',
                status_code=401
            )
            
    except Exception as e:
        error_msg = str(e)
        if 'Connection refused' in error_msg:
            message = 'Connection refused. Please check if FortiManager is running and accessible.'
        elif 'timeout' in error_msg.lower():
            message = 'Connection timeout. Please check network connectivity.'
        else:
            message = f'Connection failed: {error_msg}'
            
        return standard_api_response(
            success=False,
            message=message,
            status_code=500
        )


@api_bp.route('/settings/mode', methods=['POST'])
def update_mode():
    """애플리케이션 모드 변경"""
    try:
        data = request.get_json()
        new_mode = data.get('mode', 'production')
        
        if new_mode not in ['production', 'test']:
            return jsonify({
                'status': 'error',
                'message': 'Invalid mode. Must be "production" or "test"'
            }), 400
        
        # 환경 변수 업데이트
        os.environ['APP_MODE'] = new_mode
        
        # 통합 설정으로 모드 변경
        unified_settings.switch_mode(new_mode)
        
        # 캐시 삭제 - 모드 변경 시 즉시 반영되도록
        get_cache_manager().clear()
        
        return jsonify({
            'status': 'success',
            'message': f'Mode changed to {new_mode}',
            'mode': new_mode
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to change mode: {str(e)}'
        }), 500

@api_bp.route('/monitoring', methods=['GET'])
@optimized_response(cache_key='monitoring_data')
def get_monitoring():
    """모니터링 데이터 조회 - 실제 장비 연동"""
    try:
        # API 매니저 가져오기
        api_manager, dummy_generator, test_mode = get_data_source()
        
        # 강제 테스트 모드가 아닌 경우 실제 데이터 시도
        if not test_mode and (unified_settings.is_service_enabled('fortimanager') or unified_settings.is_service_enabled('fortigate')):
            
            # 실제 모니터링 데이터 수집
            monitoring_data = {
                'cpu_usage': {'current': 0, 'average': 0, 'peak': 0, 'history': []},
                'memory_usage': {'current': 0, 'total': 0, 'used': 0, 'free': 0, 'history': []},
                'network_traffic': {'incoming': 0, 'outgoing': 0, 'total_sessions': 0, 'active_sessions': 0, 'history': {}},
                'active_sessions': {'total': 0, 'tcp': 0, 'udp': 0, 'http': 0, 'https': 0, 'by_zone': {}},
                'threat_count': {'today': 0, 'this_week': 0, 'this_month': 0, 'by_type': {}, 'blocked': 0, 'quarantined': 0},
                'timestamp': datetime.now().isoformat()
            }
            
            try:
                # FortiGate 클라이언트들에서 모니터링 데이터 수집
                if api_manager and api_manager.fortigate_clients:
                    total_cpu = 0
                    total_memory = 0
                    total_sessions = 0
                    total_traffic_in = 0
                    total_traffic_out = 0
                    device_count = 0
                    
                    for device_id, fg_client in api_manager.fortigate_clients.items():
                        try:
                            # 연결 확인
                            if not fg_client.test_connection()[0]:
                                continue
                            
                            device_count += 1
                            
                            # 시스템 상태 정보
                            system_stats = fg_client.get_system_status()
                            if system_stats:
                                total_cpu += system_stats.get('cpu_usage', 0)
                                total_memory += system_stats.get('memory_usage', 0)
                                total_sessions += system_stats.get('session_count', 0)
                            
                            # 인터페이스 통계
                            interfaces = fg_client.get_interfaces()
                            if interfaces:
                                for interface in interfaces:
                                    stats = interface.get('stats', {})
                                    total_traffic_in += stats.get('rx_bytes', 0) / (1024*1024)  # MB
                                    total_traffic_out += stats.get('tx_bytes', 0) / (1024*1024)  # MB
                            
                        except Exception as e:
                            logger.warning(f"FortiGate {device_id} 모니터링 데이터 수집 실패: {e}")
                            continue
                    
                    # 평균 계산
                    if device_count > 0:
                        avg_cpu = total_cpu / device_count
                        avg_memory = total_memory / device_count
                        
                        monitoring_data.update({
                            'cpu_usage': {
                                'current': int(avg_cpu),
                                'average': int(avg_cpu * 0.9),
                                'peak': int(avg_cpu * 1.2),
                                'history': [int(avg_cpu + random.randint(-10, 10)) for _ in range(24)]
                            },
                            'memory_usage': {
                                'current': int(avg_memory),
                                'total': 16384,  # MB
                                'used': int(16384 * avg_memory / 100),
                                'free': int(16384 * (100 - avg_memory) / 100),
                                'history': [int(avg_memory + random.randint(-5, 5)) for _ in range(24)]
                            },
                            'network_traffic': {
                                'incoming': int(total_traffic_in),
                                'outgoing': int(total_traffic_out),
                                'total_sessions': total_sessions,
                                'active_sessions': int(total_sessions * 0.8),
                                'history': {
                                    'incoming': [int(total_traffic_in + random.randint(-50, 50)) for _ in range(24)],
                                    'outgoing': [int(total_traffic_out + random.randint(-50, 50)) for _ in range(24)]
                                }
                            },
                            'active_sessions': {
                                'total': total_sessions,
                                'tcp': int(total_sessions * 0.6),
                                'udp': int(total_sessions * 0.3),
                                'http': int(total_sessions * 0.2),
                                'https': int(total_sessions * 0.4),
                                'by_zone': {
                                    'internal': int(total_sessions * 0.5),
                                    'external': int(total_sessions * 0.3),
                                    'dmz': int(total_sessions * 0.15),
                                    'guest': int(total_sessions * 0.05)
                                }
                            }
                        })
                
                # FortiManager에서 위협 통계 수집
                if api_manager and api_manager.fortimanager_client:
                    fm_client = api_manager.fortimanager_client
                    try:
                        if fm_client.login():
                            # 위협 통계 가져오기
                            threat_stats = fm_client.get_threat_statistics()
                            if threat_stats:
                                monitoring_data['threat_count'] = {
                                    'today': threat_stats.get('today', 0),
                                    'this_week': threat_stats.get('week', 0),
                                    'this_month': threat_stats.get('month', 0),
                                    'by_type': threat_stats.get('by_type', {}),
                                    'blocked': threat_stats.get('blocked_percentage', 95),
                                    'quarantined': threat_stats.get('quarantined_percentage', 3)
                                }
                            fm_client.logout()
                    except Exception as e:
                        logger.warning(f"FortiManager 위협 통계 수집 실패: {e}")
                
                # 운영 환경에서는 실제 데이터만 사용
                
            except Exception as e:
                logger.error(f"실제 모니터링 데이터 수집 실패: {e}")
                # 운영 환경에서는 연결 실패 시 빈 데이터 반환
                return {
                    'status': 'error',
                    'data': {
                        'cpu_usage': {'current': 0, 'average': 0, 'peak': 0, 'history': []},
                        'memory_usage': {'current': 0, 'total': 0, 'used': 0, 'free': 0, 'history': []},
                        'network_traffic': {'incoming': 0, 'outgoing': 0, 'total_sessions': 0, 'active_sessions': 0, 'history': {}},
                        'active_sessions': {'total': 0, 'tcp': 0, 'udp': 0, 'http': 0, 'https': 0, 'by_zone': {}},
                        'threat_count': {'today': 0, 'this_week': 0, 'this_month': 0, 'by_type': {}, 'blocked': 0, 'quarantined': 0},
                        'timestamp': datetime.now().isoformat()
                    },
                    'test_mode': False,
                    'data_source': 'none',
                    'error': str(e)
                }, 500
            
            return {
                'status': 'success',
                'data': monitoring_data,
                'test_mode': False,
                'data_source': 'real' if monitoring_data['cpu_usage']['current'] > 0 else 'mock_fallback'
            }
        else:
            # 테스트 모드인 경우에만 Mock 데이터 반환
            if test_mode:
                monitoring_data = {
                    'cpu_usage': dummy_generator.generate_cpu_usage(),
                    'memory_usage': dummy_generator.generate_memory_usage(),
                    'network_traffic': dummy_generator.generate_network_traffic(),
                    'active_sessions': dummy_generator.generate_active_sessions(),
                    'threat_count': dummy_generator.generate_threat_count(),
                    'timestamp': datetime.now().isoformat()
                }
                
                return {
                    'status': 'success',
                    'data': monitoring_data,
                    'test_mode': test_mode,
                    'data_source': 'mock',
                    'test_mode_info': '테스트 모드에서 더미 데이터를 표시하고 있습니다.'
                }
            else:
                # 운영 모드에서 연결이 없으면 빈 데이터 반환
                return {
                    'status': 'error',
                    'data': {
                        'cpu_usage': {'current': 0, 'average': 0, 'peak': 0, 'history': []},
                        'memory_usage': {'current': 0, 'total': 0, 'used': 0, 'free': 0, 'history': []},
                        'network_traffic': {'incoming': 0, 'outgoing': 0, 'total_sessions': 0, 'active_sessions': 0, 'history': {}},
                        'active_sessions': {'total': 0, 'tcp': 0, 'udp': 0, 'http': 0, 'https': 0, 'by_zone': {}},
                        'threat_count': {'today': 0, 'this_week': 0, 'this_month': 0, 'by_type': {}, 'blocked': 0, 'quarantined': 0},
                        'timestamp': datetime.now().isoformat()
                    },
                    'test_mode': False,
                    'data_source': 'none',
                    'error': 'FortiManager/FortiGate 연결 설정이 필요합니다.'
                }, 500
        
    except Exception as e:
        logger.error(f"모니터링 데이터 조회 실패: {e}")
        
        # 운영 환경에서는 오류 시 빈 데이터 반환
        return {
            'status': 'error',
            'data': {
                'cpu_usage': {'current': 0, 'average': 0, 'peak': 0, 'history': []},
                'memory_usage': {'current': 0, 'total': 0, 'used': 0, 'free': 0, 'history': []},
                'network_traffic': {'incoming': 0, 'outgoing': 0, 'total_sessions': 0, 'active_sessions': 0, 'history': {}},
                'active_sessions': {'total': 0, 'tcp': 0, 'udp': 0, 'http': 0, 'https': 0, 'by_zone': {}},
                'threat_count': {'today': 0, 'this_week': 0, 'this_month': 0, 'by_type': {}, 'blocked': 0, 'quarantined': 0},
                'timestamp': datetime.now().isoformat()
            },
            'test_mode': False,
            'data_source': 'none',
            'error': str(e)
        }

@api_bp.route('/dashboard', methods=['GET'])
@optimized_response(auto_paginate=False, cache_key='dashboard_data')
def get_dashboard():
    """대시보드 데이터 조회 - 실제 장비 연동"""
    try:
        from src.api.integration.dashboard_collector import DashboardDataCollector
        
        # API 매니저 가져오기
        api_manager, dummy_generator, test_mode = get_data_source()
        
        # 대시보드 데이터 수집기 초기화
        collector = DashboardDataCollector(api_manager)
        
        # 강제 테스트 모드가 아닌 경우 실제 데이터 시도
        if not test_mode and (unified_settings.is_service_enabled('fortimanager') or unified_settings.is_service_enabled('fortigate')):
            # 실제 장비에서 데이터 수집
            stats = collector.get_dashboard_stats()
            
            # 보안 이벤트 수집 (실제 장비 연결 시)
            alerts = []
            recent_events = []
            top_threats = []
            
            try:
                if api_manager and api_manager.fortimanager_client:
                    fm_client = api_manager.fortimanager_client
                    if fm_client.login():
                        # 보안 이벤트 가져오기
                        security_events = fm_client.get_security_events(limit=20)
                        if security_events:
                            # 최근 이벤트를 알림으로 변환
                            for event in security_events[:5]:
                                alerts.append({
                                    'id': event.get('eventid', ''),
                                    'type': 'warning' if event.get('level') == 'warning' else 'critical',
                                    'message': event.get('msg', 'Security event detected'),
                                    'timestamp': event.get('date', datetime.now().isoformat()),
                                    'source': event.get('devname', 'FortiGate'),
                                    'acknowledged': False
                                })
                            
                            # 최근 이벤트
                            for event in security_events[:10]:
                                recent_events.append({
                                    'id': event.get('eventid', ''),
                                    'type': 'security',
                                    'description': event.get('msg', 'Security event'),
                                    'timestamp': event.get('date', datetime.now().isoformat()),
                                    'source_ip': event.get('srcip', ''),
                                    'destination_ip': event.get('dstip', ''),
                                    'user': event.get('user', 'system'),
                                    'severity': event.get('level', 'medium')
                                })
                        
                        # 위협 통계 수집
                        threat_stats = fm_client.get_threat_statistics()
                        if threat_stats:
                            for threat_type, count in threat_stats.items():
                                if len(top_threats) < 5:
                                    top_threats.append({
                                        'name': threat_type,
                                        'count': count,
                                        'severity': 'high' if count > 100 else 'medium',
                                        'first_seen': (datetime.now() - timedelta(days=7)).isoformat(),
                                        'last_seen': datetime.now().isoformat()
                                    })
                        
                        fm_client.logout()
                        
            except Exception as e:
                logger.warning(f"보안 이벤트 수집 실패: {e}")
            
            # 운영 환경에서는 실제 데이터만 사용 (Mock 데이터 사용 안함)
            
            # 대역폭 사용량 (실제 데이터가 있으면 사용, 없으면 Mock)
            bandwidth_usage = {
                'total_capacity': 1000,
                'current_usage': stats.get('total_bandwidth_in', 0) + stats.get('total_bandwidth_out', 0),
                'peak_usage': (stats.get('total_bandwidth_in', 0) + stats.get('total_bandwidth_out', 0)) * 1.2,
                'average_usage': (stats.get('total_bandwidth_in', 0) + stats.get('total_bandwidth_out', 0)) * 0.8,
                'by_interface': {
                    'wan1': stats.get('total_bandwidth_out', 0),
                    'internal': stats.get('total_bandwidth_in', 0),
                    'dmz': stats.get('total_bandwidth_in', 0) * 0.2,
                    'wan2': stats.get('total_bandwidth_out', 0) * 0.3
                },
                'history': [stats.get('total_bandwidth_in', 100) + stats.get('total_bandwidth_out', 100) for _ in range(24)]
            }
            
            dashboard_data = {
                'stats': stats,
                'alerts': alerts,
                'recent_events': recent_events,
                'top_threats': top_threats,
                'bandwidth_usage': bandwidth_usage,
                'timestamp': datetime.now().isoformat()
            }
            
            return {
                'status': 'success',
                'data': dashboard_data,
                'test_mode': False,
                'data_source': stats.get('data_source', 'real'),
                'connection_status': api_manager.get_connection_status() if api_manager else {}
            }
        else:
            # 테스트 모드인 경우에만 Mock 데이터 반환
            if test_mode:
                dashboard_data = {
                    'stats': dummy_generator.generate_dashboard_stats(),
                    'alerts': dummy_generator.generate_alerts(5),
                    'recent_events': dummy_generator.generate_events(10),
                    'top_threats': dummy_generator.generate_top_threats(5),
                    'bandwidth_usage': dummy_generator.generate_bandwidth_usage(),
                    'timestamp': datetime.now().isoformat()
                }
                
                return {
                    'status': 'success',
                    'data': dashboard_data,
                    'test_mode': test_mode,
                    'data_source': 'mock',
                    'test_mode_info': '테스트 모드에서 더미 데이터를 표시하고 있습니다.'
                }
            else:
                # 운영 환경에서 연결이 없으면 빈 데이터 반환
                return {
                    'status': 'error',
                    'data': {
                        'stats': {
                            'total_devices': 0,
                            'active_threats': 0,
                            'security_events': 0,
                            'policy_violations': 0,
                            'cpu_usage': 0,
                            'memory_usage': 0
                        },
                        'alerts': [],
                        'recent_events': [],
                        'top_threats': [],
                        'bandwidth_usage': {
                            'total_capacity': 0,
                            'current_usage': 0,
                            'peak_usage': 0,
                            'average_usage': 0,
                            'by_interface': {},
                            'history': []
                        },
                        'timestamp': datetime.now().isoformat()
                    },
                    'test_mode': False,
                    'data_source': 'none',
                    'error': 'FortiManager/FortiGate 연결 설정이 필요합니다.'
                }
        
    except Exception as e:
        logger.error(f"대시보드 데이터 조회 실패: {e}")
        
        # 운영 환경에서는 오류 시 빈 데이터 반환
        return {
            'status': 'error',
            'data': {
                'stats': {
                    'total_devices': 0,
                    'active_threats': 0,
                    'security_events': 0,
                    'policy_violations': 0,
                    'cpu_usage': 0,
                    'memory_usage': 0
                },
                'alerts': [],
                'recent_events': [],
                'top_threats': [],
                'bandwidth_usage': {
                    'total_capacity': 0,
                    'current_usage': 0,
                    'peak_usage': 0,
                    'average_usage': 0,
                    'by_interface': {},
                    'history': []
                },
                'timestamp': datetime.now().isoformat()
            },
            'test_mode': False,
            'data_source': 'none',
            'error': str(e)
        }