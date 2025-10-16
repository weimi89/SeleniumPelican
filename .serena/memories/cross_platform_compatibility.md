# SeleniumPelican 跨平台相容性設計分析

## 支援平台
- **Windows**: Windows 10/11 (PowerShell 5.1+ / PowerShell 7+)
- **macOS**: macOS 10.14+
- **Linux**: Ubuntu 18.04+ 及其他主流發行版

## 跨平台設計策略

### 1. 執行腳本多版本支援
**Windows 使用者**:
- `*.cmd`: 批次檔，自動啟動 PowerShell 7
- `*.ps1`: PowerShell 7 腳本 (推薦)
- 智慧執行順序: Windows Terminal → PowerShell 7 → 舊版 PowerShell

**Unix/Linux 使用者**:
- `*.sh`: Bash shell 腳本
- 自動設定必要環境變數

### 2. 字符編碼相容性
**Windows 特殊處理**:
- Unicode emoji 自動轉換為文字標籤 (✅ → [OK])
- UTF-8 編碼設定和控制台代碼頁配置
- safe_print() 函數自動偵測平台並調整輸出

### 3. 路徑處理
**跨平台路徑管理**:
- 使用 Python `pathlib.Path` 處理檔案路徑
- 自動處理不同平台的路徑分隔符
- 絕對路徑和相對路徑智能轉換

### 4. 瀏覽器相容性
**Chrome 路徑配置**:
```
# macOS
CHROME_BINARY_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Windows
CHROME_BINARY_PATH="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

# Linux
CHROME_BINARY_PATH="/usr/bin/google-chrome"
```

**ChromeDriver 管理**:
- 多重備援策略適應不同平台
- Windows 使用 CREATE_NO_WINDOW 隱藏控制台
- Linux/macOS 使用 devnull 重導向輸出

### 5. 環境變數處理
**平台特定設定**:

**Windows PowerShell**:
```powershell
$env:PYTHONUNBUFFERED='1'
$env:PYTHONPATH=$PWD.Path
```

**Windows 命令提示字元**:
```cmd
set PYTHONUNBUFFERED=1
set PYTHONPATH=%cd%
```

**Unix/Linux**:
```bash
export PYTHONUNBUFFERED=1
export PYTHONPATH="$(pwd)"
```

## 平台特定最佳化

### 1. Windows 最佳化
- PowerShell 7 優先策略提供最佳體驗
- UTF-8 輸出編碼確保中文正確顯示
- 彩色終端輸出支援

### 2. macOS 最佳化
- Homebrew 套件管理器整合
- 系統 Chrome 路徑自動偵測
- Terminal.app 完整支援

### 3. Linux 最佳化
- 主流發行版套件管理器支援
- X11/Wayland 視窗系統相容
- 無頭伺服器環境支援

## 測試覆蓋
所有跨平台功能都經過以下環境測試：
- Windows 10/11 (PowerShell 5.1, 7.x)
- macOS Monterey+ (zsh, bash)
- Ubuntu 20.04/22.04 (bash)

## 部署注意事項

### Windows 部署
1. 確保安裝 PowerShell 7+ (推薦)
2. 設定執行政策: `Set-ExecutionPolicy RemoteSigned`
3. 安裝 Google Chrome 瀏覽器

### macOS 部署
1. 安裝 Xcode Command Line Tools
2. 使用 Homebrew 安裝 Python 和 uv
3. 確保 Chrome 已安裝在標準位置

### Linux 部署
1. 安裝系統依賴: `google-chrome-stable`, `python3`, `python3-pip`
2. 設定 Chrome 無頭模式權限
3. 確保 X11 forwarding (如果需要顯示模式)
