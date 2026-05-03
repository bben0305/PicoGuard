// PicoGuard 儀表板 JavaScript

// Chart.js 圖表實例
let tempChart = null;
let moistureChart = null;

// DOM 元素
const dashboardElements = {
    lastUpdate: document.getElementById('last-update'),
    deviceStatus: document.getElementById('device-status'),
    waterBtn: document.getElementById('water-btn'),
    updateFrequency: document.getElementById('update-frequency'),
    dataTableBody: document.getElementById('data-table-body'),
    avgTemp: document.getElementById('avg-temp'),
    avgMoisture: document.getElementById('avg-moisture'),
    minTemp: document.getElementById('min-temp'),
    maxTemp: document.getElementById('max-temp')
};

// 初始化圖表
function initCharts() {
    // 溫度趨勢圖
    const tempCtx = document.getElementById('tempChart').getContext('2d');
    tempChart = new Chart(tempCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '溫度 (°C)',
                data: [],
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });

    // 土壤濕度圖
    const moistureCtx = document.getElementById('moistureChart').getContext('2d');
    moistureChart = new Chart(moistureCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '土壤濕度 (%)',
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
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// 更新圖表數據
function updateCharts(data) {
    if (!data || data.length === 0) return;

    // 準備圖表數據（最近20筆）
    const recentData = data.slice(0, 20).reverse();
    const labels = recentData.map(item => {
        const date = new Date(item.timestamp);
        // 转换为台湾时间 (UTC+8)
        const taiwanTime = new Date(date.getTime() + (8 * 60 * 60 * 1000));
        return taiwanTime.toLocaleTimeString('zh-TW', {
            hour: '2-digit',
            minute: '2-digit'
        });
    });

    const temperatures = recentData.map(item => item.temperature);
    const moisture = recentData.map(item => item.soil_moisture);

    // 更新溫度圖表
    tempChart.data.labels = labels;
    tempChart.data.datasets[0].data = temperatures;
    tempChart.update();

    // 更新濕度圖表
    moistureChart.data.labels = labels;
    moistureChart.data.datasets[0].data = moisture;
    moistureChart.update();
}

// 更新數據表格
function updateDataTable(data) {
    if (!data || data.length === 0) {
        dashboardElements.dataTableBody.innerHTML = `
            <tr>
                <td colspan="4" style="text-align: center; color: var(--text-secondary);">
                    無數據
                </td>
            </tr>
        `;
        return;
    }

    const rows = data.slice(0, 10).map(item => {
        const date = new Date(item.timestamp);
        // 转换为台湾时间 (UTC+8)
        const taiwanTime = new Date(date.getTime() + (8 * 60 * 60 * 1000));
        const timeStr = taiwanTime.toLocaleString('zh-TW', {
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });

        const tempDisplay = item.temperature !== null ? `${item.temperature}°C` : '-';
        const moistureDisplay = `${item.soil_moisture}%`;
        const rawDisplay = item.soil_raw !== null ? item.soil_raw : '-';

        return `
            <tr>
                <td>${timeStr}</td>
                <td>${tempDisplay}</td>
                <td>${moistureDisplay}</td>
                <td>${rawDisplay}</td>
            </tr>
        `;
    }).join('');

    dashboardElements.dataTableBody.innerHTML = rows;
}

// 更新統計數據
function updateStats(data) {
    if (!data || data.length === 0) {
        dashboardElements.avgTemp.textContent = '-';
        dashboardElements.avgMoisture.textContent = '-';
        dashboardElements.minTemp.textContent = '-';
        dashboardElements.maxTemp.textContent = '-';
        return;
    }

    const validTemps = data.filter(item => item.temperature !== null).map(item => item.temperature);
    const moistureValues = data.map(item => item.soil_moisture);

    if (validTemps.length > 0) {
        const avgTemp = validTemps.reduce((a, b) => a + b, 0) / validTemps.length;
        const minTemp = Math.min(...validTemps);
        const maxTemp = Math.max(...validTemps);

        dashboardElements.avgTemp.textContent = avgTemp.toFixed(1);
        dashboardElements.minTemp.textContent = minTemp.toFixed(1);
        dashboardElements.maxTemp.textContent = maxTemp.toFixed(1);
    }

    if (moistureValues.length > 0) {
        const avgMoisture = moistureValues.reduce((a, b) => a + b, 0) / moistureValues.length;
        dashboardElements.avgMoisture.textContent = avgMoisture.toFixed(1);
    }
}

// 更新裝置狀態
async function updateDeviceStatus() {
    try {
        const response = await PicoGuard.apiRequest('/sensors/devices');
        
        if (response.status === 'success' && response.devices.length > 0) {
            const device = response.devices[0];
            
            let statusHtml = '';
            if (device.is_online) {
                statusHtml = '<span class="badge badge-success">在線</span>';
                dashboardElements.waterBtn.disabled = false;
            } else if (device.offline_minutes !== null && device.offline_minutes < 30) {
                statusHtml = '<span class="badge badge-warning">離線 ' + device.offline_minutes + ' 分鐘</span>';
                dashboardElements.waterBtn.disabled = true;
            } else {
                statusHtml = '<span class="badge badge-danger">離線</span>';
                dashboardElements.waterBtn.disabled = true;
            }

            dashboardElements.deviceStatus.innerHTML = statusHtml;
        } else {
            dashboardElements.deviceStatus.innerHTML = '<span class="badge badge-danger">無裝置</span>';
            dashboardElements.waterBtn.disabled = true;
        }
    } catch (error) {
        dashboardElements.deviceStatus.innerHTML = '<span class="badge badge-danger">錯誤</span>';
        dashboardElements.waterBtn.disabled = true;
    }
}

// 觸發澆水
async function triggerWatering() {
    if (!confirm('確定要啟動澆水嗎？')) return;

    dashboardElements.waterBtn.disabled = true;
    dashboardElements.waterBtn.textContent = '執行中...';

    try {
        // 實作澆水 API
        const response = await PicoGuard.apiRequest('/controls/water', {
            method: 'POST',
            body: JSON.stringify({ duration: 3000 })
        });
        
        console.log('澆水響應:', response);
        alert('澆水指令已發送！Pico 將在下一次數據上傳時執行澆水。');
    } catch (error) {
        console.error('澆水請求失敗:', error);
        alert('澆水失敗: ' + error.message);
    } finally {
        dashboardElements.waterBtn.disabled = false;
        dashboardElements.waterBtn.textContent = '啟動澆水 (2秒)';
    }
}

// 更新最後更新時間
function updateLastUpdateTime() {
    const now = new Date();
    // 转换为台湾时间 (UTC+8)
    const taiwanTime = new Date(now.getTime() + (8 * 60 * 60 * 1000));
    dashboardElements.lastUpdate.textContent = 
        '最後更新: ' + taiwanTime.toLocaleTimeString('zh-TW');
}

// 重新整理儀表板
async function refreshDashboard() {
    console.log('重新整理儀表板...');
    
    try {
        // 獲取最新數據
        const data = await PicoGuard.apiRequest('/sensors/data?limit=50');
        
        // 更新各個組件
        updateCharts(data);
        updateDataTable(data);
        updateStats(data);
        updateDeviceStatus();
        updateLastUpdateTime();
        
    } catch (error) {
        console.error('重新整理失敗:', error);
    }
}

// 自動更新儀表板
let autoUpdateInterval = null;

function startAutoUpdate() {
    const frequency = parseInt(dashboardElements.updateFrequency.value) * 1000;
    
    // 清除舊的定時器
    if (autoUpdateInterval) {
        clearInterval(autoUpdateInterval);
    }
    
    // 設定新的定時器
    autoUpdateInterval = setInterval(refreshDashboard, frequency);
    console.log('自動更新已啟動，頻率:', frequency / 1000, '秒');
}

// 監聽更新頻率變化
dashboardElements.updateFrequency.addEventListener('change', startAutoUpdate);

// 初始化儀表板
async function initDashboard() {
    console.log('初始化儀表板...');
    
    // 初始化圖表
    initCharts();
    
    // 初始載入數據
    await refreshDashboard();
    
    // 啟動自動更新
    startAutoUpdate();
}

// 頁面載入完成後初始化
document.addEventListener('DOMContentLoaded', initDashboard);

// 導出函數供 HTML 使用
window.triggerWatering = triggerWatering;
window.refreshDashboard = refreshDashboard;
