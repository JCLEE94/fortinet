"""
Main routes for pages
"""
from flask import Blueprint, render_template, current_app
import os
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """홈페이지 - 원래 Nextrade 대시보드로 리다이렉트"""
    from flask import redirect, url_for
    return redirect(url_for('main.dashboard'))

@main_bp.route('/policy-analysis')
def policy_analysis():
    """FortiGate 정책 분석 페이지 (기존 index.html)"""
    return render_template('index.html')

@main_bp.route('/batch')
def batch():
    return render_template('batch.html')

@main_bp.route('/topology')
def topology():
    return render_template('topology.html')

@main_bp.route('/compliance')
def compliance():
    return render_template('compliance.html')

@main_bp.route('/logs')
def logs_management():
    """로그 관리 페이지"""
    return render_template('logs.html')

@main_bp.route('/logs/live')
def live_logs():
    """실시간 로그 스트리밍 페이지"""
    return render_template('live_logs.html')

@main_bp.route('/batch/results')
def batch_results():
    """배치 분석 결과 페이지"""
    from flask import session
    from src.config.batch_defaults import get_default_batch_results
    
    # 세션에서 배치 분석 결과 가져오기
    results = session.get('batch_results')
    
    if not results:
        # 기본 예시 데이터 사용
        results = get_default_batch_results()
    
    return render_template('batch_results.html', results=results)

@main_bp.route('/devices')
def devices():
    """장치 목록 페이지"""
    from src.config.device_defaults import get_device_config
    
    # 장치 관리 설정 로드
    device_config = get_device_config()
    
    return render_template('devices.html', config=device_config)

@main_bp.route('/packet_sniffer')
def packet_sniffer():
    return render_template('packet_sniffer.html')

@main_bp.route('/settings')
def settings():
    # 설정 페이지
    return render_template('settings.html')

@main_bp.route('/monitoring')
def monitoring():
    return render_template('dashboard.html')

@main_bp.route('/text-overflow-test')
def text_overflow_test():
    # 텍스트 오버플로우 테스트를 위한 샘플 데이터
    sample_data = {
        'long_text': 'This is a very long text that might overflow in certain UI elements. ' * 10,
        'items': [
            {'name': 'Item ' + str(i), 'description': 'Description ' * 5} 
            for i in range(1, 11)
        ]
    }
    return render_template('text_overflow_test.html', **sample_data)

@main_bp.route('/dashboard/modern')
def dashboard_modern():
    return render_template('dashboard_modern.html')

@main_bp.route('/dashboard')
def dashboard():
    """대시보드 페이지"""
    from src.api.integration.api_integration import APIIntegrationManager
    from src.mock.data_generator import DummyDataGenerator
    from src.config.unified_settings import unified_settings
    from src.config.dashboard_defaults import get_dashboard_config, generate_mock_alerts
    
    # 대시보드 설정 로드
    dashboard_config = get_dashboard_config()
    
    try:
        # 실제 FortiManager 연결 시도
        api_manager = APIIntegrationManager(unified_settings.get_api_config())
        api_manager.initialize_connections()
        
        fm_client = api_manager.get_fortimanager_client()
        if fm_client and fm_client.login():
            devices = api_manager.get_all_devices()
            data = {
                'devices': devices,
                'connection_status': api_manager.get_connection_status(),
                'stats': {
                    'total_devices': len(devices),
                    'uptime_percentage': dashboard_config['stats']['uptime_percentage'],
                    'network_traffic': dashboard_config['stats']['network_traffic'],
                    'active_alerts': dashboard_config['stats']['active_alerts']
                },
                'alerts': generate_mock_alerts(dashboard_config['stats']['active_alerts'])
            }
        else:
            # 연결 실패 시 더미 데이터 사용
            dummy_generator = DummyDataGenerator()
            data = {
                'stats': dummy_generator.generate_dashboard_stats(),
                'devices': dummy_generator.generate_devices(
                    dashboard_config['device_list']['top_devices_limit'] * 2
                ),
                'events': dummy_generator.generate_security_events(
                    dashboard_config['security_events']['max_events_display']
                ),
                'alerts': generate_mock_alerts(dashboard_config['stats']['active_alerts'])
            }
            
    except Exception as e:
        print(f"Dashboard error: {e}")
        # 오류 발생 시 더미 데이터 사용
        dummy_generator = DummyDataGenerator()
        data = {
            'stats': dummy_generator.generate_dashboard_stats(),
            'devices': dummy_generator.generate_devices(
                dashboard_config['device_list']['top_devices_limit'] * 2
            ),
            'events': dummy_generator.generate_security_events(
                dashboard_config['security_events']['max_events_display']
            ),
            'alerts': generate_mock_alerts(dashboard_config['stats']['active_alerts'])
        }
    
    # 대시보드 설정도 템플릿에 전달
    data['config'] = dashboard_config
    
    return render_template('dashboard.html', data=data)

@main_bp.route('/result')
def result():
    """분석 결과 페이지"""
    from flask import request, session
    from src.config.result_defaults import get_default_result
    
    # 세션에서 분석 결과 가져오기 (분석 후 리다이렉트된 경우)
    data = session.get('analysis_result')
    
    if not data:
        # 기본 예시 데이터 사용
        data = get_default_result()
    
    return render_template('result.html', data=data)

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/policy-scenarios')
def policy_scenarios():
    """정책 분석 시나리오 페이지"""
    return render_template('policy_scenarios.html')

@main_bp.route('/help')
def help():
    return render_template('help.html')

@main_bp.route('/offline.html')
def offline():
    return render_template('offline.html')