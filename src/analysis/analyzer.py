from utils.unified_logger import setup_logger

logger = setup_logger("analyzer")


class PolicyAnalyzer:
    """
    통합 정책 분석 클래스 - 여러 모듈로 분할됨

    이전 버전과의 호환성을 위한 래퍼 클래스입니다.
    실제 구현은 components 모듈에 분리되어 있습니다.
    """

    def __init__(self, data_loader=None, rule_validator=None):
        """Initialize PolicyAnalyzer with optional dependencies"""
        from .components.data_loader import DataLoader
        from .components.path_tracer import PathTracer
        from .components.policy_analyzer import \
            PolicyAnalyzer as PolicyAnalyzerComponent
        from .components.rule_validator import RuleValidator
        from .components.session_manager import SessionManager

        # Initialize components with defaults if not provided
        self.data_loader = data_loader or DataLoader()
        self.rule_validator = rule_validator or RuleValidator()
        self.policy_analyzer = PolicyAnalyzerComponent(
            self.data_loader, self.rule_validator
        )
        self.path_tracer = PathTracer(self.data_loader, self.policy_analyzer)
        self.session_manager = SessionManager(
            self.data_loader, self.policy_analyzer, self.path_tracer
        )
        self.logger = logger

        # Delegate methods
        self.load_fortigate_data = self.data_loader.load_fortigate_data
        self.load_fortimanager_data = self.data_loader.load_fortimanager_data
        self.analyze_packet_path = self.path_tracer.analyze_packet_path
        self.get_analysis_session = self.session_manager.get_analysis_session
        self.create_analysis_session = self.session_manager.create_analysis_session
        self.analyze_traffic = self.policy_analyzer.analyze_traffic
        self.find_matching_policy = self.policy_analyzer.find_matching_policy

    def validate_ip_in_range(self, ip, ip_range):
        """Delegate to rule validator"""
        return self.rule_validator.validate_ip_in_range(ip, ip_range)

    def validate_service(self, port, protocol, service_def):
        """Delegate to rule validator"""
        return self.rule_validator.validate_service(port, protocol, service_def)


class FirewallRuleAnalyzer:
    """
    방화벽 규칙 분석 클래스

    FortiGate 방화벽 정책 및 라우팅 테이블을 분석하여 특정 트래픽이 허용되는지 여부와
    해당 트래픽이 통과하는 방화벽 규칙을 식별합니다.

    이 클래스는 여러 컴포넌트를 조합하여 방화벽 분석 기능을 제공합니다:
    - DataLoader: 방화벽 데이터 로드
    - PolicyAnalyzer: 정책 매칭 분석
    - PathTracer: 패킷 경로 추적
    - RuleValidator: 규칙 유효성 검증
    - SessionManager: 분석 세션 관리
    """

    def __init__(self, fortigate_client=None, fortimanager_client=None):
        """
        방화벽 규칙 분석기 초기화

        Args:
            fortigate_client: FortiGate API 클라이언트 인스턴스
            fortimanager_client: FortiManager API 클라이언트 인스턴스
        """
        from .components.data_loader import DataLoader
        from .components.path_tracer import PathTracer
        from .components.policy_analyzer import \
            PolicyAnalyzer as PolicyAnalyzerComponent
        from .components.rule_validator import RuleValidator
        from .components.session_manager import SessionManager

        # 컴포넌트 초기화
        self.data_loader = DataLoader(fortigate_client, fortimanager_client)
        self.rule_validator = RuleValidator()
        self.policy_analyzer = PolicyAnalyzerComponent(
            self.data_loader, self.rule_validator
        )
        self.path_tracer = PathTracer(self.data_loader, self.policy_analyzer)
        self.session_manager = SessionManager(
            self.data_loader, self.policy_analyzer, self.path_tracer
        )

        self.logger = logger

        # 클라이언트 참조 저장
        self.fortigate_client = fortigate_client
        self.fortimanager_client = fortimanager_client

    # Delegate data loading methods
    def load_fortigate_data(self):
        """FortiGate 데이터 로드"""
        return self.data_loader.load_fortigate_data()

    def load_fortimanager_data(self):
        """FortiManager 데이터 로드"""
        return self.data_loader.load_fortimanager_data()

    # Delegate analysis methods
    def analyze_traffic(
        self, src_ip, dst_ip, dst_port, protocol="tcp", firewall_id="default"
    ):
        """트래픽 분석"""
        return self.policy_analyzer.analyze_traffic(
            src_ip, dst_ip, dst_port, protocol, firewall_id
        )

    def find_matching_policy(self, src_ip, dst_ip, dst_port, protocol, policies):
        """매칭 정책 찾기"""
        return self.policy_analyzer.find_matching_policy(
            src_ip, dst_ip, dst_port, protocol, policies
        )

    def analyze_packet_path(self, src_ip, dst_ip, dst_port, protocol="tcp"):
        """패킷 경로 분석"""
        return self.path_tracer.analyze_packet_path(src_ip, dst_ip, dst_port, protocol)

    # Delegate session management methods
    def get_analysis_session(self, session_id):
        """분석 세션 조회"""
        return self.session_manager.get_analysis_session(session_id)

    def create_analysis_session(self, src_ip, dst_ip, service, protocol="tcp"):
        """분석 세션 생성"""
        return self.session_manager.create_analysis_session(
            src_ip, dst_ip, service, protocol
        )

    # Delegate validation methods
    def validate_ip_in_range(self, ip, ip_range):
        """IP 범위 검증"""
        return self.rule_validator.validate_ip_in_range(ip, ip_range)

    def validate_service(self, port, protocol, service_def):
        """서비스 검증"""
        return self.rule_validator.validate_service(port, protocol, service_def)
