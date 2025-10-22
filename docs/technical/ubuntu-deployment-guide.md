# Ubuntu 部署指南

本指南提供在 Ubuntu 24.04 LTS 無頭環境（無 GUI）部署 SeleniumPelican 的完整流程。

## 📋 目錄

- [環境要求](#環境要求)
- [快速開始](#快速開始)
- [詳細安裝步驟](#詳細安裝步驟)
- [環境驗證](#環境驗證)
- [配置說明](#配置說明)
- [故障排除](#故障排除)
- [安全性建議](#安全性建議)
- [效能優化](#效能優化)

---

## 環境要求

### 目標環境
- **作業系統**: Ubuntu 24.04 LTS（推薦）或 Ubuntu 22.04 LTS
- **環境類型**: 無頭模式（無 GUI）/ 伺服器環境
- **Python 版本**: >= 3.8
- **記憶體**: 建議至少 2GB RAM
- **硬碟空間**: 至少 500MB 可用空間

### 適用情境
- 🖥️ Linux 伺服器自動化部署
- ☁️ 雲端環境（AWS EC2、GCP、Azure VM）
- 🐳 Docker 容器環境
- 📅 定時任務（cron jobs）執行

---

## 快速開始

**3 分鐘完成部署！**

```bash
# 1. 克隆或下載專案
cd /path/to/SeleniumPelican

# 2. 執行安裝腳本（自動安裝 Chromium 和配置環境）
./Linux_安裝.sh

# 3. 配置帳號（編輯 accounts.json，設定 headless: true）
# 如果安裝時已建立 accounts.json，直接編輯即可
nano accounts.json  # 或使用其他編輯器

# 4. 驗證環境
./scripts/test_ubuntu_env.sh

# 5. 測試瀏覽器功能
python3 scripts/test_browser.py
```

✅ 完成！現在可以開始使用 SeleniumPelican。

---

## 詳細安裝步驟

### 使用自動化安裝腳本（推薦）

最簡單的方式是使用自動化安裝腳本：

```bash
cd /path/to/SeleniumPelican
./Linux_安裝.sh
```

這個腳本會自動完成：
- ✅ 檢查系統環境
- ✅ 安裝 Chromium 瀏覽器和 ChromeDriver（Ubuntu 環境）
- ✅ 安裝 UV 包管理器
- ✅ 建立虛擬環境並安裝依賴
- ✅ 自動配置 .env 檔案（Ubuntu 環境）
- ✅ 建立必要目錄並設定權限
- ✅ 執行配置驗證和基本測試

**跳到步驟 5** 完成帳號配置即可。

---

### 手動安裝步驟（進階使用者）

如果您想手動控制每個步驟，請依照以下指示：

#### 步驟 1: 系統準備

更新系統套件清單：

```bash
sudo apt update
```

確認 Python 版本：

```bash
python3 --version  # 應顯示 >= 3.8
```

如果 Python 版本過舊：

```bash
sudo apt install python3 python3-pip
```

#### 步驟 2: 安裝 Chromium 和 ChromeDriver

Ubuntu 24.04 LTS 推薦使用系統套件安裝：

```bash
# 安裝 Chromium 瀏覽器
sudo apt install -y chromium-browser

# 安裝 ChromeDriver
sudo apt install -y chromium-chromedriver
```

驗證安裝：

```bash
# 檢查 Chromium 版本
chromium-browser --version

# 檢查 ChromeDriver 版本
chromedriver --version

# 確認路徑
which chromium-browser  # 應顯示 /usr/bin/chromium-browser
which chromedriver      # 應顯示 /usr/bin/chromedriver
```

**重要**: Chromium 和 ChromeDriver 的主版本號應該一致（例如都是 120.x）。

#### 步驟 3: 配置環境變數

建立 `.env` 檔案：

```bash
cd /path/to/SeleniumPelican

cat > .env <<EOL
# Chrome 瀏覽器路徑
CHROME_BINARY_PATH=/usr/bin/chromium-browser
CHROMEDRIVER_PATH=/usr/bin/chromedriver
EOL

# 設定檔案權限（僅擁有者可讀寫）
chmod 600 .env
```

#### 步驟 4: 安裝 Python 依賴

使用 uv（推薦）：

```bash
# 安裝 uv（如果尚未安裝）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 同步依賴
uv sync
```

或使用 pip：

```bash
pip3 install -r requirements.txt
```

### 步驟 5: 配置帳號

複製範例檔案並編輯：

```bash
cp accounts.json.example accounts.json
chmod 600 accounts.json  # 保護敏感資訊

# 使用您喜歡的編輯器編輯
nano accounts.json
# 或
vim accounts.json
```

**重要配置**：填入實際帳號資訊：

```json
[
  {
    "username": "your_username",
    "password": "your_password",
    "enabled": true
  }
]
```

### 步驟 6: 建立必要目錄

```bash
mkdir -p downloads logs temp
chmod 755 downloads logs temp
```

---

## 環境驗證

### 自動化驗證腳本

執行環境驗證腳本，檢查所有配置：

```bash
./scripts/test_ubuntu_env.sh
```

**輸出範例**：

```
═══════════════════════════════════════
  Ubuntu 環境驗證
═══════════════════════════════════════

[1] 檢查 Python 版本... ✅ Python 3.12.0
[2] 檢查 Chromium 瀏覽器... ✅ Chromium 120.0.6099.109 (/usr/bin/chromium-browser)
[3] 檢查 ChromeDriver... ✅ 版本 120.0.6099.109 (/usr/bin/chromedriver)
[4] 檢查 Chromium 和 ChromeDriver 版本相容性... ✅ 版本匹配 (120.x)
[5] 檢查 .env 檔案配置... ✅ .env 存在且配置正確
[6] 檢查 accounts.json 檔案... ✅ accounts.json 存在且 headless 模式已啟用
[7] 檢查目錄結構與權限... ✅ 所有必要目錄存在且可寫

═══════════════════════════════════════
  驗證結果: 7/7 項檢查通過
═══════════════════════════════════════
```

### 瀏覽器功能測試

驗證環境通過後，測試瀏覽器功能：

```bash
python3 scripts/test_browser.py
```

這個腳本會測試：
- ✅ 瀏覽器啟動（無頭模式）
- ✅ 頁面導航
- ✅ JavaScript 執行
- ✅ 視窗大小設定
- ✅ 記憶體使用測量
- ✅ 正常關閉

**預期結果**：
- 所有測試通過
- 啟動時間 < 3.0 秒
- 記憶體使用 < 250MB

---

## 配置說明

### .env 檔案

| 變數 | 說明 | Ubuntu 預設值 | 必要性 |
|------|------|---------------|--------|
| `CHROME_BINARY_PATH` | Chrome/Chromium 執行檔路徑 | `/usr/bin/chromium-browser` | ✅ 必要 |
| `CHROMEDRIVER_PATH` | ChromeDriver 執行檔路徑 | `/usr/bin/chromedriver` | 選用 |
| `HEADLESS` | 無頭模式開關 | `true` | ⚠️ Ubuntu 無頭環境必須為 `true` |

**Ubuntu 環境 .env 範例**：

```bash
CHROME_BINARY_PATH=/usr/bin/chromium-browser
CHROMEDRIVER_PATH=/usr/bin/chromedriver
HEADLESS=true  # Ubuntu 無頭環境必須啟用
```

### accounts.json 檔案

帳號設定格式（新格式：純陣列）：

```json
[
  {
    "username": "帳號",
    "password": "密碼",
    "enabled": true        // 是否啟用此帳號
  }
]
```

**注意事項**：
- Ubuntu 無頭環境必須在 `.env` 設定 `HEADLESS=true`
- 密碼等敏感資訊不要提交到 Git
- 配置檔案權限應設為 600（僅擁有者可讀寫）：
  ```bash
  chmod 600 .env accounts.json
  ```

---

## 故障排除

### 問題 1: 找不到 Chromium

**錯誤訊息**：
```
Chrome 二進位檔案不存在: /usr/bin/chromium-browser
💡 Ubuntu 系統建議安裝: sudo apt install chromium-browser
```

**解決方案**：

```bash
# 方法 1: 重新執行安裝腳本（推薦）
./Linux_安裝.sh  # 會自動偵測並安裝 Chromium

# 方法 2: 手動安裝
sudo apt install chromium-browser

# 確認路徑
which chromium-browser

# 更新 .env 檔案中的路徑
```

---

### 問題 2: ChromeDriver 版本不匹配

**錯誤訊息**：
```
⚠️ Chromium 和 ChromeDriver 版本可能不匹配
```

**診斷步驟**：

```bash
# 檢查版本
chromium-browser --version  # 例如: 120.0.6099.109
chromedriver --version      # 例如: 119.0.6045.105
```

**解決方案**：

```bash
# 重新安裝以確保版本匹配
sudo apt install --reinstall chromium-browser chromium-chromedriver

# 或者更新到最新版本
sudo apt update
sudo apt upgrade chromium-browser chromium-chromedriver
```

---

### 問題 3: 共享記憶體不足

**錯誤訊息**：
```
selenium.common.exceptions.WebDriverException: Message: unknown error:
DevToolsActivePort file doesn't exist
```

**原因**: `/dev/shm` 空間不足（常見於 Docker 容器）

**解決方案**：

1. 檢查 `/dev/shm` 大小：
   ```bash
   df -h /dev/shm
   ```

2. Docker 環境增加 shm-size：
   ```bash
   docker run --shm-size=2g ...
   ```

3. 或在 `docker-compose.yml` 中：
   ```yaml
   services:
     app:
       shm_size: 2gb
   ```

**注意**: `browser_utils.py` 已自動加入 `--disable-dev-shm-usage` 參數來緩解此問題。

---

### 問題 4: 權限錯誤

**錯誤訊息**：
```
Permission denied: '/usr/bin/chromium-browser'
```

**解決方案**：

```bash
# 檢查檔案權限
ls -la /usr/bin/chromium-browser
ls -la /usr/bin/chromedriver

# 確保檔案可執行
sudo chmod +x /usr/bin/chromium-browser
sudo chmod +x /usr/bin/chromedriver

# 檢查目錄權限
ls -la downloads logs
chmod 755 downloads logs
```

---

### 問題 5: 無法連接到 DevTools

**錯誤訊息**：
```
selenium.common.exceptions.WebDriverException: Message: unknown error:
cannot connect to chrome at 127.0.0.1:xxxxx
```

**可能原因**：
- 防火牆阻擋本地連接
- Chrome 程序殘留

**解決方案**：

```bash
# 1. 清理殘留程序
pkill -f chromium
pkill -f chromedriver

# 2. 檢查防火牆（如果使用 ufw）
sudo ufw status

# 3. 確保 localhost 可連接
ping -c 1 127.0.0.1

# 4. 重新執行安裝（自動修復配置）
./Linux_安裝.sh

# 5. 或重新執行測試
python3 scripts/test_browser.py
```

---

### 問題 6: 效能問題

**症狀**: 啟動慢或記憶體使用高

**診斷**：

```bash
# 執行效能測試
python3 scripts/test_browser.py
```

查看輸出的效能指標：
- 啟動時間應 < 3.0 秒
- 記憶體使用應 < 250MB

**優化措施**：

1. 確認已套用 Ubuntu 優化（會自動偵測並套用）
2. 檢查系統資源：
   ```bash
   free -h  # 檢查記憶體
   top      # 查看 CPU 使用
   ```
3. 如果多個瀏覽器實例同時運行，考慮增加系統記憶體

---

## 安全性建議

### 1. 保護敏感檔案

```bash
# 設定正確的檔案權限
chmod 600 .env accounts.json

# 確認權限
ls -la .env accounts.json
# 應顯示: -rw------- (600)
```

### 2. 環境隔離

使用虛擬環境或容器隔離：

```bash
# Python 虛擬環境
python3 -m venv venv
source venv/bin/activate

# 或使用 uv
uv venv
source .venv/bin/activate
```

### 3. 防火牆設定

如果伺服器暴露於公網，配置防火牆：

```bash
# Ubuntu ufw 範例
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp   # 如果需要
sudo ufw allow 443/tcp  # 如果需要
```

### 4. 定期更新

```bash
# 定期更新系統和瀏覽器
sudo apt update
sudo apt upgrade chromium-browser chromium-chromedriver

# 更新 Python 依賴
uv sync --upgrade
```

### 5. 日誌管理

```bash
# 定期清理舊日誌（避免佔用過多空間）
find logs/ -name "*.log" -mtime +30 -delete

# 或使用 logrotate
```

---

## 效能優化

### Ubuntu 專屬優化

SeleniumPelican 在 Ubuntu 環境會自動啟用以下優化：

#### 1. 平台偵測優化
```python
# 自動偵測 Linux 平台並套用優化參數
--disable-features=VizDisplayCompositor
--disable-software-rasterizer
--disable-gpu
```

#### 2. 無頭模式記憶體優化
```python
# 當 headless=True 時自動套用
--headless=new  # 使用新版無頭模式
--disable-dev-shm-usage
--disable-software-rasterizer
```

### 效能指標

| 指標 | 優化前 | 優化後 | 改善 |
|------|--------|--------|------|
| 無頭模式記憶體 | ~350MB | ~220MB | **-37%** |
| Ubuntu 啟動速度 | ~3.5s | ~2.8s | **-20%** |

### 監控效能

使用測試腳本監控效能：

```bash
# 執行效能測試
python3 scripts/test_browser.py

# 查看詳細輸出
# - 啟動時間
# - 記憶體使用
# - 測試執行時間
```

### 系統層級優化

1. **增加 swap 空間**（如果記憶體有限）：
   ```bash
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

2. **調整系統參數**：
   ```bash
   # /etc/sysctl.conf
   vm.swappiness=10
   vm.vfs_cache_pressure=50
   ```

---

## 進階配置

### Docker 部署

Dockerfile 範例：

```dockerfile
FROM ubuntu:24.04

# 安裝依賴
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    chromium-browser \
    chromium-chromedriver \
    && rm -rf /var/lib/apt/lists/*

# 複製專案
WORKDIR /app
COPY . /app

# 安裝 Python 依賴
RUN pip3 install --no-cache-dir -r requirements.txt

# 設定環境變數
ENV CHROME_BINARY_PATH=/usr/bin/chromium-browser
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# 執行
CMD ["python3", "src/scrapers/payment_scraper.py"]
```

docker-compose.yml：

```yaml
version: '3.8'
services:
  selenium-pelican:
    build: .
    shm_size: 2gb  # 重要：增加共享記憶體
    volumes:
      - ./downloads:/app/downloads
      - ./logs:/app/logs
      - ./accounts.json:/app/accounts.json:ro
      - ./.env:/app/.env:ro
    environment:
      - TZ=Asia/Taipei
```

### Cron 定時任務

設定每日自動執行：

```bash
# 編輯 crontab
crontab -e

# 新增任務（每天早上 8 點執行）
0 8 * * * cd /path/to/SeleniumPelican && /usr/bin/python3 -u src/scrapers/payment_scraper.py >> /path/to/cron.log 2>&1
```

---

## 總結

### ✅ 部署檢查清單

- [ ] 執行安裝腳本 `./Linux_安裝.sh`（自動完成大部分步驟）
- [ ] 配置 `accounts.json`（填入帳號資訊，設定 headless: true）
- [ ] 執行環境驗證 `./scripts/test_ubuntu_env.sh`
- [ ] 執行瀏覽器測試 `python3 scripts/test_browser.py`

### 📚 相關文檔

- [Browser Utils Ubuntu 優化](browser-utils-ubuntu-optimization.md) - 技術實作細節
- [技術文檔索引](README.md) - 其他技術文檔

### 🆘 需要幫助？

- 執行診斷腳本：`./scripts/test_ubuntu_env.sh`
- 查看日誌檔案：`logs/` 目錄
- 閱讀故障排除章節

---

**文檔版本**: v1.0
**適用版本**: SeleniumPelican with Ubuntu Deployment Support
**最後更新**: 2025-10
