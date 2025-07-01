"""
Main routes for pages
"""
from flask import Blueprint, render_template, current_app
import os
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
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
    # 더미 결과 데이터 생성
    sample_results = [
        {
            'src_ip': '192.168.1.10',
            'dst_ip': '10.0.0.50',
            'port': 443,
            'protocol': 'tcp',
            'status': 'Allowed',
            'path_length': 3,
            'path_data': {
                'allowed': True,
                'path': [
                    {
                        'firewall_name': 'FortiGate-HQ-01',
                        'policy_id': '101',
                        'src_ip': '192.168.1.10',
                        'dst_ip': '10.0.0.50',
                        'action': 'accept'
                    }
                ]
            }
        },
        {
            'src_ip': '172.16.10.20',
            'dst_ip': '8.8.8.8',
            'port': 80,
            'protocol': 'tcp',
            'status': 'Blocked',
            'blocked_by': {
                'firewall': 'FortiGate-DMZ-01',
                'policy_id': '202'
            },
            'path_data': {
                'allowed': False,
                'blocked_by': {
                    'firewall_name': 'FortiGate-DMZ-01',
                    'policy_id': '202'
                },
                'path': [
                    {
                        'firewall_name': 'FortiGate-DMZ-01',
                        'policy_id': '202',
                        'src_ip': '172.16.10.20',
                        'dst_ip': '8.8.8.8',
                        'action': 'deny'
                    }
                ]
            }
        }
    ]
    
    return render_template('batch_results.html', results=sample_results)

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
    import time
    from src.api.integration.api_integration import APIIntegrationManager
    from src.mock.data_generator import DummyDataGenerator
    from src.config.unified_settings import unified_settings
    from src.config.dashboard_defaults import get_dashboard_config, generate_mock_alerts
    
    # 대시보드 설정 로드
    dashboard_config = get_dashboard_config()
    
    try:
        # 테스트 모드인지 확인
        if unified_settings.is_test_mode():
            # 더미 데이터 사용
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
        else:
            # 실제 FortiManager 연결 시도
            api_manager = APIIntegrationManager(unified_settings.get_api_config())
            api_manager.initialize_connections()
            
            fm_client = api_manager.get_fortimanager_client()
            if fm_client and fm_client.login():
                data = {
                    'devices': api_manager.get_all_devices(),
                    'connection_status': api_manager.get_connection_status(),
                    'stats': {
                        'total_devices': len(api_manager.get_all_devices()),
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
    # 분석 결과 데이터 제공 (템플릿이 기대하는 형식)
    data = {
        'allowed': True,
        'src_ip': '192.168.1.10',
        'dst_ip': '10.0.0.50',
        'port': 443,
        'protocol': 'tcp',
        'path': [
            {
                'firewall_name': 'FortiGate-HQ-01',
                'policy_id': '101',
                'action': 'accept',
                'src_zone': 'internal',
                'dst_zone': 'dmz'
            }
        ],
        'summary': {
            'source_ip': '192.168.1.10',
            'destination_ip': '10.0.0.50',
            'total_hops': 3,
            'port': 443,
            'protocol': 'tcp'
        },
        'path': [
            {
                'firewall_name': 'FortiGate-HQ-01',
                'policy_id': '101',
                'action': 'accept',
                'src_ip': '192.168.1.10',
                'dst_ip': '10.0.0.50'
            }
        ]
    }
    return render_template('result.html', data=data)

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/help')
def help():
    return render_template('help.html')

@main_bp.route('/offline.html')
def offline():
    return render_template('offline.html')