"""
PicoGuard 主程式 - Legacy 整合版
基於使用者原有腳本，整合防鏽讀取與 ThingSpeak 支援

硬體接線：
- ESP01 TX/RX -> UART0 (GPIO 0/1)
- 土壤濕度感測器 VCC -> GPIO 22 (電源開關)
- 土壤濕度感測器 SIG -> ADC0 (GPIO 26)
- 內建 LED -> GPIO 25
"""

import machine
import utime

# --- 設定區 ---
SSID = "3322"
PWD = "0975583835"
API_KEY = "004T94AG5DPR5QHY"
# --------------

# --- 逃生延遲 (超級重要！) ---
print("開機緩衝中，準備按停止鍵可攔截...")
utime.sleep(5)

# 硬體初始化
led = machine.Pin(25, machine.Pin.OUT)  # 內建燈
esp01 = machine.UART(0, baudrate=115200, tx=machine.Pin(0), rx=machine.Pin(1))
adc = machine.ADC(26)
# 設定 GP22 作為感測器的電源開關（防鏽設計）
sensor_power = machine.Pin(22, machine.Pin.OUT)
sensor_power.value(0)  # 預設關閉電源


def flash_once(duration=0.2):
    """LED 閃爍一次"""
    led.value(1)
    utime.sleep(duration)
    led.value(0)


def send_at(cmd, expected="OK", timeout=5000):
    """發送 AT 指令並等待回應"""
    if esp01.any():
        esp01.read()
    esp01.write(cmd + "\r\n")
    start = utime.ticks_ms()
    full_res = ""
    while (utime.ticks_ms() - start) < timeout:
        if esp01.any():
            try:
                res = esp01.read().decode('utf-8', 'ignore')
                full_res += res
                if expected in full_res:
                    return True
            except:
                pass
        utime.sleep(0.1)
    return False


def init_wifi():
    """初始化 WiFi 連線"""
    print("正在連網...")
    send_at("AT+CWMODE=1")
    if send_at(f'AT+CWJAP="{SSID}","{PWD}"', "WIFI GOT IP", 15000):
        return True
    return False


def get_moisture():
    """
    防鏽讀取邏輯
    使用 GPIO 22 控制感測器電源，讀取後立即斷電防止電解反應
    """
    sensor_power.value(1)     # 1. 通電
    utime.sleep(0.2)          # 2. 等待感測器穩定
    raw_val = adc.read_u16()  # 3. 讀取數值
    sensor_power.value(0)     # 4. 立即斷電 (防止電解反應生鏽)

    # 換算百分比 (根據實測調整 60000/20000 這兩個數值)
    moisture = int((60000 - raw_val) / 40000 * 100)
    moisture = max(0, min(100, moisture))
    return moisture, raw_val


def upload_to_thingspeak(value):
    """上傳數據到 ThingSpeak"""
    if send_at('AT+CIPSTART="TCP","api.thingspeak.com",80', "CONNECT"):
        path = f"GET /update?api_key={API_KEY}&field1={value}\r\n"
        if send_at(f"AT+CIPSEND={len(path)}", ">"):
            esp01.write(path)
            utime.sleep(1)
            flash_once()
            print(f"✅ 上傳成功: {value}%")
        send_at("AT+CIPCLOSE")


# --- 主循環 ---
def run_system():
    if not init_wifi():
        raise Exception("WiFi 連線失敗")

    while True:
        moisture, raw = get_moisture()
        print(f"讀取濕度: {moisture}% (原始值: {raw})")

        upload_to_thingspeak(moisture)

        # 為了保護感測器，建議拉長間隔
        # 每 1 分鐘測一次就好，不需要一直測
        print("進入深度休眠 60 秒...")
        utime.sleep(60)


if __name__ == "__main__":
    while True:
        try:
            run_system()
        except Exception as e:
            flash_once(1)
            flash_once(1)
            print(f"異常重啟: {e}")
            utime.sleep(10)
            machine.reset()
