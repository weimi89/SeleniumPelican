#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代收貨款查詢工具
使用基礎類別實作代收貨款匯款明細查詢功能
"""


import argparse
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import openpyxl
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.core.constants import Timeouts

# 新架構模組
from src.core.improved_base_scraper import ImprovedBaseScraper
from src.core.multi_account_manager import MultiAccountManager
from src.core.type_aliases import DownloadResult, RecordDict, RecordList

# 向後兼容
from src.utils.windows_encoding_utils import check_pythonunbuffered

# 檢查 PYTHONUNBUFFERED 環境變數
check_pythonunbuffered()


class PaymentScraper(ImprovedBaseScraper):
    """
    代收貨款查詢工具
    繼承 BaseScraper 實作代收貨款匯款明細查詢
    """

    def __init__(
        self,
        username: str,
        password: str,
        headless: bool = False,
        download_base_dir: str = "downloads",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ):
        """
        初始化代收貨款查詢工具

        Args:
            username: 使用者名稱
            password: 密碼
            headless: 是否使用無頭模式
            download_base_dir: 下載目錄
            start_date: 開始日期 (YYYYMMDD)
            end_date: 結束日期 (YYYYMMDD)
        """
        # WEDI 系統固定 URL
        url = "http://wedinlb03.e-can.com.tw/wEDI2012/wedilogin.asp"

        # 調用新的父類構造函數
        super().__init__(
            url=url, username=username, password=password, headless=headless
        )

        # 代收貨款查詢特有的屬性
        self.start_date = start_date
        self.end_date = end_date
        self.download_base_dir = download_base_dir

        # 注意：下載目錄已由父類 ImprovedBaseScraper 設置
        # 不需要再次覆蓋，保持與父類一致

    def set_date_range(self) -> bool:
        """設定查詢日期範圍 - 使用wedi_selenium_scraper.py的邏輯"""
        assert self.driver is not None, "WebDriver must be initialized"
        self.logger.info("📅 設定日期範圍...", operation="set_date_range")

        # 使用指定的日期範圍，如果沒有指定則使用預設值(當日)
        if self.start_date and self.end_date:
            # start_date 和 end_date 已經是 YYYYMMDD 格式的字串
            start_date = self.start_date
            end_date = self.end_date
        else:
            # 預設值:當日
            today = datetime.now()
            start_date = today.strftime("%Y%m%d")
            end_date = today.strftime("%Y%m%d")

        self.logger.info(
            f"📅 查詢日期範圍: {start_date} ~ {end_date}",
            start_date=start_date,
            end_date=end_date,
            operation="date_range_config",
        )

        try:
            # 快速檢查是否有日期輸入框 (2秒超時)
            # WEDI 某些查詢頁面可能不需要手動輸入日期
            has_date_inputs = False
            if self.waiter:
                has_date_inputs = self.waiter.wait_for_element_visible(
                    By.CSS_SELECTOR, 'input[type="text"]', timeout=2
                )

            # 嘗試尋找所有日期輸入框
            date_inputs = self.driver.find_elements(
                By.CSS_SELECTOR, 'input[type="text"]'
            )

            if len(date_inputs) >= 2:
                try:
                    # 填入開始日期
                    date_inputs[0].clear()
                    date_inputs[0].send_keys(start_date)
                    self.logger.log_operation_success("設定開始日期", start_date=start_date)

                    # 填入結束日期
                    date_inputs[1].clear()
                    date_inputs[1].send_keys(end_date)
                    self.logger.log_operation_success("設定結束日期", end_date=end_date)
                except Exception as date_error:
                    self.logger.warning(
                        "⚠️ 填入日期失敗", error=str(date_error), operation="date_input"
                    )

                # 嘗試多種方式尋找查詢按鈕
                query_button_found = False
                button_selectors = [
                    'input[value*="查詢"]',
                    'button[title*="查詢"]',
                    'input[type="submit"]',
                    'button[type="submit"]',
                    'input[value*="搜尋"]',
                    'button:contains("查詢")',
                ]

                for selector in button_selectors:
                    try:
                        query_button = self.driver.find_element(
                            By.CSS_SELECTOR, selector
                        )
                        query_button.click()
                        self.logger.log_operation_success("點擊查詢按鈕", selector=selector)
                        time.sleep(Timeouts.QUERY_SUBMIT)
                        query_button_found = True
                        break
                    except (
                        NoSuchElementException,
                        ElementClickInterceptedException,
                        TimeoutException,
                    ):
                        continue

                if not query_button_found:
                    self.logger.warning(
                        "⚠️ 未找到查詢按鈕，直接繼續流程", operation="query_button_search"
                    )
            else:
                # 頁面沒有足夠的日期輸入框，這在某些 WEDI 查詢類型中是正常的
                self.logger.info(
                    "ℹ️ 頁面無需手動設定日期 (未找到日期輸入框)",
                    found_inputs=len(date_inputs),
                    operation="date_input_check",
                )

            return True

        except Exception as e:
            # 使用診斷管理器捕獲異常詳細資訊
            diagnostic_report = self.diagnostic_manager.capture_exception(
                e,
                context={
                    "operation": "set_date_range",
                    "username": self.username,
                    "start_date": self.start_date,
                    "end_date": self.end_date,
                },
                capture_screenshot=True,
                capture_page_source=True,
                driver=self.driver,
            )

            self.logger.warning(
                "⚠️ 日期範圍設定過程中出現問題，但繼續執行",
                error=str(e),
                operation="set_date_range",
                continue_execution=True,
                diagnostic_report=diagnostic_report,
            )
            return True  # 即使失敗也返回True，讓流程繼續

    def get_payment_records(self) -> RecordList:
        """直接在iframe中搜尋代收貨款相關數據 - 使用wedi_selenium_scraper.py的邏輯"""
        assert self.driver is not None, "WebDriver must be initialized"
        self.logger.info("📊 搜尋當前頁面中的代收貨款數據...", operation="get_payment_records")

        records = []
        try:
            # 此時已經在datamain iframe中，直接搜尋數據
            self.logger.info("🔍 分析當前頁面內容...", operation="analyze_page_content")

            # 搜尋所有連結，找出代收貨款相關項目
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            self.logger.info(f"   找到 {len(all_links)} 個連結")

            # 定義代收貨款匯款明細相關關鍵字（更精確）
            payment_keywords = ["代收貨款", "匯款明細", "(2-1)"]

            # 定義排除關鍵字（增加不需要的項目）
            excluded_keywords = [
                "語音取件",
                "三節加價",
                "系統公告",
                "操作說明",
                "維護通知",
                "Home",
                "首頁",
                "登出",
                "系統設定",
                "代收款已收未結帳明細",
                "已收未結帳",
                "未結帳明細",  # 不需要下載的項目
            ]

            for i, link in enumerate(all_links):
                try:
                    link_text = link.text.strip()
                    if link_text:
                        # 檢查是否需要排除
                        should_exclude = any(
                            keyword in link_text for keyword in excluded_keywords
                        )

                        # 更精確的匹配：必須包含「代收貨款」和「匯款明細」
                        is_payment_remittance = (
                            "代收貨款" in link_text and "匯款明細" in link_text
                        ) or "(2-1)" in link_text

                        if is_payment_remittance and not should_exclude:
                            # 生成檔案ID
                            file_id = (
                                link_text.replace(" ", "_")
                                .replace("[", "")
                                .replace("]", "")
                                .replace("-", "_")
                            )
                            records.append(
                                {
                                    "index": str(i + 1),
                                    "title": link_text,
                                    "payment_no": file_id,
                                    "link": link.get_attribute("href") or "",
                                }
                            )
                            self.logger.info(
                                f"   ✅ 找到代收貨款匯款明細: {link_text}",
                                link_text=link_text,
                                match_type="payment_remittance",
                            )
                        elif should_exclude:
                            self.logger.debug(
                                f"   ⏭️ 跳過排除項目: {link_text}",
                                link_text=link_text,
                                match_type="excluded",
                            )
                        elif "代收" in link_text:
                            self.logger.debug(
                                f"   ⏭️ 跳過非匯款明細項目: {link_text}",
                                link_text=link_text,
                                match_type="non_remittance",
                            )
                except (AttributeError, StaleElementReferenceException):
                    continue

            # 如果沒有找到任何代收貨款連結，嘗試搜尋表格數據
            if not records:
                self.logger.info("🔍 未找到代收貨款連結，搜尋表格數據...", operation="search_table_data")
                tables = self.driver.find_elements(By.TAG_NAME, "table")

                for table in tables:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    for row in rows:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        for cell in cells:
                            cell_text = cell.text.strip()
                            if any(
                                keyword in cell_text for keyword in payment_keywords
                            ):
                                self.logger.info(
                                    f"   📋 找到表格中的代收貨款數據: {cell_text}",
                                    cell_text=cell_text,
                                    match_type="table_data",
                                )

            self.logger.log_data_info("搜尋代收貨款記錄完成", count=len(records))
            return records

        except Exception as e:
            # 使用診斷管理器捕獲搜尋異常
            diagnostic_report = self.diagnostic_manager.capture_exception(
                e,
                context={
                    "operation": "get_payment_records",
                    "username": self.username,
                    "current_url": self.driver.current_url if self.driver else None,
                    "records_found": len(records),
                },
                capture_screenshot=True,
                capture_page_source=True,
                driver=self.driver,
            )

            self.logger.log_operation_failure(
                "搜尋代收貨款數據", e, diagnostic_report=diagnostic_report
            )
            return records

    def download_excel_for_record(self, record: RecordDict) -> DownloadResult:
        """為特定記錄下載Excel檔案 - 使用wedi_selenium_scraper.py的完整邏輯"""
        assert self.driver is not None, "WebDriver must be initialized"
        self.logger.info(
            f"📥 下載記錄 {record['payment_no']} 的Excel檔案...", operation="download"
        )

        try:
            # 已經在iframe中，直接查找連結
            links = self.driver.find_elements(By.TAG_NAME, "a")
            found_link = None

            # 尋找匹配的連結
            for link in links:
                try:
                    if record["title"] in link.text:
                        found_link = link
                        break
                except (AttributeError, StaleElementReferenceException):
                    continue

            if found_link:
                # 使用JavaScript點擊避免元素遮蔽問題
                self.driver.execute_script("arguments[0].click();", found_link)
                time.sleep(Timeouts.PAGE_LOAD)
            else:
                raise Exception(f"找不到標題為 '{record['title']}' 的可點擊連結")

            downloaded_files = []
            payment_no = record["payment_no"]

            # 調試：查看頁面上的所有按鈕和表單元素
            self.logger.debug(f"🔍 頁面調試資訊:")
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            forms = self.driver.find_elements(By.TAG_NAME, "form")

            self.logger.debug(f"   找到 {len(buttons)} 個按鈕:")
            for i, btn in enumerate(buttons[:10]):  # 只顯示前10個
                try:
                    text = (
                        btn.text
                        or btn.get_attribute("value")
                        or btn.get_attribute("title")
                    )
                    self.logger.info(f"     按鈕 {i+1}: {text}")
                except (AttributeError, StaleElementReferenceException):
                    pass

            self.logger.info(f"   找到 {len(inputs)} 個input元素:")
            for i, inp in enumerate(inputs[:10]):  # 只顯示前10個
                try:
                    inp_type = inp.get_attribute("type")
                    value = inp.get_attribute("value") or inp.text
                    self.logger.info(
                        f"     Input {i+1}: type='{inp_type}' value='{value}'"
                    )
                except (AttributeError, StaleElementReferenceException):
                    pass

            self.logger.info(f"   找到 {len(forms)} 個表單")

            # 在詳細頁面填入查詢日期範圍
            self.logger.info(f"📅 在詳細頁面填入查詢日期...", operation="search")
            try:
                # 使用指定的日期範圍
                if self.start_date and self.end_date:
                    # start_date 和 end_date 已經是 YYYYMMDD 格式的字串
                    start_date = self.start_date
                    end_date = self.end_date
                else:
                    # 預設值:當日
                    today = datetime.now()
                    start_date = today.strftime("%Y%m%d")
                    end_date = today.strftime("%Y%m%d")

                # 找到日期輸入框
                date_inputs = self.driver.find_elements(
                    By.CSS_SELECTOR, 'input[type="text"]'
                )
                if len(date_inputs) >= 2:
                    # 填入開始日期
                    date_inputs[0].clear()
                    date_inputs[0].send_keys(start_date)
                    self.logger.info(f"✅ 已填入開始日期: {start_date}")

                    # 填入結束日期
                    date_inputs[1].clear()
                    date_inputs[1].send_keys(end_date)
                    self.logger.info(f"✅ 已填入結束日期: {end_date}")
                elif len(date_inputs) >= 1:
                    # 只有一個日期輸入框，填入結束日期
                    date_inputs[0].clear()
                    date_inputs[0].send_keys(end_date)
                    self.logger.info(f"✅ 已填入查詢日期: {end_date}", operation="search")

                # 嘗試點擊查詢按鈕
                try:
                    query_button = self.driver.find_element(
                        By.CSS_SELECTOR, 'input[value*="查詢"]'
                    )
                    query_button.click()
                    self.logger.info(f"✅ 已點擊查詢按鈕", operation="search")
                    time.sleep(Timeouts.PAGE_LOAD)  # 等待查詢結果
                except (NoSuchElementException, ElementClickInterceptedException):
                    self.logger.warning(f"⚠️ 未找到查詢按鈕，跳過此步驟", operation="search")

                # 查詢後再次檢查頁面元素
                self.logger.debug(f"🔍 查詢後頁面調試資訊:", operation="search")
                buttons_after = self.driver.find_elements(By.TAG_NAME, "button")
                inputs_after = self.driver.find_elements(By.TAG_NAME, "input")
                links_after = self.driver.find_elements(By.TAG_NAME, "a")

                self.logger.info(f"   查詢後找到 {len(buttons_after)} 個按鈕:")
                for i, btn in enumerate(buttons_after[:10]):
                    try:
                        text = (
                            btn.text
                            or btn.get_attribute("value")
                            or btn.get_attribute("title")
                        )
                        self.logger.info(f"     按鈕 {i+1}: {text}")
                    except (AttributeError, StaleElementReferenceException):
                        pass

                self.logger.info(f"   查詢後找到 {len(inputs_after)} 個input元素:")
                for i, inp in enumerate(inputs_after[:15]):
                    try:
                        inp_type = inp.get_attribute("type")
                        value = inp.get_attribute("value") or inp.text
                        self.logger.info(
                            f"     Input {i+1}: type='{inp_type}' value='{value}'"
                        )
                    except (AttributeError, StaleElementReferenceException):
                        pass

                self.logger.info(f"   查詢後找到 {len(links_after)} 個連結:")
                for i, link in enumerate(links_after[:10]):
                    try:
                        text = link.text.strip()
                        if text and ("匯出" in text or "Excel" in text or "下載" in text):
                            self.logger.info(f"     重要連結 {i+1}: {text}")
                    except (AttributeError, StaleElementReferenceException):
                        pass

                # 查詢結果頁面載入完成

                # 查找查詢結果中的匯款編號連結
                self.logger.debug(f"🔍 尋找查詢結果中的匯款編號連結...", operation="search")

                # 使用多種策略尋找匯款編號連結
                payment_links = []

                # 策略1: 原始XPath（JavaScript連結或以4開頭）
                try:
                    links_xpath1 = self.driver.find_elements(
                        By.XPATH,
                        "//a[contains(@href, 'javascript:') or starts-with(text(), '4')]",
                    )
                    payment_links.extend(links_xpath1)
                    self.logger.debug(f"   策略1找到 {len(links_xpath1)} 個連結")
                except Exception as e:
                    self.logger.debug(f"   策略1失敗: {e}")

                # 策略2: 尋找所有包含數字的連結（可能是匯款編號）
                try:
                    all_links = self.driver.find_elements(By.TAG_NAME, "a")
                    for link in all_links:
                        try:
                            link_text = link.text.strip()
                            # 放寬檢查條件：長度>6且包含數字，或者全數字且長度>8
                            is_potential_payment = False
                            if link_text:
                                # 條件1: 長度>6且包含數字
                                if len(link_text) > 6 and any(
                                    c.isdigit() for c in link_text
                                ):
                                    is_potential_payment = True
                                # 條件2: 全數字且長度>8
                                elif link_text.isdigit() and len(link_text) > 8:
                                    is_potential_payment = True
                                # 條件3: 包含常見匯款編號模式（數字+字母組合）
                                elif (
                                    len(link_text) > 8
                                    and any(c.isdigit() for c in link_text)
                                    and any(c.isalpha() for c in link_text)
                                ):
                                    is_potential_payment = True

                            if is_potential_payment and link not in payment_links:
                                payment_links.append(link)
                                self.logger.debug(f"   策略2找到可能的匯款編號: {link_text}")
                        except:
                            continue
                    self.logger.debug(
                        f"   策略2添加了 {len(payment_links) - len(links_xpath1)} 個額外連結"
                    )
                except Exception as e:
                    self.logger.debug(f"   策略2失敗: {e}")

                # 策略3: 在表格中尋找可點擊的數字內容
                try:
                    tables = self.driver.find_elements(By.TAG_NAME, "table")
                    for table in tables:
                        cells = table.find_elements(By.TAG_NAME, "td")
                        for cell in cells:
                            try:
                                cell_text = cell.text.strip()
                                # 放寬檢查條件：長度>6且包含數字，或符合匯款編號模式
                                is_potential_payment = False
                                if cell_text:
                                    # 條件1: 長度>6且包含數字
                                    if len(cell_text) > 6 and any(
                                        c.isdigit() for c in cell_text
                                    ):
                                        is_potential_payment = True
                                    # 條件2: 全數字且長度>8
                                    elif cell_text.isdigit() and len(cell_text) > 8:
                                        is_potential_payment = True

                                if is_potential_payment:
                                    # 檢查cell中是否有連結
                                    cell_links = cell.find_elements(By.TAG_NAME, "a")
                                    for cell_link in cell_links:
                                        if cell_link not in payment_links:
                                            payment_links.append(cell_link)
                                            self.logger.debug(
                                                f"   策略3找到表格中的匯款編號: {cell_text}"
                                            )

                                    # 如果cell本身就是連結（檢查父元素）
                                    if not cell_links:
                                        try:
                                            if (
                                                cell.tag_name == "a"
                                                or cell.find_element(
                                                    By.XPATH, "./parent::a"
                                                )
                                            ):
                                                if cell not in payment_links:
                                                    payment_links.append(cell)
                                                    self.logger.debug(
                                                        f"   策略3找到cell連結: {cell_text}"
                                                    )
                                        except:
                                            pass
                            except:
                                continue
                    self.logger.debug(f"   策略3完成")
                except Exception as e:
                    self.logger.debug(f"   策略3失敗: {e}")

                # 去重
                unique_payment_links = []
                seen_hrefs = set()
                for link in payment_links:
                    try:
                        href = (
                            link.get_attribute("href")
                            or link.get_attribute("onclick")
                            or ""
                        )
                        if href not in seen_hrefs:
                            unique_payment_links.append(link)
                            seen_hrefs.add(href)
                    except:
                        unique_payment_links.append(link)

                payment_links = unique_payment_links

                if payment_links:
                    self.logger.info(f"   找到 {len(payment_links)} 個匯款編號連結")
                    for i, link in enumerate(payment_links):
                        try:
                            link_text = link.text.strip()
                            self.logger.info(f"   連結 {i+1}: {link_text}")
                        except (AttributeError, StaleElementReferenceException):
                            pass

                    # 收集所有匯款編號
                    payment_numbers = []
                    for i, link in enumerate(payment_links):
                        try:
                            link_text = link.text.strip()
                            # 放寬匯款編號的條件：長度大於6且包含數字
                            if (
                                link_text
                                and len(link_text) > 6
                                and any(c.isdigit() for c in link_text)
                            ):
                                payment_numbers.append(link_text)
                                self.logger.info(f"   收集匯款編號: {link_text}")
                        except (AttributeError, StaleElementReferenceException):
                            pass

                    # 分別處理每個匯款編號 - 使用多視窗方式
                    for i, payment_no in enumerate(payment_numbers):
                        self.logger.info(
                            f"🔗 正在處理匯款編號 ({i+1}/{len(payment_numbers)}): {payment_no}"
                        )

                        try:
                            # 保存當前主視窗handle
                            main_window = self.driver.current_window_handle

                            # 使用多策略重新找到匯款編號連結
                            target_link = None

                            # 策略1: 原始XPath（JavaScript連結或以4開頭）
                            try:
                                links_xpath1 = self.driver.find_elements(
                                    By.XPATH,
                                    "//a[contains(@href, 'javascript:') or starts-with(text(), '4')]",
                                )
                                for link in links_xpath1:
                                    if link.text.strip() == payment_no:
                                        target_link = link
                                        break
                                if target_link:
                                    self.logger.debug(f"   策略1找到目標連結: {payment_no}")
                            except Exception as e:
                                self.logger.debug(f"   策略1失敗: {e}")

                            # 策略2: 如果策略1沒找到，搜尋所有包含此匯款編號的連結
                            if not target_link:
                                try:
                                    all_links = self.driver.find_elements(
                                        By.TAG_NAME, "a"
                                    )
                                    for link in all_links:
                                        try:
                                            link_text = link.text.strip()
                                            if link_text == payment_no:
                                                target_link = link
                                                self.logger.debug(
                                                    f"   策略2找到目標連結: {payment_no}"
                                                )
                                                break
                                        except:
                                            continue
                                except Exception as e:
                                    self.logger.debug(f"   策略2失敗: {e}")

                            # 策略3: 如果前面都沒找到，在表格中搜尋
                            if not target_link:
                                try:
                                    tables = self.driver.find_elements(
                                        By.TAG_NAME, "table"
                                    )
                                    for table in tables:
                                        cells = table.find_elements(By.TAG_NAME, "td")
                                        for cell in cells:
                                            try:
                                                cell_text = cell.text.strip()
                                                if cell_text == payment_no:
                                                    cell_links = cell.find_elements(
                                                        By.TAG_NAME, "a"
                                                    )
                                                    if cell_links:
                                                        target_link = cell_links[0]
                                                        self.logger.debug(
                                                            f"   策略3找到目標連結: {payment_no}"
                                                        )
                                                        break
                                            except:
                                                continue
                                        if target_link:
                                            break
                                        if target_link:
                                            break
                                except Exception as e:
                                    self.logger.debug(f"   策略3失敗: {e}")

                            if target_link:
                                # 獲取連結的href屬性
                                link_href = target_link.get_attribute("href")
                                self.logger.info(f"🔗 連結href: {link_href}")

                                if link_href and "javascript:" in link_href:
                                    # JavaScript連結需要在新視窗中執行
                                    # 使用Ctrl+Click或者執行JavaScript來開新視窗
                                    self.driver.execute_script(
                                        "window.open('about:blank', '_blank');"
                                    )

                                    # 切換到新視窗
                                    new_windows = [
                                        handle
                                        for handle in self.driver.window_handles
                                        if handle != main_window
                                    ]
                                    if new_windows:
                                        new_window = new_windows[-1]
                                        self.driver.switch_to.window(new_window)

                                        # 在新視窗中重新導航到相同頁面
                                        self.driver.get(
                                            self.driver.current_url
                                            if hasattr(self, "current_url")
                                            else "about:blank"
                                        )
                                        time.sleep(Timeouts.IFRAME_SWITCH)

                                        # 切換回原始iframe
                                        try:
                                            iframe = WebDriverWait(
                                                self.driver, 10
                                            ).until(
                                                EC.presence_of_element_located(
                                                    (By.NAME, "datamain")
                                                )
                                            )
                                            self.driver.switch_to.frame(iframe)
                                        except (
                                            TimeoutException,
                                            NoSuchElementException,
                                        ):
                                            pass

                                        # 重新執行查詢和點擊目標連結
                                        try:
                                            # 重新填入查詢條件
                                            self.refill_query_conditions()

                                            # 使用多策略重新尋找並點擊目標連結
                                            new_target_link = None

                                            # 策略1: XPath搜尋
                                            try:
                                                new_links = self.driver.find_elements(
                                                    By.XPATH,
                                                    "//a[contains(@href, 'javascript:') or starts-with(text(), '4')]",
                                                )
                                                for link in new_links:
                                                    if link.text.strip() == payment_no:
                                                        new_target_link = link
                                                        break
                                            except:
                                                pass

                                            # 策略2: 如果策略1沒找到，搜尋所有連結
                                            if not new_target_link:
                                                try:
                                                    all_new_links = (
                                                        self.driver.find_elements(
                                                            By.TAG_NAME, "a"
                                                        )
                                                    )
                                                    for link in all_new_links:
                                                        try:
                                                            if (
                                                                link.text.strip()
                                                                == payment_no
                                                            ):
                                                                new_target_link = link
                                                                break
                                                        except:
                                                            continue
                                                except:
                                                    pass

                                            if new_target_link:
                                                self.driver.execute_script(
                                                    "arguments[0].click();",
                                                    new_target_link,
                                                )
                                                time.sleep(Timeouts.QUERY_SUBMIT)
                                            else:
                                                self.logger.warning(
                                                    f"⚠️ 在新視窗中找不到匯款編號 {payment_no} 的連結"
                                                )

                                        except Exception as nav_e:
                                            self.logger.warning(
                                                f"⚠️ 新視窗導航失敗: {nav_e}",
                                                error="{nav_e}",
                                                operation="navigation",
                                            )
                                            # 如果新視窗導航失敗，切換回主視窗並使用原方法
                                            self.driver.close()
                                            self.driver.switch_to.window(main_window)
                                            continue
                                else:
                                    # 普通連結可以直接在新視窗中開啟
                                    self.driver.execute_script(
                                        "window.open(arguments[0], '_blank');",
                                        link_href,
                                    )
                                    new_windows = [
                                        handle
                                        for handle in self.driver.window_handles
                                        if handle != main_window
                                    ]
                                    if new_windows:
                                        new_window = new_windows[-1]
                                        self.driver.switch_to.window(new_window)
                                        time.sleep(Timeouts.PAGE_LOAD)

                                # 匯款詳細頁面載入完成

                                # 下載這個匯款記錄的Excel檔案
                                download_success = self.download_excel_for_payment(
                                    payment_no
                                )
                                if download_success:
                                    downloaded_files.append(
                                        f"代收貨款匯款明細_{self.username}_{payment_no}.xlsx"
                                    )

                                # 關閉新視窗並回到主視窗
                                self.driver.close()
                                self.driver.switch_to.window(main_window)

                                # 切換回iframe
                                try:
                                    iframe = WebDriverWait(self.driver, 5).until(
                                        EC.presence_of_element_located(
                                            (By.NAME, "datamain")
                                        )
                                    )
                                    self.driver.switch_to.frame(iframe)
                                except (TimeoutException, NoSuchElementException):
                                    pass

                                self.logger.info(
                                    f"✅ 已關閉新視窗，回到主查詢頁面", operation="search"
                                )

                            else:
                                self.logger.warning(f"⚠️ 找不到匯款編號 {payment_no} 的連結")

                        except Exception as link_e:
                            self.logger.warning(
                                f"⚠️ 處理匯款編號 {payment_no} 時發生錯誤: {link_e}"
                            )

                            # 確保回到主視窗
                            try:
                                if len(self.driver.window_handles) > 1:
                                    self.driver.close()
                                    self.driver.switch_to.window(main_window)
                            except WebDriverException:
                                pass
                            continue

                    # 處理完所有連結後返回
                    return downloaded_files

                else:
                    self.logger.error(f"❌ 沒有找到匯款編號連結")

            except Exception as date_e:
                self.logger.warning(
                    f"⚠️ 填入查詢日期失敗: {date_e}", error="{date_e}", operation="search"
                )

            # 尋找並點擊匯出xlsx按鈕
            try:
                # 嘗試多種可能的匯出按鈕選擇器
                xlsx_selectors = [
                    "//button[contains(text(), '匯出xlsx')]",
                    "//input[@value*='匯出xlsx']",
                    "//a[contains(text(), '匯出xlsx')]",
                    "//button[contains(text(), 'Excel')]",
                    "//input[@value*='Excel']",
                    "//form//input[@type='submit'][contains(@value, '匯出')]",
                ]

                xlsx_button = None
                wait = WebDriverWait(self.driver, Timeouts.DEFAULT_WAIT)
                for selector in xlsx_selectors:
                    try:
                        xlsx_button = wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        break
                    except (TimeoutException, NoSuchElementException):
                        continue

                if xlsx_button:
                    # 獲取下載前的檔案列表
                    before_files = set(self.download_dir.glob("*"))

                    # 使用JavaScript點擊避免元素遮蔽問題
                    self.driver.execute_script("arguments[0].click();", xlsx_button)
                    self.logger.info(f"✅ 已點擊匯出xlsx按鈕")
                    time.sleep(Timeouts.DOWNLOAD_WAIT)  # 等待下載開始
                else:
                    raise Exception("找不到xlsx匯出按鈕")

                # 獲取新下載的檔案
                after_files = set(self.download_dir.glob("*"))
                new_files = after_files - before_files

                # 重命名新下載的檔案
                for new_file in new_files:
                    if new_file.suffix.lower() in [".xlsx", ".xls"]:
                        new_name = f"{self.username}_{payment_no}{new_file.suffix}"
                        new_path = self.download_dir / new_name
                        new_file.rename(new_path)
                        downloaded_files.append(str(new_path))
                        self.logger.info(f"✅ 已重命名為: {new_name}")

            except Exception as e:
                self.logger.warning(
                    f"⚠️ xlsx下載失敗: {e}", error="{e}", operation="download"
                )

            # 保持在iframe中，不切換回主frame
            return downloaded_files

        except Exception as e:
            # 使用診斷管理器捕獲下載異常
            diagnostic_report = self.diagnostic_manager.capture_exception(
                e,
                context={
                    "operation": "download_excel_for_record",
                    "username": self.username,
                    "record": record,
                    "current_url": self.driver.current_url if self.driver else None,
                },
                capture_screenshot=True,
                capture_page_source=True,
                driver=self.driver,
            )

            self.logger.log_operation_failure(
                "下載記錄", e, diagnostic_report=diagnostic_report
            )
            return []

    def refill_query_conditions(self) -> None:
        """在新視窗中重新填入查詢條件"""
        assert self.driver is not None, "WebDriver must be initialized"
        self.logger.info(f"📅 重新填入查詢條件...", operation="search")

        try:
            # 使用指定的日期範圍
            if self.start_date and self.end_date:
                # start_date 和 end_date 已經是 YYYYMMDD 格式的字串
                start_date = self.start_date
                end_date = self.end_date
            else:
                # 預設值:當日
                today = datetime.now()
                start_date = today.strftime("%Y%m%d")
                end_date = today.strftime("%Y%m%d")

            # 尋找日期輸入框
            date_inputs = self.driver.find_elements(
                By.CSS_SELECTOR, 'input[type="text"]'
            )

            if len(date_inputs) >= 2:
                # 填入開始日期
                date_inputs[0].clear()
                date_inputs[0].send_keys(start_date)

                # 填入結束日期
                date_inputs[1].clear()
                date_inputs[1].send_keys(end_date)

                self.logger.info(f"✅ 已重新填入日期範圍: {start_date} ~ {end_date}")

                # 點擊查詢按鈕
                try:
                    query_button = self.driver.find_element(
                        By.CSS_SELECTOR, 'input[value*="查詢"]'
                    )
                    query_button.click()
                    time.sleep(Timeouts.QUERY_SUBMIT)
                    self.logger.info(f"✅ 已執行查詢", operation="search")
                except (NoSuchElementException, ElementClickInterceptedException):
                    self.logger.warning(f"⚠️ 找不到查詢按鈕", operation="search")
            else:
                self.logger.warning(f"⚠️ 找不到足夠的日期輸入框")

        except Exception as e:
            self.logger.warning(f"⚠️ 重新填入查詢條件失敗: {e}", error="{e}", operation="search")

    def download_excel_for_payment(self, payment_no: str) -> Optional[str]:
        """為單個匯款記錄下載Excel檔案 - 使用 data-fileblob 提取"""
        assert self.driver is not None, "WebDriver must be initialized"
        self.logger.info(f"📥 下載匯款編號 {payment_no} 的Excel檔案...", operation="download")

        try:
            # 直接從頁面提取 data-fileblob 數據並生成 Excel
            self.logger.info(f"🚀 嘗試從頁面提取 data-fileblob 數據...")

            # 尋找包含 data-fileblob 屬性的按鈕
            fileblob_buttons = self.driver.find_elements(
                By.CSS_SELECTOR, "button[data-fileblob]"
            )

            if fileblob_buttons:
                fileblob_button = fileblob_buttons[0]
                fileblob_data = fileblob_button.get_attribute("data-fileblob")

                if fileblob_data:
                    try:
                        # 解析 JSON 數據
                        blob_json = json.loads(fileblob_data)
                        data_array = blob_json.get("data", [])

                        if data_array:
                            # 使用 openpyxl 創建 Excel 檔案
                            wb = openpyxl.Workbook()
                            ws = wb.active
                            assert (
                                ws is not None
                            ), "Workbook active sheet should not be None"
                            ws.title = "代收貨款匯款明細"

                            # 將數據寫入工作表
                            for row_index, row_data in enumerate(data_array, 1):
                                for col_index, cell_value in enumerate(row_data, 1):
                                    # 清理 HTML 實體和空白字符
                                    if isinstance(cell_value, str):
                                        cell_value = cell_value.replace(
                                            "&nbsp;", ""
                                        ).strip()

                                    cell = ws.cell(
                                        row=row_index,
                                        column=col_index,
                                        value=cell_value,
                                    )

                                    # 設定標題行格式
                                    if row_index == 1:
                                        from openpyxl.styles import Font

                                        cell.font = Font(bold=True)

                            # 自動調整欄寬
                            from openpyxl.cell.cell import Cell

                            for column in ws.columns:
                                max_length = 0
                                # 取得第一個 Cell 的 column_letter (跳過 MergedCell)
                                column_letter = None
                                for cell in column:
                                    if isinstance(cell, Cell) and hasattr(
                                        cell, "column_letter"
                                    ):
                                        column_letter = cell.column_letter
                                        break

                                if column_letter is None:
                                    continue

                                for cell in column:
                                    try:
                                        if cell.value:
                                            max_length = max(
                                                max_length, len(str(cell.value))
                                            )
                                    except (AttributeError, TypeError):
                                        pass
                                adjusted_width = min(max_length + 2, 50)
                                ws.column_dimensions[
                                    column_letter
                                ].width = adjusted_width

                            # 生成檔案名稱
                            new_name = f"代收貨款匯款明細_{self.username}_{payment_no}.xlsx"
                            new_path = self.download_dir / new_name

                            # 如果目標檔案已存在，直接覆蓋
                            if new_path.exists():
                                self.logger.warning(f"⚠️ 檔案已存在，將覆蓋: {new_name}")
                                new_path.unlink()

                            # 保存 Excel 檔案
                            wb.save(new_path)
                            self.logger.info(
                                f"✅ 已生成 Excel 檔案: {new_name} (共 {len(data_array)} 行數據)"
                            )

                            return new_name

                        else:
                            self.logger.error(f"❌ data-fileblob 中沒有找到數據陣列")
                            return None

                    except json.JSONDecodeError as json_e:
                        self.logger.error(
                            f"❌ 解析 data-fileblob JSON 失敗: {json_e}", error="{json_e}"
                        )
                        self.logger.info(f"   原始數據前500字元: {fileblob_data[:500]}")
                        return None

                    except Exception as excel_e:
                        self.logger.error(
                            f"❌ 生成 Excel 檔案失敗: {excel_e}", error="{excel_e}"
                        )
                        return None

                else:
                    self.logger.error(f"❌ data-fileblob 屬性為空")
                    return None

            else:
                self.logger.warning(
                    f"⚠️ 未找到包含 data-fileblob 的元素，嘗試傳統下載方式...", operation="download"
                )
                return self._fallback_download_excel(payment_no)

        except Exception as blob_e:
            self.logger.error(f"❌ data-fileblob 提取失敗: {blob_e}", error="{blob_e}")
            self.logger.info(f"🔄 嘗試傳統下載方式...", operation="download")
            return self._fallback_download_excel(payment_no)

    def _fallback_download_excel(self, payment_no: str) -> Optional[str]:
        """備用的傳統下載方式"""
        assert self.driver is not None, "WebDriver must be initialized"
        try:
            # 尋找並點擊匯出xlsx按鈕
            xlsx_selectors = [
                "//button[contains(text(), '匯出xlsx')]",
                "//input[@value*='匯出xlsx']",
                "//a[contains(text(), '匯出xlsx')]",
                "//button[contains(text(), 'Excel')]",
                "//input[@value*='Excel']",
                "//form//input[@type='submit'][contains(@value, '匯出')]",
            ]

            xlsx_button = None
            for selector in xlsx_selectors:
                try:
                    xlsx_button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except (TimeoutException, NoSuchElementException):
                    continue

            if xlsx_button:
                # 獲取下載前的檔案列表
                before_files = set(self.download_dir.glob("*"))

                # 使用JavaScript點擊避免元素遮蔽問題
                self.driver.execute_script("arguments[0].click();", xlsx_button)
                self.logger.info(f"✅ 已點擊匯出xlsx按鈕")
                time.sleep(Timeouts.DOWNLOAD_WAIT)  # 等待下載完成

                # 獲取新下載的檔案
                after_files = set(self.download_dir.glob("*"))
                new_files = after_files - before_files

                # 重命名新下載的檔案
                for new_file in new_files:
                    if new_file.suffix.lower() in [".xlsx", ".xls"]:
                        new_name = (
                            f"代收貨款匯款明細_{self.username}_{payment_no}{new_file.suffix}"
                        )
                        new_path = self.download_dir / new_name

                        # 如果目標檔案已存在，直接覆蓋
                        if new_path.exists():
                            self.logger.warning(f"⚠️ 檔案已存在，將覆蓋: {new_name}")
                            new_path.unlink()  # 刪除舊檔案

                        new_file.rename(new_path)
                        self.logger.info(f"✅ 已重命名為: {new_name}")
                        return new_name

                # 處理.crdownload檔案（Chrome下載中的檔案）
                crdownload_files = list(self.download_dir.glob("*.crdownload"))
                if crdownload_files:
                    crdownload_file = crdownload_files[0]
                    new_name = f"代收貨款匯款明細_{self.username}_{payment_no}.xlsx"
                    new_path = self.download_dir / new_name

                    if new_path.exists():
                        self.logger.warning(f"⚠️ 檔案已存在，將覆蓋: {new_name}")
                        new_path.unlink()  # 刪除舊檔案

                    crdownload_file.rename(new_path)
                    self.logger.info(f"✅ 已重命名.crdownload檔案為: {new_name}")
                    return new_name

                # 返回第一個新檔案的名稱,如果有的話
                if new_files:
                    return next(iter(new_files)).name
                return None
            else:
                self.logger.warning(f"⚠️ 找不到xlsx匯出按鈕")
                return None

        except Exception as e:
            self.logger.warning(f"⚠️ 傳統下載方式失敗: {e}", error="{e}", operation="download")
            return None

    def run_full_process(self) -> List[str]:
        """執行完整的自動化流程"""
        all_downloads: DownloadResult = []
        records: RecordList = []

        try:
            self.logger.info("=" * 60)
            self.logger.info(
                f"🤖 開始執行代收貨款查詢流程 (帳號: {self.username})", operation="search"
            )
            self.logger.info("=" * 60)

            # 瀏覽器已在建構函式中自動初始化

            # 2. 登入
            login_success = self.login()
            if not login_success:
                self.logger.log_operation_failure(f"帳號 {self.username} 登入", "登入失敗")
                return []  # 登入失敗,返回空列表

            # 3. 導航到查詢頁面
            nav_success = self.navigate_to_query()
            if not nav_success:
                self.logger.log_operation_failure(f"帳號 {self.username} 導航", "導航失敗")
                return []  # 導航失敗,返回空列表

            # 4. 先設定日期範圍（雖然可能找不到輸入框）
            self.set_date_range()

            # 5. 獲取付款記錄
            records = self.get_payment_records()

            if not records:
                self.logger.warning(f"⚠️ 帳號 {self.username} 沒有找到付款記錄")
                return []  # 沒有記錄,返回空列表

            # 6. 下載每個記錄的Excel檔案
            for record in records:
                try:
                    downloads = self.download_excel_for_record(record)
                    all_downloads.extend(downloads)
                except Exception as download_e:
                    self.logger.warning(
                        f"⚠️ 帳號 {self.username} 下載記錄 "
                        f"{record.get('payment_no', 'unknown')} 失敗: {download_e}",
                        operation="download",
                    )
                    continue

            self.logger.info(f"🎉 帳號 {self.username} 自動化流程完成！")

            return all_downloads

        except Exception as e:
            self.logger.info(f"💥 帳號 {self.username} 流程執行失敗: {e}", error="{e}")
            return all_downloads  # 返回已下載的檔案列表,即使發生錯誤
        finally:
            self.close()


def main():
    """主程式入口"""

    from datetime import datetime, timedelta

    from src.core.logging_config import get_logger

    # 設置主程式日誌器
    logger = get_logger("payment_scraper_main")

    parser = argparse.ArgumentParser(description="代收貨款自動下載工具")
    parser.add_argument("--headless", action="store_true", help="使用無頭模式")
    parser.add_argument(
        "--start-date", type=str, help="開始日期 (格式: YYYYMMDD，例如: 20241201)"
    )
    parser.add_argument("--end-date", type=str, help="結束日期 (格式: YYYYMMDD，例如: 20241208)")

    args = parser.parse_args()

    # 日期參數驗證和處理
    try:
        today = datetime.now()

        # 處理開始日期：如果未指定則使用往前7天
        if args.start_date:
            start_date = datetime.strptime(args.start_date, "%Y%m%d")
        else:
            start_date = today - timedelta(days=7)

        # 處理結束日期：如果未指定則使用當日
        if args.end_date:
            end_date = datetime.strptime(args.end_date, "%Y%m%d")
        else:
            end_date = today

        # 驗證日期範圍
        if start_date > end_date:
            logger.error("⛔ 錯誤: 開始日期不能晚於結束日期")
            return 1

        # 顯示查詢範圍
        if args.start_date and args.end_date:
            logger.info(
                f"📅 使用指定日期範圍: {start_date.strftime('%Y%m%d')} ~ {end_date.strftime('%Y%m%d')}"
            )
        elif args.start_date:
            logger.info(
                f"📅 從指定日期到當日: {start_date.strftime('%Y%m%d')} ~ {end_date.strftime('%Y%m%d')}"
            )
        elif args.end_date:
            logger.info(
                f"📅 從7天前到指定日期: {start_date.strftime('%Y%m%d')} ~ {end_date.strftime('%Y%m%d')}"
            )
        else:
            logger.info(
                f"📅 查詢日期範圍: {start_date.strftime('%Y%m%d')} ~ {end_date.strftime('%Y%m%d')} (預設7天)",
                operation="search",
            )

    except ValueError as e:
        logger.error(f"⛔ 日期格式錯誤: {e}")
        logger.info("💡 日期格式應為 YYYYMMDD，例如: 20241201")
        return 1

    try:
        # 統一使用多帳號管理模式
        logger.info(f"🏢 代收貨款自動下載工具", operation="download")

        manager = MultiAccountManager("accounts.json")
        manager.run_all_accounts(
            scraper_class=PaymentScraper,
            headless_override=args.headless if args.headless else None,
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
        )

        return 0

    except (FileNotFoundError, ValueError, RuntimeError) as e:
        logger.error(f"⛔ 錯誤: {e}")
        return 1
    except KeyboardInterrupt:
        logger.warning("\n⛔ 使用者中斷執行")
        return 1
    except Exception as e:
        logger.error(f"⛔ 未知錯誤: {e}")
        return 1


if __name__ == "__main__":
    main()
