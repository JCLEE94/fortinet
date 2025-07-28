#!/usr/bin/env python3
"""
보안 스캐너 - 취약점 스캔 및 보안 강화 자동화
CLAUDE.md 지시사항에 따른 완전 자율적 보안 관리 시스템
"""
import hashlib
import json
import logging
import os
import re
import subprocess
import threading
import time
from datetime import datetime
from typing import Any, Callable, Dict, Optional

import psutil

logger = logging.getLogger(__name__)

    class SecurityScanner:
        """보안 스캐너 및 취약점 관리"""

    def __init__(self):
        self.is_scanning = False
        self.scan_thread = None
        self.scan_results = []
            self.vulnerability_database = {}
        self.security_policies = {}
        self.listeners = []

        # 스캔 설정
            self.scan_config = {
                "port_scan": True,
                    "vulnerability_scan": True,
                        "file_integrity_check": True,
                        "network_scan": True,
                            "docker_security_scan": True,
                                "log_analysis": True,
                                    }

        # 보안 기준점
        self.security_baselines = {
            "open_ports": [22, 80, 443, 7777],  # 허용된 포트
                "critical_files": [
                    "/etc/passwd",
                        "/etc/shadow",
                            "/etc/hosts",
                            "/home/jclee/dev/fortinet/.env",
                                "/home/jclee/dev/fortinet/data/config.json",
                                    ],
                                        "suspicious_processes": ["nc", "netcat", "ncat", "socat", "telnet"],
                                        "required_services": ["docker", "ssh"],
                                        "forbidden_users": ["guest", "anonymous"],
                                        }

        # 파일 무결성 체크섬
        self.file_checksums = {}

    def start_continuous_scan(self, interval_hours: int = 6):
        """지속적 보안 스캔 시작"""
        if self.is_scanning:
            logger.warning("보안 스캔이 이미 실행 중입니다")
                return

        self.is_scanning = True
        self.scan_thread = threading.Thread(
                                            target=self._continuous_scan_loop, args=(
                                             interval_hours,), daemon=True)
            self.scan_thread.start()
            logger.info(f"지속적 보안 스캔 시작 (주기: {interval_hours}시간)")

            def stop_scanning(self):
                """보안 스캔 중지"""
        self.is_scanning = False
        if self.scan_thread:
            self.scan_thread.join(timeout=10)
                logger.info("보안 스캔 중지됨")

            def run_full_security_scan(self) -> Dict[str, Any]:
                """전체 보안 스캔 실행"""
        logger.info("전체 보안 스캔 시작")

            scan_result: Dict[str, Any] = {
                "timestamp": datetime.now().isoformat(),
                                          "scan_id": hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:8],
                                                                "results": {},
                                                                    "vulnerabilities": [],
                                                                        "recommendations": [],
                                                      "severity_summary": {"critical": 0, "high": 0, "medium": 0, "low": 0},
                                                          }

        try:
            # 1. 포트 스캔
            if self.scan_config["port_scan"]:
                scan_result["results"]["port_scan"] = self._scan_open_ports()

            # 2. 취약점 스캔
                    if self.scan_config["vulnerability_scan"]:
                        scan_result["results"]["vulnerability_scan"] = self._scan_vulnerabilities(
                                                                                                  )

            # 3. 파일 무결성 검사
                    if self.scan_config["file_integrity_check"]:
                        scan_result["results"]["file_integrity"] = self._check_file_integrity(
                                                                                              )

            # 4. 네트워크 보안 검사
                    if self.scan_config["network_scan"]:
                        scan_result["results"]["network_security"] = self._scan_network_security(
                                                                                                 )

            # 5. Docker 보안 검사
                    if self.scan_config["docker_security_scan"]:
                        scan_result["results"]["docker_security"] = self._scan_docker_security(
                                                                                               )

            # 6. 로그 분석
                    if self.scan_config["log_analysis"]:
                        scan_result["results"]["log_analysis"] = self._analyze_security_logs(
                                                                                             )

            # 7. 시스템 보안 설정 검사
                    scan_result["results"]["system_security"] = self._check_system_security(
                                                                                            )

            # 취약점 분석 및 우선순위 지정
                self._analyze_vulnerabilities(scan_result)

            # 자동 수정 제안
                self._generate_recommendations(scan_result)

            # 결과 저장
                self.scan_results.append(scan_result)

            # 리스너들에게 알림
                self._notify_listeners("scan_completed", scan_result)

                logger.info(
                            f"보안 스캔 완료: {len(scan_result['vulnerabilities'])}개 취약점 발견")

                except Exception as e:
                    logger.error(f"보안 스캔 실패: {e}")
                scan_result["error"] = str(e)

                return scan_result

    def auto_fix_vulnerabilities(
                                 self, scan_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """취약점 자동 수정"""
        if not scan_result:
            # 최신 스캔 결과 사용
            if self.scan_results:
                scan_result = self.scan_results[-1]
                    else:
                        logger.warning("스캔 결과가 없습니다. 먼저 보안 스캔을 실행하세요.")
                    return {"status": "error",
                        "message": "No scan results available"}

        fix_results = {
            "timestamp": datetime.now().isoformat(),
                                      "fixed_vulnerabilities": [],
                                          "failed_fixes": [],
                                              "manual_intervention_required": [],
                                                  }

        for vuln in scan_result.get("vulnerabilities", []):
            if vuln.get("auto_fixable", False):
                success = self._auto_fix_vulnerability(vuln)

                    if success:
                        fix_results["fixed_vulnerabilities"].append(vuln)
                        logger.info(f"취약점 자동 수정 완료: {vuln['title']}")
                        else:
                            fix_results["failed_fixes"].append(vuln)
                        logger.error(f"취약점 자동 수정 실패: {vuln['title']}")
                        else:
                            fix_results["manual_intervention_required"].append(
                                                                               vuln)

        # 수정 결과 알림
                    self._notify_listeners("auto_fix_completed", fix_results)

            return fix_results

    def harden_system(self) -> Dict[str, Any]:
        """시스템 보안 강화"""
        logger.info("시스템 보안 강화 시작")

            hardening_results = {
                "timestamp": datetime.now().isoformat(),
                                          "applied_settings": [],
                                              "failed_settings": [],
                                              "recommendations": [],
                                                  }

        # 보안 강화 설정 적용
        hardening_actions = [
            ("disable_unused_services", self._disable_unused_services),
             ("configure_firewall", self._configure_firewall),
              ("secure_ssh_config", self._secure_ssh_config),
               ("set_file_permissions", self._set_secure_file_permissions),
                ("configure_docker_security", self._configure_docker_security),
                    ("enable_audit_logging", self._enable_audit_logging),
                        ("configure_fail2ban", self._configure_fail2ban),
                            ]

        for action_name, action_func in hardening_actions:
            try:
                _result = action_func()
                    if _result:
                        hardening_results["applied_settings"].append(
                                                                     {
                                                                     "action": action_name, "status": "success", "details": _result}
                                                                 )
                else:
                    hardening_results["failed_settings"].append(
                                                                {"action": action_name, "status": "failed"})
                        except Exception as e:
                            logger.error(f"보안 강화 실패 ({action_name}): {e}")
                                        hardening_results["failed_settings"].append(
                                                                                    {"action": action_name,
                                                                                        "status": "error",
                                                                                            "error": str(e)}
                    )

                    logger.info("시스템 보안 강화 완료")
            return hardening_results

    def get_security_dashboard(self) -> Dict:
        """보안 대시보드 데이터"""
        if not self.scan_results:
            return {
                "status": "no_data",
                    "message": "No security scan results available",
                        }

        latest_scan = self.scan_results[-1]

            return {
                "last_scan": latest_scan["timestamp"],
                    "scan_id": latest_scan["scan_id"],
                        "total_vulnerabilities": len(latest_scan["vulnerabilities"]),
                                                 "severity_breakdown": latest_scan["severity_summary"],
                                                     "critical_issues": [v for v in latest_scan["vulnerabilities"] if v.get("severity") == "critical"],
                                                                                                                            "system_health": self._get_security_health_score(latest_scan),
                                                                                                                                                                             "trending": self._get_security_trends(),
                                                                                                                                                                                                                   "recommendations": latest_scan.get(
                                                                                                                                                                                                                     "recommendations",
                                                                                                                                                                                                                         [])[:5]
                                                                                 )
                                                                         }

    def _continuous_scan_loop(self, interval_hours: int):
        """지속적 스캔 루프"""
        logger.info("지속적 보안 스캔 루프 시작")

            while self.is_scanning:
                try:
                    # 전체 보안 스캔 실행
                scan_result = self.run_full_security_scan()

                # 중요한 취약점이 발견되면 자동 수정 시도
                    critical_vulns = [
                        v
                    for v in scan_result.get("vulnerabilities", [])
                        if v.get("severity") == "critical" and v.get("auto_fixable", False)
                        ]

                if critical_vulns:
                    logger.warning(f"{len(critical_vulns)}개 중요 취약점 발견, 자동 수정 시도")
                        self.auto_fix_vulnerabilities(scan_result)

                # 다음 스캔까지 대기
                        time.sleep(interval_hours * 3600)

                    except Exception as e:
                        logger.error(f"지속적 스캔 루프 오류: {e}")
                    time.sleep(3600)  # 1시간 대기 후 재시도

                    logger.info("지속적 보안 스캔 루프 종료")

            def _scan_open_ports(self) -> Dict:
                """오픈 포트 스캔"""
        try:
            _result = subprocess.run(["netstat", "-tlnp"], capture_output=True, text=True, timeout=30)

                open_ports = []
                unauthorized_ports = []

                for line in _result.stdout.split("\n"):
                    if "LISTEN" in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            address = parts[3]
                            if ":" in address:
                                port = int(address.split(":")[-1])
                                open_ports.append(port)

                                if port not in self.security_baselines["open_ports"]:
                                    unauthorized_ports.append(port)

                                    return {
                                        "open_ports": open_ports,
                                            "unauthorized_ports": unauthorized_ports,
                                                "status": "safe" if not unauthorized_ports else "warning",
                            }

        except Exception as e:
            logger.error(f"포트 스캔 실패: {e}")
                return {"error": str(e)}

                def _scan_vulnerabilities(self) -> Dict:
                    """시스템 취약점 스캔"""
        vulnerabilities = []

            try:
                # 1. 패키지 업데이트 확인
            _result = subprocess.run(
                                     ["apt", "list", "--upgradable"],
                                         capture_output=True,
                                             text=True,
                                                 timeout=60,
                                                     )

            if _result.stdout:
                outdated_packages = len(_result.stdout.split("\n")) - 1
                    if outdated_packages > 0:
                        vulnerabilities.append(
                                               {
                                               "type": "outdated_packages",
                                                   "severity": "medium",
                                                       "count": outdated_packages,
                                        "description": f"{outdated_packages}개 패키지 업데이트 필요",
                                            }
                                        )

            # 2. 시스템 사용자 확인
            with open("/etc/passwd", "r") as f:
                users = f.read()

                    for forbidden_user in self.security_baselines["forbidden_users"]:
                        if forbidden_user in users:
                            vulnerabilities.append(
                                           {
                                               "type": "forbidden_user",
                                                   "severity": "high",
                                                       "user": forbidden_user,
                                        "description": f"금지된 사용자 계정 발견: {forbidden_user}",
                                            }
                                        )

            # 3. 의심스러운 프로세스 확인
            for proc in psutil.process_iter(["name"]):
                if proc.info["name"] in self.security_baselines["suspicious_processes"]:
                    vulnerabilities.append(
                                           {
                                               "type": "suspicious_process",
                                                   "severity": "high",
                                                       "process": proc.info["name"],
                                        "description": f'의심스러운 프로세스 실행 중: {proc.info["name"]}',
                                            }
                                        )

            return {
                "vulnerabilities": vulnerabilities,
                    "total_count": len(vulnerabilities),
                                       }

        except Exception as e:
            logger.error(f"취약점 스캔 실패: {e}")
                return {"error": str(e)}

                def _check_file_integrity(self) -> Dict:
                    """파일 무결성 검사"""
        integrity_issues = []

            try:
                for file_path in self.security_baselines["critical_files"]:
                    if os.path.exists(file_path):
                    # 파일 해시 계산
                    with open(file_path, "rb") as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()

                    # 이전 해시와 비교
                            if file_path in self.file_checksums:
                                if self.file_checksums[file_path] != file_hash:
                                    integrity_issues.append(
                                                    {
                                                        "file": file_path,
                                                            "issue": "modified",
                                                                "severity": "high",
                                                }
                                                )
                    else:
                        # 첫 번째 스캔 시 기준점 설정
                        self.file_checksums[file_path] = file_hash

                    # 파일 권한 확인
                            stat = os.stat(file_path)
                        permissions = oct(stat.st_mode)[-3:]

                    # 중요 파일이 너무 관대한 권한을 가지는지 확인
                        if file_path in ["/etc/passwd", "/etc/shadow"]:
                            if permissions != "644" and permissions != "640":
                                integrity_issues.append(
                                                    {
                                                        "file": file_path,
                                                            "issue": "insecure_permissions",
                                                                "permissions": permissions,
                                                "severity": "medium",
                                                    }
                                                )
                else:
                    integrity_issues.append({"file": file_path, "issue": "missing", "severity": "medium"})

                        return {
                            "integrity_issues": integrity_issues,
                                "files_checked": len(self.security_baselines["critical_files"]),
                                                     "issues_found": len(integrity_issues),
                                                             }

        except Exception as e:
            logger.error(f"파일 무결성 검사 실패: {e}")
                return {"error": str(e)}

                def _scan_network_security(self) -> Dict:
                    """네트워크 보안 검사"""
        network_issues = []

            try:
                # 1. 방화벽 상태 확인
            try:
                _result = subprocess.run(["ufw", "status"], capture_output=True, text=True, timeout=10)

                    if "inactive" in _result.stdout.lower():
                        network_issues.append(
                                              {
                                              "type": "firewall_disabled",
                                                  "severity": "high",
                                                      "description": "UFW 방화벽이 비활성화됨",
                                        }
                                        )
            except Exception:
                pass

            # 2. SSH 설정 확인
            if os.path.exists("/etc/ssh/sshd_config"):
                with open("/etc/ssh/sshd_config", "r") as f:
                    ssh_config = f.read()

                # 루트 로그인 허용 여부
                        if "PermitRootLogin yes" in ssh_config:
                            network_issues.append(
                                                  {
                                              "type": "ssh_root_login",
                                                  "severity": "high",
                                                      "description": "SSH 루트 로그인이 허용됨",
                                        }
                                        )

                # 패스워드 인증 허용 여부
                if "PasswordAuthentication yes" in ssh_config:
                    network_issues.append(
                                          {
                                              "type": "ssh_password_auth",
                                                  "severity": "medium",
                                                      "description": "SSH 패스워드 인증이 허용됨",
                                        }
                                        )

            # 3. 네트워크 연결 확인
            connections = psutil.net_connections()
                external_connections = [conn for conn in connections if conn.status == "ESTABLISHED" and conn.raddr]

                suspicious_connections = []
                for conn in external_connections:
                    if conn.raddr.ip not in ["127.0.0.1", "::1"]:
                        # 외부 연결 중 의심스러운 것들 확인
                    if conn.raddr.port in [23, 135, 139, 445]:  # 의심스러운 포트
                        suspicious_connections.append(conn)

                            if suspicious_connections:
                                network_issues.append(
                                                      {
                                          "type": "suspicious_connections",
                                              "severity": "medium",
                                                  "count": len(suspicious_connections),
                                             "description": f"{len(suspicious_connections)}개 의심스러운 외부 연결",
                                                                   }
                                                      )

            return {
                "network_issues": network_issues,
                    "external_connections": len(external_connections),
                                                "suspicious_connections": len(suspicious_connections),
                                                                              }

        except Exception as e:
            logger.error(f"네트워크 보안 검사 실패: {e}")
                return {"error": str(e)}

                def _scan_docker_security(self) -> Dict:
                    """Docker 보안 검사"""
        docker_issues = []

            try:
                # Docker 컨테이너 보안 검사
            _result = subprocess.run(
                                     ["docker", "ps", "--format", "json"],
                                         capture_output=True,
                                             text=True,
                                                 timeout=30,
                                                     )

            if _result.returncode == 0:
                containers = []
                    for line in _result.stdout.strip().split("\n"):
                        if line:
                            containers.append(json.loads(line))

                            for container in containers:
                                container_name = container.get("Names", "")

                    # 컨테이너 권한 검사
                        inspect_result = subprocess.run(
                                                        ["docker", "inspect", container_name],
                                                            capture_output=True,
                                                                text=True,
                                                                timeout=10,
                                                                    )

                    if inspect_result.returncode == 0:
                        inspect_data = json.loads(inspect_result.stdout)[0]

                        # Privileged 모드 검사
                            if inspect_data.get("HostConfig", {}).get("Privileged", False):
                                docker_issues.append(
                                                     {
                                                     "type": "privileged_container",
                                                         "severity": "high",
                                                             "container": container_name,
                                                "description": f"컨테이너가 privileged 모드로 실행 중: {container_name}",
                                                    }
                                                )

                        # 호스트 네트워크 모드 검사
                        network_mode = inspect_data.get("HostConfig", {}).get("NetworkMode", "")
                            if network_mode == "host":
                                docker_issues.append(
                                                     {
                                                     "type": "host_network_mode",
                                                         "severity": "medium",
                                                             "container": container_name,
                                                "description": f"컨테이너가 호스트 네트워크 모드 사용: {container_name}",
                                                    }
                                                )

            return {
                "docker_issues": docker_issues,
                    "containers_checked": (len(containers) if "containers" in locals() else 0),
                                           }

        except Exception as e:
            logger.error(f"Docker 보안 검사 실패: {e}")
                return {"error": str(e)}

                def _analyze_security_logs(self) -> Dict:
                    """보안 로그 분석"""
        security_events = []

            try:
                # 시스템 로그 분석
            log_files = [
                "/var/log/auth.log",
                    "/var/log/syslog",
                        "/home/jclee/dev/fortinet/logs/app.log",
                            ]

            suspicious_patterns = [
                r"Failed password",
                    r"Invalid user",
                        r"Connection closed by",
                            r"ERROR",
                                r"CRITICAL",
                                    r"authentication failure",
                                        ]

            for log_file in log_files:
                if os.path.exists(log_file):
                    try:
                        with open(log_file, "r") as f:
                            recent_lines = f.readlines()[-1000:]  # 최근 1000줄만

                                for line in recent_lines:
                                    for pattern in suspicious_patterns:
                                        if re.search(pattern, line, re.IGNORECASE):
                                    security_events.append(
                                                           {
                                                               "log_file": log_file,
                                                                   "pattern": pattern,
                                                                       "line": line.strip(),
                                                                       "timestamp": datetime.now().isoformat(),
                                                                                                 }
                                                                              )
                                    break
                    except Exception:
                        continue

            return {
                "security_events": security_events,
                    "events_count": len(security_events),
                                        "log_files_checked": len([f for f in log_files if os.path.exists(f)]),
                                                                 }

        except Exception as e:
            logger.error(f"보안 로그 분석 실패: {e}")
                return {"error": str(e)}

                def _check_system_security(self) -> Dict:
                    """시스템 보안 설정 검사"""
        security_config = {}

        try:
            # 1. 필수 서비스 실행 상태
            running_services = []
                for service in self.security_baselines["required_services"]:
                    try:
                        _result = subprocess.run(
                                             ["systemctl", "is-active", service],
                                                 capture_output=True,
                                                     text=True,
                                                         timeout=5,
                                                             )
                    running_services.append(
                                            {
                                                "service": service,
                                                    "status": _result.stdout.strip(),
                                                                                   "running": result.stdout.strip() == "active",
                                                                                              }
                                                                   )
                except Exception:
                    running_services.append({"service": service, "status": "unknown", "running": False})

                        security_config["services"] = running_services

            # 2. 시스템 업데이트 상태
                try:
                    _result = subprocess.run(
                                             ["apt", "list", "--upgradable"],
                                                 capture_output=True,
                                                 text=True,
                                                     timeout=30,
                                                         )
                upgradable_count = len(_result.stdout.split("\n")) - 1
                    security_config["system_updates"] = {
                        "upgradable_packages": max(0, upgradable_count),
                                                   "up_to_date": upgradable_count <= 1,
                                                       }
            except Exception:
                security_config["system_updates"] = {"error": "Unable to check updates"}

            # 3. 디스크 암호화 상태 (간단한 확인)
                    try:
                        _result = subprocess.run(["lsblk", "-"], capture_output=True, text=True, timeout=10)
                    security_config["disk_encryption"] = {
                        "encrypted_partitions": "crypt" in _result.stdout,
                            "details": (_result.stdout if "crypt" in _result.stdout else "No encrypted partitions found"),
                                        }
            except Exception:
                security_config["disk_encryption"] = {"error": "Unable to check disk encryption"}

                    return security_config

        except Exception as e:
            logger.error(f"시스템 보안 검사 실패: {e}")
                return {"error": str(e)}

                def _analyze_vulnerabilities(self, scan_result: Dict):
                    """취약점 분석 및 우선순위 지정"""
        vulnerabilities = []

        # 각 스캔 결과에서 취약점 추출
            for scan_type, result in scan_result["results"].items():
                if scan_type == "port_scan" and result.get("unauthorized_ports"):
                    for port in result["unauthorized_ports"]:
                    vulnerabilities.append(
                                           {
                                               "id": f"open_port_{port}",
                                                   "title": f"승인되지 않은 포트 개방: {port}",
                                                       "severity": "medium",
                                        "type": "network",
                                            "auto_fixable": False,
                                                "description": f"포트 {port}가 보안 정책에 위배되어 개방되어 있습니다.",
                                                    "recommendation": f"포트 {port}를 차단하거나 보안 정책을 업데이트하세요.",
                                                    }
                                        )

            elif scan_type == "vulnerability_scan":
                for vuln in result.get("vulnerabilities", []):
                    vulnerabilities.append(
                                           {
                                               "id": f"{vuln['type']}_{vuln.get('count', 1)}",
                                                                                "title": vuln["description"],
                                                                                    "severity": vuln["severity"],
                                                                                        "type": "system",
                                                                         "auto_fixable": vuln["type"] == "outdated_packages",
                                                                             "description": vuln["description"],
                                                    "recommendation": self._get_vulnerability_recommendation(vuln),
                                                                                                         }
                                                                                             )

            elif scan_type == "file_integrity":
                for issue in result.get("integrity_issues", []):
                    severity = "critical" if issue["issue"] == "modified" else "medium"
                        vulnerabilities.append(
                                               {
                                                   "id": f"file_integrity_{issue['file']}",
                                                       "title": f"파일 무결성 문제: {issue['file']}",
                                                       "severity": severity,
                                        "type": "integrity",
                                            "auto_fixable": issue["issue"] == "insecure_permissions",
                                                "description": f"파일 {issue['file']}에서 {issue['issue']} 문제 발견",
                                                    "recommendation": f"파일 {issue['file']}의 상태를 검토하고 복구하세요.",
                                                    }
                                        )

            elif scan_type == "network_security":
                for issue in result.get("network_issues", []):
                    vulnerabilities.append(
                                           {
                                               "id": f"network_{issue['type']}",
                                                   "title": issue["description"],
                                                       "severity": issue["severity"],
                                        "type": "network",
                                            "auto_fixable": issue["type"] in ["firewall_disabled"],
                                                "description": issue["description"],
                                                    "recommendation": self._get_network_recommendation(issue["type"]),
                                                                                                   }
                                                                                       )

            elif scan_type == "docker_security":
                for issue in result.get("docker_issues", []):
                    vulnerabilities.append(
                                           {
                                               "id": f"docker_{issue['type']}_{issue['container']}",
                                                   "title": issue["description"],
                                                       "severity": issue["severity"],
                                        "type": "container",
                                            "auto_fixable": False,
                                                "description": issue["description"],
                                                    "recommendation": f"컨테이너 {issue['container']}의 보안 설정을 검토하세요.",
                                                    }
                                        )

        # 심각도별 집계
        for vuln in vulnerabilities:
            scan_result["severity_summary"][vuln["severity"]] += 1

                scan_result["vulnerabilities"] = vulnerabilities

            def _generate_recommendations(self, scan_result: Dict):
                """보안 개선 권장사항 생성"""
        recommendations = []

        # 취약점 기반 권장사항
            critical_vulns = [v for v in scan_result["vulnerabilities"] if v["severity"] == "critical"]
            high_vulns = [v for v in scan_result["vulnerabilities"] if v["severity"] == "high"]

            if critical_vulns:
                recommendations.append(
                                       {
                                       "priority": "urgent",
                                           "title": f"{len(critical_vulns)}개 중요 취약점 즉시 해결",
                                                           "description": "중요 취약점이 발견되었습니다. 즉시 해결이 필요합니다.",
                                                               "action": "auto_fix_critical_vulnerabilities",
                                                }
                                )

        if high_vulns:
            recommendations.append(
                                   {
                                       "priority": "high",
                                           "title": f"{len(high_vulns)}개 높은 위험도 취약점 해결",
                                                           "description": "높은 위험도 취약점이 발견되었습니다.",
                                                               "action": "review_high_risk_vulnerabilities",
                                                }
                                )

        # 시스템 강화 권장사항
        recommendations.append(
                               {
                                   "priority": "medium",
                                       "title": "시스템 보안 강화",
                                           "description": "전반적인 시스템 보안을 강화하세요.",
                            "action": "run_security_hardening",
                                }
                            )

        # 정기 스캔 권장사항
        recommendations.append(
                               {
                                   "priority": "low",
                                       "title": "정기적 보안 스캔 설정",
                                           "description": "정기적인 보안 스캔을 설정하여 지속적인 보안 관리를 하세요.",
                            "action": "setup_continuous_scanning",
                                }
                            )

        scan_result["recommendations"] = recommendations

            def _auto_fix_vulnerability(self, vulnerability: Dict) -> bool:
                """개별 취약점 자동 수정"""
        try:
            vuln_type = vulnerability.get("type")

                if vuln_type == "system" and "outdated_packages" in vulnerability["id"]:
                    # 패키지 업데이트
                _result = subprocess.run(
                                         ["sudo", "apt", "upgrade", "-y"],
                                             capture_output=True,
                                                 text=True,
                                                     timeout=300,
                                                         )
                return _result.returncode == 0

            elif vuln_type == "integrity" and "insecure_permissions" in vulnerability["id"]:
                # 파일 권한 수정
                file_path = vulnerability["id"].split("_")[-1]
                    _result = subprocess.run(
                                             ["sudo", "chmod", "644", file_path],
                                                 capture_output=True,
                                                     text=True,
                                                     timeout=10,
                                                         )
                return _result.returncode == 0

            elif vuln_type == "network" and "firewall_disabled" in vulnerability["id"]:
                # 방화벽 활성화
                _result = subprocess.run(
                                         ["sudo", "ufw", "--force", "enable"],
                                             capture_output=True,
                                                 text=True,
                                                     timeout=10,
                                                         )
                return _result.returncode == 0

        except Exception as e:
            logger.error(f"취약점 자동 수정 실패: {e}")

                return False

    def _get_vulnerability_recommendation(self, vuln: Dict) -> str:
        """취약점별 권장사항 반환"""
        vuln_type = vuln["type"]

            if vuln_type == "outdated_packages":
                return "시스템 패키지를 최신 버전으로 업데이트하세요: sudo apt upgrade"
        elif vuln_type == "forbidden_user":
            return f"금지된 사용자 계정을 삭제하세요: sudo userdel {vuln.get('user', '')}"
                elif vuln_type == "suspicious_process":
            return "의심스러운 프로세스를 종료하고 원인을 조사하세요"
        else:
            return "해당 취약점에 대한 보안 정책을 검토하고 적절한 조치를 취하세요."

    def _get_network_recommendation(self, issue_type: str) -> str:
        """네트워크 문제별 권장사항 반환"""
        recommendations = {
            "firewall_disabled": "UFW 방화벽을 활성화하세요: sudo ufw enable",
                "ssh_root_login": "SSH 설정에서 루트 로그인을 금지하세요: PermitRootLogin no",
                    "ssh_password_auth": "SSH 키 인증으로 전환하고 패스워드 인증을 비활성화하세요",
                        "suspicious_connections": "의심스러운 네트워크 연결을 조사하고 필요시 차단하세요",
                            }

        return recommendations.get(issue_type, "네트워크 보안 설정을 검토하세요.")

            def _get_security_health_score(self, scan_result: Dict) -> int:
                """보안 건강도 점수 계산 (0-100)"""
            total_vulns = len(scan_result["vulnerabilities"])

            if total_vulns == 0:
                return 100

        # 심각도별 가중치
        weights = {"critical": 25, "high": 15, "medium": 5, "low": 1}
        total_score = sum(
                          scan_result["severity_summary"].get(
                                                              severity,
                                                                  0) * weight for severity,
                                                                      weight in weights.items(
                                                              )
                          )

        # 100점 만점으로 환산 (점수가 높을수록 나쁨)
        health_score = max(0, 100 - total_score)

            return health_score

    def _get_security_trends(self) -> Dict:
        """보안 트렌드 분석"""
        if len(self.scan_results) < 2:
            return {"trend": "insufficient_data"}

        current = self.scan_results[-1]
            previous = self.scan_results[-2]

            current_score = self._get_security_health_score(current)
            previous_score = self._get_security_health_score(previous)

            trend = "stable"
        if current_score > previous_score + 5:
            trend = "improving"
        elif current_score < previous_score - 5:
            trend = "degrading"

        return {
            "trend": trend,
                "current_score": current_score,
                    "previous_score": previous_score,
                        "change": current_score - previous_score,
                            }

    def _disable_unused_services(self) -> Dict:
        """사용하지 않는 서비스 비활성화"""
        # 여기서는 시뮬레이션만 수행
        return {"action": "disable_unused_services", "status": "simulated"}

    def _configure_firewall(self) -> Dict:
        """방화벽 설정"""
        try:
            # UFW 기본 설정
            subprocess.run(["sudo", "ufw", "--force", "reset"], timeout=10)
                subprocess.run(["sudo", "ufw", "default", "deny", "incoming"], timeout=10)
                subprocess.run(["sudo", "ufw", "default", "allow", "outgoing"], timeout=10)

            # 필요한 포트 허용
                for port in self.security_baselines["open_ports"]:
                    subprocess.run(["sudo", "ufw", "allow", str(port)], timeout=10)

            # 방화벽 활성화
                    subprocess.run(["sudo", "ufw", "--force", "enable"], timeout=10)

                return {"action": "configure_firewall", "status": "success"}
        except Exception as e:
            return {"action": "configure_firewall", "status": "failed", "error": str(e)}

                def _secure_ssh_config(self) -> Dict:
                    """SSH 보안 설정"""
        # 여기서는 시뮬레이션만 수행 (실제 환경에서는 신중하게 적용)
        return {"action": "secure_ssh_config", "status": "simulated"}

    def _set_secure_file_permissions(self) -> Dict:
        """보안 파일 권한 설정"""
        try:
            # 중요 파일 권한 설정
            secure_permissions = {
                "/etc/passwd": "644",
                    "/etc/shadow": "640",
                        "/etc/hosts": "644",
                            }

            for file_path, permissions in secure_permissions.items():
                if os.path.exists(file_path):
                    subprocess.run(["sudo", "chmod", permissions, file_path], timeout=10)

                        return {"action": "set_secure_file_permissions", "status": "success"}
        except Exception as e:
            return {
                "action": "set_secure_file_permissions",
                    "status": "failed",
                        "error": str(e),
                                     }

    def _configure_docker_security(self) -> Dict:
        """Docker 보안 설정"""
        # Docker 보안 설정은 복잡하므로 시뮬레이션
        return {"action": "configure_docker_security", "status": "simulated"}

    def _enable_audit_logging(self) -> Dict:
        """감사 로깅 활성화"""
        # 감사 로깅 설정은 시뮬레이션
        return {"action": "enable_audit_logging", "status": "simulated"}

    def _configure_fail2ban(self) -> Dict:
        """Fail2ban 설정"""
        try:
            # Fail2ban 설치 확인
            _result = subprocess.run(["which", "fail2ban-server"], capture_output=True)

                if _result.returncode != 0:
                    # 설치되지 않은 경우
                return {"action": "configure_fail2ban", "status": "not_installed"}
            else:
                # 서비스 활성화
                subprocess.run(["sudo", "systemctl", "enable", "fail2ban"], timeout=10)
                    subprocess.run(["sudo", "systemctl", "start", "fail2ban"], timeout=10)
                    return {"action": "configure_fail2ban", "status": "success"}

        except Exception as e:
            return {"action": "configure_fail2ban", "status": "failed", "error": str(e)}

                def add_listener(self, callback: Callable):
                    """보안 이벤트 리스너 추가"""
        if callback not in self.listeners:
            self.listeners.append(callback)

                def _notify_listeners(self, event_type: str, data: Dict):
                    """리스너들에게 이벤트 알림"""
        for listener in self.listeners[:]:
            try:
                listener(event_type, data)
                    except Exception as e:
                        logger.error(f"보안 스캐너 리스너 호출 실패: {e}")
                    self.listeners.remove(listener)

# 전역 인스턴스
                    _global_security_scanner = None

def get_security_scanner() -> SecurityScanner:
    """전역 보안 스캐너 반환"""
    global _global_security_scanner
    if _global_security_scanner is None:
        _global_security_scanner = SecurityScanner()
            return _global_security_scanner

if __name__ == "__main__":
    # 테스트 코드
    scanner = SecurityScanner()

        def test_listener(event_type, data):
            print(f"보안 이벤트: {event_type}")
            if event_type == "scan_completed":
                print(f"취약점 {len(data['vulnerabilities'])}개 발견")

                scanner.add_listener(test_listener)

    # 전체 보안 스캔 실행
        _result = scanner.run_full_security_scan()
        print(f"보안 스캔 완료: {json.dumps(_result, indent=2, ensure_ascii=False)}")

    # 자동 수정 시도
        fix_result = scanner.auto_fix_vulnerabilities()
        print(f"자동 수정 결과: {json.dumps(fix_result, indent=2, ensure_ascii=False)}")

    # 시스템 강화
        harden_result = scanner.harden_system()
        print(f"시스템 강화 결과: {json.dumps(harden_result, indent=2, ensure_ascii=False)}")

    # 보안 대시보드
        dashboard = scanner.get_security_dashboard()
        print(f"보안 대시보드: {json.dumps(dashboard, indent=2, ensure_ascii=False)}")
