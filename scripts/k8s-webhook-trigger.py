#!/usr/bin/env python3
"""
K8s 이미지 업데이트 Webhook 서버
CI/CD에서 이 엔드포인트를 호출하면 즉시 K8s deployment를 업데이트합니다.
"""

from flask import Flask, request, jsonify
import subprocess
import logging
import os
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 설정
NAMESPACE = os.getenv('K8S_NAMESPACE', 'fortinet')
DEPLOYMENT = os.getenv('K8S_DEPLOYMENT', 'fortinet')
SECRET_TOKEN = os.getenv('WEBHOOK_SECRET', 'MySuperSecretToken12345')
PORT = int(os.getenv('WEBHOOK_PORT', '9301'))

@app.route('/health', methods=['GET'])
def health():
    """헬스 체크 엔드포인트"""
    return jsonify({
        'status': 'healthy',
        'service': 'k8s-image-updater',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/webhook/update', methods=['POST'])
def update_deployment():
    """Deployment 업데이트 트리거"""
    
    # 토큰 검증
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized'}), 401
    
    token = auth_header.split(' ')[1]
    if token != SECRET_TOKEN:
        return jsonify({'error': 'Invalid token'}), 401
    
    # 요청 데이터 파싱
    data = request.get_json() or {}
    image = data.get('image')
    force = data.get('force', True)
    
    logger.info(f"Update request received - Image: {image}, Force: {force}")
    
    try:
        # kubectl rollout restart 실행
        cmd = f"kubectl rollout restart deployment/{DEPLOYMENT} -n {NAMESPACE}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Failed to restart deployment: {result.stderr}")
            return jsonify({
                'status': 'error',
                'message': result.stderr
            }), 500
        
        # 롤아웃 상태 확인
        cmd_status = f"kubectl rollout status deployment/{DEPLOYMENT} -n {NAMESPACE} --timeout=5m"
        result_status = subprocess.run(cmd_status, shell=True, capture_output=True, text=True)
        
        return jsonify({
            'status': 'success',
            'message': 'Deployment updated successfully',
            'deployment': f"{NAMESPACE}/{DEPLOYMENT}",
            'timestamp': datetime.utcnow().isoformat(),
            'rollout_status': result_status.stdout
        })
        
    except Exception as e:
        logger.error(f"Error updating deployment: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/webhook/status', methods=['GET'])
def get_status():
    """Deployment 상태 확인"""
    try:
        cmd = f"kubectl get deployment {DEPLOYMENT} -n {NAMESPACE} -o json"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            return jsonify({'error': result.stderr}), 500
        
        import json
        deployment = json.loads(result.stdout)
        
        return jsonify({
            'name': deployment['metadata']['name'],
            'namespace': deployment['metadata']['namespace'],
            'replicas': deployment['status']['replicas'],
            'ready_replicas': deployment['status'].get('readyReplicas', 0),
            'updated_replicas': deployment['status'].get('updatedReplicas', 0),
            'image': deployment['spec']['template']['spec']['containers'][0]['image']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info(f"Starting K8s Image Updater Webhook on port {PORT}")
    app.run(host='0.0.0.0', port=PORT)