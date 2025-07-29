#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
성능 최적화 관련 API Routes
"""

from datetime import datetime

from flask import Blueprint, request

# from src.utils.api_optimizer import get_api_optimizer, optimized_response


# Dummy decorator to replace optimized_response
def optimized_response(**kwargs):
    def decorator(func):
        return func

    return decorator


from utils.api_utils import get_data_source
from utils.route_helpers import standard_api_response
from utils.security import rate_limit
from utils.unified_cache_manager import get_cache_manager
from utils.unified_logger import get_logger


# Stub functions for removed modules
def get_api_optimizer():
    """Stub for removed api_optimizer"""
    return type("obj", (object,), {"get_performance_metrics": lambda: {}})()


def get_performance_cache():
    """Stub for removed performance_cache"""
    return get_cache_manager()


class CacheWarmer:
    """Stub for removed CacheWarmer"""

    def __init__(self, cache):
        pass

    def warm_cache(self):
        pass


def get_real_time_monitor():
    """Stub for removed real_time_monitor"""
    return type(
        "obj",
        (object,),
        {
            "get_metrics": lambda: {},
            "start_monitoring": lambda: None,
            "stop_monitoring": lambda: None,
            "get_monitoring_status": lambda: {},
        },
    )()


logger = get_logger(__name__)

performance_bp = Blueprint("performance", __name__, url_prefix="/api/performance")


@performance_bp.route("/metrics", methods=["GET"])
@optimized_response()
def get_performance_metrics():
    """성능 메트릭 조회"""
    try:
        # API 최적화 메트릭
        optimizer = get_api_optimizer()
        api_metrics = optimizer.get_performance_metrics()

        # 캐시 메트릭
        cache = get_performance_cache()
        cache_metrics = cache.get_stats()

        return {
            "api_optimization": api_metrics,
            "cache_performance": cache_metrics,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"성능 메트릭 조회 실패: {e}")
        return {
            "error": str(e),
            "api_optimization": {},
            "cache_performance": {},
            "timestamp": datetime.now().isoformat(),
        }


@performance_bp.route("/cache/clear", methods=["POST"])
@rate_limit(max_requests=5, window=60)
def clear_performance_cache():
    """성능 캐시 삭제"""
    try:
        data = request.get_json() or {}
        namespace = data.get("namespace", "all")

        cache = get_performance_cache()

        if namespace == "all":
            # 전체 캐시 삭제 (메모리만, Redis는 선택적으로)
            cache.memory_cache.clear()
            cleared_count = len(cache.memory_cache)
        else:
            # 특정 네임스페이스만 삭제
            cleared_count = cache.clear_namespace(namespace)

        # 통합 캐시 매니저도 삭제
        get_cache_manager().clear()

        return standard_api_response(
            success=True,
            message=f"Cache cleared successfully. {cleared_count} items removed.",
            data={
                "namespace": namespace,
                "cleared_items": cleared_count,
                "timestamp": datetime.now().isoformat(),
            },
        )

    except Exception as e:
        logger.error(f"캐시 삭제 실패: {e}")
        return standard_api_response(
            success=False, message=f"Cache clear failed: {str(e)}", status_code=500
        )


@performance_bp.route("/cache/warmup", methods=["POST"])
@rate_limit(max_requests=3, window=300)  # 5분에 3번만 허용
def warmup_performance_cache():
    """성능 캐시 예열"""
    try:
        cache = get_performance_cache()
        warmer = CacheWarmer(cache)

        # 주요 데이터 예열 작업 정의
        def warm_devices():
            try:
                api_manager, dummy_generator, test_mode = get_data_source()
                if test_mode:
                    return dummy_generator.generate_devices(20)
                else:
                    # 실제 장치 데이터 수집 로직 (간단화)
                    return []
            except Exception:
                return []

        def warm_dashboard_stats():
            try:
                from api.integration.dashboard_collector import DashboardDataCollector

                api_manager, dummy_generator, test_mode = get_data_source()
                if test_mode:
                    return dummy_generator.generate_dashboard_stats()
                else:
                    collector = DashboardDataCollector(api_manager)
                    return collector.get_dashboard_stats()
            except Exception:
                return {}

        def warm_monitoring_data():
            try:
                api_manager, dummy_generator, test_mode = get_data_source()
                if test_mode:
                    return {
                        "cpu_usage": dummy_generator.generate_cpu_usage(),
                        "memory_usage": dummy_generator.generate_memory_usage(),
                    }
                else:
                    return {}
            except Exception:
                return {}

        # 예열 작업 추가
        warmer.add_warming_task("devices", "list", warm_devices, ttl=300)
        warmer.add_warming_task("dashboard", "stats", warm_dashboard_stats, ttl=180)
        warmer.add_warming_task("monitoring", "data", warm_monitoring_data, ttl=120)

        # 예열 실행
        results = warmer.warm_cache()

        return standard_api_response(
            success=True,
            message="Cache warming completed",
            data={
                "warmed_items": results["success"],
                "failed_items": results["failed"],
                "timestamp": datetime.now().isoformat(),
            },
        )

    except Exception as e:
        logger.error(f"캐시 예열 실패: {e}")
        return standard_api_response(
            success=False, message=f"Cache warming failed: {str(e)}", status_code=500
        )


@performance_bp.route("/cache/stats", methods=["GET"])
@optimized_response()
def get_cache_stats():
    """캐시 통계 조회"""
    try:
        cache = get_performance_cache()
        stats = cache.get_stats()

        # 만료된 캐시 정리
        expired_count = cache.cleanup_expired()

        stats["expired_cleaned"] = expired_count
        stats["timestamp"] = datetime.now().isoformat()

        return stats

    except Exception as e:
        logger.error(f"캐시 통계 조회 실패: {e}")
        return {"error": str(e), "timestamp": datetime.now().isoformat()}


@performance_bp.route("/response-time/test", methods=["GET"])
@optimized_response()
def test_response_time():
    """API 응답 시간 테스트"""
    import time

    start_time = time.time()

    # 시뮬레이션 작업
    test_data = {
        "message": "Response time test completed",
        "data_size": "medium",
        "test_items": [f"item_{i}" for i in range(100)],  # 100개 항목
        "nested_data": {"level1": {"level2": {"level3": list(range(50))}}},
    }

    processing_time = time.time() - start_time

    return {
        "test_result": test_data,
        "processing_time_seconds": round(processing_time, 4),
        "timestamp": datetime.now().isoformat(),
    }


@performance_bp.route("/compression/test", methods=["GET"])
@optimized_response()
def test_compression():
    """데이터 압축 효과 테스트"""

    # 큰 데이터 생성 (압축 효과 확인용)
    large_data = {
        "description": "This is a compression test with repeated data " * 100,
        "repeated_array": ["same_value"] * 1000,
        "numbers": list(range(1000)),
        "text_data": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 200,
        "nested_structures": [
            {
                "id": i,
                "name": f"Item {i}",
                "description": "A very long description that repeats many times " * 10,
                "tags": ["tag1", "tag2", "tag3"] * 5,
            }
            for i in range(100)
        ],
    }

    return {
        "message": "Compression test data",
        "data": large_data,
        "total_items": len(large_data["nested_structures"]),
        "estimated_size_kb": len(str(large_data)) / 1024,
        "timestamp": datetime.now().isoformat(),
    }


@performance_bp.route("/monitoring/realtime", methods=["GET"])
@optimized_response()
def get_realtime_monitoring():
    """실시간 모니터링 데이터 조회"""
    try:
        monitor = get_real_time_monitor()

        # 현재 메트릭 조회
        current_metrics = monitor.get_current_metrics()

        return {
            "status": "success",
            "is_monitoring_active": monitor.is_running,
            "current_metrics": current_metrics,
            "collection_interval": monitor.collection_interval,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"실시간 모니터링 데이터 조회 실패: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@performance_bp.route("/monitoring/start", methods=["POST"])
@rate_limit(max_requests=5, window=60)
def start_realtime_monitoring():
    """실시간 모니터링 시작"""
    try:
        monitor = get_real_time_monitor()
        monitor.start_monitoring()

        return standard_api_response(
            success=True,
            message="Real-time monitoring started successfully",
            data={
                "is_monitoring_active": monitor.is_running,
                "collection_interval": monitor.collection_interval,
                "timestamp": datetime.now().isoformat(),
            },
        )

    except Exception as e:
        logger.error(f"실시간 모니터링 시작 실패: {e}")
        return standard_api_response(
            success=False,
            message=f"Failed to start real-time monitoring: {str(e)}",
            status_code=500,
        )


@performance_bp.route("/monitoring/stop", methods=["POST"])
@rate_limit(max_requests=5, window=60)
def stop_realtime_monitoring():
    """실시간 모니터링 중지"""
    try:
        monitor = get_real_time_monitor()
        monitor.stop_monitoring()

        return standard_api_response(
            success=True,
            message="Real-time monitoring stopped successfully",
            data={
                "is_monitoring_active": monitor.is_running,
                "timestamp": datetime.now().isoformat(),
            },
        )

    except Exception as e:
        logger.error(f"실시간 모니터링 중지 실패: {e}")
        return standard_api_response(
            success=False,
            message=f"Failed to stop real-time monitoring: {str(e)}",
            status_code=500,
        )


@performance_bp.route("/monitoring/history/<metric_name>", methods=["GET"])
@optimized_response()
def get_metric_history(metric_name):
    """메트릭 히스토리 조회"""
    try:
        duration_minutes = request.args.get("duration", 60, type=int)
        duration_minutes = min(duration_minutes, 1440)  # 최대 24시간

        monitor = get_real_time_monitor()
        history = monitor.get_metric_history(metric_name, duration_minutes)

        return {
            "status": "success",
            "metric_name": metric_name,
            "duration_minutes": duration_minutes,
            "data_points": len(history),
            "history": history,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"메트릭 히스토리 조회 실패: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@performance_bp.route("/monitoring/alerts/recent", methods=["GET"])
@optimized_response()
def get_recent_alerts():
    """최근 알림 조회"""
    try:
        limit = request.args.get("limit", 50, type=int)
        limit = min(limit, 200)  # 최대 200개

        get_performance_cache()

        # 캐시에서 최근 알림들 조회 (간단한 구현)
        alerts = []

        # 실제 구현에서는 Redis나 데이터베이스에서 알림 목록을 조회
        # 여기서는 시뮬레이션 데이터 반환

        return {
            "status": "success",
            "total_alerts": len(alerts),
            "alerts": alerts,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"최근 알림 조회 실패: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }
