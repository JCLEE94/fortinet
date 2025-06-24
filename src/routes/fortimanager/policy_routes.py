"""
FortiManager 정책 관리 라우트

방화벽 정책 조회, 생성, 수정, 삭제 및 패킷 경로 분석 등 정책 관련 기능을 담당합니다.
"""

from flask import Blueprint, jsonify, request
from src.utils.unified_cache_manager import cached
from src.utils.security import rate_limit
from src.utils.api_helper import get_data_source, is_test_mode, get_api_manager, get_dummy_generator
from src.utils.unified_logger import setup_logger
from src.analysis.refactored_analyzer import RefactoredFirewallAnalyzer

logger = setup_logger('policy_routes')
policy_bp = Blueprint('policies', __name__, url_prefix='/policies')


@policy_bp.route('/', methods=['GET'])
@cached(ttl=180)
def get_policies():
    """방화벽 정책 목록 조회"""
    try:
        device_id = request.args.get('device_id', 'default')
        adom = request.args.get('adom', 'root')
        
        if is_test_mode():
            dummy_generator = get_dummy_generator()
            policies = dummy_generator.generate_firewall_policies(device_id)
            return jsonify({
                'policies': policies,
                'total': len(policies),
                'device_id': device_id,
                'mode': 'test'
            })
        
        api_manager = get_api_manager()
        fm_client = api_manager.get_fortimanager_client()
        
        if not fm_client:
            return jsonify({'error': 'FortiManager client not available'}), 503
        
        policies = fm_client.get_firewall_policies(device_id, adom)
        return jsonify({
            'policies': policies or [],
            'total': len(policies) if policies else 0,
            'device_id': device_id,
            'adom': adom,
            'mode': 'production'
        })
        
    except Exception as e:
        logger.error(f"정책 목록 조회 중 오류: {str(e)}")
        return jsonify({'error': str(e)}), 500


@policy_bp.route('/', methods=['POST'])
@rate_limit(max_requests=10, window=60)
def create_policy():
    """새 방화벽 정책 생성"""
    try:
        policy_data = request.get_json()
        
        if not policy_data:
            return jsonify({'error': 'Policy data is required'}), 400
        
        device_id = policy_data.get('device_id', 'default')
        adom = policy_data.get('adom', 'root')
        
        if is_test_mode():
            # 테스트 모드에서는 mock 응답 반환
            return jsonify({
                'success': True,
                'policy_id': f"test_policy_{hash(str(policy_data)) % 10000}",
                'message': 'Policy created successfully (test mode)',
                'mode': 'test'
            })
        
        api_manager = get_api_manager()
        fm_client = api_manager.get_fortimanager_client()
        
        if not fm_client:
            return jsonify({'error': 'FortiManager client not available'}), 503
        
        result = fm_client.create_firewall_policy(policy_data, adom)
        if result:
            return jsonify({
                'success': True,
                'policy_id': result.get('policyid'),
                'message': 'Policy created successfully',
                'mode': 'production'
            })
        else:
            return jsonify({'error': 'Failed to create policy'}), 500
        
    except Exception as e:
        logger.error(f"정책 생성 중 오류: {str(e)}")
        return jsonify({'error': str(e)}), 500


@policy_bp.route('/<policy_id>', methods=['PUT'])
@rate_limit(max_requests=15, window=60)
def update_policy(policy_id):
    """방화벽 정책 수정"""
    try:
        policy_data = request.get_json()
        
        if not policy_data:
            return jsonify({'error': 'Policy data is required'}), 400
        
        device_id = policy_data.get('device_id', 'default')
        adom = policy_data.get('adom', 'root')
        
        if is_test_mode():
            return jsonify({
                'success': True,
                'policy_id': policy_id,
                'message': 'Policy updated successfully (test mode)',
                'mode': 'test'
            })
        
        api_manager = get_api_manager()
        fm_client = api_manager.get_fortimanager_client()
        
        if not fm_client:
            return jsonify({'error': 'FortiManager client not available'}), 503
        
        result = fm_client.update_firewall_policy(policy_id, policy_data, adom)
        if result:
            return jsonify({
                'success': True,
                'policy_id': policy_id,
                'message': 'Policy updated successfully',
                'mode': 'production'
            })
        else:
            return jsonify({'error': 'Failed to update policy'}), 500
        
    except Exception as e:
        logger.error(f"정책 수정 중 오류 ({policy_id}): {str(e)}")
        return jsonify({'error': str(e)}), 500


@policy_bp.route('/<policy_id>', methods=['DELETE'])
@rate_limit(max_requests=5, window=60)
def delete_policy(policy_id):
    """방화벽 정책 삭제"""
    try:
        adom = request.args.get('adom', 'root')
        
        if is_test_mode():
            return jsonify({
                'success': True,
                'policy_id': policy_id,
                'message': 'Policy deleted successfully (test mode)',
                'mode': 'test'
            })
        
        api_manager = get_api_manager()
        fm_client = api_manager.get_fortimanager_client()
        
        if not fm_client:
            return jsonify({'error': 'FortiManager client not available'}), 503
        
        result = fm_client.delete_firewall_policy(policy_id, adom)
        if result:
            return jsonify({
                'success': True,
                'policy_id': policy_id,
                'message': 'Policy deleted successfully',
                'mode': 'production'
            })
        else:
            return jsonify({'error': 'Failed to delete policy'}), 500
        
    except Exception as e:
        logger.error(f"정책 삭제 중 오류 ({policy_id}): {str(e)}")
        return jsonify({'error': str(e)}), 500


@policy_bp.route('/analyze-packet-path', methods=['POST'])
@rate_limit(max_requests=30, window=60)
def analyze_packet_path():
    """패킷 경로 분석"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        src_ip = data.get('src_ip')
        dst_ip = data.get('dst_ip')
        dst_port = data.get('port', 80)
        protocol = data.get('protocol', 'tcp').lower()
        device_id = data.get('device_id', 'default')
        
        if not src_ip or not dst_ip:
            return jsonify({'error': 'src_ip and dst_ip are required'}), 400
        
        if is_test_mode():
            # 테스트 모드에서는 mock 분석 결과 반환
            dummy_generator = get_dummy_generator()
            analysis_result = dummy_generator.generate_packet_analysis(
                src_ip, dst_ip, dst_port, protocol
            )
            return jsonify({
                'analysis': analysis_result,
                'mode': 'test'
            })
        
        # 리팩토링된 분석기 사용
        api_manager = get_api_manager()
        fm_client = api_manager.get_fortimanager_client()
        fg_client = api_manager.get_fortigate_client()
        
        analyzer = RefactoredFirewallAnalyzer(fg_client, fm_client)
        
        # 데이터 로드
        if not analyzer.load_data(device_id):
            return jsonify({'error': 'Failed to load firewall data'}), 500
        
        # 트래픽 분석 수행
        analysis_result = analyzer.analyze_traffic(
            src_ip, dst_ip, dst_port, protocol, device_id
        )
        
        return jsonify({
            'analysis': analysis_result,
            'mode': 'production'
        })
        
    except Exception as e:
        logger.error(f"패킷 경로 분석 중 오류: {str(e)}")
        return jsonify({'error': str(e)}), 500


@policy_bp.route('/conflicts', methods=['GET'])
@cached(ttl=300)
def analyze_policy_conflicts():
    """정책 충돌 분석"""
    try:
        device_id = request.args.get('device_id', 'default')
        
        if is_test_mode():
            dummy_generator = get_dummy_generator()
            conflicts = dummy_generator.generate_policy_conflicts(device_id)
            return jsonify({
                'conflicts': conflicts,
                'device_id': device_id,
                'mode': 'test'
            })
        
        # 리팩토링된 분석기 사용
        api_manager = get_api_manager()
        fm_client = api_manager.get_fortimanager_client()
        fg_client = api_manager.get_fortigate_client()
        
        analyzer = RefactoredFirewallAnalyzer(fg_client, fm_client)
        
        # 데이터 로드
        if not analyzer.load_data(device_id):
            return jsonify({'error': 'Failed to load firewall data'}), 500
        
        # 정책 충돌 분석
        conflicts_result = analyzer.analyze_policy_conflicts(device_id)
        
        return jsonify({
            'conflicts': conflicts_result,
            'device_id': device_id,
            'mode': 'production'
        })
        
    except Exception as e:
        logger.error(f"정책 충돌 분석 중 오류: {str(e)}")
        return jsonify({'error': str(e)}), 500


@policy_bp.route('/topology', methods=['GET'])
@cached(ttl=240)
def get_network_topology():
    """네트워크 토폴로지 정보 조회"""
    try:
        device_id = request.args.get('device_id', 'default')
        
        if is_test_mode():
            dummy_generator = get_dummy_generator()
            topology = dummy_generator.generate_network_topology(device_id)
            return jsonify({
                'topology': topology,
                'device_id': device_id,
                'mode': 'test'
            })
        
        api_manager = get_api_manager()
        fm_client = api_manager.get_fortimanager_client()
        
        if not fm_client:
            return jsonify({'error': 'FortiManager client not available'}), 503
        
        topology = fm_client.get_network_topology(device_id)
        return jsonify({
            'topology': topology or {},
            'device_id': device_id,
            'mode': 'production'
        })
        
    except Exception as e:
        logger.error(f"네트워크 토폴로지 조회 중 오류: {str(e)}")
        return jsonify({'error': str(e)}), 500