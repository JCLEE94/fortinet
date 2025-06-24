#!/usr/bin/env python3
"""
FortiGate Nextrade 배포 후 자동 모니터링 스크립트
CLAUDE.md 지시사항에 따른 완전 자율적 모니터링 시스템
"""
import requests
import time
import os
import sys
import json
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/deployment_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DeploymentMonitor:
    def __init__(self):
        self.deploy_host = os.getenv('DEPLOY_HOST', 'localhost')
        self.deploy_port = os.getenv('DEPLOY_PORT', '7777')
        self.base_url = f"http://{self.deploy_host}:{self.deploy_port}"
        self.session = requests.Session()
        self.session.timeout = 10
        
        # 모니터링 설정
        self.check_interval = 30  # 30초마다 체크
        self.max_checks = 20  # 최대 20회 체크 (10분)
        self.critical_endpoints = [
            '/api/settings',
            '/api/system/stats', 
            '/api/devices',
            '/api/dashboard',
            '/api/fortimanager/status'
        ]
        
    def check_endpoint(self, endpoint):
        """개별 엔드포인트 상태 확인"""
        try:
            url = self.base_url + endpoint
            response = self.session.get(url)
            
            return {
                'endpoint': endpoint,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'success': response.status_code < 400,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'endpoint': endpoint,
                'error': str(e),
                'success': False,
                'timestamp': datetime.now().isoformat()
            }
    
    def run_health_check(self):
        """전체 헬스체크 실행"""
        results = []
        total_success = 0
        
        logger.info(f"🩺 헬스체크 시작 - {len(self.critical_endpoints)}개 엔드포인트 확인")
        
        for endpoint in self.critical_endpoints:
            result = self.check_endpoint(endpoint)
            results.append(result)
            
            if result['success']:
                total_success += 1
                logger.info(f"✅ {endpoint}: {result['status_code']} ({result.get('response_time', 0):.2f}s)")
            else:
                error_msg = result.get('error', f"HTTP {result.get('status_code', 'Unknown')}")
                logger.warning(f"❌ {endpoint}: {error_msg}")
        
        success_rate = (total_success / len(self.critical_endpoints)) * 100
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_endpoints': len(self.critical_endpoints),
            'successful': total_success,
            'success_rate': success_rate,
            'results': results
        }
    
    def detect_issues(self, health_check_result):
        """문제 상황 감지 및 분석"""
        issues = []
        
        if health_check_result['success_rate'] < 80:
            issues.append({
                'severity': 'high',
                'type': 'service_degradation',
                'message': f"서비스 성능 저하 감지 (성공률: {health_check_result['success_rate']:.1f}%)"
            })
        
        failed_endpoints = [r for r in health_check_result['results'] if not r['success']]
        if failed_endpoints:
            for endpoint_result in failed_endpoints:
                issues.append({
                    'severity': 'medium',
                    'type': 'endpoint_failure',
                    'endpoint': endpoint_result['endpoint'],
                    'error': endpoint_result.get('error', 'Unknown error')
                })
        
        # 응답 시간 체크
        slow_endpoints = [r for r in health_check_result['results'] 
                         if r['success'] and r.get('response_time', 0) > 5.0]
        if slow_endpoints:
            for endpoint_result in slow_endpoints:
                issues.append({
                    'severity': 'low',
                    'type': 'slow_response',
                    'endpoint': endpoint_result['endpoint'],
                    'response_time': endpoint_result['response_time']
                })
        
        return issues
    
    def auto_fix_attempt(self, issues):
        """자동 수정 시도 (CLAUDE.md 자율적 문제 해결)"""
        logger.info("🔧 자동 수정 시도 시작")
        
        high_severity_issues = [issue for issue in issues if issue['severity'] == 'high']
        
        if high_severity_issues:
            logger.warning("🚨 심각한 문제 감지 - 자동 복구 시도")
            
            # Docker 컨테이너 재시작 시도
            try:
                import subprocess
                logger.info("🔄 Docker 컨테이너 재시작 시도")
                
                # 원격 서버에서 컨테이너 재시작
                restart_cmd = f"""
                ssh -o StrictHostKeyChecking=no {os.getenv('DEPLOY_USER')}@{self.deploy_host} '
                    docker restart fortigate-nextrade || 
                    (docker stop fortigate-nextrade && docker start fortigate-nextrade)
                '
                """
                
                result = subprocess.run(restart_cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info("✅ 컨테이너 재시작 성공")
                    time.sleep(30)  # 재시작 후 대기
                    return True
                else:
                    logger.error(f"❌ 컨테이너 재시작 실패: {result.stderr}")
                    
            except Exception as e:
                logger.error(f"❌ 자동 수정 실패: {e}")
        
        return False
    
    def continuous_monitoring(self):
        """지속적 모니터링 실행"""
        logger.info(f"📊 연속 모니터링 시작 - {self.max_checks}회 확인 예정")
        
        monitoring_report = {
            'start_time': datetime.now().isoformat(),
            'checks': [],
            'total_issues': 0,
            'auto_fix_attempts': 0
        }
        
        for check_num in range(1, self.max_checks + 1):
            logger.info(f"📈 모니터링 체크 {check_num}/{self.max_checks}")
            
            # 헬스체크 실행
            health_result = self.run_health_check()
            monitoring_report['checks'].append(health_result)
            
            # 문제 감지
            issues = self.detect_issues(health_result)
            
            if issues:
                monitoring_report['total_issues'] += len(issues)
                logger.warning(f"⚠️ {len(issues)}개 문제 감지")
                
                for issue in issues:
                    logger.warning(f"  - {issue['severity'].upper()}: {issue['message'] if 'message' in issue else issue['type']}")
                
                # 자동 수정 시도
                if self.auto_fix_attempt(issues):
                    monitoring_report['auto_fix_attempts'] += 1
                    logger.info("🔧 자동 수정 시도 완료")
            else:
                logger.info("✅ 모든 시스템 정상")
            
            # 마지막 체크가 아니면 대기
            if check_num < self.max_checks:
                time.sleep(self.check_interval)
        
        monitoring_report['end_time'] = datetime.now().isoformat()
        
        # 모니터링 결과 요약
        self.generate_monitoring_summary(monitoring_report)
        
        return monitoring_report
    
    def generate_monitoring_summary(self, report):
        """모니터링 결과 요약 생성"""
        total_checks = len(report['checks'])
        successful_checks = sum(1 for check in report['checks'] if check['success_rate'] >= 80)
        
        logger.info("📊 모니터링 결과 요약:")
        logger.info(f"  - 총 체크 수: {total_checks}")
        logger.info(f"  - 성공 체크: {successful_checks}")
        logger.info(f"  - 성공률: {(successful_checks/total_checks)*100:.1f}%")
        logger.info(f"  - 감지된 문제: {report['total_issues']}")
        logger.info(f"  - 자동 수정 시도: {report['auto_fix_attempts']}")
        
        # 결과를 파일로 저장
        report_file = f"/tmp/monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 상세 리포트 저장: {report_file}")

def main():
    """메인 실행 함수"""
    monitor = DeploymentMonitor()
    
    try:
        # 초기 헬스체크
        logger.info("🚀 FortiGate Nextrade 배포 모니터링 시작")
        initial_check = monitor.run_health_check()
        
        if initial_check['success_rate'] >= 80:
            logger.info("✅ 초기 헬스체크 통과 - 연속 모니터링 시작")
            final_report = monitor.continuous_monitoring()
            
            # 최종 상태 확인
            if final_report['total_issues'] == 0:
                logger.info("🎉 모니터링 완료 - 모든 시스템 안정적으로 운영 중")
                sys.exit(0)
            else:
                logger.warning(f"⚠️ 모니터링 완료 - {final_report['total_issues']}개 문제 감지됨")
                sys.exit(1)
        else:
            logger.error(f"❌ 초기 헬스체크 실패 (성공률: {initial_check['success_rate']:.1f}%)")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"💥 모니터링 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()