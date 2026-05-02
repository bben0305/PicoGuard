"""
Pico API 測試程式
用於測試與 Railway 的連接
"""

from machine import Pin, UART
import time
import json

def test_api_connection():
    """測試 API 連接"""
    print("🔍 開始測試 API 連接...")
    
    # 初始化 UART (與主程式相同設定)
    uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))
    
    if uart is None:
        print("❌ UART 初始化失敗")
        return False
    
    print("✅ UART 初始化完成")
    
    # 測試 ESP01 通訊
    uart.write("AT\r\n".encode())
    time.sleep(1)
    
    response = b""
    while uart.any():
        response += uart.read()
    
    if b"OK" not in response:
        print("❌ ESP01 未回應")
        return False
    
    print("✅ ESP01 通訊正常")
    
    # 測試 HTTP POST 到測試端點
    test_url = "http://picoguard-production.up.railway.app/api/v1/sensors/test"
    test_data = {"test": "data", "timestamp": time.time()}
    
    print(f"🔍 測試 URL: {test_url}")
    print(f"🔍 測試數據: {test_data}")
    
    # 發送 HTTP 請求
    try:
        # 解析 URL
        url_parts = test_url.replace("http://", "").split("/")
        host_port = url_parts[0].split(":")
        host = host_port[0]
        port = host_port[1] if len(host_port) > 1 else "80"
        path = "/" + "/".join(url_parts[1:]) if len(url_parts) > 1 else "/"
        
        print(f"🔍 連接到 {host}:{port}{path}")
        
        # 建立 TCP 連接
        connect_cmd = f'AT+CIPSTART="TCP","{host}",{port}'
        print(f"🔍 發送: {connect_cmd}")
        uart.write((connect_cmd + "\r\n").encode())
        time.sleep(3)
        
        # 檢查連接回應
        response = b""
        while uart.any():
            response += uart.read()
        print(f"🔍 連接回應: {response}")
        
        # 準備 HTTP 請求
        json_str = json.dumps(test_data)
        http_request = f"""POST {path} HTTP/1.1\r
Host: {host}:{port}\r
Content-Type: application/json\r
X-API-Key: picoguard-device-key-2024\r
Content-Length: {len(json_str)}\r
\r
{json_str}"""
        
        print(f"🔍 HTTP 請求長度: {len(http_request)}")
        
        # 發送數據
        cipsend_cmd = f"AT+CIPSEND={len(http_request)}"
        print(f"🔍 發送: {cipsend_cmd}")
        uart.write((cipsend_cmd + "\r\n").encode())
        time.sleep(1)
        
        uart.write(http_request.encode())
        time.sleep(2)
        
        # 讀取回應
        response = b""
        timeout = time.time() + 5
        while time.time() < timeout:
            if uart.any():
                data = uart.read()
                response += data
                print(f"🔍 接收數據: {data}")
            time.sleep(0.1)
        
        print(f"🔍 完整回應: {response.decode('utf-8', errors='ignore')}")
        
        if b"200" in response or b"OK" in response:
            print("✅ API 測試成功")
            return True
        else:
            print("❌ API 測試失敗")
            return False
            
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        return False

if __name__ == "__main__":
    test_api_connection()
