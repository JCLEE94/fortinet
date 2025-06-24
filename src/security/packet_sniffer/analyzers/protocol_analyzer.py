#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
프로토콜 분석기 - 패킷 프로토콜 식별 및 분석의 메인 엔진
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Type
from dataclasses import dataclass, field
import time

from ..base_sniffer import PacketInfo, ProtocolIdentifier
from src.utils.unified_logger import get_logger


@dataclass
class ProtocolAnalysisResult:
    """프로토콜 분석 결과"""
    protocol: str
    confidence: float
    details: Dict[str, Any] = field(default_factory=dict)
    flags: Dict[str, bool] = field(default_factory=dict)
    hierarchy: List[str] = field(default_factory=list)
    security_flags: Dict[str, Any] = field(default_factory=dict)
    anomalies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'protocol': self.protocol,
            'confidence': self.confidence,
            'details': self.details,
            'flags': self.flags,
            'hierarchy': self.hierarchy,
            'security_flags': self.security_flags,
            'anomalies': self.anomalies
        }


class BaseProtocolAnalyzer:
    """프로토콜 분석기 기본 클래스"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(f"analyzer_{name}", 'advanced')
    
    def can_analyze(self, packet: PacketInfo) -> bool:
        """이 분석기가 패킷을 분석할 수 있는지 확인"""
        raise NotImplementedError
    
    def analyze(self, packet: PacketInfo) -> Optional[ProtocolAnalysisResult]:
        """패킷 분석"""
        raise NotImplementedError
    
    def get_confidence_score(self, packet: PacketInfo) -> float:
        """신뢰도 점수 계산"""
        return 0.0


class ProtocolAnalyzer:
    """메인 프로토콜 분석기 - 다양한 분석기들을 조율"""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__, 'advanced')
        self.analyzers: Dict[str, BaseProtocolAnalyzer] = {}
        self.analysis_cache: Dict[str, ProtocolAnalysisResult] = {}
        self.cache_max_size = 1000
        
        # 통계
        self.stats = {
            'total_analyzed': 0,
            'cache_hits': 0,
            'analysis_errors': 0,
            'analyzer_usage': {}
        }
        
        self._register_analyzers()
        self.logger.info(f"프로토콜 분석기 초기화됨 ({len(self.analyzers)}개 분석기)")
    
    def _register_analyzers(self) -> None:
        """분석기들 등록"""
        try:
            # HTTP 분석기
            from .http_analyzer import HttpAnalyzer
            self.register_analyzer('http', HttpAnalyzer())
            
            # TLS 분석기  
            from .tls_analyzer import TlsAnalyzer
            self.register_analyzer('tls', TlsAnalyzer())
            
            # DNS 분석기
            from .dns_analyzer import DnsAnalyzer
            self.register_analyzer('dns', DnsAnalyzer())
            
            # 네트워크 분석기 (TCP/UDP/ICMP)
            from .network_analyzer import NetworkAnalyzer
            self.register_analyzer('network', NetworkAnalyzer())
            
            # 애플리케이션 분석기 (SSH, MQTT 등)
            from .application_analyzer import ApplicationAnalyzer
            self.register_analyzer('application', ApplicationAnalyzer())
            
        except ImportError as e:
            self.logger.warning(f"일부 분석기 등록 실패: {e}")
    
    def register_analyzer(self, name: str, analyzer: BaseProtocolAnalyzer) -> None:
        """분석기 등록"""
        self.analyzers[name] = analyzer
        self.stats['analyzer_usage'][name] = 0
        self.logger.debug(f"분석기 등록됨: {name}")
    
    def perform_deep_packet_inspection(self, packet: PacketInfo) -> Dict[str, Any]:
        """심층 패킷 검사 - 원래의 거대한 함수를 대체"""
        try:
            # 캐시 확인
            cache_key = self._generate_cache_key(packet)
            if cache_key in self.analysis_cache:
                self.stats['cache_hits'] += 1
                return self.analysis_cache[cache_key].to_dict()
            
            # 분석 결과 초기화
            inspection_result = self._initialize_inspection_result()
            
            # 기본 정보 추출
            src_port, dst_port, payload = self._extract_packet_info(packet)
            
            # 1단계: 명시적 프로토콜 분석
            explicit_result = self._analyze_explicit_protocols(packet, payload, inspection_result)
            
            # 2단계: 바이너리 시그니처 분석
            if not explicit_result:
                self._analyze_binary_signatures(payload, inspection_result)
            
            # 3단계: 포트 기반 프로토콜 추정
            self._analyze_port_based_protocols(packet, inspection_result)
            
            # 4단계: 보안 플래그 감지
            self._detect_security_flags(packet, inspection_result)
            
            # 5단계: 이상 패턴 감지
            self._detect_suspicious_patterns(payload, inspection_result)
            
            # 6단계: 프로토콜 계층 구조 구성
            self._build_protocol_hierarchy(packet, inspection_result)
            
            # 7단계: 신뢰도 계산
            confidence = self._calculate_protocol_confidence(inspection_result)
            inspection_result['confidence'] = confidence
            
            # 캐시에 저장
            result = ProtocolAnalysisResult(
                protocol=inspection_result.get('protocol', 'Unknown'),
                confidence=confidence,
                details=inspection_result.get('details', {}),
                flags=inspection_result.get('flags', {}),
                hierarchy=inspection_result.get('hierarchy', []),
                security_flags=inspection_result.get('security_flags', {}),
                anomalies=inspection_result.get('anomalies', [])
            )
            
            self._cache_result(cache_key, result)
            
            # 통계 업데이트
            self.stats['total_analyzed'] += 1
            
            return result.to_dict()
            
        except Exception as e:
            self.logger.error(f"심층 패킷 검사 실패: {e}")
            self.stats['analysis_errors'] += 1
            return self._get_error_result(str(e))
    
    def _initialize_inspection_result(self) -> Dict[str, Any]:
        """검사 결과 초기화"""
        return {
            'protocol': 'Unknown',
            'confidence': 0.0,
            'details': {},
            'flags': {
                'encrypted': False,
                'tunneled': False,
                'fragmented': False,
                'suspicious': False
            },
            'hierarchy': [],
            'security_flags': {},
            'anomalies': [],
            'analysis_time': time.time()
        }
    
    def _extract_packet_info(self, packet: PacketInfo) -> Tuple[int, int, bytes]:
        """패킷에서 기본 정보 추출"""
        return packet.src_port, packet.dst_port, packet.payload
    
    def _analyze_explicit_protocols(self, packet: PacketInfo, payload: bytes, 
                                   result: Dict[str, Any]) -> bool:
        """명시적 프로토콜 분석"""
        analyzed = False
        
        # HTTP/HTTPS 분석
        if 'http' in self.analyzers:
            http_result = self.analyzers['http'].analyze(packet)
            if http_result and http_result.confidence > 0.7:
                self._merge_analysis_result(result, http_result)
                self.stats['analyzer_usage']['http'] += 1
                analyzed = True
        
        # DNS 분석
        if not analyzed and 'dns' in self.analyzers:
            dns_result = self.analyzers['dns'].analyze(packet)
            if dns_result and dns_result.confidence > 0.7:
                self._merge_analysis_result(result, dns_result)
                self.stats['analyzer_usage']['dns'] += 1
                analyzed = True
        
        # TLS 분석
        if not analyzed and 'tls' in self.analyzers:
            tls_result = self.analyzers['tls'].analyze(packet)
            if tls_result and tls_result.confidence > 0.7:
                self._merge_analysis_result(result, tls_result)
                self.stats['analyzer_usage']['tls'] += 1
                analyzed = True
        
        return analyzed
    
    def _analyze_binary_signatures(self, payload: bytes, result: Dict[str, Any]) -> bool:
        """바이너리 시그니처 기반 분석"""
        if not payload:
            return False
        
        # 프로토콜 시그니처 매칭
        detected_protocol = ProtocolIdentifier.identify_by_signature(payload)
        if detected_protocol:
            result['protocol'] = detected_protocol
            result['confidence'] = max(result.get('confidence', 0), 0.8)
            result['details']['detection_method'] = 'binary_signature'
            return True
        
        # 애플리케이션 프로토콜 분석
        if 'application' in self.analyzers:
            app_result = self.analyzers['application'].analyze_payload(payload)
            if app_result:
                self._merge_analysis_result(result, app_result)
                self.stats['analyzer_usage']['application'] += 1
                return True
        
        return False
    
    def _analyze_port_based_protocols(self, packet: PacketInfo, result: Dict[str, Any]) -> None:
        """포트 기반 프로토콜 분석"""
        # 목적지 포트 기반 식별
        dst_protocol = ProtocolIdentifier.identify_by_port(packet.dst_port, packet.protocol)
        if dst_protocol:
            if result.get('confidence', 0) < 0.5:
                result['protocol'] = dst_protocol
                result['confidence'] = 0.6
                result['details']['detection_method'] = 'dst_port'
        
        # 출발지 포트 기반 식별 (낮은 우선순위)
        src_protocol = ProtocolIdentifier.identify_by_port(packet.src_port, packet.protocol)
        if src_protocol and result.get('confidence', 0) < 0.3:
            result['protocol'] = src_protocol
            result['confidence'] = 0.3
            result['details']['detection_method'] = 'src_port'
        
        # 네트워크 레벨 분석
        if 'network' in self.analyzers:
            network_result = self.analyzers['network'].analyze(packet)
            if network_result:
                # 네트워크 레벨 정보를 상세 정보에 추가
                result['details'].update(network_result.details)
                self.stats['analyzer_usage']['network'] += 1
    
    def _detect_security_flags(self, packet: PacketInfo, result: Dict[str, Any]) -> None:
        """보안 플래그 감지"""
        security_flags = {}
        
        # 암호화 프로토콜 감지
        encrypted_protocols = ['HTTPS', 'TLS', 'SSL', 'SSH', 'FTPS', 'IMAPS', 'POP3S', 'SMTPS']
        if result.get('protocol', '').upper() in encrypted_protocols:
            result['flags']['encrypted'] = True
            security_flags['encryption_type'] = result.get('protocol')
        
        # 터널링 프로토콜 감지
        tunneling_protocols = ['VPN', 'IPSec', 'GRE', 'L2TP']
        for tunnel_proto in tunneling_protocols:
            if tunnel_proto.lower() in result.get('protocol', '').lower():
                result['flags']['tunneled'] = True
                security_flags['tunnel_type'] = tunnel_proto
        
        # 포트 스캔 패턴 감지
        if packet.flags.get('syn') and not packet.flags.get('ack'):
            security_flags['potential_scan'] = True
        
        # 비표준 포트 사용 감지
        standard_ports = list(ProtocolIdentifier.TCP_PORTS.keys()) + list(ProtocolIdentifier.UDP_PORTS.keys())
        if packet.dst_port not in standard_ports and packet.dst_port > 1024:
            security_flags['non_standard_port'] = True
        
        result['security_flags'] = security_flags
    
    def _detect_suspicious_patterns(self, payload: bytes, result: Dict[str, Any]) -> None:
        """이상 패턴 감지"""
        anomalies = []
        
        if payload:
            payload_str = payload.decode('utf-8', errors='ignore')
            
            # SQL 인젝션 패턴
            sql_patterns = ['union select', 'drop table', 'insert into', "' or '1'='1"]
            for pattern in sql_patterns:
                if pattern.lower() in payload_str.lower():
                    anomalies.append(f"Potential SQL injection: {pattern}")
                    result['flags']['suspicious'] = True
            
            # XSS 패턴
            xss_patterns = ['<script>', 'javascript:', 'onerror=', 'onload=']
            for pattern in xss_patterns:
                if pattern.lower() in payload_str.lower():
                    anomalies.append(f"Potential XSS: {pattern}")
                    result['flags']['suspicious'] = True
            
            # 명령 인젝션 패턴
            cmd_patterns = ['|', ';', '&&', '||', '`']
            for pattern in cmd_patterns:
                if pattern in payload_str and len(payload_str) > 50:
                    anomalies.append(f"Potential command injection: {pattern}")
                    result['flags']['suspicious'] = True
            
            # 대용량 페이로드 (DoS 공격 가능성)
            if len(payload) > 10000:
                anomalies.append(f"Large payload size: {len(payload)} bytes")
        
        result['anomalies'] = anomalies
    
    def _build_protocol_hierarchy(self, packet: PacketInfo, result: Dict[str, Any]) -> None:
        """프로토콜 계층 구조 구성"""
        hierarchy = []
        
        # 네트워크 계층
        if packet.protocol:
            hierarchy.append(packet.protocol.upper())
        
        # 전송 계층
        if packet.protocol.upper() in ['TCP', 'UDP']:
            hierarchy.append(packet.protocol.upper())
        
        # 애플리케이션 계층
        app_protocol = result.get('protocol', 'Unknown')
        if app_protocol != 'Unknown' and app_protocol not in hierarchy:
            hierarchy.append(app_protocol)
        
        result['hierarchy'] = hierarchy
    
    def _calculate_protocol_confidence(self, result: Dict[str, Any]) -> float:
        """프로토콜 식별 신뢰도 계산"""
        base_confidence = result.get('confidence', 0.0)
        
        # 검증 요소들
        verification_bonus = 0.0
        
        # 프로토콜 시그니처가 있으면 신뢰도 증가
        if result.get('details', {}).get('detection_method') == 'binary_signature':
            verification_bonus += 0.2
        
        # 포트와 프로토콜이 일치하면 신뢰도 증가
        if result.get('details', {}).get('port_protocol_match'):
            verification_bonus += 0.1
        
        # 페이로드 분석 결과가 있으면 신뢰도 증가
        if result.get('details', {}).get('payload_analysis'):
            verification_bonus += 0.1
        
        final_confidence = min(base_confidence + verification_bonus, 1.0)
        return round(final_confidence, 3)
    
    def _merge_analysis_result(self, main_result: Dict[str, Any], 
                              analyzer_result: ProtocolAnalysisResult) -> None:
        """분석 결과 병합"""
        if analyzer_result.confidence > main_result.get('confidence', 0):
            main_result['protocol'] = analyzer_result.protocol
            main_result['confidence'] = analyzer_result.confidence
        
        # 상세 정보 병합
        main_result['details'].update(analyzer_result.details)
        main_result['flags'].update(analyzer_result.flags)
        main_result['security_flags'].update(analyzer_result.security_flags)
        main_result['anomalies'].extend(analyzer_result.anomalies)
    
    def _generate_cache_key(self, packet: PacketInfo) -> str:
        """캐시 키 생성"""
        # 패킷의 핵심 정보로 캐시 키 생성
        key_parts = [
            packet.protocol,
            str(packet.src_port),
            str(packet.dst_port),
            str(len(packet.payload)),
            str(hash(packet.payload[:100]))  # 페이로드 앞부분 해시
        ]
        return '_'.join(key_parts)
    
    def _cache_result(self, cache_key: str, result: ProtocolAnalysisResult) -> None:
        """결과 캐시에 저장"""
        if len(self.analysis_cache) >= self.cache_max_size:
            # 가장 오래된 항목 제거 (간단한 LRU)
            oldest_key = next(iter(self.analysis_cache))
            del self.analysis_cache[oldest_key]
        
        self.analysis_cache[cache_key] = result
    
    def _get_error_result(self, error_message: str) -> Dict[str, Any]:
        """오류 결과 생성"""
        return {
            'protocol': 'Error',
            'confidence': 0.0,
            'details': {'error': error_message},
            'flags': {},
            'hierarchy': [],
            'security_flags': {},
            'anomalies': [f"Analysis error: {error_message}"]
        }
    
    def get_analyzer_stats(self) -> Dict[str, Any]:
        """분석기 통계 조회"""
        return {
            'total_analyzed': self.stats['total_analyzed'],
            'cache_hits': self.stats['cache_hits'],
            'cache_hit_rate': self.stats['cache_hits'] / max(self.stats['total_analyzed'], 1) * 100,
            'analysis_errors': self.stats['analysis_errors'],
            'error_rate': self.stats['analysis_errors'] / max(self.stats['total_analyzed'], 1) * 100,
            'analyzer_usage': self.stats['analyzer_usage'].copy(),
            'cache_size': len(self.analysis_cache),
            'registered_analyzers': list(self.analyzers.keys())
        }
    
    def clear_cache(self) -> None:
        """캐시 정리"""
        self.analysis_cache.clear()
        self.logger.info("분석 캐시 정리됨")
    
    def analyze_packet_batch(self, packets: List[PacketInfo]) -> List[Dict[str, Any]]:
        """패킷 배치 분석"""
        results = []
        for packet in packets:
            result = self.perform_deep_packet_inspection(packet)
            results.append(result)
        return results


# 전역 프로토콜 분석기 인스턴스
_global_analyzer: Optional[ProtocolAnalyzer] = None


def get_protocol_analyzer() -> ProtocolAnalyzer:
    """전역 프로토콜 분석기 반환"""
    global _global_analyzer
    if _global_analyzer is None:
        _global_analyzer = ProtocolAnalyzer()
    return _global_analyzer


# 편의 함수
def analyze_packet(packet: PacketInfo) -> Dict[str, Any]:
    """패킷 분석 편의 함수"""
    return get_protocol_analyzer().perform_deep_packet_inspection(packet)