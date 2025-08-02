import ipaddress

from utils.unified_logger import setup_logger

logger = setup_logger("analyzer")


class FirewallRuleAnalyzer:
    """
    방화벽 규칙 분석 클래스

    FortiGate 방화벽 정책 및 라우팅 테이블을 분석하여 특정 트래픽이 허용되는지 여부와
    해당 트래픽이 통과하는 방화벽 규칙을 식별합니다.
    """

    def __init__(self, fortigate_client=None, fortimanager_client=None):
        """
        방화벽 규칙 분석기 초기화

        Args:
            fortigate_client: FortiGate API 클라이언트 인스턴스
            fortimanager_client: FortiManager API 클라이언트 인스턴스
        """
        self.fortigate_client = fortigate_client
        self.fortimanager_client = fortimanager_client
        self.logger = logger

        # 분석에 필요한 데이터 캐시
        self._policies = {}  # 방화벽 ID별 정책 캐시
        self._addresses = {}  # 방화벽 ID별 주소 객체 캐시
        self._address_groups = {}  # 방화벽 ID별 주소 그룹 캐시
        self._services = {}  # 방화벽 ID별 서비스 객체 캐시
        self._service_groups = {}  # 방화벽 ID별 서비스 그룹 캐시
        self._routing_tables = {}  # 방화벽 ID별 라우팅 테이블 캐시
        self._firewalls = {}  # 방화벽 장비 정보 캐시

        # 세션 관리를 위한 변수
        self._sessions = {}  # 세션 ID별 저장 데이터

    def load_data(self, firewall_id="default"):
        """
        특정 방화벽의 데이터 로드

        Args:
            firewall_id (str): 방화벽 식별자

        Returns:
            bool: 데이터 로드 성공 여부
        """
        try:
            if self.fortigate_client:
                # 직접 FortiGate API를 통한 데이터 로드
                self._policies[firewall_id] = self.fortigate_client.get_firewall_policies()
                self._addresses[firewall_id] = self.fortigate_client.get_firewall_addresses()
                self._address_groups[firewall_id] = self.fortigate_client.get_firewall_address_groups()
                self._services[firewall_id] = self.fortigate_client.get_firewall_services()
                self._service_groups[firewall_id] = self.fortigate_client.get_firewall_service_groups()
                self._routing_tables[firewall_id] = self.fortigate_client.get_routing_table()
                return True

            elif self.fortimanager_client:
                # FortiManager 인스턴스가 있는 경우 필요한 데이터 로드
                # 여기서는 가정: firewall_id가 FortiManager의 장치 이름이라고 가정
                self.logger.info(f"FortiManager를 통해 {firewall_id} 방화벽 데이터 로드 중...")

                # ADOM 정보 (일반적으로 "root" 사용)
                adom = "root"

                # 장치 정보 로드
                device_info = self.fortimanager_client.get_device_info(firewall_id, adom)
                if not device_info:
                    self.logger.error(f"장치 정보를 로드할 수 없습니다: {firewall_id}")
                    return False

                self._firewalls[firewall_id] = device_info

                # 정책 패키지 정보 로드
                policy_packages = self.fortimanager_client.get_policy_packages(adom)
                if not policy_packages:
                    self.logger.error(f"{firewall_id}에 대한 정책 패키지를 로드할 수 없습니다.")
                    return False

                # 장치에 할당된 정책 패키지 찾기
                # 실제 구현에서는 장치와 정책 패키지 간의 관계를 정확히 파악해야 함
                # 여기서는 단순화를 위해 첫 번째 정책 패키지 사용
                policy_package = policy_packages[0]["name"] if policy_packages and len(policy_packages) > 0 else None

                if policy_package:
                    self._policies[firewall_id] = self.fortimanager_client.get_firewall_policies(policy_package, adom)

                # 주소 객체 및 서비스 객체 로드
                self._addresses[firewall_id] = self.fortimanager_client.get_firewall_addresses(adom)
                self._address_groups[firewall_id] = self.fortimanager_client.get_firewall_address_groups(adom)
                self._services[firewall_id] = self.fortimanager_client.get_firewall_services(adom)
                self._service_groups[firewall_id] = self.fortimanager_client.get_firewall_service_groups(adom)

                # 라우팅 테이블 로드
                self._routing_tables[firewall_id] = self.fortimanager_client.get_device_routing_table(firewall_id, adom)

                return True

            else:
                self.logger.error("FortiGate 또는 FortiManager 클라이언트가 필요합니다.")
                return False

        except Exception as e:
            self.logger.error(f"데이터 로드 중 오류 발생: {str(e)}")
            return False

    def load_all_firewalls(self):
        """
        FortiManager를 통해 모든 방화벽 장치의 데이터 로드

        Returns:
            bool: 데이터 로드 성공 여부
        """
        if not self.fortimanager_client:
            self.logger.error("FortiManager 클라이언트가 필요합니다.")
            return False

        try:
            # ADOM 목록 가져오기
            adoms = self.fortimanager_client.get_adoms()
            if not adoms:
                self.logger.error("ADOM 목록을 가져올 수 없습니다.")
                return False

            loaded = False

            # 각 ADOM에서 장치 로드
            for adom in adoms:
                adom_name = adom.get("name")
                if not adom_name:
                    continue

                devices = self.fortimanager_client.get_devices(adom_name)
                if not devices:
                    self.logger.warning(f"ADOM '{adom_name}'에서 장치를 찾을 수 없습니다.")
                    continue

                for device in devices:
                    device_name = device.get("name")
                    if not device_name:
                        continue

                    if self.load_data(device_name):
                        loaded = True

            return loaded

        except Exception as e:
            self.logger.error(f"모든 방화벽 데이터 로드 중 오류 발생: {str(e)}")
            return False

    def is_ip_in_address_object(self, ip, address_obj, firewall_id="default"):
        """
        IP가 주소 객체에 포함되는지 확인

        Args:
            ip (str): 확인할 IP 주소
            address_obj (dict): 주소 객체
            firewall_id (str): 방화벽 식별자

        Returns:
            bool: IP가 주소 객체에 포함되는지 여부
        """
        try:
            obj_type = address_obj.get("type")

            if obj_type == "ipmask":
                # CIDR 표기법으로 된 서브넷
                subnet = address_obj.get("subnet", "0.0.0.0/0")
                # subnet 형식이 '192.168.1.0 255.255.255.0'인 경우 CIDR 형식으로 변환
                if " " in subnet:
                    ip_part, mask_part = subnet.split(" ")
                    mask_prefix = sum([bin(int(x)).count("1") for x in mask_part.split(".")])
                    subnet = f"{ip_part}/{mask_prefix}"

                return ipaddress.ip_address(ip) in ipaddress.ip_network(subnet)

            elif obj_type == "iprange":
                # IP 범위
                start_ip = address_obj.get("start-ip", "0.0.0.0")
                end_ip = address_obj.get("end-ip", "255.255.255.255")
                ip_int = int(ipaddress.ip_address(ip))
                start_int = int(ipaddress.ip_address(start_ip))
                end_int = int(ipaddress.ip_address(end_ip))

                return start_int <= ip_int <= end_int

            elif obj_type == "fqdn" or obj_type == "wildcard-fqdn":
                # FQDN은 IP 확인에 적합하지 않음
                return False

            else:
                # 지원되지 않는 주소 객체 유형
                self.logger.warning(f"지원되지 않는 주소 객체 유형: {obj_type}")
                return False

        except Exception as e:
            self.logger.error(f"주소 객체 확인 중 오류: {str(e)}")
            return False

    def is_ip_in_address_group(self, ip, group_name, firewall_id="default"):
        """
        IP가 주소 그룹에 포함되는지 확인

        Args:
            ip (str): 확인할 IP 주소
            group_name (str): 주소 그룹 이름
            firewall_id (str): 방화벽 식별자

        Returns:
            bool: IP가 주소 그룹에 포함되는지 여부
        """
        if firewall_id not in self._address_groups:
            self.logger.error(f"방화벽 {firewall_id}의 주소 그룹 데이터가 로드되지 않았습니다.")
            return False

        # 그룹 찾기
        group = None
        for addr_group in self._address_groups[firewall_id]:
            if addr_group.get("name") == group_name:
                group = addr_group
                break

        if not group:
            self.logger.warning(f"주소 그룹을 찾을 수 없음: {group_name}")
            return False

        # 그룹 멤버 확인
        members = group.get("member", [])

        for member in members:
            member_name = member.get("name")

            # 멤버가 다른 주소 그룹인 경우 재귀적으로 확인
            is_group = False
            for addr_group in self._address_groups[firewall_id]:
                if addr_group.get("name") == member_name:
                    is_group = True
                    if self.is_ip_in_address_group(ip, member_name, firewall_id):
                        return True
                    break

            if not is_group:
                # 주소 객체 찾기
                for addr in self._addresses[firewall_id]:
                    if addr.get("name") == member_name:
                        if self.is_ip_in_address_object(ip, addr, firewall_id):
                            return True
                        break

        return False

    def is_service_match(self, port, protocol, service_obj):
        """
        포트와 프로토콜이 서비스 객체와 일치하는지 확인

        Args:
            port (int): 포트 번호
            protocol (str): 프로토콜 (tcp, udp, icmp)
            service_obj (dict): 서비스 객체

        Returns:
            bool: 서비스 일치 여부
        """
        try:
            if protocol == "tcp":
                tcp_portrange = service_obj.get("tcp-portrange", "")
                if not tcp_portrange:
                    return False

                for portrange in tcp_portrange.split(" "):
                    if "-" in portrange:
                        start, end = map(int, portrange.split("-"))
                        if start <= port <= end:
                            return True
                    elif int(portrange) == port:
                        return True

            elif protocol == "udp":
                udp_portrange = service_obj.get("udp-portrange", "")
                if not udp_portrange:
                    return False

                for portrange in udp_portrange.split(" "):
                    if "-" in portrange:
                        start, end = map(int, portrange.split("-"))
                        if start <= port <= end:
                            return True
                    elif int(portrange) == port:
                        return True

            elif protocol == "icmp":
                # ICMP 프로토콜은 포트를 사용하지 않음
                return "protocol" in service_obj and service_obj.get("protocol") == "ICMP"

            return False

        except Exception as e:
            self.logger.error(f"서비스 객체 확인 중 오류: {str(e)}")
            return False

    def is_service_in_group(self, port, protocol, group_name, firewall_id="default"):
        """
        포트와 프로토콜이 서비스 그룹에 포함되는지 확인

        Args:
            port (int): 포트 번호
            protocol (str): 프로토콜 (tcp, udp, icmp)
            group_name (str): 서비스 그룹 이름
            firewall_id (str): 방화벽 식별자

        Returns:
            bool: 서비스가 그룹에 포함되는지 여부
        """
        if firewall_id not in self._service_groups:
            self.logger.error(f"방화벽 {firewall_id}의 서비스 그룹 데이터가 로드되지 않았습니다.")
            return False

        # 그룹 찾기
        group = None
        for svc_group in self._service_groups[firewall_id]:
            if svc_group.get("name") == group_name:
                group = svc_group
                break

        if not group:
            self.logger.warning(f"서비스 그룹을 찾을 수 없음: {group_name}")
            return False

        # 그룹 멤버 확인
        members = group.get("member", [])

        for member in members:
            member_name = member.get("name")

            # 멤버가 다른 서비스 그룹인 경우 재귀적으로 확인
            is_group = False
            for svc_group in self._service_groups[firewall_id]:
                if svc_group.get("name") == member_name:
                    is_group = True
                    if self.is_service_in_group(port, protocol, member_name, firewall_id):
                        return True
                    break

            if not is_group:
                # 서비스 객체 찾기
                for svc in self._services[firewall_id]:
                    if svc.get("name") == member_name:
                        if self.is_service_match(port, protocol, svc):
                            return True
                        break

        return False

    def get_next_hop(self, dest_ip, firewall_id="default"):
        """
        목적지 IP에 대한 다음 홉 라우터 찾기

        Args:
            dest_ip (str): 목적지 IP 주소
            firewall_id (str): 방화벽 식별자

        Returns:
            dict: 다음 홉 정보 (없으면 None)
        """
        if firewall_id not in self._routing_tables:
            self.logger.error(f"방화벽 {firewall_id}의 라우팅 테이블이 로드되지 않았습니다.")
            return None

        try:
            dest_ip_addr = ipaddress.ip_address(dest_ip)
            matching_route = None
            longest_prefix = -1

            for route in self._routing_tables[firewall_id]:
                dst = route.get("dst", "0.0.0.0/0")

                # dst 형식이 '192.168.1.0 255.255.255.0'인 경우 CIDR 형식으로 변환
                if " " in dst:
                    ip_part, mask_part = dst.split(" ")
                    mask_prefix = sum([bin(int(x)).count("1") for x in mask_part.split(".")])
                    dst = f"{ip_part}/{mask_prefix}"

                try:
                    route_network = ipaddress.ip_network(dst)
                    if dest_ip_addr in route_network:
                        prefix_len = route_network.prefixlen
                        if prefix_len > longest_prefix:
                            longest_prefix = prefix_len
                            matching_route = route
                except ValueError:
                    continue

            return matching_route

        except Exception as e:
            self.logger.error(f"다음 홉 찾기 중 오류: {str(e)}")
            return None

    def check_policy_match(self, src_ip, dst_ip, port, protocol, firewall_id="default"):
        """
        특정 트래픽이 방화벽 정책과 일치하는지 확인

        Args:
            src_ip (str): 출발지 IP 주소
            dst_ip (str): 목적지 IP 주소
            port (int): 포트 번호
            protocol (str): 프로토콜 (tcp, udp, icmp)
            firewall_id (str): 방화벽 식별자

        Returns:
            tuple: (일치하는 정책, 액션, 순서)
        """
        if firewall_id not in self._policies:
            self.logger.error(f"방화벽 {firewall_id}의 정책 데이터가 로드되지 않았습니다.")
            return None, None, None

        matching_policies = []

        for policy in self._policies[firewall_id]:
            # 정책이 활성화되어 있는지 확인
            if policy.get("status") != "enable":
                continue

            # 소스 주소 확인
            src_match = False
            for src_addr in policy.get("srcaddr", []):
                src_name = src_addr.get("name")

                # 'all' 주소 객체 확인
                if src_name == "all":
                    src_match = True
                    break

                # 주소 그룹 확인
                is_group = False
                for addr_group in self._address_groups[firewall_id]:
                    if addr_group.get("name") == src_name:
                        is_group = True
                        if self.is_ip_in_address_group(src_ip, src_name, firewall_id):
                            src_match = True
                            break

                if src_match:
                    break

                if not is_group:
                    # 주소 객체 확인
                    for addr in self._addresses[firewall_id]:
                        if addr.get("name") == src_name:
                            if self.is_ip_in_address_object(src_ip, addr, firewall_id):
                                src_match = True
                                break

                if src_match:
                    break

            if not src_match:
                continue

            # 목적지 주소 확인
            dst_match = False
            for dst_addr in policy.get("dstaddr", []):
                dst_name = dst_addr.get("name")

                # 'all' 주소 객체 확인
                if dst_name == "all":
                    dst_match = True
                    break

                # 주소 그룹 확인
                is_group = False
                for addr_group in self._address_groups[firewall_id]:
                    if addr_group.get("name") == dst_name:
                        is_group = True
                        if self.is_ip_in_address_group(dst_ip, dst_name, firewall_id):
                            dst_match = True
                            break

                if dst_match:
                    break

                if not is_group:
                    # 주소 객체 확인
                    for addr in self._addresses[firewall_id]:
                        if addr.get("name") == dst_name:
                            if self.is_ip_in_address_object(dst_ip, addr, firewall_id):
                                dst_match = True
                                break

                if dst_match:
                    break

            if not dst_match:
                continue

            # 서비스 확인
            service_match = False
            for service in policy.get("service", []):
                service_name = service.get("name")

                # 'ALL' 서비스 확인
                if service_name.upper() == "ALL":
                    service_match = True
                    break

                # 서비스 그룹 확인
                is_group = False
                for svc_group in self._service_groups[firewall_id]:
                    if svc_group.get("name") == service_name:
                        is_group = True
                        if self.is_service_in_group(port, protocol, service_name, firewall_id):
                            service_match = True
                            break

                if service_match:
                    break

                if not is_group:
                    # 서비스 객체 확인
                    for svc in self._services[firewall_id]:
                        if svc.get("name") == service_name:
                            if self.is_service_match(port, protocol, svc):
                                service_match = True
                                break

                if service_match:
                    break

            if not service_match:
                continue

            # 모든 조건이 일치하면 정책을 추가
            matching_policies.append(
                {
                    "policy": policy,
                    "action": policy.get("action", "deny"),
                    "policy_id": policy.get("policyid", 0),
                }
            )

        # 정책 ID로 정렬 (FortiGate는 오름차순으로 정책을 평가함)
        matching_policies.sort(key=lambda x: x["policy_id"])

        # 일치하는 첫 번째 정책 반환 (순서가 가장 낮은 정책)
        if matching_policies:
            match = matching_policies[0]
            return match["policy"], match["action"], match["policy_id"]

        return None, None, None

    def trace_packet_path(self, src_ip, dst_ip, port, protocol, session_id=None):
        """
        패킷 경로 추적 - 출발지에서 목적지까지의 모든 방화벽 및 적용되는 규칙 분석

        Args:
            src_ip (str): 출발지 IP 주소
            dst_ip (str): 목적지 IP 주소
            port (int): 포트 번호
            protocol (str): 프로토콜 (tcp, udp, icmp)
            session_id (str, optional): 세션 ID. 지정되지 않으면 새로 생성됨

        Returns:
            dict: 패킷 경로 분석 결과
        """
        # 세션 ID 생성 또는 기존 세션 확인
        import datetime
        import uuid

        if not session_id:
            session_id = str(uuid.uuid4())

        # 세션 시작 시간 및 상태 기록
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 세션 데이터 초기화
        self._sessions[session_id] = {
            "start_time": current_time,
            "status": "running",
            "source_ip": src_ip,
            "destination_ip": dst_ip,
            "port": port,
            "protocol": protocol,
            "progress": 0,
        }

        # 데이터가 로드되었는지 확인
        if not self._firewalls:
            self.logger.error("방화벽 데이터가 로드되지 않았습니다. load_data() 또는 load_all_firewalls()를 먼저 호출하세요.")

            # 세션 오류 상태 업데이트
            self._sessions[session_id].update(
                {
                    "status": "error",
                    "end_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "error": "방화벽 데이터가 로드되지 않음",
                    "allowed": False,
                    "path": [],
                }
            )

            return {
                "allowed": False,
                "error": "방화벽 데이터가 로드되지 않음",
                "path": [],
            }

        # 결과 구조 초기화
        result = {
            "allowed": True,
            "path": [],
            "blocked_by": None,
            "final_destination": dst_ip,
            "source_zone": self._determine_network_zone(src_ip),
            "destination_zone": self._determine_network_zone(dst_ip),
            "source_ip": src_ip,
            "destination_ip": dst_ip,
            "port": port,
            "protocol": protocol,
            "network_path": [],  # 전체 네트워크 경로 정보 (구간별)
            "session_id": session_id,
        }

        try:
            # 네트워크 토폴로지 정보 분석 및 경로 결정
            firewall_path = self._determine_firewall_path(src_ip, dst_ip)
            if not firewall_path:
                self.logger.error(f"방화벽 경로를 결정할 수 없습니다: {src_ip} -> {dst_ip}")
                return {
                    "allowed": False,
                    "error": "방화벽 경로를 결정할 수 없음",
                    "path": [],
                }

            current_src = src_ip
            current_dst = dst_ip

            # 네트워크 경로 구성 (방화벽 전체 경로)
            for i, hop in enumerate(firewall_path):
                is_first = i == 0
                is_last = i == len(firewall_path) - 1

                # 네트워크 경로 항목 추가
                network_hop = {
                    "hop_index": i,
                    "source_ip": src_ip if is_first else hop.get("next_hop", "unknown"),
                    "destination_ip": (
                        dst_ip
                        if is_last
                        else (firewall_path[i + 1].get("next_hop", "unknown") if not is_last else "unknown")
                    ),
                    "zone": hop.get("ingress_zone", "unknown"),
                    "next_zone": hop.get("egress_zone", "unknown"),
                    "hop_type": hop.get("hop_type", "transit"),
                }

                result["network_path"].append(network_hop)

            # 경로 추적 - 모든 방화벽 경유
            for hop_index, firewall_info in enumerate(firewall_path):
                current_firewall = firewall_info["firewall_id"]
                ingress_iface = firewall_info.get("ingress_interface")
                egress_iface = firewall_info.get("egress_interface")
                ingress_zone = firewall_info.get("ingress_zone")
                egress_zone = firewall_info.get("egress_zone")
                next_hop = firewall_info.get("next_hop")
                hop_type = firewall_info.get("hop_type", "transit")

                self.logger.info(f"Hop {hop_index+1}: {current_firewall} 분석 중 ({current_src} -> {current_dst})")
                self.logger.info(f"  구간: {ingress_zone} -> {egress_zone}, 인터페이스: {ingress_iface} -> {egress_iface}")

                # 현재 방화벽에서 정책 확인
                policy, action, policy_id = self.check_policy_match(
                    current_src, current_dst, port, protocol, current_firewall
                )

                # 매칭된 정책에서 추가 세부 정보 추출
                policy_details = {}
                if policy:
                    policy_details = {
                        "policy_name": policy.get("name", ""),
                        "comments": policy.get("comments", ""),
                        "status": policy.get("status", ""),
                        "schedule": policy.get("schedule", ""),
                        "service": [s.get("name", "") for s in policy.get("service", [])],
                        "srcaddr": [s.get("name", "") for s in policy.get("srcaddr", [])],
                        "dstaddr": [s.get("name", "") for s in policy.get("dstaddr", [])],
                        "action": action,
                    }

                hop_result = {
                    "hop_index": hop_index + 1,
                    "firewall_id": current_firewall,
                    "firewall_name": self._firewalls[current_firewall].get("name", current_firewall),
                    "src_ip": current_src,
                    "dst_ip": current_dst,
                    "protocol": protocol,
                    "port": port,
                    "ingress_interface": ingress_iface,
                    "egress_interface": egress_iface,
                    "ingress_zone": ingress_zone,
                    "egress_zone": egress_zone,
                    "hop_type": hop_type,
                    "policy": policy,
                    "policy_id": policy_id,
                    "policy_details": policy_details,
                    "action": action,
                    "next_hop": next_hop,
                }

                result["path"].append(hop_result)

                # 정책 액션 확인 - 차단된 경우
                if not policy or action == "deny":
                    result["allowed"] = False
                    result["blocked_by"] = {
                        "hop_index": hop_index + 1,
                        "firewall_id": current_firewall,
                        "firewall_name": self._firewalls[current_firewall].get("name", current_firewall),
                        "policy_id": policy_id,
                        "ingress_zone": ingress_zone,
                        "ingress_interface": ingress_iface,
                        "src_ip": current_src,
                        "dst_ip": current_dst,
                    }
                    break

                # 다음 홉이 있는 경우
                if next_hop:
                    current_src = next_hop
                else:
                    # 마지막 방화벽이면 종료
                    pass

            # 경로가 존재하는 경우 경로 최적화 추천 분석 실행
            if result["path"] and len(result["path"]) > 0:
                result["optimization_recommendations"] = self._analyze_path_for_optimization(result["path"])

            # 세션 데이터 업데이트
            import datetime

            # 세션 완료 상태 업데이트
            self._sessions[session_id].update(
                {
                    "status": "completed",
                    "end_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "allowed": result["allowed"],
                    "path": result["path"],
                    "blocked_by": result["blocked_by"],
                    "network_path": result["network_path"],
                    "progress": 100,
                }
            )

            if "optimization_recommendations" in result:
                self._sessions[session_id]["optimization_recommendations"] = result["optimization_recommendations"]

            return result

        except Exception as e:
            # 오류 발생 시 세션 상태 업데이트
            import datetime

            self.logger.error(f"패킷 경로 추적 중 오류: {str(e)}")

            self._sessions[session_id].update(
                {
                    "status": "error",
                    "end_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "error": str(e),
                    "allowed": False,
                    "path": result.get("path", []),
                    "progress": 0,
                }
            )

            return {
                "allowed": False,
                "error": str(e),
                "path": result.get("path", []),
                "session_id": session_id,
            }

    def _determine_firewall_path(self, src_ip, dst_ip):
        """
        출발지에서 목적지로의 경로에 있는 방화벽 순서 및 경로 정보 결정
        라우팅 테이블을 기반으로 정확한 경로를 결정합니다.

        Args:
            src_ip (str): 출발지 IP 주소
            dst_ip (str): 목적지 IP 주소

        Returns:
            list: 방화벽 경로 정보 (예: [{firewall_id, ingress_interface, egress_interface, next_hop, zone_info}, ...])
        """
        try:
            # 네트워크 토폴로지 정보 분석 및 방화벽 경로 결정
            ipaddress.ip_address(src_ip)
            ipaddress.ip_address(dst_ip)

            # 네트워크 구간은 라우팅 테이블 참조를 위한 보조 정보로만 사용
            src_zone = self._determine_network_zone(src_ip)
            dst_zone = self._determine_network_zone(dst_ip)

            self.logger.info(f"출발지 {src_ip}는 {src_zone} 구간에 위치, 목적지 {dst_ip}는 {dst_zone} 구간에 위치")

            firewall_path = []

            # 이미 로드된 방화벽 목록과 그들의 라우팅 테이블 분석
            relevant_firewalls = self._identify_relevant_firewalls_from_routing(src_ip, dst_ip)
            self.logger.info(f"라우팅 분석 결과, 관련 방화벽: {relevant_firewalls}")

            # 단일 방화벽 환경의 경우
            if len(relevant_firewalls) == 1:
                firewall_id = relevant_firewalls[0]
                # 라우팅 테이블에서 인터페이스 정보 조회
                ingress_route = self._find_route_for_ip(src_ip, firewall_id)
                egress_route = self._find_route_for_ip(dst_ip, firewall_id)

                ingress_iface = (
                    ingress_route.get("interface")
                    if ingress_route
                    else self._find_interface_for_ip(src_ip, firewall_id)
                )
                egress_iface = (
                    egress_route.get("interface") if egress_route else self._find_interface_for_ip(dst_ip, firewall_id)
                )

                # 인터페이스 정보에 구간 정보 추가
                ingress_zone = self._get_interface_zone(ingress_iface, firewall_id) or src_zone
                egress_zone = self._get_interface_zone(egress_iface, firewall_id) or dst_zone

                firewall_path.append(
                    {
                        "firewall_id": firewall_id,
                        "firewall_name": self._firewalls[firewall_id].get("name", firewall_id),
                        "ingress_interface": ingress_iface,
                        "egress_interface": egress_iface,
                        "ingress_zone": ingress_zone,
                        "egress_zone": egress_zone,
                        "next_hop": None,
                        "hop_type": "endpoint",
                        "route_info": {
                            "ingress_route": ingress_route,
                            "egress_route": egress_route,
                        },
                    }
                )
                return firewall_path

            # 다중 방화벽 환경의 경우
            # 라우팅 테이블을 기반으로 최적 경로 결정
            current_ip = src_ip
            current_zone = src_zone
            next_firewall_idx = 0
            max_hops = 10  # 최대 홉 제한 (무한 루프 방지)
            hop_count = 0

            while next_firewall_idx < len(relevant_firewalls) and hop_count < max_hops:
                firewall_id = relevant_firewalls[next_firewall_idx]
                is_first = next_firewall_idx == 0
                is_last = next_firewall_idx == len(relevant_firewalls) - 1

                self.logger.info(f"방화벽 {firewall_id} 분석 중 (현재 IP: {current_ip}, 목적지: {dst_ip})")

                # 현재 소스 IP에 대한 라우팅 정보
                ingress_route = self._find_route_for_ip(current_ip, firewall_id)

                # 목적지 IP에 대한 라우팅 정보
                dst_route = self._find_route_for_ip(dst_ip, firewall_id)

                # 인터페이스 정보 결정
                ingress_iface = (
                    ingress_route.get("interface")
                    if ingress_route
                    else self._find_interface_for_ip(current_ip, firewall_id)
                )

                # 목적지까지의 경로가 직접적으로 연결되어 있는지 확인
                if is_last or (dst_route and not dst_route.get("gateway")):
                    # 마지막 방화벽이거나 직접 연결된 경우
                    egress_iface = (
                        dst_route.get("interface") if dst_route else self._find_interface_for_ip(dst_ip, firewall_id)
                    )
                    next_hop = dst_ip
                    next_firewall_idx = len(relevant_firewalls)  # 루프 종료
                else:
                    # 다음 홉을 라우팅 테이블에서 결정
                    dst_route = self.get_next_hop(dst_ip, firewall_id)

                    if dst_route and dst_route.get("gateway"):
                        next_hop = dst_route.get("gateway")
                        egress_iface = dst_route.get("interface")

                        # 다음 방화벽 결정 (다음 홉이 다른 방화벽에 속하는지 확인)
                        for idx, fw_id in enumerate(
                            relevant_firewalls[next_firewall_idx + 1 :],
                            next_firewall_idx + 1,
                        ):
                            if self._is_ip_managed_by_firewall(next_hop, fw_id):
                                next_firewall_idx = idx
                                break
                        else:
                            # 다음 홉이 다른 방화벽에 속하지 않으면 순서대로 진행
                            next_firewall_idx += 1
                    else:
                        # 라우팅 정보가 없으면 다음 순서의 방화벽으로 진행
                        next_firewall_idx += 1
                        next_hop = self._estimate_next_hop(
                            firewall_id,
                            (
                                relevant_firewalls[next_firewall_idx]
                                if next_firewall_idx < len(relevant_firewalls)
                                else None
                            ),
                            dst_ip,
                        )
                        egress_iface = self._find_egress_interface(next_hop, firewall_id)

                # 인터페이스 구간 정보 결정
                ingress_zone = self._get_interface_zone(ingress_iface, firewall_id) or (
                    src_zone if is_first else current_zone
                )
                egress_zone = self._get_interface_zone(egress_iface, firewall_id) or (
                    dst_zone if is_last else "transit"
                )

                # 방화벽 홉 유형 결정
                hop_type = (
                    "source"
                    if is_first
                    else ("destination" if is_last or next_firewall_idx >= len(relevant_firewalls) else "transit")
                )

                # 경로 정보 추가
                firewall_path.append(
                    {
                        "firewall_id": firewall_id,
                        "firewall_name": self._firewalls[firewall_id].get("name", firewall_id),
                        "ingress_interface": ingress_iface,
                        "egress_interface": egress_iface,
                        "ingress_zone": ingress_zone,
                        "egress_zone": egress_zone,
                        "next_hop": next_hop,
                        "hop_type": hop_type,
                        "route_info": {
                            "ingress_route": ingress_route,
                            "dst_route": dst_route,
                        },
                    }
                )

                # 다음 iteration을 위해 현재 위치 업데이트
                current_ip = next_hop
                current_zone = egress_zone
                hop_count += 1

                # 목적지에 도달했거나 마지막 방화벽을 처리한 경우 종료
                if next_hop == dst_ip or next_firewall_idx >= len(relevant_firewalls):
                    break

            return firewall_path

        except Exception as e:
            self.logger.error(f"방화벽 경로 결정 중 오류: {str(e)}")
            import traceback

            self.logger.error(traceback.format_exc())
            return None

    def _determine_network_zone(self, ip):
        """
        IP 주소가 속한 네트워크 구간 결정 (DMZ, 내부망, 외부망 등)

        Args:
            ip (str): IP 주소

        Returns:
            str: 네트워크 구간 이름 (internal, dmz, external 등)
        """
        try:
            ip_obj = ipaddress.ip_address(ip)

            # 사설 IP 범위 정의
            private_ranges = [
                ipaddress.ip_network("10.0.0.0/8"),
                ipaddress.ip_network("172.16.0.0/12"),
                ipaddress.ip_network("192.168.0.0/16"),
            ]

            # DMZ 범위 정의 (예: 특정 서브넷)
            dmz_ranges = [
                ipaddress.ip_network("10.10.0.0/16"),  # 가정: 10.10.x.x 대역은 DMZ
                ipaddress.ip_network("172.16.10.0/24"),  # 가정: 172.16.10.x 대역은 DMZ
            ]

            # DMZ 범위 확인
            if any(ip_obj in dmz_range for dmz_range in dmz_ranges):
                return "dmz"

            # 사설 IP 확인 (DMZ가 아닌 경우)
            if any(ip_obj in private_range for private_range in private_ranges):
                return "internal"

            # 그 외는 외부 네트워크로 간주
            return "external"

        except Exception as e:
            self.logger.error(f"네트워크 구간 결정 중 오류: {str(e)}")
            return "unknown"

    def _identify_relevant_firewalls(self, src_ip, dst_ip, src_zone, dst_zone):
        """
        출발지에서 목적지로 가는 경로에 관련된 방화벽 식별

        Args:
            src_ip (str): 출발지 IP 주소
            dst_ip (str): 목적지 IP 주소
            src_zone (str): 출발지 네트워크 구간
            dst_zone (str): 목적지 네트워크 구간

        Returns:
            list: 관련 방화벽 ID 목록
        """
        try:
            # 데이터가 로드된 모든 방화벽 목록
            all_firewalls = list(self._firewalls.keys())

            # 방화벽이 없는 경우
            if not all_firewalls:
                self.logger.error("로드된 방화벽이 없습니다.")
                return []

            # 방화벽이 하나만 있는 경우
            if len(all_firewalls) == 1:
                return all_firewalls

            # 방화벽이 여러 개 있는 경우, 토폴로지 분석 필요
            # 이 예시에서는 방화벽과 네트워크 구간 간의 매핑을 분석하여 경로 결정

            # 출발지/목적지 구간에 따른 경로 결정
            if src_zone == dst_zone:
                if src_zone == "internal":
                    # 내부 -> 내부: 내부 방화벽만 경유
                    return [self._find_zone_firewall("internal")]
                elif src_zone == "dmz":
                    # DMZ -> DMZ: DMZ 방화벽만 경유
                    return [self._find_zone_firewall("dmz")]
                elif src_zone == "external":
                    # 외부 -> 외부: 외부 방화벽만 경유
                    return [self._find_zone_firewall("external")]
            elif src_zone == "internal" and dst_zone == "external":
                # 내부 -> 외부: 내부 방화벽 -> 외부 방화벽
                return [
                    self._find_zone_firewall("internal"),
                    self._find_zone_firewall("external"),
                ]
            elif src_zone == "external" and dst_zone == "internal":
                # 외부 -> 내부: 외부 방화벽 -> 내부 방화벽
                return [
                    self._find_zone_firewall("external"),
                    self._find_zone_firewall("internal"),
                ]
            elif src_zone == "internal" and dst_zone == "dmz":
                # 내부 -> DMZ: 내부 방화벽 -> DMZ 방화벽
                return [
                    self._find_zone_firewall("internal"),
                    self._find_zone_firewall("dmz"),
                ]
            elif src_zone == "dmz" and dst_zone == "internal":
                # DMZ -> 내부: DMZ 방화벽 -> 내부 방화벽
                return [
                    self._find_zone_firewall("dmz"),
                    self._find_zone_firewall("internal"),
                ]
            elif src_zone == "external" and dst_zone == "dmz":
                # 외부 -> DMZ: 외부 방화벽 -> DMZ 방화벽
                return [
                    self._find_zone_firewall("external"),
                    self._find_zone_firewall("dmz"),
                ]
            elif src_zone == "dmz" and dst_zone == "external":
                # DMZ -> 외부: DMZ 방화벽 -> 외부 방화벽
                return [
                    self._find_zone_firewall("dmz"),
                    self._find_zone_firewall("external"),
                ]

            # 기본값: 모든 방화벽을 순서대로 경유
            self.logger.warning(f"특정 경로를 결정할 수 없어 모든 방화벽을 사용합니다: {src_zone} -> {dst_zone}")
            return all_firewalls

        except Exception as e:
            self.logger.error(f"관련 방화벽 식별 중 오류: {str(e)}")
            return list(self._firewalls.keys())  # 오류 시 모든 방화벽 반환

    def _find_zone_firewall(self, zone):
        """
        특정 네트워크 구간을 담당하는 방화벽 찾기

        Args:
            zone (str): 네트워크 구간 (internal, dmz, external 등)

        Returns:
            str: 방화벽 ID 또는 기본값
        """
        # 방화벽 이름 또는 설명에서 구간 정보 찾기
        for firewall_id, firewall_info in self._firewalls.items():
            name = firewall_info.get("name", "").lower()
            desc = firewall_info.get("desc", "").lower()

            # 이름이나 설명에 구간 정보가 포함되어 있는지 확인
            if zone.lower() in name or zone.lower() in desc:
                return firewall_id

        # 구간 정보를 찾을 수 없으면 기본값 반환
        if len(self._firewalls) == 1:
            return list(self._firewalls.keys())[0]

        # 방화벽이 여러 개인 경우, 위치에 따라 할당
        firewalls = list(self._firewalls.keys())
        if zone == "internal":
            return firewalls[0]  # 첫 번째 방화벽을 내부 구간 담당으로 가정
        elif zone == "dmz":
            if len(firewalls) >= 3:
                return firewalls[1]  # 중간 방화벽을 DMZ 담당으로 가정
            else:
                return firewalls[0]  # 방화벽이 2개 이하면 첫 번째를 DMZ 담당으로 가정
        elif zone == "external":
            return firewalls[-1]  # 마지막 방화벽을 외부 구간 담당으로 가정
        else:
            return firewalls[0]  # 기본값

    def _estimate_next_hop(self, current_firewall, next_firewall, dst_ip):
        """
        다음 홉 IP 주소 추정

        Args:
            current_firewall (str): 현재 방화벽 ID
            next_firewall (str): 다음 방화벽 ID
            dst_ip (str): 최종 목적지 IP

        Returns:
            str: 다음 홉 IP 주소
        """
        try:
            # 라우팅 테이블에서 다음 홉 찾기
            route = self.get_next_hop(dst_ip, current_firewall)
            if route and route.get("gateway"):
                return route.get("gateway")

            # 방화벽 간 연결을 위한 가상 IP 생성 (실제 구현에서는 방화벽 정보에서 가져와야 함)
            # 여기서는 현재와 다음 방화벽 ID를 조합하여 가상 IP 생성
            current_idx = list(self._firewalls.keys()).index(current_firewall)
            next_idx = list(self._firewalls.keys()).index(next_firewall)

            # 간단한 가상 IP 매핑 (실제 환경에서는 방화벽 인터페이스 정보를 사용해야 함)
            return f"10.{current_idx}.{next_idx}.1"

        except Exception as e:
            self.logger.error(f"다음 홉 추정 중 오류: {str(e)}")

            # 기본 다음 홉 IP 반환
            current_idx = 0
            try:
                current_idx = list(self._firewalls.keys()).index(current_firewall)
            except (ValueError, KeyError):
                pass

            return f"10.{current_idx+1}.0.1"

    def _find_egress_interface(self, next_hop_ip, firewall_id):
        """
        다음 홉으로 가는 출구 인터페이스 찾기

        Args:
            next_hop_ip (str): 다음 홉 IP 주소
            firewall_id (str): 방화벽 식별자

        Returns:
            str: 인터페이스 이름
        """
        try:
            # 라우팅 테이블을 통해 인터페이스 찾기
            routing_table = self._routing_tables.get(firewall_id, [])

            for route in routing_table:
                if route.get("gateway") == next_hop_ip:
                    return route.get("interface")

            # 주소 객체에서 인터페이스 정보를 찾을 수도 있음
            # 예: 특정 주소 객체가 특정 인터페이스에 연결되어 있는 경우

            # 인터페이스를 찾을 수 없으면 IP 특성에 따라 추정
            return self._find_interface_for_ip(next_hop_ip, firewall_id)

        except Exception as e:
            self.logger.error(f"출구 인터페이스 찾기 중 오류: {str(e)}")
            return "unknown"

    def _get_interface_zone(self, interface_name, firewall_id):
        """
        인터페이스의 네트워크 구간 정보 조회

        Args:
            interface_name (str): 인터페이스 이름
            firewall_id (str): 방화벽 식별자

        Returns:
            str: 네트워크 구간 이름 또는 None
        """
        # 인터페이스 정보 매핑 (실제 구현에서는 방화벽 설정에서 가져와야 함)
        # 여기서는 인터페이스 이름에 따라 간단히 구간 결정
        try:
            if not interface_name:
                return None

            # 인터페이스 이름에 따른 구간 결정
            interface_lower = interface_name.lower()

            if "internal" in interface_lower or "inside" in interface_lower or "lan" in interface_lower:
                return "internal"
            elif "dmz" in interface_lower:
                return "dmz"
            elif "external" in interface_lower or "outside" in interface_lower or "wan" in interface_lower:
                return "external"

            # 서브넷 기반 결정
            # 실제 구현에서는 인터페이스의 IP 주소 범위를 확인하여 구간 결정

            return None

        except Exception as e:
            self.logger.error(f"인터페이스 구간 정보 조회 중 오류: {str(e)}")
            return None

    def _analyze_path_for_optimization(self, path):
        """
        경로 최적화 추천 분석 - 불필요하거나 중복된 규칙 식별 및 개선 제안

        Args:
            path (list): 패킷 경로 정보 리스트

        Returns:
            list: 최적화 추천 사항 목록
        """
        recommendations = []

        # 분석을 위한 방화벽 및 정책 목록 추출
        analyzed_firewalls = {}

        try:
            # 각 방화벽별 통과 정책 수집
            for hop in path:
                firewall_id = hop.get("firewall_id")
                if not firewall_id:
                    continue

                policy = hop.get("policy")
                policy_id = hop.get("policy_id")
                if not policy or not policy_id:
                    continue

                # 방화벽별 분석 정보 수집
                if firewall_id not in analyzed_firewalls:
                    analyzed_firewalls[firewall_id] = {
                        "policies": [],
                        "interfaces": set(),
                        "zones": set(),
                    }

                # 정책 정보 수집
                analyzed_firewalls[firewall_id]["policies"].append(
                    {
                        "policy": policy,
                        "policy_id": policy_id,
                        "ingress_interface": hop.get("ingress_interface"),
                        "egress_interface": hop.get("egress_interface"),
                        "ingress_zone": hop.get("ingress_zone"),
                        "egress_zone": hop.get("egress_zone"),
                    }
                )

                # 인터페이스 및 구간 정보 수집
                if hop.get("ingress_interface"):
                    analyzed_firewalls[firewall_id]["interfaces"].add(hop.get("ingress_interface"))
                if hop.get("egress_interface"):
                    analyzed_firewalls[firewall_id]["interfaces"].add(hop.get("egress_interface"))
                if hop.get("ingress_zone"):
                    analyzed_firewalls[firewall_id]["zones"].add(hop.get("ingress_zone"))
                if hop.get("egress_zone"):
                    analyzed_firewalls[firewall_id]["zones"].add(hop.get("egress_zone"))

            # 1. 광범위한 'ANY' 규칙 사용 확인 및 개선 제안
            for firewall_id, data in analyzed_firewalls.items():
                for p_data in data["policies"]:
                    policy = p_data["policy"]

                    # 출발지/목적지 ANY 사용 확인
                    src_any = False
                    dst_any = False
                    svc_any = False

                    for src in policy.get("srcaddr", []):
                        if src.get("name") == "all":
                            src_any = True
                            break

                    for dst in policy.get("dstaddr", []):
                        if dst.get("name") == "all":
                            dst_any = True
                            break

                    for svc in policy.get("service", []):
                        if svc.get("name").upper() == "ALL":
                            svc_any = True
                            break

                    # ANY 사용 시 추천 사항 제공
                    if src_any and dst_any and svc_any:
                        recommendations.append(
                            {
                                "firewall_id": firewall_id,
                                "policy_id": p_data["policy_id"],
                                "severity": "high",
                                "type": "security_improvement",
                                "issue": "ALL 설정 사용",
                                "description": (
                                    f"방화벽 '{firewall_id}'의 정책 {p_data['policy_id']}에서 "
                                    "출발지, 목적지, 서비스 모두 'ANY'를 사용하고 있어 보안 위험이 큽니다."
                                ),
                                "recommendation": "출발지, 목적지, 서비스를 필요한 최소 범위로 제한하세요.",
                            }
                        )
                    elif src_any:
                        recommendations.append(
                            {
                                "firewall_id": firewall_id,
                                "policy_id": p_data["policy_id"],
                                "severity": "medium",
                                "type": "security_improvement",
                                "issue": "출발지 ANY 설정",
                                "description": (
                                    f"방화벽 '{firewall_id}'의 정책 {p_data['policy_id']}에서 "
                                    "출발지를 'ANY'로 설정하여 모든 출발지로부터의 접근을 허용하고 있습니다."
                                ),
                                "recommendation": "출발지를 필요한 IP 또는 네트워크 범위로 제한하세요.",
                            }
                        )
                    elif dst_any:
                        recommendations.append(
                            {
                                "firewall_id": firewall_id,
                                "policy_id": p_data["policy_id"],
                                "severity": "medium",
                                "type": "security_improvement",
                                "issue": "목적지 ANY 설정",
                                "description": (
                                    f"방화벽 '{firewall_id}'의 정책 {p_data['policy_id']}에서 "
                                    "목적지를 'ANY'로 설정하여 모든 목적지로의 접근을 허용하고 있습니다."
                                ),
                                "recommendation": "목적지를 필요한 IP 또는 네트워크 범위로 제한하세요.",
                            }
                        )
                    elif svc_any:
                        recommendations.append(
                            {
                                "firewall_id": firewall_id,
                                "policy_id": p_data["policy_id"],
                                "severity": "medium",
                                "type": "security_improvement",
                                "issue": "서비스 ANY 설정",
                                "description": (
                                    f"방화벽 '{firewall_id}'의 정책 {p_data['policy_id']}에서 "
                                    "서비스를 'ALL'로 설정하여 모든 포트와 프로토콜을 허용하고 있습니다."
                                ),
                                "recommendation": "필요한 특정 서비스(포트/프로토콜)만 허용하도록 제한하세요.",
                            }
                        )

            # 2. 중복 정책 확인 및 정책 통합 제안
            for firewall_id, data in analyzed_firewalls.items():
                if len(data["policies"]) > 1:
                    # 동일 방화벽 내 여러 정책이 동일한 구간에 적용되는 경우 확인
                    zone_policies = {}

                    for p_data in data["policies"]:
                        zone_key = f"{p_data.get('ingress_zone')}_{p_data.get('egress_zone')}"

                        if zone_key not in zone_policies:
                            zone_policies[zone_key] = []

                        zone_policies[zone_key].append(p_data)

                    # 동일 구간에 여러 정책이 적용되는 경우 확인
                    for zone_key, policies in zone_policies.items():
                        if len(policies) > 1:
                            zones = zone_key.split("_")
                            recommendations.append(
                                {
                                    "firewall_id": firewall_id,
                                    "policy_ids": [p.get("policy_id") for p in policies],
                                    "severity": "low",
                                    "type": "performance_improvement",
                                    "issue": "동일 구간 다중 정책",
                                    "description": (
                                        f"방화벽 '{firewall_id}'에서 {zones[0]} -> {zones[1]} 구간에 "
                                        f"{len(policies)}개의 정책이 적용되고 있습니다."
                                    ),
                                    "recommendation": "가능한 경우 유사한 정책들을 하나로 통합하여 성능을 개선하고 관리를 단순화하세요.",
                                }
                            )

            # 3. 방화벽 장비 구간별 인터페이스 규칙 최적화 제안
            for firewall_id, data in analyzed_firewalls.items():
                # 하나의 방화벽이 여러 구간을 관리하는 경우 구간별 규칙 최적화 제안
                if len(data["zones"]) > 2:
                    recommendations.append(
                        {
                            "firewall_id": firewall_id,
                            "severity": "low",
                            "type": "architecture_improvement",
                            "issue": "다중 구간 관리",
                            "description": f"방화벽 '{firewall_id}'가 {', '.join(data['zones'])} 등 여러 구간을 동시에 관리하고 있습니다.",
                            "recommendation": "가능한 경우 구간별로 전용 방화벽을 구성하거나, 인터페이스별 정책 세트를 명확히 분리하세요.",
                        }
                    )

            # 4. 로깅 설정 권장 사항
            for firewall_id, data in analyzed_firewalls.items():
                for p_data in data["policies"]:
                    policy = p_data["policy"]

                    # 로깅 설정 확인 (FortiGate의 경우 logtraffic 필드 확인)
                    logtraffic = policy.get("logtraffic", "")

                    if not logtraffic or logtraffic == "disable":
                        recommendations.append(
                            {
                                "firewall_id": firewall_id,
                                "policy_id": p_data["policy_id"],
                                "severity": "medium",
                                "type": "logging_improvement",
                                "issue": "로그 비활성화",
                                "description": f"방화벽 '{firewall_id}'의 정책 {p_data['policy_id']}에서 트래픽 로깅이 비활성화되어 있습니다.",
                                "recommendation": "보안 감사 및 문제 해결을 위해 중요 정책의 로깅을 활성화하세요.",
                            }
                        )

            return recommendations

        except Exception as e:
            self.logger.error(f"경로 최적화 분석 중 오류: {str(e)}")
            return [
                {
                    "severity": "error",
                    "type": "analysis_error",
                    "issue": "분석 오류",
                    "description": f"경로 최적화 분석 중 오류가 발생했습니다: {str(e)}",
                    "recommendation": "로그를 확인하고 문제를 해결하세요.",
                }
            ]

    def _identify_relevant_firewalls_from_routing(self, src_ip, dst_ip):
        """
        라우팅 테이블을 기반으로 출발지에서 목적지로 가는 경로에 관련된 방화벽 식별
        라우팅 정보가 충분하지 않을 경우 기존 서브넷 기반 방식으로 폴백

        Args:
            src_ip (str): 출발지 IP 주소
            dst_ip (str): 목적지 IP 주소

        Returns:
            list: 관련 방화벽 ID 목록 (라우팅 순서대로)
        """
        try:
            # 데이터가 로드된 모든 방화벽 목록
            all_firewalls = list(self._firewalls.keys())

            # 방화벽이 없는 경우
            if not all_firewalls:
                self.logger.error("로드된 방화벽이 없습니다.")
                return []

            # 방화벽이 하나만 있는 경우
            if len(all_firewalls) == 1:
                return all_firewalls

            # 라우팅 테이블이 비어있는지 확인
            has_routing_data = False
            for firewall_id in all_firewalls:
                if firewall_id in self._routing_tables and self._routing_tables[firewall_id]:
                    has_routing_data = True
                    break

            # 라우팅 테이블이 없으면 기존 서브넷 기반 방식으로 폴백
            if not has_routing_data:
                self.logger.warning("라우팅 테이블 정보가 없어 서브넷 기반 경로 결정으로 전환합니다.")
                return self._identify_relevant_firewalls(
                    src_ip,
                    dst_ip,
                    self._determine_network_zone(src_ip),
                    self._determine_network_zone(dst_ip),
                )

            # 방화벽이 여러 개 있는 경우, 라우팅 테이블 분석 필요
            relevant_firewalls = []

            # 각 방화벽의 라우팅 테이블 분석
            firewalls_with_routing = {}

            # 1. 출발지 IP를 직접 관리하는 방화벽 찾기
            src_firewall_id = None
            for firewall_id in all_firewalls:
                # 출발지 IP에 대한 라우팅 경로 확인
                route = self._find_route_for_ip(src_ip, firewall_id)
                if route:
                    # 출발지 IP가 해당 방화벽에 직접 연결되어 있거나 해당 방화벽이 관리하는 네트워크에 속함
                    if not route.get("gateway"):  # 게이트웨이가 없으면 직접 연결된 네트워크
                        src_firewall_id = firewall_id
                        firewalls_with_routing[firewall_id] = {"src_route": route}
                        break

            # 2. 목적지 IP를 직접 관리하는 방화벽 찾기
            dst_firewall_id = None
            for firewall_id in all_firewalls:
                # 목적지 IP에 대한 라우팅 경로 확인
                route = self._find_route_for_ip(dst_ip, firewall_id)
                if route:
                    # 목적지 IP가 해당 방화벽에 직접 연결되어 있거나 해당 방화벽이 관리하는 네트워크에 속함
                    if not route.get("gateway"):  # 게이트웨이가 없으면 직접 연결된 네트워크
                        dst_firewall_id = firewall_id
                        if firewall_id in firewalls_with_routing:
                            firewalls_with_routing[firewall_id]["dst_route"] = route
                        else:
                            firewalls_with_routing[firewall_id] = {"dst_route": route}
                        break

            # 3. 출발지와 목적지 사이의 라우팅 경로 분석
            # 출발지와 목적지를 모두 관리하는 방화벽이 하나이면 그 방화벽만 반환
            if src_firewall_id and dst_firewall_id and src_firewall_id == dst_firewall_id:
                return [src_firewall_id]

            # 출발지와 목적지가 다른 방화벽에 속하는 경우, 라우팅 경로 찾기
            if src_firewall_id:
                relevant_firewalls.append(src_firewall_id)
            else:
                # 출발지 IP를 관리하는 방화벽을 찾지 못한 경우, 가장 가능성 높은 방화벽 추가
                for firewall_id in all_firewalls:
                    if self._is_ip_managed_by_firewall(src_ip, firewall_id):
                        relevant_firewalls.append(firewall_id)
                        break

                # 여전히 방화벽을 찾지 못한 경우, 첫 번째 방화벽 추가
                if not relevant_firewalls:
                    relevant_firewalls.append(all_firewalls[0])

            # 목적지까지의 라우팅 경로 찾기
            max_hops = 10  # 최대 홉 제한
            visited_firewalls = set(relevant_firewalls)

            for _ in range(max_hops):
                if len(relevant_firewalls) > 0:
                    current_firewall = relevant_firewalls[-1]
                else:
                    # 방화벽이 없으면 처음부터 시작
                    current_firewall = all_firewalls[0]
                    relevant_firewalls.append(current_firewall)
                    visited_firewalls.add(current_firewall)

                # 현재 방화벽에서 목적지까지 라우팅 경로 확인
                next_hop = None
                dst_route = self.get_next_hop(dst_ip, current_firewall)

                if dst_route:
                    # 다음 홉 확인
                    next_hop = dst_route.get("gateway")

                    if not next_hop:
                        # 다음 홉이 없으면 목적지가 현재 방화벽에 직접 연결된 것
                        break

                    # 다음 홉이 목적지 IP인 경우
                    if next_hop == dst_ip:
                        break

                    # 다음 홉을 관리하는 방화벽 찾기
                    next_firewall = None
                    for firewall_id in all_firewalls:
                        if firewall_id != current_firewall and self._is_ip_managed_by_firewall(next_hop, firewall_id):
                            next_firewall = firewall_id
                            break

                    if next_firewall and next_firewall not in visited_firewalls:
                        relevant_firewalls.append(next_firewall)
                        visited_firewalls.add(next_firewall)
                    else:
                        # 다음 방화벽을 찾지 못하거나 이미 방문한 방화벽인 경우
                        break
                else:
                    # 라우팅 경로가 없으면 중단
                    if dst_firewall_id and dst_firewall_id not in visited_firewalls:
                        relevant_firewalls.append(dst_firewall_id)
                    break

            # 목적지를 직접 관리하는 방화벽이 있고 경로에 포함되지 않은 경우 추가
            if dst_firewall_id and dst_firewall_id not in relevant_firewalls:
                relevant_firewalls.append(dst_firewall_id)

            # 경로가 결정되지 않은 경우, 모든 방화벽을 순서대로 사용
            if not relevant_firewalls:
                self.logger.warning("라우팅 경로를 결정할 수 없어 모든 방화벽을 사용합니다.")
                return all_firewalls

            return relevant_firewalls

        except Exception as e:
            self.logger.error(f"라우팅 기반 방화벽 식별 중 오류: {str(e)}")
            import traceback

            self.logger.error(traceback.format_exc())
            return list(self._firewalls.keys())

    def _find_route_for_ip(self, ip, firewall_id="default"):
        """
        특정 IP에 대한 라우팅 경로 찾기

        Args:
            ip (str): IP 주소
            firewall_id (str): 방화벽 식별자

        Returns:
            dict: 라우팅 경로 정보 (없으면 None)
        """
        try:
            if firewall_id not in self._routing_tables:
                self.logger.error(f"방화벽 {firewall_id}의 라우팅 테이블이 로드되지 않았습니다.")
                return None

            ip_addr = ipaddress.ip_address(ip)
            matching_route = None
            longest_prefix = -1

            for route in self._routing_tables[firewall_id]:
                dst = route.get("dst", "0.0.0.0/0")

                # dst 형식이 '192.168.1.0 255.255.255.0'인 경우 CIDR 형식으로 변환
                if " " in dst:
                    ip_part, mask_part = dst.split(" ")
                    try:
                        mask_prefix = sum([bin(int(x)).count("1") for x in mask_part.split(".")])
                        dst = f"{ip_part}/{mask_prefix}"
                    except (ValueError, AttributeError, IndexError):
                        # 형식 변환 실패 시 다음 라우트로
                        continue

                try:
                    route_network = ipaddress.ip_network(dst)
                    if ip_addr in route_network:
                        prefix_len = route_network.prefixlen
                        if prefix_len > longest_prefix:
                            longest_prefix = prefix_len
                            matching_route = route
                except ValueError:
                    # 유효하지 않은 네트워크 형식은 무시
                    continue

            return matching_route

        except Exception as e:
            self.logger.error(f"IP에 대한 라우팅 경로 찾기 중 오류: {str(e)}")
            return None

    def _is_ip_managed_by_firewall(self, ip, firewall_id):
        """
        특정 IP가 방화벽이 관리하는 네트워크에 속하는지 확인

        Args:
            ip (str): IP 주소
            firewall_id (str): 방화벽 식별자

        Returns:
            bool: 관리 여부
        """
        try:
            # 라우팅 테이블에서 직접 연결된 네트워크 확인
            route = self._find_route_for_ip(ip, firewall_id)
            if route and not route.get("gateway"):
                return True

            # 방화벽 인터페이스 정보 확인 (추가 구현 필요)
            # FortiGate API를 통해 인터페이스 정보를 가져와야 함

            return False

        except Exception as e:
            self.logger.error(f"IP 관리 여부 확인 중 오류: {str(e)}")
            return False

    def _find_interface_for_ip(self, ip, firewall_id="default"):
        """
        특정 IP가 속한 인터페이스 찾기
        라우팅 테이블과 인터페이스 정보를 기반으로 결정

        Args:
            ip (str): IP 주소
            firewall_id (str): 방화벽 식별자

        Returns:
            str: 인터페이스 이름 또는 None
        """
        try:
            # 1. 라우팅 테이블에서 해당 IP의 라우팅 정보 조회
            route = self._find_route_for_ip(ip, firewall_id)
            if route and route.get("interface"):
                return route.get("interface")

            # 2. 인터페이스 정보 조회 시도 (실제 구현에서는 API로 조회 필요)
            # 3. 위 정보가 없으면 IP 주소 특성에 따라 추론
            ip_obj = ipaddress.ip_address(ip)

            # 사설 IP 범위 정의
            private_ranges = [
                ipaddress.ip_network("10.0.0.0/8"),
                ipaddress.ip_network("172.16.0.0/12"),
                ipaddress.ip_network("192.168.0.0/16"),
            ]

            # DMZ 범위 정의 (예: 특정 서브넷)
            dmz_ranges = [
                ipaddress.ip_network("10.10.0.0/16"),  # 가정: 10.10.x.x 대역은 DMZ
                ipaddress.ip_network("172.16.10.0/24"),  # 가정: 172.16.10.x 대역은 DMZ
            ]

            # DMZ 범위 확인
            if any(ip_obj in dmz_range for dmz_range in dmz_ranges):
                return "dmz"

            # 일반 사설 IP 확인
            if any(ip_obj in private_range for private_range in private_ranges):
                # IP 대역에 따라 다른 내부 인터페이스 지정
                if ip_obj in ipaddress.ip_network("10.0.0.0/8"):
                    return "port1"  # 가정: port1은 10.x.x.x 대역 담당
                elif ip_obj in ipaddress.ip_network("172.16.0.0/12"):
                    return "port2"  # 가정: port2는 172.16.x.x 대역 담당
                elif ip_obj in ipaddress.ip_network("192.168.0.0/16"):
                    return "port3"  # 가정: port3은 192.168.x.x 대역 담당
                return "internal"

            # 그 외는 외부 IP로 간주
            return "external"

        except Exception as e:
            self.logger.error(f"인터페이스 결정 중 오류: {str(e)}")
            return "unknown"

    # 세션 관리 메서드 (Active Sessions 기능용)

    def get_all_sessions(self):
        """
        모든 경로 분석 세션 정보 반환

        Returns:
            list: 세션 정보 목록
        """
        try:
            sessions_list = []

            for session_id, session_data in self._sessions.items():
                # 세션 상태 및 메타데이터 포함
                session_info = {
                    "id": session_id,
                    "start_time": session_data.get("start_time", ""),
                    "end_time": session_data.get("end_time", ""),
                    "status": session_data.get("status", "unknown"),
                    "src_ip": session_data.get("source_ip", ""),
                    "dst_ip": session_data.get("destination_ip", ""),
                    "port": session_data.get("port", ""),
                    "protocol": session_data.get("protocol", ""),
                    "allowed": session_data.get("allowed", False),
                    "progress": session_data.get("progress", 0),
                }

                sessions_list.append(session_info)

            # 세션 시작 시간 기준 정렬 (최신 순)
            sessions_list.sort(key=lambda x: x.get("start_time", ""), reverse=True)

            return sessions_list

        except Exception as e:
            self.logger.error(f"세션 목록 조회 중 오류: {str(e)}")
            return []

    def get_session_details(self, session_id):
        """
        특정 세션의 상세 정보 반환

        Args:
            session_id (str): 세션 ID

        Returns:
            dict: 세션 상세 정보
        """
        try:
            if session_id not in self._sessions:
                self.logger.warning(f"요청한 세션이 존재하지 않음: {session_id}")
                return None

            session_data = self._sessions[session_id]

            # 기본 세션 정보
            session_details = {
                "id": session_id,
                "start_time": session_data.get("start_time", ""),
                "end_time": session_data.get("end_time", ""),
                "status": session_data.get("status", "unknown"),
                "src_ip": session_data.get("source_ip", ""),
                "dst_ip": session_data.get("destination_ip", ""),
                "port": session_data.get("port", ""),
                "protocol": session_data.get("protocol", ""),
                "allowed": session_data.get("allowed", False),
                "progress": session_data.get("progress", 0),
            }

            # 경로 정보 추가
            if "path" in session_data:
                session_details["path"] = session_data["path"]

            # 차단 정보 추가
            if "blocked_by" in session_data:
                session_details["blocked_by"] = session_data["blocked_by"]

            # 네트워크 경로 추가
            if "network_path" in session_data:
                session_details["network_path"] = session_data["network_path"]

            # 최적화 권장사항 추가
            if "optimization_recommendations" in session_data:
                session_details["optimization_recommendations"] = session_data["optimization_recommendations"]

            return session_details

        except Exception as e:
            self.logger.error(f"세션 상세 정보 조회 중 오류: {str(e)}")
            return None

    def delete_session(self, session_id):
        """
        특정 세션 삭제

        Args:
            session_id (str): 세션 ID

        Returns:
            bool: 삭제 성공 여부
        """
        try:
            if session_id not in self._sessions:
                self.logger.warning(f"삭제할 세션이 존재하지 않음: {session_id}")
                return False

            del self._sessions[session_id]
            self.logger.info(f"세션 삭제 완료: {session_id}")
            return True

        except Exception as e:
            self.logger.error(f"세션 삭제 중 오류: {str(e)}")
            return False
