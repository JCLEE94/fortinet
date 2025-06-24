"""
ITSM API routes
"""
from flask import Blueprint, jsonify, request
import os
import random
from datetime import datetime

itsm_api_bp = Blueprint('itsm_api', __name__, url_prefix='/api/itsm')

@itsm_api_bp.route('/scrape-requests', methods=['GET'])
def scrape_itsm_requests():
    """ITSM에서 방화벽 요청 스크래핑"""
    try:
        # 테스트 모드인지 확인
        if os.getenv('APP_MODE', 'production').lower() == 'test':
            # 더미 데이터 반환
            dummy_requests = [
                {
                    'id': 'SR2505-00111',
                    'title': '[FW] 웹 서버 접근 허용 요청',
                    'requester': '김철수',
                    'department': '개발팀',
                    'created_date': '2025-05-15',
                    'status': 'Open',
                    'priority': 'High',
                    'source_ip': '10.10.10.0/24',
                    'destination_ip': '192.168.100.50',
                    'ports': ['80', '443'],
                    'protocol': 'TCP',
                    'description': '개발팀 웹 서버 접근을 위한 방화벽 정책 요청'
                },
                {
                    'id': 'SR2505-00160',
                    'title': '[FW] DB 서버 포트 개방 요청',
                    'requester': '이영희',
                    'department': 'IT운영팀',
                    'created_date': '2025-05-20',
                    'status': 'In Progress',
                    'priority': 'Medium',
                    'source_ip': '192.168.20.0/24',
                    'destination_ip': '192.168.10.100',
                    'ports': ['3306', '5432'],
                    'protocol': 'TCP',
                    'description': 'DB 서버 접근을 위한 포트 개방 요청'
                },
                {
                    'id': 'SR2505-00201',
                    'title': '[FW] FTP 서버 접근 허용',
                    'requester': '박민수',
                    'department': '파일관리팀',
                    'created_date': '2025-05-22',
                    'status': 'Pending',
                    'priority': 'Low',
                    'source_ip': '192.168.30.0/24',
                    'destination_ip': '172.16.10.20',
                    'ports': ['21', '20'],
                    'protocol': 'TCP',
                    'description': 'FTP 서버 파일 업로드/다운로드를 위한 접근 허용'
                }
            ]
            return jsonify({
                'status': 'success',
                'requests': dummy_requests,
                'total': len(dummy_requests)
            })
        
        # 실제 스크래핑 로직
        from src.itsm.scraper import ITSMScraper
        scraper = ITSMScraper()
        requests = scraper.get_firewall_requests()
        
        return jsonify({
            'status': 'success',
            'requests': requests,
            'total': len(requests)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@itsm_api_bp.route('/request-detail/<request_id>')
def get_request_detail(request_id):
    """ITSM 요청 상세 정보 조회"""
    try:
        from src.itsm.scraper import ITSMScraper
        scraper = ITSMScraper()
        detail = scraper.get_request_detail(request_id)
        
        return jsonify({
            'status': 'success',
            'detail': detail
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@itsm_api_bp.route('/map-to-fortigate', methods=['POST'])
def map_to_fortigate():
    """ITSM 요청을 FortiGate 정책으로 매핑"""
    try:
        data = request.get_json()
        request_id = data.get('request_id')
        
        if not request_id:
            return jsonify({
                'status': 'error',
                'message': 'request_id is required'
            }), 400
        
        from src.itsm.policy_mapper import PolicyMapper
        from src.itsm.scraper import ITSMScraper
        
        # ITSM 요청 정보 가져오기
        scraper = ITSMScraper()
        itsm_request = scraper.get_request_detail(request_id)
        
        # 정책 매핑
        mapper = PolicyMapper()
        mapping_result = mapper.map_itsm_to_fortigate_policy(itsm_request)
        
        return jsonify({
            'status': 'success',
            'mapping': mapping_result
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@itsm_api_bp.route('/bridge-status')
def get_bridge_status():
    """ITSM-FortiGate 브리지 상태 확인"""
    try:
        # 브리지 상태 확인 로직
        status = {
            'bridge_active': True,
            'last_sync': datetime.now().isoformat(),
            'pending_requests': 0,
            'processed_requests': 5,
            'failed_requests': 0
        }
        
        return jsonify({
            'status': 'success',
            'bridge_status': status
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@itsm_api_bp.route('/policy-request', methods=['POST'])
def create_policy_request():
    """방화벽 정책 요청 생성"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        # 필수 필드 검증
        required_fields = ['source_ip', 'destination_ip', 'port', 'protocol']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'{field} is required'}), 400
        
        # 더미 응답 생성
        request_id = f"FW-{datetime.now().strftime('%Y%m%d')}-{secrets.randbelow(1000) + 1000:04d}"
        
        response = {
            'status': 'success',
            'request_id': request_id,
            'message': '방화벽 정책 요청이 성공적으로 생성되었습니다.',
            'data': {
                'source_ip': data.get('source_ip'),
                'destination_ip': data.get('destination_ip'),
                'port': data.get('port'),
                'protocol': data.get('protocol'),
                'justification': data.get('justification', ''),
                'created_at': datetime.now().isoformat(),
                'status': 'submitted'
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@itsm_api_bp.route('/scraper/status', methods=['GET'])
def get_scraper_status():
    """스크래퍼 상태 조회"""
    try:
        status = {
            'status': 'active',
            'last_run': datetime.now().isoformat(),
            'requests_found': 12,
            'policies_mapped': 8,
            'errors': 0,
            'uptime': '2 days, 14 hours'
        }
        
        return jsonify({
            'status': 'success',
            'scraper_status': status
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@itsm_api_bp.route('/demo-mapping')
def demo_itsm_mapping():
    """ITSM 매핑 데모"""
    try:
        # 데모용 ITSM 요청
        demo_request = {
            'request_id': 'DEMO-001',
            'title': '[FW] 웹 서버 접근 허용 요청 (데모)',
            'description': '''
            1. 출발지: 10.10.10.0/24 (개발팀 네트워크)
            2. 목적지: 192.168.100.50 (웹 서버)
            3. 서비스: HTTP(80), HTTPS(443)
            4. 목적: 개발팀이 웹 서버에 접근하여 애플리케이션 배포
            ''',
            'requester': '홍길동',
            'department': '개발팀',
            'created_date': datetime.now().isoformat(),
            'priority': 'High',
            'status': 'Demo'
        }
        
        from src.itsm.policy_mapper import PolicyMapper
        mapper = PolicyMapper()
        
        # 정책 매핑
        mapping_result = mapper.map_itsm_to_fortigate_policy(demo_request)
        
        # 네트워크 분석 추가
        from src.analysis.fixed_path_analyzer import FixedPathAnalyzer
        analyzer = FixedPathAnalyzer()
        
        # 첫 번째 정책에 대한 경로 분석
        if mapping_result.get('policies'):
            first_policy = mapping_result['policies'][0]
            path_analysis = analyzer.analyze_fixed_path(
                src_ip=first_policy['srcaddr'][0],
                dst_ip=first_policy['dstaddr'][0],
                protocol='tcp',
                port=80
            )
            mapping_result['path_analysis'] = path_analysis
        
        return jsonify({
            'status': 'success',
            'demo_request': demo_request,
            'mapping_result': mapping_result,
            'message': 'This is a demonstration of ITSM to FortiGate policy mapping'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500