# Firmware (Pico) 子專案上下文

## 🎯 本模組目標
MicroPython 韌體，負責感測器數據收集並透過 ESP01 WiFi 模組上傳至後端 API。

## 📁 檔案結構
```
firmware/pico/
├── main.py              # 主程式 (PicoGuardDevice 類)
├── config.py            # 裝置設定參數
└── main_legacy.py       # 備份：原始 ThingSpeak 版本
```

## 🔧 技術棧
- **語言**: MicroPython (相容 Python 3 語法子集)
- **硬體**: Raspberry Pi Pico (RP2040)
- **WiFi**: ESP01 (ESP8266) 透過 UART0 AT 指令
- **感測器**: 土壤濕度 (ADC), DHT22 (可選)

## 🔌 硬體接線

### ESP01 連接 (UART0)
| ESP01 | Pico | 說明 |
|-------|------|------|
| TX    | GP0  | UART0 RX |
| RX    | GP1  | UART0 TX |
| VCC   | 3.3V | 電源 |
| GND   | GND  | 接地 |
| EN    | 3.3V | 啟用 |

### 感測器連接
| 感測器 | Pico | 說明 |
|--------|------|------|
| 土壤 VCC | GP22 | 防鏽電源控制 |
| 土壤 SIG | GP26 (ADC0) | 類比訊號 |
| DHT22 Data | GP16 | 溫濕度 (可選) |

## ⚠️ 已遇到的問題

### Issue #1: MicroPython 語法不相容 ✅
- **錯誤**: `int | None` 型別提示不被支援
- **解法**: 移除型別提示，改為 `SENSOR_POWER_PIN = 22`

### Issue #2: 感測器生鏽問題 ✅
- **解法**: GPIO 22 電源控制，讀取時通電、讀完斷電

### Issue #3: 開發除錯卡死 ✅
- **解法**: `ESCAPE_DELAY` 開機延遲，給 Thonny 時間攔截

### Issue #4: HTTP POST 請求失敗（最終修復） ✅
- **原因**: UART 緩衝區太小 + AT 指令干擾數據傳輸
- **關鍵修復**: 
  1. **UART 緩衝區**: `txbuf=1024, rxbuf=1024` 容納 329+ bytes
  2. **強制完整寫入**: 循環確保所有 bytes 進入硬體
  3. **1.5秒冷靜期**: 避免後續 AT 指令干擾
  4. **統一緩衝區讀取**: 防止 SEND OK 吞掉伺服器回應
  5. **移除 +++**: 非透傳模式不需要
- **狀態**: ✅ 已解決，數據穩定上傳無污染

## 📝 關鍵程式碼片段

### ESP01 AT 指令發送
```python
def esp_at_command(self, cmd: str, timeout: int = 2000) -> str:
    self.uart.write(f"{cmd}\r\n")
    time.sleep_ms(timeout)
    response = b""
    while self.uart.any():
        response += self.uart.read()
    return response.decode('utf-8', errors='ignore')
```

### 防鏽讀取邏輯
```python
def read_soil_moisture(self) -> tuple:
    self.sensor_power.value(1)     # 通電
    time.sleep_ms(200)              # 等待穩定
    raw_val = self.soil_sensor.read_u16()
    self.sensor_power.value(0)     # 斷電防鏽
    # ... 換算百分比
```

## 📋 配置參數 (config.py)
| 參數 | 預設值 | 說明 |
|------|--------|------|
| `WIFI_SSID` | "3322" | WiFi 名稱 |
| `WIFI_PASSWORD` | "0975583835" | WiFi 密碼 |
| `API_BASE_URL` | "http://192.168.1.100:8000" | 後端位址 |
| `SENSOR_POWER_PIN` | 22 | 防鏽電源腳位 |
| `SOIL_DRY_VALUE` | 60000 | 乾燥校準值 |
| `SOIL_WET_VALUE` | 20000 | 潮濕校準值 |
| `ESCAPE_DELAY` | 0 | 開機延遲秒數 |
| `SEND_INTERVAL` | 60 | 上傳間隔秒數 |

## 🔧 除錯技巧
1. 使用 Thonny IDE 直接連接 Pico REPL
2. 設定 `ESCAPE_DELAY = 5` 避免卡死
3. 監看 UART 輸出確認 ESP01 回應
4. 手動測試 AT 指令：`uart.write(b"AT\r\n")`
