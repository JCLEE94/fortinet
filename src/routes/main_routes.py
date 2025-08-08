"""
Main routes for pages
"""

from utils.common_imports import Blueprint, os, render_template
from flask import redirect, url_for

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """홈페이지 - 원래 Nextrade 대시보드로 리다이렉트"""
    return redirect(url_for("main.dashboard"))


@main_bp.route("/policy-analysis")
def policy_analysis():
    """FortiGate 정책 분석 페이지 (기존 index.html)"""
    return render_template(
        "index.html",
        example_src_ip=os.getenv("EXAMPLE_SRC_IP", "10.0.0.100"),
        example_dst_ip=os.getenv("EXAMPLE_DST_IP", "8.8.8.8"),
    )


@main_bp.route("/batch")
def batch():
    batch_examples = [
        {
            "src_ip": os.getenv("BATCH_EXAMPLE_SRC1", "10.10.1.10"),
            "dst_ip": os.getenv("BATCH_EXAMPLE_DST1", "10.20.0.15"),
            "port": "443",
            "protocol": "tcp",
        },
        {
            "src_ip": os.getenv("BATCH_EXAMPLE_SRC2", "10.10.2.20"),
            "dst_ip": os.getenv("BATCH_EXAMPLE_DST2", "172.20.5.30"),
            "port": "80",
            "protocol": "tcp",
        },
        {
            "src_ip": os.getenv("BATCH_EXAMPLE_SRC3", "10.20.0.5"),
            "dst_ip": os.getenv("BATCH_EXAMPLE_DST3", "8.8.8.8"),
            "port": "53",
            "protocol": "udp",
        },
    ]
    return render_template("batch.html", batch_examples=batch_examples)


@main_bp.route("/topology")
def topology():
    return render_template("topology.html")


@main_bp.route("/compliance")
def compliance():
    return render_template("compliance.html")


@main_bp.route("/logs")
def logs_management():
    """로그 관리 페이지"""
    return render_template("logs.html")


@main_bp.route("/logs/live")
def live_logs():
    """실시간 로그 스트리밍 페이지"""
    return render_template("live_logs.html")


@main_bp.route("/batch/results")
def batch_results():
    """배치 분석 결과 페이지"""
    from flask import session

    from config.batch_defaults import get_default_batch_results

    # 세션에서 배치 분석 결과 가져오기
    results = session.get("batch_results")

    if not results:
        # 기본 예시 데이터 사용
        results = get_default_batch_results()

    return render_template("batch_results.html", results=results)


@main_bp.route("/devices")
def devices():
    """장치 목록 페이지"""
    from config.device_defaults import get_device_config

    # 장치 관리 설정 로드
    device_config = get_device_config()

    return render_template("devices.html", config=device_config)


@main_bp.route("/packet_sniffer")
def packet_sniffer():
    # 예시 IP와 장치 정보를 환경변수에서 가져오거나 기본값 사용
    import os

    example_devices = [
        {
            "id": "firewall1",
            "name": "방화벽-01",
            "ip": os.getenv("EXAMPLE_FW1_IP", "192.168.1.1"),
        },
        {
            "id": "firewall2",
            "name": "방화벽-02",
            "ip": os.getenv("EXAMPLE_FW2_IP", "192.168.2.1"),
        },
        {
            "id": "firewall3",
            "name": "방화벽-03",
            "ip": os.getenv("EXAMPLE_FW3_IP", "192.168.3.1"),
        },
    ]

    example_filters = {
        "host": os.getenv("EXAMPLE_HOST_IP", "192.168.1.1"),
        "src_ip": os.getenv("EXAMPLE_SRC_IP", "192.168.1.10"),
        "host_to_host": (
            f"host {os.getenv('EXAMPLE_HOST1_IP', '192.168.1.1')} and "
            f"host {os.getenv('EXAMPLE_HOST2_IP', '192.168.1.2')}"
        ),
    }

    return render_template(
        "packet_sniffer.html", devices=example_devices, example_filters=example_filters
    )


@main_bp.route("/settings")
def settings():
    # 설정 페이지
    return render_template("settings.html")


@main_bp.route("/monitoring")
def monitoring():
    """모니터링 페이지"""
    from config.dashboard_defaults import (generate_mock_alerts,
                                           get_dashboard_config)
    from mock.data_generator import DummyDataGenerator

    # 모니터링용 더미 데이터 생성
    dummy_generator = DummyDataGenerator()
    dashboard_config = get_dashboard_config()

    data = {
        "stats": dummy_generator.generate_dashboard_stats(),
        "devices": dummy_generator.generate_devices(
            dashboard_config["device_list"]["top_devices_limit"] * 2
        ),
        "events": dummy_generator.generate_security_events(
            dashboard_config["security_events"]["max_events_display"]
        ),
        "alerts": generate_mock_alerts(dashboard_config["stats"]["active_alerts"]),
        "monitoring": dummy_generator.generate_monitoring_data(),
    }

    # 대시보드 설정도 템플릿에 전달 (중요!)
    data["config"] = dashboard_config

    return render_template("dashboard.html", data=data)


@main_bp.route("/text-overflow-test")
def text_overflow_test():
    # 텍스트 오버플로우 테스트를 위한 샘플 데이터
    sample_data = {
        "long_text": "This is a very long text that might overflow in certain UI elements. "
        * 10,
        "items": [
            {"name": "Item " + str(i), "description": "Description " * 5}
            for i in range(1, 11)
        ],
    }
    return render_template("text_overflow_test.html", **sample_data)


@main_bp.route("/dashboard/modern")
def dashboard_modern():
    return render_template("dashboard_modern.html")


@main_bp.route("/dashboard")
def dashboard():
    """대시보드 페이지"""
    from api.integration.api_integration import APIIntegrationManager
    from config.dashboard_defaults import (generate_mock_alerts,
                                           get_dashboard_config)
    from config.unified_settings import unified_settings
    from mock.data_generator import DummyDataGenerator

    # 대시보드 설정 로드
    dashboard_config = get_dashboard_config()

    try:
        # 실제 FortiManager 연결 시도
        api_manager = APIIntegrationManager(unified_settings.get_api_config())
        api_manager.initialize_connections()

        fm_client = api_manager.get_fortimanager_client()
        if fm_client and fm_client.login():
            devices = api_manager.get_all_devices()
            data = {
                "devices": devices,
                "connection_status": api_manager.get_connection_status(),
                "stats": {
                    "total_devices": len(devices),
                    "uptime_percentage": dashboard_config["stats"]["uptime_percentage"],
                    "network_traffic": dashboard_config["stats"]["network_traffic"],
                    "active_alerts": dashboard_config["stats"]["active_alerts"],
                },
                "alerts": generate_mock_alerts(
                    dashboard_config["stats"]["active_alerts"]
                ),
            }
        else:
            # 연결 실패 시 더미 데이터 사용
            dummy_generator = DummyDataGenerator()
            data = {
                "stats": dummy_generator.generate_dashboard_stats(),
                "devices": dummy_generator.generate_devices(
                    dashboard_config["device_list"]["top_devices_limit"] * 2
                ),
                "events": dummy_generator.generate_security_events(
                    dashboard_config["security_events"]["max_events_display"]
                ),
                "alerts": generate_mock_alerts(
                    dashboard_config["stats"]["active_alerts"]
                ),
            }

    except Exception as e:
        print(f"Dashboard error: {e}")
        # 오류 발생 시 더미 데이터 사용
        dummy_generator = DummyDataGenerator()
        data = {
            "stats": dummy_generator.generate_dashboard_stats(),
            "devices": dummy_generator.generate_devices(
                dashboard_config["device_list"]["top_devices_limit"] * 2
            ),
            "events": dummy_generator.generate_security_events(
                dashboard_config["security_events"]["max_events_display"]
            ),
            "alerts": generate_mock_alerts(dashboard_config["stats"]["active_alerts"]),
        }

    # 대시보드 설정도 템플릿에 전달
    data["config"] = dashboard_config

    return render_template("dashboard.html", data=data)


@main_bp.route("/result")
def result():
    """분석 결과 페이지"""
    from flask import session

    from config.result_defaults import get_default_result

    # 세션에서 분석 결과 가져오기 (분석 후 리다이렉트된 경우)
    data = session.get("analysis_result")

    if not data:
        # 기본 예시 데이터 사용
        data = get_default_result()

    return render_template("result.html", data=data)


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/policy-scenarios")
def policy_scenarios():
    """정책 분석 시나리오 페이지"""
    return render_template(
        "policy_scenarios.html",
        example_src_ip=os.getenv("EXAMPLE_SRC_IP", "10.0.0.100"),
        example_dst_ip=os.getenv("EXAMPLE_DST_IP", "10.20.0.50"),
    )


@main_bp.route("/help")
def help():
    batch_examples = [
        {
            "src_ip": os.getenv("BATCH_EXAMPLE_SRC1", "10.10.1.10"),
            "dst_ip": os.getenv("BATCH_EXAMPLE_DST1", "10.20.0.15"),
            "port": "443",
            "protocol": "tcp",
        },
        {
            "src_ip": os.getenv("BATCH_EXAMPLE_SRC2", "10.10.2.20"),
            "dst_ip": os.getenv("BATCH_EXAMPLE_DST2", "172.20.5.30"),
            "port": "80",
            "protocol": "tcp",
        },
        {
            "src_ip": os.getenv("BATCH_EXAMPLE_SRC3", "10.20.0.5"),
            "dst_ip": os.getenv("BATCH_EXAMPLE_DST3", "8.8.8.8"),
            "port": "53",
            "protocol": "udp",
        },
    ]
    return render_template(
        "help.html",
        batch_examples=batch_examples,
        example_src_ip=os.getenv("EXAMPLE_SRC_IP", "10.0.0.100"),
        example_dst_ip=os.getenv("EXAMPLE_DST_IP", "10.20.0.15"),
    )


@main_bp.route("/offline.html")
def offline():
    return render_template("offline.html")
