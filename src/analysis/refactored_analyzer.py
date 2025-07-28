"""
리팩토링된 방화벽 규칙 분석기

기존의 거대한 FirewallRuleAnalyzer를 컴포넌트별로 분리하여 재구성한 메인 클래스입니다.
단일 책임 원칙을 따라 각 컴포넌트가 특정 기능을 담당하도록 설계되었습니다.
"""

from utils.unified_logger import setup_logger

from .components import (DataLoader, PathTracer, PolicyAnalyzer, RuleValidator,
                         SessionManager)

logger = setup_logger("refactored_analyzer")

   class RefactoredFirewallAnalyzer:
        """
    리팩토링된 방화벽 규칙 분석기

    기존의 거대한 단일 클래스를 여러 컴포넌트로 분리하여
    유지보수성과 테스트 가능성을 향상시킨 클래스입니다.
    """

    def __init__(self, fortigate_client=None, fortimanager_client=None):
        """
        분석기 초기화

        Args:
            fortigate_client: FortiGate API 클라이언트
            fortimanager_client: FortiManager API 클라이언트
        """
        self.logger = logger

        # 컴포넌트 초기화
        self.data_loader = DataLoader(fortigate_client, fortimanager_client)
           self.rule_validator = RuleValidator(self.data_loader)
            self.policy_analyzer = PolicyAnalyzer(
                                                  self.data_loader, self.rule_validator)
            self.path_tracer = PathTracer(self.data_loader)
            self.session_manager = SessionManager()

        # 호환성을 위한 레거시 속성
            self.fortigate_client = fortigate_client
        self.fortimanager_client = fortimanager_client

    def load_data(self, firewall_id="default"):
        """
        특정 방화벽의 데이터 로드

        Args:
            firewall_id (str): 방화벽 식별자

                Returns:
            bool: 데이터 로드 성공 여부
        """
        return self.data_loader.load_firewall_data(firewall_id)

           def load_all_firewalls(self):
                """
        FortiManager를 통해 모든 방화벽 장치의 데이터 로드

        Returns:
            bool: 데이터 로드 성공 여부
        """
        return self.data_loader.load_all_firewalls()

           def analyze_traffic(
                               self,
                                   src_ip,
                    dst_ip,
                    dst_port,
                    protocol="tcp",
                    firewall_id="default",
                    session_id=None,
                    ):
        """
        트래픽 분석 수행

        Args:
            src_ip (str): 소스 IP 주소
                dst_ip (str): 목적지 IP 주소
                dst_port (int): 목적지 포트
                protocol (str): 프로토콜
                firewall_id (str): 방화벽 식별자
                session_id (str, optional): 세션 ID

                Returns:
            dict: 분석 결과
        """
        try:
            # 정책 분석
            policy_result = self.policy_analyzer.analyze_traffic(
                                                                 src_ip, dst_ip, dst_port, protocol, firewall_id)

            # 경로 추적
               path_result = self.path_tracer.trace_packet_path(src_ip, dst_ip, firewall_id)

            # 결합된 결과 생성
                combined_result = {
                    "firewall_id": firewall_id,
                        "traffic": {
                        "src_ip": src_ip,
                            "dst_ip": dst_ip,
                                "dst_port": dst_port,
                                "protocol": protocol,
                                },
                                "policy_analysis": policy_result,
                                        "path_analysis": path_result,
                                            "timestamp": self._get_timestamp(),
                                                                         }

            # 세션에 결과 저장
            if session_id:
                self.session_manager.store_analysis_result(
                                                           session_id, "traffic_analysis", combined_result)

                   self.logger.info(f"트래픽 분석 완료: {src_ip} -> {dst_ip}:{dst_port}")
                return combined_result

        except Exception as e:
            self.logger.error(f"트래픽 분석 중 오류: {str(e)}")
               return {
                   "firewall_id": firewall_id,
                    "error": str(e),
                                 "timestamp": self._get_timestamp(),
                                                     }

    def analyze_policy_conflicts(self, firewall_id="default", session_id=None):
        """
        정책 충돌 분석

        Args:
            firewall_id (str): 방화벽 식별자
                session_id (str, optional): 세션 ID

                Returns:
            dict: 충돌 분석 결과
        """
        try:
            conflicts = self.policy_analyzer.analyze_policy_conflicts(
                                                                      firewall_id)

               _result = {
                   "firewall_id": firewall_id,
                    "conflicts": conflicts,
                        "conflict_count": len(conflicts),
                                              "timestamp": self._get_timestamp(),
                                                     }

            # 세션에 결과 저장
            if session_id:
                self.session_manager.store_analysis_result(
                                                           session_id, "policy_conflict_analysis", result)

                   self.logger.info(f"정책 충돌 분석 완료: {firewall_id} - {len(conflicts)}개 충돌 발견")
                return _result

        except Exception as e:
            self.logger.error(f"정책 충돌 분석 중 오류: {str(e)}")
               return {
                   "firewall_id": firewall_id,
                    "error": str(e),
                                 "timestamp": self._get_timestamp(),
                                                     }

    def analyze_routing_loops(self, firewall_id="default", session_id=None):
        """
        라우팅 루프 분석

        Args:
            firewall_id (str): 방화벽 식별자
                session_id (str, optional): 세션 ID

                Returns:
            dict: 라우팅 루프 분석 결과
        """
        try:
            loops = self.path_tracer.analyze_routing_loops(firewall_id)

               _result = {
                   "firewall_id": firewall_id,
                    "loops": loops,
                        "loop_count": len(loops),
                                          "timestamp": self._get_timestamp(),
                                                     }

            # 세션에 결과 저장
            if session_id:
                self.session_manager.store_analysis_result(
                                                           session_id, "routing_loop_analysis", result)

                   self.logger.info(f"라우팅 루프 분석 완료: {firewall_id} - {len(loops)}개 루프 발견")
                return _result

        except Exception as e:
            self.logger.error(f"라우팅 루프 분석 중 오류: {str(e)}")
               return {
                   "firewall_id": firewall_id,
                    "error": str(e),
                                 "timestamp": self._get_timestamp(),
                                                     }

    def get_interface_statistics(self, firewall_id="default"):
        """
        인터페이스 통계 정보 조회

        Args:
            firewall_id (str): 방화벽 식별자

                Returns:
            dict: 인터페이스 통계
        """
        return self.path_tracer.get_interface_statistics(firewall_id)

           def create_analysis_session(self, user_id=None, session_name=None):
                """
        분석 세션 생성

        Args:
            user_id (str, optional): 사용자 ID
                session_name (str, optional): 세션 이름

                Returns:
            str: 세션 ID
        """
        return self.session_manager.create_session(user_id, session_name)

           def get_analysis_history(self, session_id, analysis_type=None, limit=50):
                """
        분석 이력 조회

        Args:
            session_id (str): 세션 ID
                analysis_type (str, optional): 분석 유형
                limit (int): 조회 제한

                Returns:
            list: 분석 이력
        """
        return self.session_manager.get_analysis_history(
                                                         session_id, analysis_type, limit)

           def get_comprehensive_analysis(self, firewall_id="default", session_id=None):
                """
        종합 분석 수행

        Args:
            firewall_id (str): 방화벽 식별자
                session_id (str, optional): 세션 ID

                Returns:
            dict: 종합 분석 결과
        """
        try:
            # 정책 충돌 분석
            policy_conflicts = self.policy_analyzer.analyze_policy_conflicts(
                                                                             firewall_id)

            # 라우팅 루프 분석
               routing_loops = self.path_tracer.analyze_routing_loops(firewall_id)

            # 인터페이스 통계
                interface_stats = self.path_tracer.get_interface_statistics(
                                                                            firewall_id)

            # 종합 결과 생성
                _result = {
                    "firewall_id": firewall_id,
                        "summary": {
                        "policy_conflicts": len(policy_conflicts),
                                                    "routing_loops": len(routing_loops),
                                                        "interfaces": len(interface_stats),
                                                     },
                                                  "policy_conflicts": policy_conflicts,
                        "routing_loops": routing_loops,
                        "interface_statistics": interface_stats,
                        "timestamp": self._get_timestamp(),
                                                     }

            # 세션에 결과 저장
            if session_id:
                self.session_manager.store_analysis_result(
                                                           session_id, "comprehensive_analysis", result)

                   self.logger.info(f"종합 분석 완료: {firewall_id}")
                return _result

        except Exception as e:
            self.logger.error(f"종합 분석 중 오류: {str(e)}")
               return {
                   "firewall_id": firewall_id,
                    "error": str(e),
                                 "timestamp": self._get_timestamp(),
                                                     }

    def _get_timestamp(self):
        """현재 타임스탬프 반환"""

        import time

        return time.time()

    # 호환성을 위한 레거시 메서드들

           def is_ip_in_address_object(self, ip, address_obj, firewall_id="default"):
                """레거시 호환성: IP 주소 객체 확인"""
        return self.rule_validator.is_ip_in_address_object(
                                                           ip, address_obj, firewall_id)

           def is_ip_in_address_group(self, ip, group_name, firewall_id="default"):
                """레거시 호환성: IP 주소 그룹 확인"""
        return self.rule_validator.is_ip_in_address_group(
                                                          ip, group_name, firewall_id)

           def is_port_in_service_object(self, port, protocol, service_obj, firewall_id="default"):
                """레거시 호환성: 포트 서비스 객체 확인"""
        return self.rule_validator.is_port_in_service_object(
                                                             port, protocol, service_obj, firewall_id)

           def is_port_in_service_group(self, port, protocol, group_name, firewall_id="default"):
                """레거시 호환성: 포트 서비스 그룹 확인"""
        return self.rule_validator.is_port_in_service_group(
                                                            port, protocol, group_name, firewall_id)
