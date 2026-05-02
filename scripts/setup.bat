@echo off
chcp 65001 >nul
:: PicoGuard Windows 安裝腳本

echo ==========================================
echo    🌱 PicoGuard 智能植栽監控系統
echo    開發環境安裝腳本
echo ==========================================
echo.

:: 檢查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤：找不到 Python，請先安裝 Python 3.11+
    exit /b 1
)

echo ✅ Python 已安裝

:: 建立虛擬環境
echo.
echo 📦 建立虛擬環境...
cd ..\backend
if exist venv (
    echo ⚠️ 虛擬環境已存在，跳過建立
) else (
    python -m venv venv
    echo ✅ 虛擬環境已建立
)

:: 啟動虛擬環境並安裝依賴
echo.
echo 📦 安裝 Python 依賴...
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ 依賴安裝失敗
    exit /b 1
)

echo ✅ 依賴安裝完成

:: 建立本地設定檔
echo.
echo 📝 建立設定檔...
if not exist .env (
    copy ..\scripts\.env.example .env >nul 2>&1
    echo ✅ .env 已建立，請編輯設定
) else (
    echo ⚠️ .env 已存在
)

echo.
echo ==========================================
echo    ✅ 安裝完成！
echo.
echo  啟動後端服務：
echo    cd backend
echo    venv\Scripts\activate
echo    uvicorn main:app --reload
echo.
echo  開啟瀏覽器訪問：
echo    http://localhost:8000
echo    http://localhost:8000/docs ^(API 文件^)
echo ==========================================

pause
