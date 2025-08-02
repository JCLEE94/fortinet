#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
애플리케이션 프로토콜 분석기 (SSH, MQTT, FTP, SMTP 등)
고레벨 애플리케이션 프로토콜 분석 및 보안 검사
"""

import logging
import re
import struct
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ApplicationAnalyzer:
    """애플리케이션 프로토콜 분석기"""

    # 애플리케이션 포트 매핑
    APPLICATION_PORTS = {
        21: "FTP",
        22: "SSH",
        23: "TELNET",
        25: "SMTP",
        53: "DNS",
        69: "TFTP",
        79: "FINGER",
        80: "HTTP",
        110: "POP3",
        119: "NNTP",
        143: "IMAP",
        161: "SNMP",
        194: "IRC",
        389: "LDAP",
        443: "HTTPS",
        445: "SMB",
        993: "IMAPS",
        995: "POP3S",
        1883: "MQTT",
        8883: "MQTT-TLS",
        5432: "POSTGRESQL",
        3306: "MYSQL",
        1433: "MSSQL",
        1521: "ORACLE",
        6379: "REDIS",
        27017: "MONGODB",
    }

    # SSH 메시지 타입
    SSH_MSG_TYPES = {
        1: "SSH_MSG_DISCONNECT",
        2: "SSH_MSG_IGNORE",
        3: "SSH_MSG_UNIMPLEMENTED",
        4: "SSH_MSG_DEBUG",
        5: "SSH_MSG_SERVICE_REQUEST",
        6: "SSH_MSG_SERVICE_ACCEPT",
        20: "SSH_MSG_KEXINIT",
        21: "SSH_MSG_NEWKEYS",
        30: "SSH_MSG_KEXDH_INIT",
        31: "SSH_MSG_KEXDH_REPLY",
        50: "SSH_MSG_USERAUTH_REQUEST",
        51: "SSH_MSG_USERAUTH_FAILURE",
        52: "SSH_MSG_USERAUTH_SUCCESS",
        53: "SSH_MSG_USERAUTH_BANNER",
        60: "SSH_MSG_USERAUTH_PK_OK",
        90: "SSH_MSG_CHANNEL_OPEN",
        91: "SSH_MSG_CHANNEL_OPEN_CONFIRMATION",
        92: "SSH_MSG_CHANNEL_OPEN_FAILURE",
        93: "SSH_MSG_CHANNEL_WINDOW_ADJUST",
        94: "SSH_MSG_CHANNEL_DATA",
        95: "SSH_MSG_CHANNEL_EXTENDED_DATA",
        96: "SSH_MSG_CHANNEL_EOF",
        97: "SSH_MSG_CHANNEL_CLOSE",
        98: "SSH_MSG_CHANNEL_REQUEST",
        99: "SSH_MSG_CHANNEL_SUCCESS",
        100: "SSH_MSG_CHANNEL_FAILURE",
    }

    # MQTT 메시지 타입
    MQTT_MSG_TYPES = {
        1: "CONNECT",
        2: "CONNACK",
        3: "PUBLISH",
        4: "PUBACK",
        5: "PUBREC",
        6: "PUBREL",
        7: "PUBCOMP",
        8: "SUBSCRIBE",
        9: "SUBACK",
        10: "UNSUBSCRIBE",
        11: "UNSUBACK",
        12: "PINGREQ",
        13: "PINGRESP",
        14: "DISCONNECT",
    }

    def __init__(self):
        self.sessions = {}  # 세션 추적
        self.protocols_detected = {}  # 감지된 프로토콜

    def analyze(self, packet_data: bytes, packet_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        애플리케이션 패킷 분석

        Args:
            packet_data: 패킷 데이터
            packet_info: 패킷 기본 정보

        Returns:
            dict: 애플리케이션 분석 결과
        """
        try:
            analysis = {
                "protocols": [],
                "application_data": {},
                "security_issues": [],
                "session_info": {},
                "timestamp": packet_info.get("timestamp", datetime.now().isoformat()),
            }

            # 포트 기반 프로토콜 식별
            src_port = packet_info.get("src_port")
            dst_port = packet_info.get("dst_port")

            identified_protocol = None
            if dst_port in self.APPLICATION_PORTS:
                identified_protocol = self.APPLICATION_PORTS[dst_port]
            elif src_port in self.APPLICATION_PORTS:
                identified_protocol = self.APPLICATION_PORTS[src_port]

            # 페이로드 추출
            payload = self._extract_payload(packet_data, packet_info)
            if not payload:
                return analysis

            # 프로토콜별 분석
            if identified_protocol:
                analysis["protocols"].append(identified_protocol)
                app_analysis = self._analyze_protocol(identified_protocol, payload, packet_info)
                if app_analysis:
                    analysis["application_data"] = app_analysis

            # 프로토콜 패턴 기반 자동 감지
            detected_protocols = self._detect_protocols_by_pattern(payload)
            for proto in detected_protocols:
                if proto not in analysis["protocols"]:
                    analysis["protocols"].append(proto)
                    proto_analysis = self._analyze_protocol(proto, payload, packet_info)
                    if proto_analysis:
                        analysis["application_data"][proto.lower()] = proto_analysis

            # 세션 정보 업데이트
            session_info = self._update_session_info(analysis, packet_info)
            analysis["session_info"] = session_info

            # 보안 검사
            security_issues = self._check_application_security(analysis, payload, packet_info)
            analysis["security_issues"] = security_issues

            return analysis

        except Exception as e:
            logger.error(f"애플리케이션 분석 오류: {e}")
            return {
                "error": str(e),
                "timestamp": packet_info.get("timestamp", datetime.now().isoformat()),
            }

    def _extract_payload(self, packet_data: bytes, packet_info: Dict[str, Any]) -> Optional[bytes]:
        """애플리케이션 페이로드 추출"""
        try:
            # IP 헤더 길이 계산
            if len(packet_data) < 20:
                return None

            ip_header_length = (packet_data[0] & 0xF) * 4

            # TCP/UDP 헤더 건너뛰기
            protocol = packet_info.get("protocol")
            if protocol == "TCP":
                if len(packet_data) < ip_header_length + 20:
                    return None
                tcp_header_length = ((packet_data[ip_header_length + 12] >> 4) & 0xF) * 4
                payload_start = ip_header_length + tcp_header_length
            elif protocol == "UDP":
                payload_start = ip_header_length + 8
            else:
                return None

            if payload_start >= len(packet_data):
                return None

            return packet_data[payload_start:]

        except Exception as e:
            logger.error(f"페이로드 추출 오류: {e}")
            return None

    def _detect_protocols_by_pattern(self, payload: bytes) -> List[str]:
        """패턴 기반 프로토콜 자동 감지"""
        detected = []

        try:
            if len(payload) < 4:
                return detected

            # HTTP 감지
            if payload.startswith((b"GET ", b"POST ", b"PUT ", b"DELETE ", b"HEAD ", b"OPTIONS ")):
                detected.append("HTTP")
            elif payload.startswith(b"HTTP/"):
                detected.append("HTTP")

            # SSH 감지
            if payload.startswith(b"SSH-"):
                detected.append("SSH")

            # FTP 감지
            if payload.startswith((b"220 ", b"USER ", b"PASS ", b"QUIT ")):
                detected.append("FTP")

            # SMTP 감지
            if payload.startswith((b"220 ", b"HELO ", b"EHLO ", b"MAIL FROM:", b"RCPT TO:")):
                detected.append("SMTP")

            # POP3 감지
            if payload.startswith((b"+OK ", b"-ERR ", b"USER ", b"PASS ", b"QUIT ")):
                detected.append("POP3")

            # IMAP 감지
            if b"IMAP" in payload[:50] or payload.startswith((b"* OK", b"* BAD", b"* NO")):
                detected.append("IMAP")

            # MQTT 감지
            if len(payload) >= 2:
                mqtt_type = (payload[0] >> 4) & 0xF
                if mqtt_type in self.MQTT_MSG_TYPES:
                    detected.append("MQTT")

            # SNMP 감지 (ASN.1 시작)
            if payload.startswith((b"\x30\x82", b"\x30\x81", b"\x30")):
                detected.append("SNMP")

            # DNS 감지 (UDP)
            if len(payload) >= 12:
                # DNS 헤더 체크
                try:
                    flags = struct.unpack(">H", payload[2:4])[0]
                    if (flags & 0x8000) == 0 or (flags & 0x8000) == 0x8000:  # QR bit
                        detected.append("DNS")
                except Exception:
                    pass

        except Exception as e:
            logger.error(f"프로토콜 패턴 감지 오류: {e}")

        return detected

    def _analyze_protocol(self, protocol: str, payload: bytes, packet_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """프로토콜별 상세 분석"""
        try:
            if protocol == "SSH":
                return self._analyze_ssh(payload, packet_info)
            elif protocol == "HTTP":
                return self._analyze_http(payload, packet_info)
            elif protocol == "FTP":
                return self._analyze_ftp(payload, packet_info)
            elif protocol == "SMTP":
                return self._analyze_smtp(payload, packet_info)
            elif protocol == "POP3":
                return self._analyze_pop3(payload, packet_info)
            elif protocol == "IMAP":
                return self._analyze_imap(payload, packet_info)
            elif protocol == "MQTT":
                return self._analyze_mqtt(payload, packet_info)
            elif protocol == "SNMP":
                return self._analyze_snmp(payload, packet_info)
            elif protocol == "DNS":
                # DNS는 별도 분석기에서 처리됨
                return {"protocol": "DNS", "note": "Handled by DNS analyzer"}
            else:
                return self._analyze_generic(payload, packet_info)

        except Exception as e:
            logger.error(f"{protocol} 분석 오류: {e}")
            return None

    def _analyze_ssh(self, payload: bytes, packet_info: Dict[str, Any]) -> Dict[str, Any]:
        """SSH 프로토콜 분석"""
        try:
            analysis = {"protocol": "SSH"}

            # SSH 버전 문자열 분석
            if payload.startswith(b"SSH-"):
                version_line = payload.split(b"\r\n")[0] if b"\r\n" in payload else payload.split(b"\n")[0]
                version_str = version_line.decode("utf-8", errors="ignore")

                analysis.update({"version_string": version_str, "phase": "version_exchange"})

                # SSH 버전 파싱
                if len(version_str.split("-")) >= 3:
                    parts = version_str.split("-")
                    analysis.update(
                        {
                            "protocol_version": parts[1],
                            "software_version": "-".join(parts[2:]),
                        }
                    )

            # SSH 메시지 분석 (바이너리 프로토콜)
            elif len(payload) >= 5:
                try:
                    # SSH 패킷 길이
                    packet_length = struct.unpack(">I", payload[0:4])[0]
                    padding_length = payload[4]

                    if len(payload) >= 6:
                        msg_type = payload[5]

                        analysis.update(
                            {
                                "packet_length": packet_length,
                                "padding_length": padding_length,
                                "message_type": msg_type,
                                "message_name": self.SSH_MSG_TYPES.get(msg_type, f"unknown_{msg_type}"),
                                "phase": "binary_protocol",
                            }
                        )

                        # 특정 메시지 타입 분석
                        if msg_type == 20:  # SSH_MSG_KEXINIT
                            analysis["phase"] = "key_exchange"
                        elif msg_type in [50, 51, 52]:  # 인증 관련
                            analysis["phase"] = "authentication"
                        elif msg_type in [90, 91, 92]:  # 채널 관련
                            analysis["phase"] = "channel_management"

                except struct.error:
                    pass

            return analysis

        except Exception as e:
            logger.error(f"SSH 분석 오류: {e}")
            return {"protocol": "SSH", "error": str(e)}

    def _analyze_http(self, payload: bytes, packet_info: Dict[str, Any]) -> Dict[str, Any]:
        """HTTP 프로토콜 분석"""
        try:
            analysis = {"protocol": "HTTP"}

            try:
                payload_str = payload.decode("utf-8", errors="ignore")
            except Exception:
                payload_str = payload.decode("latin1", errors="ignore")

            lines = payload_str.split("\r\n")
            if not lines:
                return analysis

            first_line = lines[0]

            # HTTP 요청 분석
            if first_line.startswith(("GET ", "POST ", "PUT ", "DELETE ", "HEAD ", "OPTIONS ")):
                parts = first_line.split(" ")
                if len(parts) >= 3:
                    analysis.update(
                        {
                            "type": "request",
                            "method": parts[0],
                            "uri": parts[1],
                            "version": parts[2],
                        }
                    )

            # HTTP 응답 분석
            elif first_line.startswith("HTTP/"):
                parts = first_line.split(" ")
                if len(parts) >= 3:
                    analysis.update(
                        {
                            "type": "response",
                            "version": parts[0],
                            "status_code": parts[1],
                            "reason_phrase": " ".join(parts[2:]),
                        }
                    )

            # 헤더 분석
            headers = {}
            body_start = 0

            for i, line in enumerate(lines[1:], 1):
                if line == "":  # 헤더와 바디 구분
                    body_start = i + 1
                    break

                if ":" in line:
                    key, value = line.split(":", 1)
                    headers[key.strip().lower()] = value.strip()

            analysis["headers"] = headers

            # 바디 분석
            if body_start < len(lines):
                body = "\r\n".join(lines[body_start:])
                analysis["body_size"] = len(body.encode("utf-8"))
                analysis["has_body"] = len(body) > 0

                # Content-Type 기반 바디 분석
                content_type = headers.get("content-type", "")
                if "json" in content_type:
                    analysis["body_type"] = "json"
                elif "xml" in content_type:
                    analysis["body_type"] = "xml"
                elif "form" in content_type:
                    analysis["body_type"] = "form"
                elif body.strip():
                    analysis["body_type"] = "text"

            return analysis

        except Exception as e:
            logger.error(f"HTTP 분석 오류: {e}")
            return {"protocol": "HTTP", "error": str(e)}

    def _analyze_ftp(self, payload: bytes, packet_info: Dict[str, Any]) -> Dict[str, Any]:
        """FTP 프로토콜 분석"""
        try:
            analysis = {"protocol": "FTP"}

            try:
                payload_str = payload.decode("utf-8", errors="ignore").strip()
            except Exception:
                payload_str = payload.decode("latin1", errors="ignore").strip()

            # FTP 응답 코드 분석
            if re.match(r"^\d{3}", payload_str):
                code = payload_str[:3]
                message = payload_str[4:] if len(payload_str) > 4 else ""

                analysis.update({"type": "response", "code": code, "message": message})

                # 응답 코드 해석
                if code.startswith("1"):
                    analysis["category"] = "preliminary"
                elif code.startswith("2"):
                    analysis["category"] = "success"
                elif code.startswith("3"):
                    analysis["category"] = "intermediate"
                elif code.startswith("4"):
                    analysis["category"] = "transient_error"
                elif code.startswith("5"):
                    analysis["category"] = "permanent_error"

            # FTP 명령어 분석
            else:
                parts = payload_str.split(" ", 1)
                command = parts[0].upper()
                args = parts[1] if len(parts) > 1 else ""

                analysis.update({"type": "command", "command": command, "arguments": args})

                # 명령어 분류
                if command in ["USER", "PASS"]:
                    analysis["category"] = "authentication"
                elif command in ["CWD", "PWD", "LIST", "NLST"]:
                    analysis["category"] = "directory"
                elif command in ["RETR", "STOR", "DELE"]:
                    analysis["category"] = "file_transfer"
                elif command in ["PORT", "PASV", "EPSV"]:
                    analysis["category"] = "data_connection"

            return analysis

        except Exception as e:
            logger.error(f"FTP 분석 오류: {e}")
            return {"protocol": "FTP", "error": str(e)}

    def _analyze_smtp(self, payload: bytes, packet_info: Dict[str, Any]) -> Dict[str, Any]:
        """SMTP 프로토콜 분석"""
        try:
            analysis = {"protocol": "SMTP"}

            try:
                payload_str = payload.decode("utf-8", errors="ignore").strip()
            except Exception:
                payload_str = payload.decode("latin1", errors="ignore").strip()

            # SMTP 응답 분석
            if re.match(r"^\d{3}", payload_str):
                code = payload_str[:3]
                message = payload_str[4:] if len(payload_str) > 4 else ""

                analysis.update({"type": "response", "code": code, "message": message})

            # SMTP 명령어 분석
            else:
                parts = payload_str.split(" ", 1)
                command = parts[0].upper()
                args = parts[1] if len(parts) > 1 else ""

                analysis.update({"type": "command", "command": command, "arguments": args})

                # 이메일 주소 추출
                if command in ["MAIL FROM:", "RCPT TO:"]:
                    email_match = re.search(r"<([^>]+)>", args)
                    if email_match:
                        analysis["email"] = email_match.group(1)

            return analysis

        except Exception as e:
            logger.error(f"SMTP 분석 오류: {e}")
            return {"protocol": "SMTP", "error": str(e)}

    def _analyze_pop3(self, payload: bytes, packet_info: Dict[str, Any]) -> Dict[str, Any]:
        """POP3 프로토콜 분석"""
        try:
            analysis = {"protocol": "POP3"}

            try:
                payload_str = payload.decode("utf-8", errors="ignore").strip()
            except Exception:
                payload_str = payload.decode("latin1", errors="ignore").strip()

            # POP3 응답 분석
            if payload_str.startswith(("+OK", "-ERR")):
                parts = payload_str.split(" ", 1)
                status = parts[0]
                message = parts[1] if len(parts) > 1 else ""

                analysis.update({"type": "response", "status": status, "message": message})

            # POP3 명령어 분석
            else:
                parts = payload_str.split(" ")
                command = parts[0].upper()
                args = parts[1:] if len(parts) > 1 else []

                analysis.update({"type": "command", "command": command, "arguments": args})

            return analysis

        except Exception as e:
            logger.error(f"POP3 분석 오류: {e}")
            return {"protocol": "POP3", "error": str(e)}

    def _analyze_imap(self, payload: bytes, packet_info: Dict[str, Any]) -> Dict[str, Any]:
        """IMAP 프로토콜 분석"""
        try:
            analysis = {"protocol": "IMAP"}

            try:
                payload_str = payload.decode("utf-8", errors="ignore").strip()
            except Exception:
                payload_str = payload.decode("latin1", errors="ignore").strip()

            # IMAP 응답 분석
            if payload_str.startswith(("* ", "+ ")):
                analysis.update({"type": "untagged_response", "content": payload_str[2:]})

            elif re.match(r"^[A-Z0-9]+ (OK|NO|BAD)", payload_str):
                parts = payload_str.split(" ", 2)
                tag = parts[0]
                status = parts[1]
                message = parts[2] if len(parts) > 2 else ""

                analysis.update(
                    {
                        "type": "tagged_response",
                        "tag": tag,
                        "status": status,
                        "message": message,
                    }
                )

            # IMAP 명령어 분석
            else:
                parts = payload_str.split(" ")
                if len(parts) >= 2:
                    tag = parts[0]
                    command = parts[1].upper()
                    args = parts[2:] if len(parts) > 2 else []

                    analysis.update(
                        {
                            "type": "command",
                            "tag": tag,
                            "command": command,
                            "arguments": args,
                        }
                    )

            return analysis

        except Exception as e:
            logger.error(f"IMAP 분석 오류: {e}")
            return {"protocol": "IMAP", "error": str(e)}

    def _analyze_mqtt(self, payload: bytes, packet_info: Dict[str, Any]) -> Dict[str, Any]:
        """MQTT 프로토콜 분석"""
        try:
            analysis = {"protocol": "MQTT"}

            if len(payload) < 2:
                return analysis

            # MQTT 고정 헤더 분석
            fixed_header = payload[0]
            msg_type = (fixed_header >> 4) & 0xF
            dup_flag = bool(fixed_header & 0x08)
            qos_level = (fixed_header >> 1) & 0x03
            retain_flag = bool(fixed_header & 0x01)

            analysis.update(
                {
                    "message_type": msg_type,
                    "message_name": self.MQTT_MSG_TYPES.get(msg_type, f"unknown_{msg_type}"),
                    "dup_flag": dup_flag,
                    "qos_level": qos_level,
                    "retain_flag": retain_flag,
                }
            )

            # 남은 길이 디코딩
            remaining_length = 0
            multiplier = 1
            offset = 1

            while offset < len(payload):
                byte = payload[offset]
                remaining_length += (byte & 0x7F) * multiplier
                if (byte & 0x80) == 0:
                    break
                multiplier *= 128
                offset += 1
                if multiplier > 128 * 128 * 128:
                    break

            analysis["remaining_length"] = remaining_length
            analysis["header_length"] = offset + 1

            # 메시지별 상세 분석
            if msg_type == 1:  # CONNECT
                analysis.update(self._analyze_mqtt_connect(payload[offset + 1 :]))
            elif msg_type == 3:  # PUBLISH
                analysis.update(self._analyze_mqtt_publish(payload[offset + 1 :], qos_level))
            elif msg_type == 8:  # SUBSCRIBE
                analysis.update(self._analyze_mqtt_subscribe(payload[offset + 1 :]))

            return analysis

        except Exception as e:
            logger.error(f"MQTT 분석 오류: {e}")
            return {"protocol": "MQTT", "error": str(e)}

    def _analyze_mqtt_connect(self, payload: bytes) -> Dict[str, Any]:
        """MQTT CONNECT 메시지 분석"""
        try:
            if len(payload) < 10:
                return {}

            # 프로토콜 이름 길이
            protocol_name_length = struct.unpack(">H", payload[0:2])[0]
            if len(payload) < 2 + protocol_name_length + 8:
                return {}

            protocol_name = payload[2 : 2 + protocol_name_length].decode("utf-8", errors="ignore")
            offset = 2 + protocol_name_length

            # 프로토콜 레벨
            protocol_level = payload[offset]
            offset += 1

            # 연결 플래그
            connect_flags = payload[offset]
            offset += 1

            # Keep Alive
            keep_alive = struct.unpack(">H", payload[offset : offset + 2])[0]
            offset += 2

            return {
                "protocol_name": protocol_name,
                "protocol_level": protocol_level,
                "clean_session": bool(connect_flags & 0x02),
                "will_flag": bool(connect_flags & 0x04),
                "will_qos": (connect_flags >> 3) & 0x03,
                "will_retain": bool(connect_flags & 0x20),
                "password_flag": bool(connect_flags & 0x40),
                "username_flag": bool(connect_flags & 0x80),
                "keep_alive": keep_alive,
            }

        except Exception as e:
            logger.error(f"MQTT CONNECT 분석 오류: {e}")
            return {}

    def _analyze_mqtt_publish(self, payload: bytes, qos_level: int) -> Dict[str, Any]:
        """MQTT PUBLISH 메시지 분석"""
        try:
            if len(payload) < 2:
                return {}

            # 토픽 이름 길이
            topic_length = struct.unpack(">H", payload[0:2])[0]
            if len(payload) < 2 + topic_length:
                return {}

            topic_name = payload[2 : 2 + topic_length].decode("utf-8", errors="ignore")
            offset = 2 + topic_length

            result = {"topic": topic_name}

            # QoS > 0인 경우 패킷 식별자
            if qos_level > 0:
                if len(payload) < offset + 2:
                    return result
                packet_id = struct.unpack(">H", payload[offset : offset + 2])[0]
                result["packet_id"] = packet_id
                offset += 2

            # 페이로드
            if offset < len(payload):
                payload_data = payload[offset:]
                result["payload_size"] = len(payload_data)

                # 페이로드 타입 추정
                try:
                    payload_str = payload_data.decode("utf-8")
                    result["payload_type"] = "text"
                    if len(payload_str) < 100:  # 짧은 경우 내용 포함
                        result["payload_preview"] = payload_str
                except Exception:
                    result["payload_type"] = "binary"

            return result

        except Exception as e:
            logger.error(f"MQTT PUBLISH 분석 오류: {e}")
            return {}

    def _analyze_mqtt_subscribe(self, payload: bytes) -> Dict[str, Any]:
        """MQTT SUBSCRIBE 메시지 분석"""
        try:
            if len(payload) < 2:
                return {}

            # 패킷 식별자
            packet_id = struct.unpack(">H", payload[0:2])[0]
            offset = 2

            topics = []

            while offset < len(payload):
                if offset + 2 > len(payload):
                    break

                # 토픽 필터 길이
                topic_length = struct.unpack(">H", payload[offset : offset + 2])[0]
                offset += 2

                if offset + topic_length + 1 > len(payload):
                    break

                # 토픽 필터
                topic_filter = payload[offset : offset + topic_length].decode("utf-8", errors="ignore")
                offset += topic_length

                # QoS
                qos = payload[offset]
                offset += 1

                topics.append({"topic_filter": topic_filter, "qos": qos})

            return {
                "packet_id": packet_id,
                "topics": topics,
                "topic_count": len(topics),
            }

        except Exception as e:
            logger.error(f"MQTT SUBSCRIBE 분석 오류: {e}")
            return {}

    def _analyze_snmp(self, payload: bytes, packet_info: Dict[str, Any]) -> Dict[str, Any]:
        """SNMP 프로토콜 분석"""
        try:
            analysis = {"protocol": "SNMP"}

            # 간단한 ASN.1 BER 디코딩
            if len(payload) < 10:
                return analysis

            # SNMP 메시지는 SEQUENCE로 시작
            if payload[0] != 0x30:
                return analysis

            # 기본적인 SNMP 정보만 추출
            analysis.update({"version": "unknown", "community": "unknown", "pdu_type": "unknown"})

            # 실제 구현에서는 pyasn1 등의 라이브러리 사용 권장

            return analysis

        except Exception as e:
            logger.error(f"SNMP 분석 오류: {e}")
            return {"protocol": "SNMP", "error": str(e)}

    def _analyze_generic(self, payload: bytes, packet_info: Dict[str, Any]) -> Dict[str, Any]:
        """일반적인 애플리케이션 데이터 분석"""
        try:
            analysis = {
                "protocol": "GENERIC",
                "payload_size": len(payload),
                "is_printable": all(32 <= b <= 126 for b in payload[:100]),
            }

            if analysis["is_printable"] and len(payload) < 500:
                try:
                    analysis["text_preview"] = payload.decode("utf-8", errors="ignore")[:200]
                except Exception:
                    pass

            return analysis

        except Exception as e:
            logger.error(f"일반 분석 오류: {e}")
            return {"protocol": "GENERIC", "error": str(e)}

    def _update_session_info(self, analysis: Dict[str, Any], packet_info: Dict[str, Any]) -> Dict[str, Any]:
        """세션 정보 업데이트"""
        try:
            session_key = (
                f"{packet_info.get('src_ip')}:{packet_info.get('src_port')}-"
                f"{packet_info.get('dst_ip')}:{packet_info.get('dst_port')}"
            )

            if session_key not in self.sessions:
                self.sessions[session_key] = {
                    "start_time": packet_info.get("timestamp"),
                    "protocols": set(),
                    "packet_count": 0,
                    "byte_count": 0,
                }

            session = self.sessions[session_key]
            session["packet_count"] += 1
            session["byte_count"] += len(packet_info.get("raw_data", b""))

            for protocol in analysis.get("protocols", []):
                session["protocols"].add(protocol)

            return {
                "session_key": session_key,
                "packet_count": session["packet_count"],
                "byte_count": session["byte_count"],
                "protocols": list(session["protocols"]),
                "duration": self._calculate_duration(session["start_time"], packet_info.get("timestamp")),
            }

        except Exception as e:
            logger.error(f"세션 정보 업데이트 오류: {e}")
            return {}

    def _check_application_security(
        self, analysis: Dict[str, Any], payload: bytes, packet_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """애플리케이션 보안 검사"""
        issues = []

        try:
            protocols = analysis.get("protocols", [])

            # 평문 프로토콜 사용 경고
            insecure_protocols = ["FTP", "TELNET", "HTTP", "POP3", "IMAP", "SMTP"]
            for protocol in protocols:
                if protocol in insecure_protocols:
                    issues.append(
                        {
                            "type": "insecure_protocol",
                            "description": f"평문 프로토콜 사용: {protocol}",
                            "severity": "medium",
                            "recommendation": f"암호화된 대안 사용 권장 (예: {protocol}S)",
                        }
                    )

            # SSH 보안 검사
            if "SSH" in protocols:
                ssh_data = analysis.get("application_data", {})
                version = ssh_data.get("software_version", "")

                # 취약한 SSH 버전 검사
                if "OpenSSH" in version:
                    try:
                        version_num = re.search(r"OpenSSH_(\d+\.\d+)", version)
                        if version_num:
                            ver = float(version_num.group(1))
                            if ver < 7.4:
                                issues.append(
                                    {
                                        "type": "vulnerable_ssh_version",
                                        "description": f"취약한 SSH 버전: {version}",
                                        "severity": "high",
                                        "recommendation": "SSH 버전 업데이트 필요",
                                    }
                                )
                    except Exception:
                        pass

            # HTTP 보안 검사
            if "HTTP" in protocols:
                http_data = analysis.get("application_data", {})
                headers = http_data.get("headers", {})

                # 보안 헤더 누락 검사
                security_headers = [
                    "x-frame-options",
                    "x-content-type-options",
                    "x-xss-protection",
                    "strict-transport-security",
                ]

                missing_headers = [h for h in security_headers if h not in headers]
                if missing_headers:
                    issues.append(
                        {
                            "type": "missing_security_headers",
                            "description": f'보안 헤더 누락: {", ".join(missing_headers)}',
                            "severity": "low",
                            "recommendation": "보안 헤더 추가 권장",
                        }
                    )

            # 평문 인증 정보 검사
            try:
                payload_str = payload.decode("utf-8", errors="ignore").lower()

                # 평문 비밀번호 패턴
                password_patterns = [
                    r"password\s*[:=]\s*\S+",
                    r"passwd\s*[:=]\s*\S+",
                    r"pass\s*[:=]\s*\S+",
                    r"pwd\s*[:=]\s*\S+",
                ]

                for pattern in password_patterns:
                    if re.search(pattern, payload_str):
                        issues.append(
                            {
                                "type": "plaintext_credentials",
                                "description": "평문 인증 정보 감지",
                                "severity": "high",
                                "recommendation": "암호화된 연결 사용 필요",
                            }
                        )
                        break

            except Exception:
                pass

        except Exception as e:
            logger.error(f"애플리케이션 보안 검사 오류: {e}")

        return issues

    def _calculate_duration(self, start_time: str, current_time: str) -> float:
        """세션 지속 시간 계산"""
        try:
            if not start_time or not current_time:
                return 0.0

            start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            current = datetime.fromisoformat(current_time.replace("Z", "+00:00"))

            return (current - start).total_seconds()

        except Exception:
            return 0.0


# 팩토리 함수
def create_application_analyzer() -> ApplicationAnalyzer:
    """애플리케이션 분석기 인스턴스 생성"""
    return ApplicationAnalyzer()
