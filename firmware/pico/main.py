"""
PicoGuard 主程式
智能植栽監控裝置韌體（Pico + ESP01 版本）

負責：
- 感測器數據收集（內建溫度、土壤濕度）
- 透過 ESP01 (ESP8266) WiFi 模組傳輸數據至後端 API
- 可選：接收指令執行澆水動作

硬體接線：
- 土壤濕度感測器 -> ADC0 (GPIO 26)
- 防鏽電源控制 -> GPIO 22
- ESP01 TX/RX -> UART0 (GPIO 0/1)
- 水泵 (可選) -> GPIO 15
- 內建 LED -> 狀態指示
- 內建溫度感測器 -> ADC4 (無需接線)
"""

import time
from machine import Pin, ADC, PWM, UART

import config


class PicoGuardDevice:
    """PicoGuard 裝置控制器（Pico + ESP01 版本）"""

    def __init__(self):
        self.uart = None
        self.connected = False
        self.last_send_time = 0

        # 初始化感測器腳位
        self.soil_sensor = ADC(Pin(config.SOIL_SENSOR_PIN))
        self.led_status = Pin(config.LED_PIN, Pin.OUT)

        # 防鏽設計：使用 GPIO 控制感測器電源
        self.sensor_power = None
        if config.SENSOR_POWER_PIN is not None:
            self.sensor_power = Pin(config.SENSOR_POWER_PIN, Pin.OUT)
            self.sensor_power.value(0)  # 預設關閉電源
            print("防鏽電源控制已啟用 (GPIO " + str(config.SENSOR_POWER_PIN) + ")")

        # 初始化 UART 連接 ESP01 (TX=GPIO0, RX=GPIO1) - 嘗試多種波特率
        baudrates = [115200, 9600, 38400, 57600]
        self.uart = None
        
        for baud in baudrates:
            try:
                print("🔍 嘗試波特率:", baud)
                test_uart = UART(0, baudrate=baud, tx=Pin(0), rx=Pin(1), txbuf=1024, rxbuf=1024)  # 加大緩衝區
                time.sleep(1)
                
                # 清空緩衝區
                while test_uart.any():
                    test_uart.read()
                
                # 測試 AT 指令
                test_uart.write("AT\r\n".encode())
                time.sleep(1)
                
                response = b""
                while test_uart.any():
                    response += test_uart.read()
                
                if b"OK" in response:
                    print("✅ ESP01 連接成功，波特率:", baud)
                    self.uart = test_uart
                    break
                else:
                    print("❌ 波特率", baud, "無回應")
                    
            except Exception as e:
                print("❌ 波特率", baud, "測試失敗:", str(e))
        
        if self.uart is None:
            print("[ERR] ESP01 連接失敗 - 檢查接線和電源")
            print("💡 提示: 確保 ESP01 EN 腳連接到 3.3V")

        # 水泵為可選，嘗試初始化
        self.pump_pin = None
        if config.ENABLE_PUMP:
            try:
                self.pump_pin = PWM(Pin(config.PUMP_PIN))
                self.pump_pin.freq(1000)
                self.pump_pin.duty_u16(0)  # 初始關閉
                print("水泵已初始化")
            except Exception as e:
                print("[WARN] 水泵初始化失敗: " + str(e))

    def esp_at_command(self, cmd, timeout=2000):
        """發送 AT 指令到 ESP01"""
        if self.uart is None:
            return ""

        # MicroPython: 使用 bytes 而非 f-string
        self.uart.write((cmd + "\r\n").encode())
        time.sleep_ms(timeout)

        response = b""
        while self.uart.any():
            response += self.uart.read()

        try:
            return response.decode('utf-8')
        except:
            return ""

    def connect_wifi(self):
        """透過 ESP01 連接 WiFi 網路"""
        print("透過 ESP01 連接 WiFi: " + config.WIFI_SSID)

        # 測試 ESP01 通訊
        response = self.esp_at_command("AT", 500)
        if "OK" not in response:
            print("[ERR] ESP01 未回應")
            return False

        print("ESP01 通訊正常")

        # 設定 WiFi 模式為 STA
        self.esp_at_command("AT+CWMODE=1", 1000)

        # 連接 WiFi
        connect_cmd = 'AT+CWJAP="' + config.WIFI_SSID + '","' + config.WIFI_PASSWORD + '"'
        response = self.esp_at_command(connect_cmd, 10000)

        if "OK" in response or "WIFI GOT IP" in response:
            self.connected = True
            # 取得 IP 位址
            ip_response = self.esp_at_command("AT+CIFSR", 1000)
            print("WiFi 已連接，IP: " + ip_response)
            return True

        print("[ERR] WiFi 連線失敗: " + response)
        return False

    def http_post(self, url, data, headers):
        """使用 ESP01 發送 HTTP POST 請求 - 使用 AT+HTTPCLIENT 指令"""
        import json

        # 解析 URL
        url_parts = url.replace("http://", "").split("/")
        host_port = url_parts[0].split(":")
        host = host_port[0]
        port = host_port[1] if len(host_port) > 1 else "80"
        path = "/" + "/".join(url_parts[1:]) if len(url_parts) > 1 else "/"
        full_url = "http://" + host + ":" + port + path

        # 直接使用 TCP 方法（ESP01 不支援 AT+HTTPCLIENT）
        api_key = getattr(config, 'API_KEY', 'NOT_FOUND')
        return self._http_post_tcp(url, data, headers, api_key)

    def read_soil_moisture(self):
        """
        讀取土壤濕度（防鏽設計）
        若有電源控制腳位，則採用：通電 → 等待 → 讀取 → 斷電 流程
        """
        # 防鏽讀取邏輯：通電
        if self.sensor_power is not None:
            self.sensor_power.value(1)
            time.sleep_ms(200)  # 等待穩定

        # 取多次平均
        soil_sum = 0
        for _ in range(config.SENSOR_READ_SAMPLES):
            soil_sum += self.soil_sensor.read_u16()
            time.sleep_ms(10)

        raw_val = soil_sum // config.SENSOR_READ_SAMPLES

        # 防鏽讀取邏輯：立即斷電
        if self.sensor_power is not None:
            self.sensor_power.value(0)

        # 換算百分比（可根據實測調整閾值）
        # 預設：乾燥時 ~60000，潮濕時 ~20000
        dry_value = getattr(config, 'SOIL_DRY_VALUE', 60000)
        wet_value = getattr(config, 'SOIL_WET_VALUE', 20000)
        range_val = dry_value - wet_value

        if range_val > 0:
            soil_percent = int((dry_value - raw_val) / range_val * 100)
        else:
            soil_percent = 50

        soil_percent = max(0, min(100, soil_percent))
        return soil_percent, raw_val

    def _http_post_tcp(self, url, data, headers, api_key):
        """使用 TCP 發送 HTTP POST 請求"""
        # 解析 URL
        url_parts = url.replace("http://", "").split("/")
        host_port = url_parts[0].split(":")
        host = host_port[0]
        port = host_port[1] if len(host_port) > 1 else "80"
        path = "/" + "/".join(url_parts[1:]) if len(url_parts) > 1 else "/"

        # 關閉任何現有連接
        self.esp_at_command("AT+CIPCLOSE", 500)
        time.sleep_ms(100)

        # 建立 TCP 連接
        connect_cmd = 'AT+CIPSTART="TCP","' + host + '",' + port
        connect_response = self.esp_at_command(connect_cmd, 5000)

        if "CONNECT" not in connect_response and "OK" not in connect_response:
            return 0, "TCP connect failed"

        # 構建 HTTP 請求
        # 關鍵修正：Content-Length 必須是 JSON 數據的 bytes 長度
        # json_bytes = data.encode('utf-8')
        # content_length = len(json_bytes)

        body_with_newline = data + "\r\n"
        json_bytes = body_with_newline.encode('utf-8')
        content_length = len(json_bytes)
        
        http_request = "POST " + path + " HTTP/1.1\r\n"
        http_request += "Host: picoguard-production.up.railway.app\r\n"  # 強制使用 Railway 域名
        http_request += "Content-Type: application/json\r\n"
        http_request += "X-API-Key: " + api_key + "\r\n"
        http_request += "Content-Length: " + str(content_length) + "\r\n"
        http_request += "Connection: close\r\n"  # 要求伺服器關閉連接
        http_request += "\r\n"
        http_request += body_with_newline

        http_bytes = http_request.encode('utf-8')
        request_length = len(http_bytes)

        # 發送 CIPSEND
        print("CIPSEND: " + str(request_length))
        cipsend_cmd = "AT+CIPSEND=" + str(request_length)
        self.uart.write((cipsend_cmd + "\r\n").encode())
        
        # 等待 > 提示符
        print("等待 > ...")
        cipsend_resp = b""
        cipsend_timeout = time.time() + 3
        got_prompt = False
        while time.time() < cipsend_timeout:
            if self.uart.any():
                chunk = self.uart.read()
                if chunk:
                    cipsend_resp += chunk
                    if b">" in cipsend_resp:
                        got_prompt = True
                        print("✓ 收到 >")
                        break
                    if b"ERROR" in cipsend_resp:
                        print("✗ CIPSEND 錯誤")
                        return 0, "CIPSEND failed"
            time.sleep_ms(100)
        
        if not got_prompt:
            print("✗ 未收到 >")
            return 0, "No prompt"
        
        # 發送 HTTP 數據
        # 確保完整寫入
        bytes_to_send = len(http_bytes)
        written = 0
        while written < bytes_to_send:
            result = self.uart.write(http_bytes[written:])
            if result:
                written += result
        time.sleep_ms(1500)  # 冷靜期
        
        # 讀取回應
        time.sleep_ms(500)
        raw_buffer = b""
        timeout = time.time() + 15
        last_data_time = time.time()
        got_send_ok = False
        
        while time.time() < timeout:
            if self.uart.any():
                chunk = self.uart.read()
                if chunk:
                    raw_buffer += chunk
                    last_data_time = time.time()
                    
                    if not got_send_ok and b"SEND OK" in raw_buffer:
                        got_send_ok = True
                    
                    if b"SEND FAIL" in raw_buffer or b"ERROR" in raw_buffer:
                        return 0, "Send failed"
            else:
                if len(raw_buffer) > 0 and (time.time() - last_data_time) > 2:
                    break
                time.sleep_ms(100)
        
        if not got_send_ok:
            return 0, "No SEND OK"
        
        response = raw_buffer
        
        # 關閉連接
        self.esp_at_command("AT+CIPCLOSE", 1000)

        response_str = response.decode('utf-8', 'ignore')

        # 解析狀態碼
        status_code = 0
        if "HTTP/1.1" in response_str:
            try:
                status_code = int(response_str.split("HTTP/1.1 ")[1].split(" ")[0])
            except:
                pass

        return status_code, response_str

    def read_sensors(self):
        """讀取所有感測器數據（土壤濕度 + 內建溫度）"""
        # 讀取土壤濕度（防鏽設計）
        soil_percent, raw_val = self.read_soil_moisture()

        # 讀取內建溫度感測器
        temperature = self._read_temperature()

        return {
            "device_id": config.DEVICE_ID,
            "soil_moisture": soil_percent,
            "soil_raw": raw_val,  # 原始值供除錯
            "temperature": temperature,
            "timestamp": time.time(),
        }

    def _read_temperature(self):
        """讀取 Pico 內建溫度感測器 (ADC4)"""
        if not config.ENABLE_TEMP_SENSOR:
            return None

        try:
            from machine import ADC

            # 內建溫度感測器在 ADC4
            sensor_temp = ADC(4)
            reading = sensor_temp.read_u16() * 3.3 / 65535
            temperature = 27 - (reading - 0.706) / 0.001721

            return round(temperature, 1)
        except Exception as e:
            print("溫度讀取失敗: " + str(e))
            return None

    def send_data(self, data):
        """透過 ESP01 傳送感測數據至後端 API"""
        if not self.connected:
            return False

        try:
            import json

            headers = {
                "Content-Type": "application/json",
            }

            json_data = json.dumps(data)
            api_url = config.API_BASE_URL + "/api/v1/sensors/data/" + config.API_KEY
            status_code, response = self.http_post(api_url, json_data, headers)

            if status_code == 200 or status_code == 201:
                print("數據已上傳")
                self.led_status.value(1)
                time.sleep_ms(100)
                self.led_status.value(0)
                return True
            else:
                print("API 錯誤: " + str(status_code))
                return False

        except Exception as e:
            print("上傳失敗: " + str(e))
            return False

    def run_pump(self, duration_ms=None):
        """執行澆水動作（可選功能）"""
        if not config.ENABLE_PUMP or self.pump_pin is None:
            print("[WARN] 水泵功能未啟用")
            return False

        if duration_ms is None:
            duration_ms = config.DEFAULT_WATER_DURATION

        print("啟動水泵 " + str(duration_ms) + "ms")
        try:
            self.pump_pin.duty_u16(65535)  # 全速
            time.sleep_ms(duration_ms)
            self.pump_pin.duty_u16(0)  # 停止
            print("澆水完成")
            return True
        except Exception as e:
            print("水泵錯誤: " + str(e))
            self.pump_pin.duty_u16(0)
            return False

    def run(self):
        """主執行迴圈"""
        # --- 逃生延遲（開發除錯用）---
        if getattr(config, 'ESCAPE_DELAY', 0) > 0:
            print("逃生延遲 " + str(config.ESCAPE_DELAY) + " 秒，可按停止鍵攔截...")
            time.sleep(config.ESCAPE_DELAY)

        print("=" * 40)
        print("PicoGuard 啟動")
        print("裝置 ID: " + config.DEVICE_ID)
        pump_status = "啟用" if config.ENABLE_PUMP else "未啟用"
        print("水泵功能: " + pump_status)
        power_status = "已啟用" if self.sensor_power else "未啟用"
        print("防鏽電源: " + power_status)
        print("=" * 40)

        # 嘗試連接 WiFi
        if not self.connect_wifi():
            print("[WARN] 無法連接網路，進入離線模式")

        # 狀態指示
        self.led_status.value(1)
        time.sleep_ms(500)
        self.led_status.value(0)

        print("開始監控循環")
        print("上傳間隔: " + str(config.SEND_INTERVAL) + " 秒")
        print("=" * 40)

        while True:
            current_time = time.time()

            # 每個循環讀取並發送數據
            if current_time - self.last_send_time >= config.SEND_INTERVAL:
                sensor_data = self.read_sensors()
                print("")
                print("感測數據:")
                print("   土壤濕度: " + str(sensor_data['soil_moisture']) + "%")
                if sensor_data['temperature'] is not None:
                    print("   溫度: " + str(sensor_data['temperature']) + "C")

                if self.connected:
                    self.send_data(sensor_data)

                self.last_send_time = current_time

            time.sleep(1)


def main():
    """程式入口"""
    device = PicoGuardDevice()
    device.run()


if __name__ == "__main__":
    main()
