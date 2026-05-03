"""
PicoGuard 裝置設定檔 - Railway 部署版本
基於原始 config.py，僅修改 API_BASE_URL 和 API_KEY
"""

# ==================== 裝置識別 ====================
DEVICE_ID = "pico-001"  # 裝置唯一識別碼

# ==================== WiFi 設定 ====================
WIFI_SSID = "3322"
WIFI_PASSWORD = "0975583835"

# ==================== API 設定 ====================
# Railway 部署後的 API 位址 (使用端口 8080)
API_BASE_URL = "http://switchyard.proxy.rlwy.net:46394"
API_KEY = "picoguard-device-key-2024"  # 與後端環境變數一致的 API 金鑰

# ==================== ESP01 設定 ====================
# ESP01 接線（UART0）：
#   ESP01 TX -> Pico GPIO 0 (UART0 RX)
#   ESP01 RX -> Pico GPIO 1 (UART0 TX)
#   ESP01 VCC -> 3.3V
#   ESP01 GND -> GND
#   ESP01 EN -> 3.3V (啟用腳)
#   ESP01 RST -> 可接 Pico GPIO 用於重置（選配）

# ==================== 硬體腳位 ====================
# 土壤濕度感測器（類比）
SOIL_SENSOR_PIN = 26  # ADC0 (GPIO 26)

# 防鏽設計：感測器電源開關（透過 GPIO 控制通斷，防止電解反應）
# 設為 None 則不使用此功能
SENSOR_POWER_PIN = 22  # GPIO 22 控制感測器電源，或設為 None 停用

# 內建溫度感測器（Pico 內建 ADC4）
ENABLE_TEMP_SENSOR = True  # Pico 內建溫度感測器，無需外接硬體

# 內建 LED（狀態指示）
LED_PIN = 25

# 水泵（可選功能）
ENABLE_PUMP = True  # 設為 True 啟用水泵
PUMP_PIN = 2  # GPIO 2 (數位控制，低電平觸發）

# ==================== 運作參數 ====================
# 數據上傳間隔（秒）
SEND_INTERVAL = 60  # 每 60 秒上傳一次

# 感測器讀取次數（用於平均值）
SENSOR_READ_SAMPLES = 5

# 澆水預設時間（毫秒）
DEFAULT_WATER_DURATION = 2000

# 土壤濕度警戒值（%）
SOIL_MOISTURE_LOW_THRESHOLD = 30  # 低於此值需要澆水
SOIL_MOISTURE_HIGH_THRESHOLD = 80  # 高於此值過濕警示

# 土壤濕度校準值（原始 ADC 數值）
# 請根據實際測量調整：乾燥時感測器懸空讀數 / 潮濕時放入水中讀數
SOIL_DRY_VALUE = 64000   # 乾燥時原始值（已更新為實際測量值）
SOIL_WET_VALUE = 20000   # 潮濕時原始值（約 20k）

# ESP01 AT 指令設定
ESP_BAUDRATE = 115200  # ESP01 通訊波特率

# 開發除錯設定
ESCAPE_DELAY = 0  # 開機延遲秒數（供 Thonny 停止程式用，上線後設為 0）
