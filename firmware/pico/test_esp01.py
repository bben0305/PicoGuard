"""
ESP01 連接測試程式
用於診斷 ESP01 模組連接問題
"""

from machine import Pin, UART
import time

def test_esp01():
    """測試 ESP01 連接和回應"""
    
    print("🔍 ESP01 連接測試開始...")
    
    # 初始化 UART (修正腳位設定)
    uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))
    
    print("📡 UART 初始化完成")
    print("📊 設定: 115200 baud, TX=GPIO0, RX=GPIO1")
    
    # 等待 ESP01 啟動
    print("⏳ 等待 ESP01 啟動...")
    time.sleep(2)
    
    # 清空緩衝區
    while uart.any():
        uart.read()
    
    # 測試 1: 發送 AT 指令
    print("\n🧪 測試 1: 基本 AT 指令")
    uart.write("AT\r\n".encode())
    time.sleep(1)
    
    response = b""
    while uart.any():
        response += uart.read()
    
    if response:
        print("✅ ESP01 回應:", response.decode('utf-8', errors='ignore'))
    else:
        print("❌ ESP01 無回應")
    
    # 測試 2: 檢查 WiFi 模式
    print("\n🧪 測試 2: 檢查 WiFi 模式")
    uart.write("AT+CWMODE?\r\n".encode())
    time.sleep(1)
    
    response = b""
    while uart.any():
        response += uart.read()
    
    if response:
        print("✅ WiFi 模式:", response.decode('utf-8', errors='ignore'))
    else:
        print("❌ 無法取得 WiFi 模式")
    
    # 測試 3: 掃描 WiFi 網路
    print("\n🧪 測試 3: 掃描 WiFi 網路")
    uart.write("AT+CWLAP\r\n".encode())
    time.sleep(5)  # 掃描需要更長時間
    
    response = b""
    start_time = time.time()
    while time.time() - start_time < 5:
        if uart.any():
            data = uart.read()
            response += data
            print("📡 接收數據:", data.decode('utf-8', errors='ignore'))
        time.sleep(0.1)
    
    if b"+CWLAP" in response:
        print("✅ WiFi 掃描成功，找到網路")
    else:
        print("❌ WiFi 掃描失敗")
    
    # 測試 4: 檢查連接狀態
    print("\n🧪 測試 4: 檢查連接狀態")
    uart.write("AT+CWJAP?\r\n".encode())
    time.sleep(2)
    
    response = b""
    while uart.any():
        response += uart.read()
    
    if response:
        print("✅ 連接狀態:", response.decode('utf-8', errors='ignore'))
    else:
        print("❌ 無法取得連接狀態")
    
    print("\n🔍 測試完成")

def hardware_check():
    """硬體檢查"""
    print("🔧 硬體接線檢查:")
    print("  ESP01 TX → Pico GPIO 0 (UART0 RX)")
    print("  ESP01 RX → Pico GPIO 1 (UART0 TX)")
    print("  ESP01 VCC → 3.3V")
    print("  ESP01 GND → GND")
    print("  ESP01 EN → 3.3V (重要！)")
    print("\n💡 提示:")
    print("  - 確保 ESP01 上的 LED 閃爍")
    print("  - 檢查 3.3V 電源是否穩定")
    print("  - 嘗試重新插拔 ESP01")

if __name__ == "__main__":
    hardware_check()
    print("\n" + "="*50)
    test_esp01()
