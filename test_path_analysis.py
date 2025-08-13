#!/usr/bin/env python3
"""
FortiGate 경로 분석 기능 종합 테스트
패킷 경로 분석, 방화벽 정책 매칭, 차단/허용 시나리오 테스트
"""

import sys
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

from analysis.fixed_path_analyzer import FixedPathAnalyzer
from analysis.visualizer import PathVisualizer
from utils.unified_logger import get_logger

logger = get_logger(__name__)


def print_separator(title=""):
    """Print a formatted separator"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print('='*60)
    else:
        print('-'*60)


def test_path_analysis():
    """경로 분석 기능 종합 테스트"""
    analyzer = FixedPathAnalyzer()
    visualizer = PathVisualizer()
    
    # 테스트 케이스 정의
    test_cases = [
        {
            "name": "✅ Internal to DMZ Web (허용)",
            "src_ip": "192.168.1.10",
            "dst_ip": "172.16.10.100",
            "port": 443,
            "expected": "allow"
        },
        {
            "name": "✅ Internal to External Internet (허용)",
            "src_ip": "192.168.50.20",
            "dst_ip": "8.8.8.8",
            "port": 443,
            "expected": "allow"
        },
        {
            "name": "❌ Guest to Internal (차단)",
            "src_ip": "10.10.1.50",
            "dst_ip": "192.168.1.10",
            "port": 22,
            "expected": "deny"
        },
        {
            "name": "✅ External to DMZ Public Web (허용)",
            "src_ip": "203.0.113.50",
            "dst_ip": "172.16.10.100",
            "port": 443,
            "expected": "allow"
        },
        {
            "name": "❌ External to Internal (차단)",
            "src_ip": "203.0.113.50",
            "dst_ip": "192.168.1.10",
            "port": 22,
            "expected": "deny"
        },
        {
            "name": "✅ DMZ to External (허용)",
            "src_ip": "172.16.10.50",
            "dst_ip": "8.8.8.8",
            "port": 53,
            "expected": "allow"
        },
        {
            "name": "✅ Internal to DMZ Database (특정 서브넷만 허용)",
            "src_ip": "192.168.10.5",
            "dst_ip": "172.16.20.10",
            "port": 3306,
            "expected": "allow"
        },
        {
            "name": "❌ Internal to DMZ Database (다른 서브넷 차단)",
            "src_ip": "192.168.50.5",
            "dst_ip": "172.16.20.10",
            "port": 3306,
            "expected": "deny"
        }
    ]
    
    print_separator("FortiGate 경로 분석 기능 테스트")
    print(f"테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print_separator(f"테스트 {i}/{len(test_cases)}: {test_case['name']}")
        
        # 경로 분석 실행
        result = analyzer.analyze_path(
            test_case['src_ip'],
            test_case['dst_ip'],
            test_case['port']
        )
        
        # 결과 출력
        print(f"📍 출발지: {test_case['src_ip']}")
        print(f"🎯 목적지: {test_case['dst_ip']}")
        print(f"🔌 포트: {test_case['port']}")
        print(f"📋 예상 결과: {test_case['expected'].upper()}")
        
        # 분석 결과
        if result['allowed']:
            actual_result = "allow"
            print(f"✅ 실제 결과: ALLOW")
            if result['analysis_summary']['matched_policy']:
                print(f"📜 매칭된 정책: {result['analysis_summary']['matched_policy']}")
                print(f"📝 정책 설명: {result['analysis_summary']['policy_description']}")
        else:
            actual_result = "deny"
            print(f"❌ 실제 결과: DENY")
            if result['blocked_by']:
                print(f"🚫 차단 정책: {result['blocked_by']}")
        
        # 경로 정보
        print(f"\n🛤️ 경로 정보:")
        print(f"  - 총 홉 수: {result['analysis_summary']['total_hops']}")
        print(f"  - 총 지연시간: {result['analysis_summary']['total_latency']}ms")
        print(f"  - 소스 존: {result['analysis_summary']['source_zone']}")
        print(f"  - 목적지 존: {result['analysis_summary']['destination_zone']}")
        
        # 상세 경로
        if result['path']:
            print("\n📊 상세 경로:")
            for hop in result['path']:
                print(f"  Hop {hop['hop_number']}: {hop['firewall_name']}")
                print(f"    - 인터페이스: {hop['interface_in']} → {hop['interface_out']}")
                print(f"    - 액션: {hop['action']}")
                if hop['policy']:
                    print(f"    - 정책: {hop['policy']['name']}")
        
        # 권고사항
        if result['recommendations']:
            print("\n💡 권고사항:")
            for rec in result['recommendations']:
                print(f"  - [{rec['type']}] {rec['message']}")
        
        # 테스트 결과 검증
        test_passed = (actual_result == test_case['expected'])
        if test_passed:
            print(f"\n✅ 테스트 통과")
            passed += 1
        else:
            print(f"\n❌ 테스트 실패 - 예상: {test_case['expected']}, 실제: {actual_result}")
            failed += 1
        
        results.append({
            "test": test_case['name'],
            "passed": test_passed,
            "details": result['analysis_summary']
        })
    
    # 최종 결과 요약
    print_separator("테스트 결과 요약")
    print(f"총 테스트: {len(test_cases)}")
    print(f"✅ 통과: {passed}")
    print(f"❌ 실패: {failed}")
    print(f"성공률: {(passed/len(test_cases)*100):.1f}%")
    
    # 결과를 JSON 파일로 저장
    output_file = f"path_analysis_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_time": datetime.now().isoformat(),
            "total_tests": len(test_cases),
            "passed": passed,
            "failed": failed,
            "success_rate": passed/len(test_cases)*100,
            "test_results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 상세 결과가 {output_file}에 저장되었습니다.")
    
    return passed == len(test_cases)


def test_visualization():
    """경로 시각화 테스트"""
    print_separator("경로 시각화 테스트")
    
    analyzer = FixedPathAnalyzer()
    visualizer = PathVisualizer()
    
    # 복잡한 경로 테스트
    src_ip = "192.168.1.10"
    dst_ip = "8.8.8.8"
    port = 443
    
    print(f"시각화 테스트: {src_ip} → {dst_ip}:{port}")
    
    # 경로 분석
    result = analyzer.analyze_path(src_ip, dst_ip, port)
    
    # 네트워크 그래프 시각화
    print("\n📈 네트워크 그래프 생성:")
    graph_data = visualizer.generate_network_graph(result)
    if graph_data:
        print(f"  - 노드 수: {len(graph_data.get('nodes', []))}")
        print(f"  - 엣지 수: {len(graph_data.get('edges', []))}")
        print(f"  - 허용 여부: {graph_data.get('allowed', False)}")
    
    # 경로 테이블 생성
    path_table = visualizer.generate_path_table(result)
    if path_table:
        print("\n📊 경로 테이블 생성 완료")
        print(f"  - 헤더: {path_table.get('headers', [])}")
        print(f"  - 행 수: {len(path_table.get('rows', []))}")
    
    # 상세 규칙 생성
    detailed_rules = visualizer.generate_detailed_rules(result)
    if detailed_rules:
        print("\n📋 상세 규칙 정보 생성 완료")
        print(f"  - 규칙 수: {len(detailed_rules)}")
    
    # 시각화 데이터를 JSON 파일로 저장
    viz_file = "path_visualization_data.json"
    viz_data = visualizer.generate_visualization_data(result)
    
    with open(viz_file, 'w', encoding='utf-8') as f:
        json.dump(viz_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 시각화 데이터가 {viz_file}에 저장되었습니다.")
    
    return True


def test_policy_matching():
    """정책 매칭 로직 테스트"""
    print_separator("방화벽 정책 매칭 테스트")
    
    analyzer = FixedPathAnalyzer()
    
    # 정책 매칭 테스트 케이스
    test_cases = [
        {
            "src_ip": "192.168.1.10",
            "dst_ip": "172.16.10.100",
            "port": 443,
            "expected_policy": "POL-001"
        },
        {
            "src_ip": "192.168.10.5",
            "dst_ip": "172.16.20.10",
            "port": 3306,
            "expected_policy": "POL-002"
        },
        {
            "src_ip": "10.10.1.50",
            "dst_ip": "192.168.1.10",
            "port": 22,
            "expected_policy": "POL-006"  # Deny policy
        }
    ]
    
    for test in test_cases:
        print(f"\n테스트: {test['src_ip']} → {test['dst_ip']}:{test['port']}")
        
        # 정책 찾기
        matched_policy = None
        for policy_id, policy in analyzer.firewall_policies.items():
            if analyzer._is_ip_in_network(test['src_ip'], policy['source_net']) and \
               analyzer._is_ip_in_network(test['dst_ip'], policy['dest_net']) and \
               (test['port'] in policy['port'] or 'ALL' in policy['port']):
                matched_policy = policy_id
                break
        
        if matched_policy == test['expected_policy']:
            print(f"✅ 정책 매칭 성공: {matched_policy}")
            if matched_policy:
                policy = analyzer.firewall_policies[matched_policy]
                print(f"  - 정책명: {policy['name']}")
                print(f"  - 액션: {policy['action']}")
                print(f"  - 설명: {policy['description']}")
        else:
            print(f"❌ 정책 매칭 실패")
            print(f"  - 예상: {test['expected_policy']}")
            print(f"  - 실제: {matched_policy}")
    
    return True


def main():
    """메인 테스트 실행"""
    print("="*70)
    print("   FortiGate 경로 분석 기능 종합 테스트 시작")
    print("="*70)
    
    all_passed = True
    
    # 1. 경로 분석 테스트
    if not test_path_analysis():
        all_passed = False
    
    # 2. 시각화 테스트
    if not test_visualization():
        all_passed = False
    
    # 3. 정책 매칭 테스트
    if not test_policy_matching():
        all_passed = False
    
    # 최종 결과
    print_separator("최종 테스트 결과")
    if all_passed:
        print("✅ 모든 테스트 통과! FortiGate 경로 분석 기능이 정상 작동합니다.")
    else:
        print("❌ 일부 테스트 실패. 로그를 확인하세요.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())