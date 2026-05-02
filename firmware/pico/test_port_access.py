"""
測試 Railway Port 存取
"""

from machine import Pin, UART
import time

def test_railway_port():
    """測試 Railway 不同端口的 HTTP 存取"""
    print("🔍 測試 Railway Port 存取...")
    
    # 初始化 UART
    uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))
    
    if uart is None:
        print("❌ UART 初始化失敗")
        return False
    
    # 測試不同端口
    ports = [80, 8080, 3000, 5000]
    host = "picoguard-production.up.railway.app"
    
    for port in ports:
        print(f"\n🔍 測試端口 {port}...")
        
        # 建立連接
        connect_cmd = f'AT+CIPSTART="TCP","{host}",{port}'
        cmd_bytes = (connect_cmd + "\r\n").encode()
        uart.write(cmd_bytes)
        time.sleep(5)
        
        # 讀取回應
        response = b""
        while uart.any():
            response += uart.read()
        
        print(f"📡 端口 {port} 回應: {response.decode('utf-8', 'ignore')}")
        
        if b"CONNECT" in response or b"OK" in response:
            print(f"✅ 端口 {port} 連接成功")
            
            # 發送簡單 HTTP 請求
            http_request = f"GET /health HTTP/1.1\r\nHost: {host}:{port}\r\n\r\n"
            cipsend_cmd = f"AT+CIPSEND={len(http_request)}"
            
            cipsend_bytes = (cipsend_cmd + "\r\n").encode()
            uart.write(cipsend_bytes)
            time.sleep(3)
            uart.write(http_request.encode())
            time.sleep(5)
            
            # 讀取回應
            response = b""
            timeout = time.time() + 3
            while time.time() < timeout:
                if uart.any():
                    response += uart.read()
                time.sleep(0.1)
            
            print(f"📄 HTTP 回應: {response.decode('utf-8', 'ignore')}")
            
            if b"200 OK" in response or b"ok" in response:
                print(f"🎉 端口 {port} 完全可用！")
                return port
        
        # 關閉連接
        close_cmd = "AT+CIPCLOSE\r\n".encode()
        uart.write(close_cmd)
        time.sleep(1)
    
    print("❌ 所有端口都無法連接")
    return False

if __name__ == "__main__":
    result = test_railway_port()
    if result:
        print(f"\n🎯 使用端口 {result}: http://picoguard-production.up.railway.app:{result}")
    else:
        print("\n❌ 需要其他解決方案")
