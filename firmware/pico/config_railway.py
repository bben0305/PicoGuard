"""
PicoGuard 裝置設定檔 - Railway 部署版本
部署到 Railway 後使用此配置
"""

# ==================== 裝置識別 ====================
DEVICE_ID = "pico-001"

# ==================== WiFi 設定 ====================
WIFI_SSID = "3322"
WIFI_PASSWORD = "0975583835"

# ==================== API 設定 ====================
# Railway 部署後的 API 位址（替換為實際網址）
API_BASE_URL = "https://your-app.railway.app"
API_KEY = "picoguard-device-key-2024"

# ==================== 硬體腳位 ====================
# 土壤濕度感測器 (ADC0)
SOIL_MOISTURE_PIN = 26

# 感測器電源控制 (GPIO22)
SENSOR_POWER_PIN = 22

# 水泵控制 (GPIO15, PWM)
PUMP_PIN = 15

# ==================== 校準值 ====================
# 土壤濕度校準（需實際測量）
SOIL_DRY_VALUE = 60000    # 乾燥時的 ADC 值
SOIL_WET_VALUE = 20000    # 濕潤時的 ADC 值

# ==================== 運作參數 ====================
# 數據上傳間隔 (秒)
UPLOAD_INTERVAL = 60

# 感測器預熱時間 (毫秒)
SENSOR_WARMUP_TIME = 2000

# 逃生延遲 - 避免無限循環 (秒)
ESCAPE_DELAY = 300

# ==================== 功能開關 ====================
ENABLE_PUMP = False          # 水泵功能
ENABLE_TEMP_SENSOR = True    # 溫度感測器

# ==================== ESP01 設定 ====================
# ESP01 UART 設定 (固定使用 UART0)
UART_BAUDRATE = 115200

# HTTP 請求超時 (毫秒)
HTTP_TIMEOUT = 10000
