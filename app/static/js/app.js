// PicoGuard 前端 JavaScript

// API 基礎 URL
const API_BASE = '/api/v1';

// DOM 元素
const elements = {
    systemStatus: document.getElementById('system-status'),
    deviceCount: document.getElementById('device-count'),
    latestTemp: document.getElementById('latest-temp'),
    latestMoisture: document.getElementById('latest-moisture'),
    dataCount: document.getElementById('data-count')
};

// 工具函數
async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API 請求失敗 ${endpoint}:`, error);
        throw error;
    }
}

// 格式化時間（台灣時間 UTC+8）
function formatTime(timestamp) {
    if (!timestamp) return '-';
    const date = new Date(timestamp);
    // 轉換為台灣時間 (UTC+8)
    const taiwanTime = new Date(date.getTime() + (8 * 60 * 60 * 1000));
    return taiwanTime.toLocaleString('zh-TW', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 更新系統狀態
async function updateSystemStatus() {
    try {
        const response = await apiRequest('/sensors/devices');
        
        if (response.status === 'success' && response.devices.length > 0) {
            const latestDevice = response.devices[0];
            
            // 使用後端計算的 is_online 和 offline_minutes
            if (latestDevice.is_online) {
                elements.systemStatus.textContent = '系統正常運行';
                elements.systemStatus.style.color = 'var(--primary-color)';
            } else if (latestDevice.offline_minutes < 30) {
                elements.systemStatus.textContent = `最後更新: ${formatTime(latestDevice.last_seen)}`;
                elements.systemStatus.style.color = '#f59e0b';
            } else {
                elements.systemStatus.textContent = '裝置離線';
                elements.systemStatus.style.color = '#ef4444';
            }
        } else {
            elements.systemStatus.textContent = '無裝置連接';
            elements.systemStatus.style.color = '#ef4444';
        }
    } catch (error) {
        elements.systemStatus.textContent = '無法連接伺服器';
        elements.systemStatus.style.color = '#ef4444';
    }
}

// 更新統計數據
async function updateStats() {
    try {
        // 獲取裝置數量
        const devicesResponse = await apiRequest('/sensors/devices');
        const deviceCount = devicesResponse.status === 'success' ? devicesResponse.devices.length : 0;
        
        // 獲取最新數據
        const dataResponse = await apiRequest('/sensors/data');
        let latestTemp = '-';
        let latestMoisture = '-';
        
        if (dataResponse.length > 0) {
            const latest = dataResponse[0];
            latestTemp = latest.temperature !== null ? `${latest.temperature}°C` : '-';
            latestMoisture = `${latest.soil_moisture}%`;
        }
        
        // 獲取總數據量
        const totalDataResponse = await apiRequest('/sensors/data?limit=1000');
        const dataCount = totalDataResponse.length;
        
        // 更新 DOM
        elements.deviceCount.textContent = deviceCount;
        elements.latestTemp.textContent = latestTemp;
        elements.latestMoisture.textContent = latestMoisture;
        elements.dataCount.textContent = dataCount;
        
    } catch (error) {
        console.error('更新統計數據失敗:', error);
        elements.deviceCount.textContent = 'Error';
        elements.latestTemp.textContent = 'Error';
        elements.latestMoisture.textContent = 'Error';
        elements.dataCount.textContent = 'Error';
    }
}

// 初始化頁面
async function initPage() {
    console.log('PicoGuard 前端初始化...');
    
    // 初始載入
    await updateSystemStatus();
    await updateStats();
    
    // 定期更新
    setInterval(updateSystemStatus, 30000); // 30秒更新一次狀態
    setInterval(updateStats, 60000);       // 60秒更新一次統計
}

// 頁面載入完成後初始化
document.addEventListener('DOMContentLoaded', initPage);

// 導出函數供其他頁面使用
window.PicoGuard = {
    apiRequest,
    formatTime,
    updateSystemStatus,
    updateStats
};
