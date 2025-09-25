# SeleniumPelican 架構文件

## 文檔概述

本目錄包含 SeleniumPelican 專案的完整架構分析和技術文檔。SeleniumPelican 是一個現代化的 WEDI 宅配通自動化工具套件，採用模組化設計，使用 Selenium 進行網頁自動化操作。

## 文檔結構

```
docs/
├── README.md                           # 文檔導覽（本檔案）
├── architecture/                       # 架構分析
│   ├── overview.md                     # 架構概述
│   ├── components.md                   # 組件分析
│   ├── design_patterns.md              # 設計模式
│   ├── technical_decisions.md          # 技術決策
│   └── improvement_suggestions.md      # 改進建議
├── development/                        # 開發指南
│   ├── setup_guide.md                  # 環境設定指南
│   ├── coding_standards.md             # 程式碼規範
│   ├── testing_guide.md                # 測試指南 (新增)
│   └── configuration_guide.md          # 配置指南 (新增)
└── technical/                          # 技術參考
    ├── api_reference.md                # API 參考
    ├── standardized_scripts.md         # 標準化腳本說明 (新增)
    └── troubleshooting.md              # 疑難排解
```

## 快速導覽

### 新手入門
1. 📖 閱讀 [架構概述](architecture/overview.md) 了解專案整體架構
2. ⚙️ 參考 [環境設定](development/setup_guide.md) 建立開發環境
3. 🏗️ 查看 [組件分析](architecture/components.md) 理解核心模組

### 開發者指南
1. 📋 遵循 [程式碼規範](development/coding_standards.md)
2. 🧪 使用 [測試策略](development/testing_strategy.md) 確保品質
3. 🔧 參考 [API 參考](technical/api_reference.md) 進行開發

### 架構師參考
1. 🎨 研究 [設計模式](architecture/design_patterns.md)
2. 💡 查看 [技術決策](architecture/technical_decisions.md)
3. 🚀 考慮 [改進建議](architecture/improvement_suggestions.md)

## 專案特色

### ✨ 現代化架構
- **模組化設計**: 採用 `src/` 目錄結構，清晰分離關注點
- **抽象基礎類別**: `BaseScraper` 提供統一的爬蟲框架
- **依賴注入**: `MultiAccountManager` 支援靈活的抓取器切換
- **測試框架**: 完整的 pytest 測試體系和 fixtures
- **配置驗證**: JSON Schema 驗證和業務邏輯檢查

### 🛡️ 強健的容錯機制
- **多重驗證碼偵測**: 5種自動偵測方法 + 手動輸入備援
- **優雅降級**: 個別失敗不影響整體流程
- **重試機制**: 自動重試失敗的操作

### 🌐 跨平台相容性
- **多平台支援**: Windows、macOS、Linux 完整支援
- **智慧執行腳本**: `.sh`、`.cmd`、`.ps1` 三套腳本系統
- **編碼相容**: Windows Unicode 字符顯示優化

### 🔧 開發者友善
- **現代工具鏈**: uv 包管理、pyproject.toml 設定
- **自動更新**: 智慧 git 操作和依賴更新
- **標準化腳本**: OS_中文名稱 格式的跨平台執行腳本
- **一鍵安裝**: 智能環境檢測和自動配置系統
- **詳盡文檔**: 完整的使用說明和 API 參考

## 版本資訊

- **架構版本**: 2.1
- **最後更新**: 2025-01-09
- **相容性**: Python 3.8+
- **主要依賴**: Selenium 4.x, uv 0.4+
- **新增功能**: 測試框架、配置驗證、標準化腳本、智能安裝系統

## 貢獻指南

1. 遵循既有的模組化架構原則
2. 保持跨平台相容性
3. 維護完整的錯誤處理機制
4. 更新相關文檔

---

📝 **文檔維護**: 此文檔會隨著專案演進持續更新，請定期檢查最新版本。