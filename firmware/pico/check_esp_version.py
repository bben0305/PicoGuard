"""
檢查 ESP01 韌體版本和支援功能
上傳到 Pico 執行，查看 Thonny 輸出
"""
import time
from machine import UART, Pin

# 初始化 UART
uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))
time.sleep(2)

def send_at(cmd, timeout=3000):
    """發送 AT 指令"""
    print(f"\n>>> 發送: {cmd}")
    uart.write((cmd + "\r\n").encode())
    time.sleep_ms(timeout)
    
    response = b""
    while uart.any():
        response += uart.read()
    
    try:
        decoded = response.decode('utf-8', 'ignore')
        print(f"<<< 回應: {decoded[:300]}")
        return decoded
    except:
        print(f"<<< 回應(原始): {response[:100]}")
        return ""

print("=" * 50)
print("ESP01 韌體檢查工具")
print("=" * 50)

# 測試基本通訊
send_at("AT", 1000)

# 檢查版本
send_at("AT+GMR", 2000)

# 檢查 WiFi 模式
send_at("AT+CWMODE?", 1000)

# 檢查是否支援 HTTPCLIENT
print("\n--- 測試 AT+HTTPCLIENT 支援 ---")
send_at("AT+HTTPCLIENT=1,0,\"httpbin.org\",80,\"/get\",\"\"", 5000)

# 檢查是否支援 CIPSTATUS
print("\n--- 測試連接狀態 ---")
send_at("AT+CIPSTATUS", 1000)

# 列出所有指令
print("\n--- 測試 AT+CMD 列表 ---")
send_at("AT+CMD", 2000)

print("\n" + "=" * 50)
print("檢查完成")
print("=" * 50)
