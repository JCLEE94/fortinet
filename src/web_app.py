#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nextrade Fortigate - 모듈화된 웹 애플리케이션
Flask + Socket.IO 기반 웹 애플리케이션 (모듈화 버전)
    """

import os
import time
from datetime import datetime

from flask import Flask, jsonify, render_template, request

from routes.api_routes import api_bp
from routes.fortimanager_routes import fortimanager_bp
from routes.itsm_api_routes import itsm_api_bp
from routes.itsm_routes import itsm_bp
from routes.main_routes import main_bp
from utils.security import (add_security_headers, csrf_protect,
                            generate_csrf_token, rate_limit)
from utils.unified_logger import get_logger

# 오프라인 모드 감지
OFFLINE_MODE = (
    os.getenv("OFFLINE_MODE", "false").lower() == "true"
    or os.getenv("NO_INTERNET", "false").lower() == "true"
    or os.getenv("DISABLE_EXTERNAL_CALLS", "false").lower() == "true"
)

if OFFLINE_MODE:
    print("🔒 OFFLINE MODE ACTIVATED - 외부 연결 차단됨")
    os.environ["DISABLE_SOCKETIO"] = "true"
    os.environ["DISABLE_UPDATES"] = "true"
    os.environ["DISABLE_TELEMETRY"] = "true"

# Socket.IO 설정
DISABLE_SOCKETIO = os.getenv("DISABLE_SOCKETIO", "false").lower() == "true"

if not DISABLE_SOCKETIO:
    try:
        from flask_socketio import SocketIO

        print("Socket.IO enabled")
    except ImportError:
        print("Warning: flask-socketio not available, disabling Socket.IO")
        DISABLE_SOCKETIO = True
else:
    print("Socket.IO disabled by environment variable")

# Route imports

# 모듈 임포트

# Removed old cache_manager import - using unified_cache_manager instead


def create_app():
    """Flask 애플리케이션 팩토리"""

    from analysis.analyzer import FirewallRuleAnalyzer
    from analysis.fixed_path_analyzer import FixedPathAnalyzer
    from config.services import APP_CONFIG
    from config.unified_settings import unified_settings
    from routes.itsm_automation_routes import itsm_automation_bp
    from routes.logs_routes import logs_bp
    from routes.performance_routes import performance_bp
    from utils.unified_cache_manager import get_cache_manager

    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "your-secret-key-here")

    # JSON 한글 인코딩 설정
    app.config["JSON_AS_ASCII"] = False
    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True

    # 애플리케이션 시작 시간 설정 (uptime 계산용)
    app.start_time = time.time()

    # 로거 설정
    logger = get_logger(__name__)

    # 통합 캐시 매니저 설정
    if OFFLINE_MODE:
        print("🔒 Redis 캐시 비활성화 (오프라인 모드)")
        # 메모리 캐시만 사용
        os.environ["REDIS_ENABLED"] = "false"

    try:
        cache_manager = get_cache_manager()
        print(
            f"통합 캐시 매니저 로드 성공: {cache_manager.get_stats()['backends']}개 백엔드"
        )
    except Exception as e:
        print(f"캐시 매니저 로드 실패: {e}")
        cache_manager = None

    # Security headers
    @app.after_request
    def after_request(response):
        return add_security_headers(response)

    # Context processor for global variables
    @app.context_processor
    def inject_global_vars():

        # 운영 환경에서는 테스트 모드 숨김
        show_test_mode = unified_settings.app_mode != "production"

        return {
            "APP_MODE": unified_settings.app_mode,
            "OFFLINE_MODE": OFFLINE_MODE,
            "show_test_mode": show_test_mode,
            "build_time": os.getenv("BUILD_TIME", "Development"),
            "csrf_token": generate_csrf_token(),
        }

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("500.html"), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {e}")
        return render_template("500.html"), 500

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(itsm_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(fortimanager_bp)
    app.register_blueprint(itsm_api_bp)

    # 성능 최적화 라우트 등록
    try:
        app.register_blueprint(performance_bp)
        logger.info("Performance optimization routes registered")
    except ImportError as e:
        logger.warning(f"Performance routes not available: {e}")

    # ITSM 자동화 라우트 등록
    try:
        app.register_blueprint(itsm_automation_bp)
        logger.info("ITSM automation routes registered")
    except ImportError as e:
        logger.warning(f"ITSM automation routes not available: {e}")

    # 로그 관리 라우트 등록
    try:
        app.register_blueprint(logs_bp)
        logger.info("Docker logs management routes registered")
    except ImportError as e:
        logger.warning(f"Logs routes not available: {e}")

    # Legacy routes for backward compatibility
    @rate_limit(max_requests=30, _window=60)
    @csrf_protect
    @app.route("/analyze_path", methods=["POST"])
    def analyze_path():
        """경로 분석 (레거시 호환성)"""
        try:
            data = request.get_json()

            analyzer = FirewallRuleAnalyzer()
            result = analyzer.analyze_path(data)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Firewall policy routes
    @rate_limit(max_requests=30, _window=60)
    @csrf_protect
    @app.route("/api/firewall-policy/analyze", methods=["POST"])
    def analyze_firewall_policy():
        """방화벽 정책 분석"""
        try:
            data = request.get_json()

            analyzer = FixedPathAnalyzer()

            _result = analyzer.analyze_path(
                src_ip=data.get("src_ip"),
                dst_ip=data.get("dst_ip"),
                protocol=data.get("protocol", "tcp"),
                port=data.get("port"),
            )

            return jsonify({"status": "success", "analysis": result})

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @rate_limit(max_requests=30, _window=60)
    @csrf_protect
    @app.route("/api/firewall-policy/create-ticket", methods=["POST"])
    def create_firewall_ticket():
        """방화벽 정책 티켓 생성"""
        try:
            data = request.get_json()

            # 티켓 생성 로직
            ticket = {
                "id": f"FW-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "title": data.get("title", "방화벽 정책 요청"),
                "description": data.get("description", ""),
                "src_ip": data.get("src_ip"),
                "dst_ip": data.get("dst_ip"),
                "protocol": data.get("protocol"),
                "port": data.get("port"),
                "status": "Created",
                "created_at": datetime.now().isoformat(),
            }

            return jsonify({"status": "success", "ticket": ticket})

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @rate_limit(max_requests=30, _window=60)
    @csrf_protect
    @rate_limit(max_requests=60, _window=60)
    @app.route("/api/firewall-policy/zones")
    def get_firewall_zones():
        """방화벽 존 정보 조회"""
        try:
            zones = [
                {"name": "internal", "description": "내부 네트워크"},
                {"name": "dmz", "description": "DMZ 네트워크"},
                {"name": "external", "description": "외부 네트워크"},
                {"name": "branch", "description": "지사 네트워크"},
                {"name": "management", "description": "관리 네트워크"},
            ]

            return jsonify({"status": "success", "zones": zones})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    return app


def main():
    """메인 실행 함수"""
    app = create_app()

    # Socket.IO 설정
    socketio = None
    if not DISABLE_SOCKETIO:
        try:
            socketio = SocketIO(
                app,
                cors_allowed_origins="*",
                async_mode="threading",
                ping_timeout=60,
                ping_interval=25,
            )
            print("Socket.IO 초기화 완료")
        except Exception as e:
            print(f"Socket.IO 초기화 실패: {e}")
            socketio = None

    # 서버 설정
    from config.services import APP_CONFIG
    from config.unified_settings import unified_settings

    host = os.environ.get("HOST_IP", unified_settings.webapp.host)
    port = int(os.environ.get("FLASK_PORT", APP_CONFIG["web_port"]))
    debug = os.environ.get("FLASK_ENV") == "development"

    print(f"🌐 서버 시작: http://{host}:{port}")
    print(f"📊 모드: {os.getenv('APP_MODE', 'production')}")
    print(f"🔒 오프라인 모드: {OFFLINE_MODE}")

    # 서버 실행
    if socketio and not DISABLE_SOCKETIO:
        socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
    else:
        app.run(host=host, port=port, debug=debug)


# Create app instance for import
app = create_app()

if __name__ == "__main__":
    main()
