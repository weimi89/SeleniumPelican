#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
多帳號管理器共用模組
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

from dotenv import load_dotenv

from ..utils.windows_encoding_utils import safe_print
from ..utils.discord_notifier import DiscordNotifier
from ..utils.email_notifier import EmailNotifier
from .browser_utils import _cleanup_headless_chrome, cleanup_temp_user_data_dirs, init_chrome_browser, check_browser_health
from .logging_config import ScrapingLogger, get_logger, log_with_safe_print
from .type_aliases import AccountConfig


def _setup_file_logger(function_name: str):
    """
    設定檔案日誌記錄器，將 stdout/stderr 同時輸出到日誌檔

    Args:
        function_name: 功能名稱，用於日誌檔命名

    Returns:
        tuple: (log_file_path, original_stdout, original_stderr, log_fh)
    """
    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"{timestamp}_{function_name}.log"

    class TeeWriter:
        """同時輸出到原始 stdout/stderr 和日誌檔"""
        def __init__(self, original, log_fh):
            self.original = original
            self.log_fh = log_fh

        def write(self, data):
            self.original.write(data)
            try:
                self.log_fh.write(data)
                self.log_fh.flush()
            except Exception:
                pass

        def flush(self):
            self.original.flush()
            try:
                self.log_fh.flush()
            except Exception:
                pass

        @property
        def encoding(self):
            return getattr(self.original, 'encoding', 'utf-8')

    log_fh = open(log_file, "w", encoding="utf-8")
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = TeeWriter(original_stdout, log_fh)
    sys.stderr = TeeWriter(original_stderr, log_fh)

    return log_file, original_stdout, original_stderr, log_fh


class MultiAccountManager:
    """多帳號管理器"""

    def __init__(self, config_file: str = "accounts.json") -> None:
        self.config_file: str = config_file
        self.logger: ScrapingLogger = get_logger("multi_account_manager")
        self.config: list[AccountConfig] = []
        self.current_function_name: Optional[str] = None
        self.discord_notifier = DiscordNotifier()
        self.email_notifier = EmailNotifier()
        load_dotenv()  # 載入環境變數
        self.load_config()

    def load_config(self) -> None:
        """載入設定檔"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(
                f"⛔ 設定檔 '{self.config_file}' 不存在！\n"
                "📝 請建立 accounts.json 檔案，格式為帳號陣列"
            )

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            # 支援新格式（純陣列）和舊格式（包含 accounts 鍵）
            if isinstance(config_data, list):
                # 新格式：直接是陣列
                self.config = config_data
            elif isinstance(config_data, dict) and "accounts" in config_data:
                # 舊格式：包含 accounts 鍵，顯示警告
                self.logger.warning(
                    "⚠️ 偵測到舊格式的 accounts.json，請考慮更新為新格式（純帳號陣列）"
                )
                self.config = config_data["accounts"]
            else:
                raise ValueError("⛔ 設定檔格式錯誤：應該是帳號陣列或包含 'accounts' 鍵的物件")

            if not self.config:
                raise ValueError("⛔ 設定檔中沒有找到帳號資訊！")

            self.logger.info(
                f"✅ 已載入設定檔: {self.config_file}",
                config_file=self.config_file,
                account_count=len(self.config),
            )

        except json.JSONDecodeError as e:
            raise ValueError(f"⛔ 設定檔格式錯誤: {e}")
        except Exception as e:
            raise RuntimeError(f"⛔ 載入設定檔失敗: {e}")

    def get_enabled_accounts(self) -> list[AccountConfig]:
        """取得啟用的帳號列表"""
        return [acc for acc in self.config if acc.get("enabled", True)]

    def _create_shared_browser(self, headless):
        """
        建立共享瀏覽器實例

        Args:
            headless: 是否使用無頭模式

        Returns:
            tuple: (driver, wait)
        """
        self.logger.info("🚀 建立共享瀏覽器...")
        driver, wait = init_chrome_browser(headless=headless, download_dir=None)
        self.logger.info("✅ 共享瀏覽器建立完成")
        return (driver, wait)

    def run_all_accounts(
        self,
        scraper_class: type,
        headless_override: Optional[bool] = None,
        progress_callback: Optional[Callable[[str], None]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        start_month: Optional[str] = None,
        end_month: Optional[str] = None,
    ) -> list[AccountConfig]:
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
        # 設定當前功能名稱（根據 scraper 類別名稱）
        if "Payment" in scraper_class.__name__:
            self.current_function_name = "代收貨款查詢"
        elif "Freight" in scraper_class.__name__:
            self.current_function_name = "運費查詢"
        elif "Unpaid" in scraper_class.__name__:
            self.current_function_name = "運費未請款查詢"
        else:
            self.current_function_name = scraper_class.__name__

        # 設定檔案日誌
        log_file, original_stdout, original_stderr, log_fh = _setup_file_logger(
            self.current_function_name
        )
        safe_print(f"📝 執行日誌: {log_file}")

        try:
            return self._run_all_accounts_inner(
                scraper_class, headless_override, progress_callback,
                start_date, end_date, start_month, end_month,
            )
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            try:
                log_fh.close()
            except Exception:
                pass

    def _run_all_accounts_inner(
        self,
        scraper_class: type,
        headless_override: Optional[bool] = None,
        progress_callback: Optional[Callable[[str], None]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        start_month: Optional[str] = None,
        end_month: Optional[str] = None,
    ) -> list[AccountConfig]:
        """run_all_accounts 的內部實作（包裹在日誌系統中）"""
        accounts = self.get_enabled_accounts()
        start_time = time.time()  # 記錄開始時間

        results = []

        if progress_callback:
            progress_callback(f"🚀 開始執行多帳號 WEDI 自動下載 (共 {len(accounts)} 個帳號)")
        else:
            self.logger.info("=" * 80)
            self.logger.info(
                f"🚀 開始執行多帳號 WEDI 自動下載 (共 {len(accounts)} 個帳號)",
                total_accounts=len(accounts),
            )
            self.logger.info("=" * 80)

        # 從環境變數讀取 HEADLESS 設定
        env_headless = os.getenv("HEADLESS", "true").lower() == "true"
        use_headless = headless_override if headless_override is not None else env_headless

        # ==================== 共享瀏覽器模式 ====================
        shared_browser = None
        if len(accounts) > 1:
            try:
                shared_browser = self._create_shared_browser(use_headless)
            except Exception as e:
                self.logger.warning(f"⚠️ 共享瀏覽器建立失敗，退回逐帳號模式: {e}")
                shared_browser = None

        max_account_retries = 2

        for i, account in enumerate(accounts, 1):
            username = account["username"]
            password = account["password"]

            progress_msg = f"📊 [{i}/{len(accounts)}] 處理帳號: {username}"
            if progress_callback:
                progress_callback(progress_msg)
            else:
                self.logger.info(
                    progress_msg,
                    account_index=i,
                    total_accounts=len(accounts),
                    username=username,
                )
                self.logger.info("-" * 50)

            # 共享模式：帳號切換前檢查瀏覽器健康
            if shared_browser and i > 1:
                alive, error_msg = check_browser_health(shared_browser[0])
                if not alive:
                    self.logger.warning(f"💀 共享瀏覽器已失效: {error_msg}，重建中...")
                    _cleanup_headless_chrome()
                    cleanup_temp_user_data_dirs()
                    time.sleep(2)
                    try:
                        shared_browser = self._create_shared_browser(use_headless)
                    except Exception as e:
                        self.logger.warning(f"⚠️ 共享瀏覽器重建失敗，退回逐帳號模式: {e}")
                        shared_browser = None

                # 批次冷卻
                if (i - 1) % 5 == 0:
                    self.logger.info("🧊 批次冷卻：等待 3 秒...")
                    time.sleep(3)

            # 準備 scraper 參數
            scraper_kwargs = {
                "username": username,
                "password": password,
                "headless": use_headless,
                "shared_driver": shared_browser,
            }

            if "Freight" in scraper_class.__name__:
                if start_month is not None:
                    scraper_kwargs["start_month"] = start_month
                if end_month is not None:
                    scraper_kwargs["end_month"] = end_month
            else:
                if start_date is not None:
                    scraper_kwargs["start_date"] = start_date
                if end_date is not None:
                    scraper_kwargs["end_date"] = end_date

            # 帳號執行（含重試機制）
            for retry in range(max_account_retries + 1):
                try:
                    scraper = scraper_class(**scraper_kwargs)

                    # 共享模式：非首帳號需要先重置瀏覽器
                    if shared_browser and i > 1:
                        scraper.reset_for_new_account(username, password)

                    downloads = scraper.run_full_process()

                    # 更新共享瀏覽器引用
                    if shared_browser and scraper._shared_driver:
                        shared_browser = scraper._shared_driver

                    result = {
                        "success": True,
                        "username": username,
                        "downloads": downloads,
                        "message": "無資料可下載" if not downloads else None,
                    }
                    results.append(result)
                    break

                except Exception as e:
                    error_str = str(e)
                    is_retryable = any(kw in error_str for kw in [
                        'RemoteDisconnected', 'Connection aborted',
                        'ConnectionResetError', 'MaxRetryError',
                        'WebDriverException', 'InvalidSessionIdException',
                        'NoSuchWindowException', 'no such session',
                        'chrome not reachable', '無法啟動 Chrome',
                    ])

                    if is_retryable and retry < max_account_retries:
                        retry_delay = 5 * (retry + 1)
                        self.logger.warning(
                            f"⚠️ 帳號 {username} 執行失敗 (第 {retry + 1} 次)，{retry_delay} 秒後重試...",
                            error=error_str[:100],
                        )

                        if shared_browser:
                            _cleanup_headless_chrome()
                            cleanup_temp_user_data_dirs()
                            time.sleep(retry_delay)
                            try:
                                shared_browser = self._create_shared_browser(use_headless)
                                scraper_kwargs["shared_driver"] = shared_browser
                            except Exception:
                                self.logger.warning("⚠️ 共享瀏覽器重建失敗，退回逐帳號模式")
                                shared_browser = None
                                scraper_kwargs["shared_driver"] = None
                        else:
                            _cleanup_headless_chrome()
                            cleanup_temp_user_data_dirs()
                            time.sleep(retry_delay)
                        continue
                    else:
                        error_msg = f"帳號 {username} 執行失敗: {error_str}"
                        if progress_callback:
                            progress_callback(error_msg)
                        else:
                            self.logger.error(error_msg, username=username, error=error_str)

                        results.append(
                            {
                                "success": False,
                                "username": username,
                                "error": error_str,
                                "downloads": [],
                            }
                        )
                        break

            # 帳號間隔等待
            if i < len(accounts):
                time.sleep(2)

        # 清理共享瀏覽器
        if shared_browser:
            self.logger.info("🔚 關閉共享瀏覽器...")
            try:
                shared_browser[0].quit()
            except Exception:
                pass
            _cleanup_headless_chrome()
            cleanup_temp_user_data_dirs()

        # 分析結果
        successful_accounts = [r for r in results if r["success"]]
        failed_accounts = [r for r in results if not r["success"]]
        total_downloads = sum(len(r["downloads"]) for r in successful_accounts)

        # 顯示統計
        self.logger.log_data_info(
            "執行統計",
            total_accounts=len(results),
            successful_accounts=len(successful_accounts),
            failed_accounts=len(failed_accounts),
            total_downloads=total_downloads,
        )

        if successful_accounts:
            self.logger.info("✅ 成功帳號詳情:")
            for result in successful_accounts:
                username = result["username"]
                download_count = len(result["downloads"])
                if result.get("message") == "無資料可下載":
                    self.logger.info(
                        f"   🔸 {username}: 無資料可下載", username=username, status="no_data"
                    )
                else:
                    self.logger.info(
                        f"   🔸 {username}: 成功下載 {download_count} 個檔案",
                        username=username,
                        download_count=download_count,
                    )

        if failed_accounts:
            self.logger.error("❌ 失敗帳號詳情:", failed_count=len(failed_accounts))
            for result in failed_accounts:
                username = result["username"]
                error = result.get("error", "未知錯誤")
                self.logger.error(
                    f"   🔸 {username}: {error}", username=username, error=error
                )

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
                "records": len(result.get("records", []))
                if result.get("records")
                else 0,
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

        self.logger.log_operation_success(
            "詳細報告保存", report_file=str(report_file), total_accounts=len(results)
        )

        # 計算執行時間（供 Discord 和 Email 通知使用）
        end_time = time.time()
        total_execution_minutes = (end_time - start_time) / 60

        # 收集所有下載的檔案清單（供 Discord 和 Email 通知使用）
        all_downloaded_files = []
        for result in successful_accounts:
            username = result["username"]
            downloads = result.get("downloads", [])
            for download in downloads:
                # downloads 是檔案路徑列表
                filename = os.path.basename(download) if isinstance(download, str) else str(download)
                all_downloaded_files.append({"username": username, "filename": filename})

        # 發送 Discord 通知
        if self.discord_notifier.is_enabled():
            safe_print("\n📢 正在發送 Discord 通知...")

            # 發送執行摘要
            self.discord_notifier.send_execution_summary(
                function_name=self.current_function_name or "未知功能",
                total_accounts=len(results),
                successful_accounts=len(successful_accounts),
                failed_accounts=len(failed_accounts),
                security_warning_accounts=0,  # 宅配通目前沒有密碼警告機制
                total_downloads=total_downloads,
                total_execution_minutes=total_execution_minutes,
                downloaded_files=all_downloaded_files,
            )

        # 發送 Email 通知
        if self.email_notifier.is_enabled():
            safe_print("\n📧 正在發送 Email 通知...")

            # 組合失敗帳號詳情
            failed_accounts_details = [
                {"username": r["username"], "error": r.get("error", "未知錯誤")}
                for r in failed_accounts
            ]
            # 執行的帳號清單
            executed_accounts = [r["username"] for r in results]

            # 發送執行摘要
            self.email_notifier.send_execution_summary(
                function_name=self.current_function_name or "未知功能",
                total_accounts=len(results),
                successful_accounts=len(successful_accounts),
                failed_accounts=len(failed_accounts),
                security_warning_accounts=0,  # 宅配通目前沒有密碼警告機制
                total_downloads=total_downloads,
                total_execution_minutes=total_execution_minutes,
                downloaded_files=all_downloaded_files,
                failed_accounts_details=failed_accounts_details,
                executed_accounts=executed_accounts,
            )

        self.logger.info("=" * 80)

        return results
