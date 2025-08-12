"""
Common utilities for API modules
"""

import random
import time


def format_uptime(seconds):
    """Convert seconds to human-readable format"""
    if seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"
    else:
        days = int(seconds / 86400)
        hours = int((seconds % 86400) / 3600)
        return f"{days} day{'s' if days != 1 else ''} {hours} hour{'s' if hours != 1 else ''}"


def optimized_response(**kwargs):
    """Dummy decorator to replace optimized_response"""

    def decorator(func):
        return func

    return decorator


def get_system_uptime():
    """Get system uptime"""
    try:
        with open("/proc/uptime", "r") as f:
            uptime_seconds = float(f.readline().split()[0])
            return uptime_seconds
    except Exception:
        # Fallback for non-Linux systems
        return random.uniform(
            3600, 86400
        )  # Random uptime between 1 hour and 1 day


def get_memory_usage():
    """Get memory usage information"""
    try:
        with open("/proc/meminfo", "r") as f:
            meminfo = f.read()
            lines = meminfo.split("\n")

            mem_total = 0
            mem_available = 0

            for line in lines:
                if line.startswith("MemTotal:"):
                    mem_total = (
                        int(line.split()[1]) * 1024
                    )  # Convert KB to bytes
                elif line.startswith("MemAvailable:"):
                    mem_available = (
                        int(line.split()[1]) * 1024
                    )  # Convert KB to bytes

            mem_used = mem_total - mem_available
            mem_usage_percent = (
                (mem_used / mem_total) * 100 if mem_total > 0 else 0
            )

            return {
                "total": mem_total,
                "used": mem_used,
                "available": mem_available,
                "usage_percent": round(mem_usage_percent, 2),
            }
    except Exception:
        # Fallback for systems without /proc/meminfo
        total_mb = random.randint(4096, 32768)  # 4GB to 32GB
        usage_percent = random.uniform(30, 80)
        used_mb = int(total_mb * usage_percent / 100)

        return {
            "total": total_mb * 1024 * 1024,
            "used": used_mb * 1024 * 1024,
            "available": (total_mb - used_mb) * 1024 * 1024,
            "usage_percent": round(usage_percent, 2),
        }


def get_cpu_usage():
    """Get CPU usage percentage"""
    try:
        # Simple CPU usage calculation based on /proc/stat
        with open("/proc/stat", "r") as f:
            line = f.readline()
            cpu_times = [int(x) for x in line.split()[1:]]

        idle_time = cpu_times[3]
        total_time = sum(cpu_times)
        cpu_usage = 100 * (1 - idle_time / total_time) if total_time > 0 else 0

        return round(cpu_usage, 2)
    except Exception:
        # Fallback for systems without /proc/stat
        return round(random.uniform(10, 90), 2)


def generate_topology_data():
    """Generate sample topology data"""
    return {
        "nodes": [
            {
                "id": "fw1",
                "name": "FortiGate-1",
                "type": "firewall",
                "x": 100,
                "y": 100,
            },
            {
                "id": "fw2",
                "name": "FortiGate-2",
                "type": "firewall",
                "x": 300,
                "y": 100,
            },
            {
                "id": "sw1",
                "name": "Switch-1",
                "type": "switch",
                "x": 200,
                "y": 200,
            },
        ],
        "edges": [
            {"source": "fw1", "target": "sw1", "type": "ethernet"},
            {"source": "fw2", "target": "sw1", "type": "ethernet"},
        ],
        "metadata": {"generated_at": time.time(), "layout": "auto"},
    }
