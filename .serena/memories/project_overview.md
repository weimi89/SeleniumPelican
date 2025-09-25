# SeleniumPelican 專案概述

## 專案目的
SeleniumPelican 是一個 WEDI (宅配通) 自動化工具套件，使用 Selenium WebDriver 自動從 WEDI 網頁系統下載各種資料。

## 核心功能
1. **代收貨款匯款明細查詢** - 自動下載代收貨款匯款明細報表
2. **運費(月結)結帳資料查詢** - 下載運費月結帳資料
3. **運費未請款明細下載** - 獲取運費未請款明細資訊

## 技術特點
- 現代化模組化架構，採用抽象基礎類別設計
- 支援多帳號批次處理
- 跨平台相容性設計 (Windows/macOS/Linux)
- 智能驗證碼自動偵測機制
- 容錯機制和錯誤恢復策略

## 架構亮點
- **Template Method Pattern**: 基礎抓取器定義通用流程，具體實作各自特化
- **Dependency Injection**: MultiAccountManager 支援不同抓取器類別的注入
- **Strategy Pattern**: 不同的下載策略適應各種資料類型
- **Factory Pattern**: 瀏覽器初始化工具提供統一的 WebDriver 建立介面