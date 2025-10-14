#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
多帳號管理器共用模組
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path

from ..utils.windows_encoding_utils import safe_print
from .logging_config import get_logger, log_with_safe_print


class MultiAccountManager:
    """多帳號管理器"""

    def __init__(self, config_file="accounts.json"):
        self.config_file = config_file
        self.logger = get_logger("multi_account_manager")
        self.load_config()

    def load_config(self):
        """載入設定檔"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(
                f"⛔ 設定檔 '{self.config_file}' 不存在！\n"
                "📝 請建立 accounts.json 檔案，包含 accounts 和 settings 設定"
            )

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.config = json.load(f)

            if "accounts" not in self.config or not self.config["accounts"]:
                raise ValueError("⛔ 設定檔中沒有找到帳號資訊！")

            self.logger.info(f"✅ 已載入設定檔: {self.config_file}", config_file=self.config_file)

        except json.JSONDecodeError as e:
            raise ValueError(f"⛔ 設定檔格式錯誤: {e}")
        except Exception as e:
            raise RuntimeError(f"⛔ 載入設定檔失敗: {e}")

    def get_enabled_accounts(self):
        """取得啟用的帳號列表"""
        return [acc for acc in self.config["accounts"] if acc.get("enabled", True)]

    def run_all_accounts(
        self,
        scraper_class,
        headless_override=None,
        progress_callback=None,
        start_date=None,
        end_date=None,
        start_month=None,
        end_month=None,
    ):
        """
        執行所有啟用的帳號

        Args:
            scraper_class: 要使用的抓取器類別 (例如 PaymentScraper, FreightScraper)
            headless_override: 覆寫無頭模式設定
            progress_callback: 進度回呼函數
            start_date: 開始日期 (用於代收貨款查詢)
            end_date: 結束日期 (用於代收貨款查詢)
            start_month: 開始月份 (用於運費查詢)
            end_month: 結束月份 (用於運費查詢)
        """
        accounts = self.get_enabled_accounts()

        results = []
        settings = self.config.get("settings", {})

        if progress_callback:
            progress_callback(f"🚀 開始執行多帳號 WEDI 自動下載 (共 {len(accounts)} 個帳號)")
        else:
            self.logger.info("=" * 80)
            self.logger.info(f"🚀 開始執行多帳號 WEDI 自動下載 (共 {len(accounts)} 個帳號)", total_accounts=len(accounts))
            self.logger.info("=" * 80)

        for i, account in enumerate(accounts, 1):
            username = account["username"]
            password = account["password"]

            progress_msg = f"📊 [{i}/{len(accounts)}] 處理帳號: {username}"
            if progress_callback:
                progress_callback(progress_msg)
            else:
                self.logger.info(progress_msg, account_index=i, total_accounts=len(accounts), username=username)
                self.logger.info("-" * 50)

            try:
                # 如果有命令列參數覆寫，則使用該設定
                use_headless = (
                    headless_override
                    if headless_override is not None
                    else settings.get("headless", False)
                )

                # 準備 scraper 參數，根據不同類型傳遞適當的日期/月份參數
                scraper_kwargs = {
                    "username": username,
                    "password": password,
                    "headless": use_headless,
                    "download_base_dir": settings.get("download_base_dir", "downloads"),
                }

                # 檢查 scraper 類別名稱來決定傳遞哪種日期參數
                if "Freight" in scraper_class.__name__:
                    # FreightScraper 使用 start_month 和 end_month
                    if start_month is not None:
                        scraper_kwargs["start_month"] = start_month
                    if end_month is not None:
                        scraper_kwargs["end_month"] = end_month
                else:
                    # PaymentScraper 和其他使用 start_date 和 end_date
                    if start_date is not None:
                        scraper_kwargs["start_date"] = start_date
                    if end_date is not None:
                        scraper_kwargs["end_date"] = end_date

                scraper = scraper_class(**scraper_kwargs)

                result = scraper.run_full_process()
                results.append(result)

                # 帳號間暫停一下避免過於頻繁
                if i < len(accounts):
                    time.sleep(2)

            except Exception as e:
                error_msg = f"帳號 {username} 執行失敗: {str(e)}"
                if progress_callback:
                    progress_callback(error_msg)
                else:
                    self.logger.error(error_msg, username=username, error=str(e))

                results.append({
                    "success": False,
                    "username": username,
                    "error": str(e),
                    "downloads": []
                })

        # 分析結果
        successful_accounts = [r for r in results if r["success"]]
        failed_accounts = [r for r in results if not r["success"]]
        total_downloads = sum(len(r["downloads"]) for r in successful_accounts)

        # 顯示統計
        self.logger.log_data_info("執行統計",
                                  total_accounts=len(results),
                                  successful_accounts=len(successful_accounts),
                                  failed_accounts=len(failed_accounts),
                                  total_downloads=total_downloads)

        if successful_accounts:
            self.logger.info("✅ 成功帳號詳情:")
            for result in successful_accounts:
                username = result["username"]
                download_count = len(result["downloads"])
                if result.get("message") == "無資料可下載":
                    self.logger.info(f"   🔸 {username}: 無資料可下載", username=username, status="no_data")
                else:
                    self.logger.info(f"   🔸 {username}: 成功下載 {download_count} 個檔案", username=username, download_count=download_count)

        if failed_accounts:
            self.logger.error("❌ 失敗帳號詳情:", failed_count=len(failed_accounts))
            for result in failed_accounts:
                username = result["username"]
                error = result.get("error", "未知錯誤")
                self.logger.error(f"   🔸 {username}: {error}", username=username, error=error)

        # 保存詳細報告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"{timestamp}.json"
        report_file = Path("reports") / report_filename

        # 確保 reports 目錄存在
        report_file.parent.mkdir(parents=True, exist_ok=True)

        # 清理結果中的不可序列化物件
        clean_results = []
        for result in results:
            clean_result = {
                "success": result["success"],
                "username": result["username"],
                "downloads": result["downloads"],
                "records": len(result.get("records", [])) if result.get("records") else 0,
            }
            if "error" in result:
                clean_result["error"] = result["error"]
            if "message" in result:
                clean_result["message"] = result["message"]
            clean_results.append(clean_result)

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "execution_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "total_accounts": len(results),
                    "successful_accounts": len(successful_accounts),
                    "failed_accounts": len(failed_accounts),
                    "total_downloads": total_downloads,
                    "details": clean_results,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        self.logger.log_operation_success("詳細報告保存", report_file=str(report_file), total_accounts=len(results))
        self.logger.info("=" * 80)
