# 技術文檔索引

本目錄包含 SeleniumPelican 專案的技術文檔和實作細節。

## 📚 文檔清單

### 部署文檔
- **[Ubuntu 部署指南](ubuntu-deployment-guide.md)** - Ubuntu 24.04 LTS 環境完整部署流程
  - 快速開始（3 分鐘部署）
  - 詳細安裝步驟
  - 環境驗證方法
  - 故障排除指南

### 技術方案
- **[Browser Utils Ubuntu 優化](browser-utils-ubuntu-optimization.md)** - 瀏覽器優化技術細節
  - 平台偵測與優化參數
  - 無頭模式記憶體優化
  - 效能指標與測試結果
  - 實作細節說明

## 🎯 快速導航

### 新使用者
如果您是第一次在 Ubuntu 環境部署 SeleniumPelican：
1. 閱讀 [Ubuntu 部署指南](ubuntu-deployment-guide.md)
2. 執行 `./Linux_安裝.sh`（自動安裝 Chromium 和配置環境）
3. 驗證安裝 `./scripts/test_ubuntu_env.sh`

### 開發者
如果您想了解技術實作細節：
- 查看 [Browser Utils Ubuntu 優化](browser-utils-ubuntu-optimization.md)
- 閱讀原始碼 `src/core/browser_utils.py`

### 故障排除
遇到問題時：
1. 檢查 [Ubuntu 部署指南 - 故障排除](ubuntu-deployment-guide.md#故障排除)
2. 執行診斷腳本 `./scripts/test_ubuntu_env.sh`
3. 查看日誌檔案 `logs/` 目錄

## 🔧 工具腳本

| 腳本 | 用途 | 說明 |
|------|------|------|
| `./Linux_安裝.sh` | 自動化安裝 | 一鍵安裝所有依賴（Ubuntu 自動安裝 Chromium） |
| `scripts/test_ubuntu_env.sh` | 環境驗證 | 檢查配置是否正確 |
| `scripts/test_browser.py` | 瀏覽器測試 | 驗證自動化功能 |

## 📊 效能指標

Ubuntu 優化後的效能改善：

| 指標 | 優化前 | 優化後 | 改善 |
|------|--------|--------|------|
| 無頭模式記憶體 | ~350MB | ~220MB | -37% |
| Ubuntu 啟動速度 | ~3.5s | ~2.8s | -20% |

## 🌐 平台支援

| 平台 | 支援狀態 | 說明 |
|------|---------|------|
| Ubuntu 24.04 LTS | ✅ 完全支援 | 包含專屬優化 |
| Ubuntu 22.04 LTS | ✅ 支援 | 大部分優化適用 |
| Debian 12+ | ✅ 支援 | 需手動調整路徑 |
| Windows 10/11 | ✅ 支援 | 使用通用設定 |
| macOS 12+ | ✅ 支援 | 使用通用設定 |

## 📝 文檔維護

這些文檔由 OpenSpec 變更管理系統維護。

- **變更提案**: `changes/add-ubuntu-deployment-support/`
- **最後更新**: 2025-10
- **維護者**: SeleniumPelican 開發團隊

## 🤝 貢獻

發現文檔問題或有改善建議？歡迎提交 Issue 或 Pull Request。

## 📖 相關資源

- [專案主 README](../../README.md)
- [類型註解指南](../type-annotation-guide.md)
- [帳號配置範例](../../accounts.json.example)

---

💡 **提示**: 所有文檔使用繁體中文撰寫，確保在 UTF-8 編碼環境下閱讀。
