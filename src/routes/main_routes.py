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
    return render_template('devices.html')

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
    from src.config.settings import Settings
    
    settings = Settings()
    fortimanager_config = settings.get_fortimanager_config()
    
    try:
        # 테스트 모드인지 확인
        if os.getenv('APP_MODE', '').lower() == 'test':
            # 더미 데이터 사용
            dummy_generator = DummyDataGenerator()
            data = {
                'stats': dummy_generator.generate_dashboard_stats(),
                'devices': dummy_generator.generate_devices(10),
                'events': dummy_generator.generate_security_events(10)
            }
        else:
            # 실제 FortiManager 연결 시도
            config_data = {
                'fortimanager': settings.fortimanager,
                'fortigate': settings.fortigate,
                'fortianalyzer': settings.fortianalyzer
            }
            api_manager = APIIntegrationManager(config_data)
            api_manager.initialize_connections()
            
            fm_client = api_manager.get_fortimanager_client()
            if fm_client and fm_client.login():
                data = {
                    'devices': api_manager.get_all_devices(),
                    'connection_status': api_manager.get_connection_status()
                }
            else:
                # 연결 실패 시 더미 데이터 사용
                dummy_generator = DummyDataGenerator()
                data = {
                    'stats': dummy_generator.generate_dashboard_stats(),
                    'devices': dummy_generator.generate_devices(10),
                    'events': dummy_generator.generate_security_events(10)
                }
                
    except Exception as e:
        print(f"Dashboard error: {e}")
        # 오류 발생 시 더미 데이터 사용
        dummy_generator = DummyDataGenerator()
        data = {
            'stats': dummy_generator.generate_dashboard_stats(),
            'devices': dummy_generator.generate_devices(10),
            'events': dummy_generator.generate_security_events(10)
        }
    
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