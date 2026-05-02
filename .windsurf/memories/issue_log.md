# PicoGuard 問題記錄簿

## 📋 問題追蹤

### 🔴 待解決

#### ISSUE-004: ESP01 AT 指令 TypeError
- **時間**: 2026-04-29
- **模組**: firmware/pico/main.py
- **症狀**: 
  ```
  TypeError: function doesn't take keyword arguments
  File "main.py", line 76, in connect_wifi
  File "main.py", line 69, in esp_at_command
  ```
- **觸發**: 執行 `esp_at_command("AT", 500)` 時
- **ESP01 回應**: 實際有回應 `b'AT\r\n\r\nOK\r\n'`，但後續跳錯誤
- **根因**: MicroPython 對函數類型提示 (`def func() -> type:`) 支援不完整
- **解法**: 
  - 移除所有函數類型提示 `-> dict`, `-> tuple`, `-> bool`
  - 改為 `(cmd + "\r\n").encode()` 而非 f-string
  - `decode('utf-8')` 外包 try/except
- **檔案**: `firmware/pico/main.py` 全檔修正
- **狀態**: ✅ 已修正已解決

#### ISSUE-005: DHT22 模組不存在 / 改用內建溫度感測器
- **時間**: 2026-04-29
- **模組**: firmware/pico/main.py, config.py
- **症狀**: `DHT22 讀取失敗: no module named 'dht'`
- **根因**: 
  1. 使用者只有 Pico 內建溫度感測器 (ADC4)，無 DHT22 硬體
  2. MicroPython 韌體可能未包含 `dht` 模組
- **解法**: 
  - 移除 DHT22 支援，改用 `ADC(4)` 內建溫度感測器
  - 使用溫度換算公式: `27 - (reading - 0.706) / 0.001721`
  - 新增 `ENABLE_TEMP_SENSOR` 設定開關
  - 更新 `read_sensors()` 回傳資料結構（移除 humidity 欄位）
- **檔案**: 
  - `firmware/pico/config.py`: 移除 ENABLE_DHT22/DHT_PIN，新增 ENABLE_TEMP_SENSOR
  - `firmware/pico/main.py`: 替換 `_read_dht22()` 為 `_read_temperature()`
- **狀態**: ✅ 已修正已解決

#### ISSUE-006: uart.write 缺少 .encode()
- **時間**: 2026-04-30
- **模組**: firmware/pico/main.py
- **症狀**: `上傳失敗: function doesn't take keyword arguments`
- **根因**: `self.uart.write(http_request)` 傳送字串而非 bytes
- **解法**: 改為 `self.uart.write(http_request.encode())`
- **位置**: `http_post()` 函數第 136 行
- **狀態**: ✅ 已修正

#### ISSUE-007: HTTP POST Body 被 AT+CIPCLOSE 污染
- **時間**: 2026-05-02
- **模組**: firmware/pico/main.py
- **症狀**: 
  ```
  Body: b'{"timestamp": ..., "temperaturAT+CIPCLOSE'
  ```
- **根因**: 
  1. ESP01 前一次連接未正確關閉
  2. ESP01 處於透傳模式，AT 指令被當成數據發送
- **解法**: 
  1. 每次 HTTP 請求前發送 `+++` 退出透傳模式
  2. 發送 `AT+CIPCLOSE` 關閉殘留連接
  3. 等待 `>` 提示符確認進入 CIPSEND 模式
  4. Host header 使用 `picoguard-production.up.railway.app`
  5. JSON body 添加 `\r\n` 結尾
- **關鍵程式碼**: `_http_post_tcp()` 函數開頭的恢復邏輯
- **狀態**: ✅ 已解決，數據成功上傳

#### ISSUE-008: HTTP POST Body 被 AT+CIPCLOSE 污染（最終修復）
- **時間**: 2026-05-02
- **症狀**: 
  1. 後端收到 `AT+CIPCLOSE` 污染的 JSON: `"temperatureAT+CIPCLOSE"`
  2. Pico 未收到 `SEND OK` 回應
  3. HTTP 數據 329 bytes 部分發送失敗
- **根因**: 
  1. UART 緩衝區太小，無法容納完整 HTTP 請求
  2. 發送後無冷靜期，AT 指令干擾數據傳輸
  3. 分離讀取 SEND OK 和伺服器回應導致數據遺失
- **解法**: 
  1. **加大 UART 緩衝區**: `txbuf=1024, rxbuf=1024`
  2. **強制完整寫入**: 循環確保所有 bytes 進入硬體
  3. **1.5秒冷靜期**: `time.sleep_ms(1500)` 確保數據離開緩衝區
  4. **統一緩衝區讀取**: 合併 SEND OK 和伺服器回應讀取
  5. **移除 +++ 退出透傳**: 非透傳模式不需要
- **關鍵程式碼**: 
  ```python
  # UART 初始化
  UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1), txbuf=1024, rxbuf=1024)
  
  # 強制完整寫入
  bytes_to_send = len(http_bytes)
  written = 0
  while written < bytes_to_send:
      result = self.uart.write(http_bytes[written:])
      if result:
          written += result
  time.sleep_ms(1500)  # 冷靜期
  
  # 統一緩衝區讀取
  raw_buffer = b""
  while time.time() < timeout:
      if self.uart.any():
          chunk = self.uart.read()
          raw_buffer += chunk
  ```
- **狀態**: ✅ 已解決，數據穩定上傳無污染

---

### 已解決

#### ISSUE-003: 開發除錯卡死風險
- **時間**: 2026-04-21
- **解法**: 加入 `ESCAPE_DELAY` 設定
- **實作**: `config.ESCAPE_DELAY` + `main.py` 開機延遲
- **狀態**: ✅ 已實作

---

## 🔍 記憶系統同步準則

### 每次重大修復後必須更新：

1. **issue_log.md** - 記錄問題、根因、解決方案、關鍵程式碼
2. **tech_stack.json** - 更新技術細節和部署狀態
3. **firmware_context.md** - 記錄韌體層面的重要修復
4. **project_overview.md** - 更新系統整體狀態

### 自動檢查清單：
- [ ] 問題是否完全解決？
- [ ] 解決方案是否記錄在 issue_log.md？
- [ ] 技術細節是否更新在 tech_stack.json？
- [ ] 上下文文件是否同步？
- [ ] 是否有遺漏的調試代碼需要清理？

#### ISSUE-002: MicroPython 語法不相容
- **時間**: 2026-04-21
- **症狀**: `int | None` 型別提示導致 SyntaxError
- **解法**: 改為 `SENSOR_POWER_PIN = 22` (移除型別提示)
- **檔案**: `firmware/pico/config.py`
- **狀態**: ✅ 已修正

#### ISSUE-001: 多個 Python 依賴缺失
- **時間**: 2026-04-21
- **症狀**: 
  - `uvicorn: The term is not recognized`
  - `ModuleNotFoundError: No module named 'fastapi'`
  - `ModuleNotFoundError: No module named 'pydantic_settings'`
- **解法**: 
  ```bash
  pip install uvicorn
  pip install fastapi
  pip install pydantic-settings python-dotenv
  ```
- **狀態**: ✅ 已解決

---

## 📚 經驗教訓

### MicroPython 開發
1. **永遠不要使用 Python 3.10+ 新語法**
   - ❌ `int | None` → ✅ 直接賦值
   - ❌ `match/case` → ✅ 使用 if/elif
   
2. **字串處理**
   - f-string 支援但可能有邊界情況
   - 傳統 `+` 連接更安全
   - `bytes` vs `str` 轉換要明確

3. **UART 通訊**
   - ESP01 AT 指令需 `\r\n` 結尾
   - 回應讀取後需解碼 `decode('utf-8', errors='ignore')`
   - 超時處理使用 `time.ticks_ms()`

### 後端開發
1. **虛擬環境啟動**
   - Windows: `.venv\Scripts\activate`
   - 確認 `(.venv)` 前綴出現再執行指令

2. **依賴安裝順序**
   - 優先安裝 `requirements.txt`
   - 個別安裝可能漏掉子依賴

---

## 🔍 除錯指令速查

### Pico MicroPython
```python
# 測試 ESP01 基本通訊
import machine
uart = machine.UART(0, baudrate=115200, tx=machine.Pin(0), rx=machine.Pin(1))
uart.write(b"AT\r\n")
uart.read()

# 測試 GPIO
from machine import Pin
p = Pin(22, Pin.OUT)
p.value(1)  # 通電
p.value(0)  # 斷電

# 測試 ADC
from machine import ADC
adc = ADC(26)
adc.read_u16()
```

### 後端
```bash
# 確認虛擬環境
which python
# 應顯示: c:/Users/bben0/PicoGuard/.venv/Scripts/python.exe

# 檢查已安裝套件
pip list | findstr fastapi
pip list | findstr uvicorn

# 啟動伺服器
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
