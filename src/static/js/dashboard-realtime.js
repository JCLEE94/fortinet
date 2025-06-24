/**
 * 대시보드 실시간 기능 고도화
 * WebSocket 연결, 실시간 업데이트, 고급 분석 통합
 */

// Socket.IO 연결
const socket = io('/dashboard', {
    transports: ['websocket', 'polling']
});

// 전역 차트 변수
let performanceChart = null;
let trafficChart = null;
let anomalyChart = null;

// 실시간 메트릭 업데이트
socket.on('metrics_update', (data) => {
    updateDashboardMetrics(data);
});

// 실시간 알림
socket.on('new_alert', (alert) => {
    displayNewAlert(alert);
    playAlertSound(alert.severity);
});

// 이상 징후 감지
socket.on('anomaly_detected', (anomaly) => {
    displayAnomaly(anomaly);
});

// 연결 상태
socket.on('connect', () => {
    console.log('Dashboard connected to real-time updates');
    updateConnectionStatus('connected');
});

socket.on('disconnect', () => {
    console.log('Dashboard disconnected from real-time updates');
    updateConnectionStatus('disconnected');
});

// 대시보드 메트릭 업데이트
function updateDashboardMetrics(metrics) {
    // 통계 카드 업데이트
    if (metrics.total_devices !== undefined) {
        animateValue('total-devices', metrics.total_devices);
    }
    if (metrics.online_devices !== undefined) {
        animateValue('online-devices', metrics.online_devices);
        updateDeviceHealthBar(metrics.online_devices, metrics.total_devices);
    }
    if (metrics.total_traffic !== undefined) {
        const trafficElement = document.getElementById('total-traffic');
        if (trafficElement) {
            trafficElement.textContent = formatTraffic(metrics.total_traffic);
        }
    }
    if (metrics.active_alerts !== undefined) {
        animateValue('active-alerts', metrics.active_alerts);
        updateAlertIndicator(metrics.active_alerts);
    }
    
    // 성능 차트 업데이트
    if (performanceChart && metrics.performance_data) {
        updatePerformanceChart(metrics.performance_data);
    }
    
    // 디바이스 리스트 업데이트
    if (metrics.top_devices) {
        updateTopDevices(metrics.top_devices);
    }
}

// 숫자 애니메이션
function animateValue(id, value, duration = 500) {
    const element = document.getElementById(id);
    if (!element) return;
    
    const current = parseInt(element.textContent) || 0;
    const increment = (value - current) / (duration / 16);
    let currentValue = current;
    
    const timer = setInterval(() => {
        currentValue += increment;
        if ((increment > 0 && currentValue >= value) || (increment < 0 && currentValue <= value)) {
            element.textContent = value;
            clearInterval(timer);
        } else {
            element.textContent = Math.round(currentValue);
        }
    }, 16);
}

// 새 알림 표시
function displayNewAlert(alert) {
    const alertHtml = `
        <div class="alert-item alert-${alert.severity} animate-slide-in" data-alert-id="${alert.id}">
            <i class="fas fa-${getAlertIcon(alert.severity)} alert-icon" style="color: var(--${getAlertColor(alert.severity)});"></i>
            <div class="alert-content">
                <div class="alert-title">${escapeHtml(alert.title)}</div>
                <div class="alert-description">${escapeHtml(alert.message)}</div>
                <div class="alert-time">${formatTime(alert.timestamp)}</div>
            </div>
            <button class="alert-action" onclick="acknowledgeAlert('${alert.id}')">
                <i class="fas fa-check"></i>
            </button>
        </div>
    `;
    
    const alertList = document.querySelector('.alert-list');
    if (alertList) {
        alertList.insertAdjacentHTML('afterbegin', alertHtml);
        
        // 최대 10개 유지
        const alerts = alertList.querySelectorAll('.alert-item');
        if (alerts.length > 10) {
            alerts[alerts.length - 1].remove();
        }
    }
    
    // 브라우저 알림
    if (alert.severity === 'critical' || alert.severity === 'error') {
        showBrowserNotification(alert);
    }
}

// 이상 징후 표시
function displayAnomaly(anomaly) {
    const anomalyHtml = `
        <div class="anomaly-card animate-pulse-once">
            <div class="anomaly-header">
                <i class="fas fa-exclamation-triangle"></i>
                <span>이상 징후 감지</span>
            </div>
            <div class="anomaly-content">
                <div class="anomaly-metric">${anomaly.metric}</div>
                <div class="anomaly-value">
                    현재: ${anomaly.current_value} 
                    (정상 범위: ${anomaly.expected_range[0]} - ${anomaly.expected_range[1]})
                </div>
            </div>
        </div>
    `;
    
    const container = document.getElementById('anomaly-container');
    if (container) {
        container.insertAdjacentHTML('beforeend', anomalyHtml);
        
        // 5초 후 제거
        setTimeout(() => {
            const card = container.lastElementChild;
            card.classList.add('animate-fade-out');
            setTimeout(() => card.remove(), 300);
        }, 5000);
    }
}

// 성능 차트 업데이트
function updatePerformanceChart(data) {
    if (!performanceChart) return;
    
    const now = new Date();
    const label = formatChartTime(now);
    
    // 새 데이터 포인트 추가
    performanceChart.data.labels.push(label);
    performanceChart.data.datasets[0].data.push(data.inbound);
    performanceChart.data.datasets[1].data.push(data.outbound);
    
    // 최대 50개 포인트 유지
    if (performanceChart.data.labels.length > 50) {
        performanceChart.data.labels.shift();
        performanceChart.data.datasets[0].data.shift();
        performanceChart.data.datasets[1].data.shift();
    }
    
    performanceChart.update('none');
}

// 상위 디바이스 업데이트
function updateTopDevices(devices) {
    const deviceList = document.querySelector('.device-list');
    if (!deviceList) return;
    
    const html = devices.map(device => `
        <div class="device-item">
            <div class="device-info">
                <div class="status-indicator status-${device.status}"></div>
                <div>
                    <div class="device-name">${escapeHtml(device.name)}</div>
                    <div class="device-ip">${device.ip}</div>
                </div>
            </div>
            <div class="device-stats">
                <div class="device-value">${formatTraffic(device.traffic)}</div>
                <div class="device-trend trend-${device.trend > 0 ? 'up' : 'down'}">
                    ${device.trend > 0 ? '↑' : '↓'} ${Math.abs(device.trend)}%
                </div>
            </div>
        </div>
    `).join('');
    
    deviceList.innerHTML = html;
}

// 고급 분석 로드
async function loadAdvancedAnalytics() {
    try {
        // 트래픽 패턴 분석
        const patternsResponse = await fetch('/api/analytics/traffic-patterns');
        const patternsData = await patternsResponse.json();
        
        if (patternsData.status === 'success') {
            updateTrafficPatterns(patternsData.patterns);
        }
        
        // 이상 징후 확인
        const anomaliesResponse = await fetch('/api/analytics/anomalies');
        const anomaliesData = await anomaliesResponse.json();
        
        if (anomaliesData.status === 'success' && anomaliesData.anomalies.length > 0) {
            anomaliesData.anomalies.forEach(anomaly => displayAnomaly(anomaly));
        }
        
        // 성능 병목 분석
        const bottlenecksResponse = await fetch('/api/analytics/bottlenecks');
        const bottlenecksData = await bottlenecksResponse.json();
        
        if (bottlenecksData.status === 'success') {
            updateBottlenecks(bottlenecksData.bottlenecks);
        }
        
    } catch (error) {
        console.error('Failed to load advanced analytics:', error);
    }
}

// 트래픽 패턴 업데이트
function updateTrafficPatterns(patterns) {
    // 피크 시간대 표시
    if (patterns.peak_hours && patterns.peak_hours.length > 0) {
        const peakHoursElement = document.getElementById('peak-hours');
        if (peakHoursElement) {
            peakHoursElement.textContent = patterns.peak_hours.join(', ') + '시';
        }
    }
    
    // 프로토콜 분포 차트 업데이트
    if (patterns.protocol_distribution) {
        updateProtocolChart(patterns.protocol_distribution);
    }
}

// 성능 병목 표시
function updateBottlenecks(bottlenecks) {
    const container = document.getElementById('bottlenecks-container');
    if (!container) return;
    
    if (bottlenecks.length === 0) {
        container.innerHTML = '<div class="no-issues">성능 이슈가 발견되지 않았습니다</div>';
        return;
    }
    
    const html = bottlenecks.map(bottleneck => `
        <div class="bottleneck-item ${bottleneck.severity}">
            <div class="bottleneck-type">
                <i class="fas fa-${getBottleneckIcon(bottleneck.type)}"></i>
                ${getBottleneckName(bottleneck.type)}
            </div>
            <div class="bottleneck-value">${bottleneck.value}%</div>
            <div class="bottleneck-recommendation">${bottleneck.recommendation}</div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

// 빠른 작업 핸들러
function handleQuickAction(action) {
    const actions = {
        '장치 추가': () => window.location.href = '/devices?action=add',
        '패킷 캡처': () => window.location.href = '/packet_sniffer',
        '리포트 생성': () => generateReport(),
        '시스템 설정': () => window.location.href = '/settings'
    };
    
    if (actions[action]) {
        actions[action]();
    }
}

// 자동 리포트 생성
async function generateReport() {
    const btn = event.target.closest('.quick-action-btn');
    const originalContent = btn.innerHTML;
    
    btn.innerHTML = '<i class="fas fa-spinner fa-spin quick-action-icon"></i><span>생성 중...</span>';
    btn.disabled = true;
    
    try {
        const response = await fetch('/api/automation/generate-report', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                report_type: 'summary',
                period: 'daily'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('리포트가 생성되었습니다', 'success');
            downloadReport(data.report_id);
        } else {
            showNotification('리포트 생성 실패', 'error');
        }
    } catch (error) {
        showNotification('리포트 생성 중 오류 발생', 'error');
    } finally {
        btn.innerHTML = originalContent;
        btn.disabled = false;
    }
}

// 리포트 다운로드
function downloadReport(reportId) {
    const link = document.createElement('a');
    link.href = `/api/reports/download/${reportId}`;
    link.download = `report_${reportId}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// 알림 확인
async function acknowledgeAlert(alertId) {
    try {
        const response = await fetch(`/api/alerts/acknowledge/${alertId}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const alertElement = document.querySelector(`[data-alert-id="${alertId}"]`);
            if (alertElement) {
                alertElement.classList.add('acknowledged');
            }
        }
    } catch (error) {
        console.error('Failed to acknowledge alert:', error);
    }
}

// 유틸리티 함수들
function getAlertIcon(severity) {
    const icons = {
        'info': 'info-circle',
        'warning': 'exclamation-triangle',
        'error': 'exclamation-circle',
        'critical': 'fire-alt'
    };
    return icons[severity] || 'info-circle';
}

function getAlertColor(severity) {
    const colors = {
        'info': 'info',
        'warning': 'warning',
        'error': 'danger',
        'critical': 'danger'
    };
    return colors[severity] || 'info';
}

function getBottleneckIcon(type) {
    const icons = {
        'cpu': 'microchip',
        'memory': 'memory',
        'network': 'network-wired',
        'disk': 'hdd'
    };
    return icons[type] || 'exclamation-triangle';
}

function getBottleneckName(type) {
    const names = {
        'cpu': 'CPU',
        'memory': '메모리',
        'network': '네트워크',
        'disk': '디스크'
    };
    return names[type] || type;
}

function formatTraffic(mbps) {
    if (mbps >= 1000) {
        return (mbps / 1000).toFixed(1) + ' Gbps';
    }
    return mbps.toFixed(0) + ' Mbps';
}

function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return '방금 전';
    if (diff < 3600000) return Math.floor(diff / 60000) + '분 전';
    if (diff < 86400000) return Math.floor(diff / 3600000) + '시간 전';
    return date.toLocaleDateString();
}

function formatChartTime(date) {
    return date.getHours().toString().padStart(2, '0') + ':' + 
           date.getMinutes().toString().padStart(2, '0');
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type} animate-slide-in`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        <span>${escapeHtml(message)}</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('animate-fade-out');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function updateConnectionStatus(status) {
    const indicator = document.getElementById('connection-status');
    if (indicator) {
        indicator.className = `connection-status ${status}`;
        indicator.title = status === 'connected' ? '실시간 연결됨' : '연결 끊김';
    }
}

function updateDeviceHealthBar(online, total) {
    const percentage = total > 0 ? (online / total) * 100 : 0;
    const healthBar = document.getElementById('device-health-bar');
    if (healthBar) {
        healthBar.style.width = percentage + '%';
        healthBar.className = `health-bar ${percentage > 90 ? 'good' : percentage > 70 ? 'warning' : 'critical'}`;
    }
}

function updateAlertIndicator(count) {
    const indicator = document.getElementById('alert-indicator');
    if (indicator) {
        indicator.className = `alert-indicator ${count > 0 ? 'active' : ''}`;
        if (count > 9) {
            indicator.textContent = '9+';
        } else if (count > 0) {
            indicator.textContent = count;
        } else {
            indicator.textContent = '';
        }
    }
}

function playAlertSound(severity) {
    if (severity === 'critical' || severity === 'error') {
        const audio = new Audio('/static/sounds/alert.mp3');
        audio.volume = 0.3;
        audio.play().catch(() => {});
    }
}

function showBrowserNotification(alert) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('Nextrade Alert', {
            body: alert.message,
            icon: '/static/img/nextrade/logo.png',
            badge: '/static/img/icons/icon-72x72.png'
        });
    }
}

// 초기화
document.addEventListener('DOMContentLoaded', () => {
    // 성능 차트 초기화
    const ctx = document.getElementById('performanceChart');
    if (ctx) {
        performanceChart = new Chart(ctx.getContext('2d'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Inbound',
                    data: [],
                    borderColor: '#22c55e',
                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Outbound',
                    data: [],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: '#94a3b8'
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(148, 163, 184, 0.1)'
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    },
                    y: {
                        grid: {
                            color: 'rgba(148, 163, 184, 0.1)'
                        },
                        ticks: {
                            color: '#94a3b8',
                            callback: function(value) {
                                return value + ' Gbps';
                            }
                        }
                    }
                }
            }
        });
    }
    
    // 빠른 작업 버튼 이벤트
    document.querySelectorAll('.quick-action-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const action = this.querySelector('span').textContent;
            handleQuickAction(action);
        });
    });
    
    // 시간 범위 선택기
    document.querySelectorAll('.btn-time').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.btn-time').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const range = this.textContent;
            loadChartData(range);
        });
    });
    
    // 고급 분석 로드
    loadAdvancedAnalytics();
    
    // 실시간 모니터링 시작
    socket.emit('subscribe_metrics', {dashboard: true});
    
    // 브라우저 알림 권한 요청
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
});

// 차트 데이터 로드
async function loadChartData(range) {
    try {
        const response = await fetch(`/api/metrics/performance?range=${encodeURIComponent(range)}`);
        const data = await response.json();
        
        if (data.success && performanceChart) {
            performanceChart.data = data.chartData;
            performanceChart.update();
        }
    } catch (error) {
        console.error('Failed to load chart data:', error);
    }
}