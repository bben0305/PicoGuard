# PicoGuard Railway 部署指南

## 🚀 快速部署到 Railway

### 1. 準備 GitHub 儲存庫
```bash
git init
git add .
git commit -m "Initial PicoGuard deployment"
git branch -M main
git remote add origin https://github.com/yourusername/picoguard.git
git push -u origin main
```

### 2. Railway 部署步驟
1. 前往 [railway.app](https://railway.app)
2. 使用 GitHub 登入
3. 點擊 "New Project" → "Deploy from GitHub repo"
4. 選擇 PicoGuard 儲存庫
5. Railway 會自動偵測 Python 應用程式

### 3. 設定環境變數
在 Railway 專案設定中添加：
```
DATABASE_URL=sqlite:///./picoguard.db
API_KEY=picoguard-device-key-2024
SECRET_KEY=your-production-secret-key
ENVIRONMENT=production
```

### 4. 部署完成
- Railway 會提供一個 `.railway.app` 網域
- API 文件：`https://your-app.railway.app/docs`
- 健康檢查：`https://your-app.railway.app/health`

## 📱 更新 Pico 配置

部署成功後，更新 `firmware/pico/config.py`：
```python
# 從 Railway 取得實際網址
API_BASE_URL = "https://your-app.railway.app"
API_KEY = "picoguard-device-key-2024"  # 與 Railway 環境變數一致
```

## 🔧 故障排除

### 常見問題
1. **部署失敗**：檢查 `requirements.txt` 格式
2. **500 錯誤**：查看 Railway 日誌
3. **CORS 錯誤**：設定 `ALLOWED_ORIGINS` 環境變數

### 日誌查看
- Railway Dashboard → Logs
- 本地測試：`railway logs`

## 📊 監控
- Railway 提供基礎監控
- 免費額度：$5/月，包含 500 小時執行時間
- 自動睡眠：30 分鐘無活動後休眠
