#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WEDI 運費查詢工具
使用基礎類別實作運費(月結)結帳資料查詢功能
"""

import sys
import os
import time
import re
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# 使用共用的模組和基礎類別
from src.utils.windows_encoding_utils import safe_print, check_pythonunbuffered
from src.core.base_scraper import BaseScraper
from src.core.multi_account_manager import MultiAccountManager

# 檢查 PYTHONUNBUFFERED 環境變數
check_pythonunbuffered()

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class FreightScraper(BaseScraper):
    """
    WEDI 運費查詢工具
    繼承 BaseScraper 實作運費(月結)結帳資料查詢
    """
    
    def __init__(self, username, password, headless=False, download_base_dir="downloads", start_month=None, end_month=None):
        # 調用父類構造函數
        super().__init__(username, password, headless, download_base_dir)
        
        # 子類特有的屬性
        self.start_month = start_month
        self.end_month = end_month
        
        # 轉換月份為日期格式供日期操作使用
        self.start_date = None
        self.end_date = None
        
        if start_month:
            try:
                year = int(start_month[:4])
                month = int(start_month[4:])
                self.start_date = datetime(year, month, 1)
            except (ValueError, IndexError):
                safe_print(f"❌ 月份格式錯誤: {start_month}")

        if end_month:
            try:
                year = int(end_month[:4])
                month = int(end_month[4:])
                # 計算該月最後一天
                if month == 12:
                    next_year = year + 1
                    next_month = 1
                else:
                    next_year = year
                    next_month = month + 1
                last_day = datetime(next_year, next_month, 1) - timedelta(days=1)
                self.end_date = last_day
            except (ValueError, IndexError):
                safe_print(f"❌ 月份格式錯誤: {end_month}")

    def get_default_date_range(self):
        """獲取預設月份範圍：上個月"""
        today = datetime.now()

        # 計算上個月
        if today.month == 1:
            prev_month = 12
            prev_year = today.year - 1
        else:
            prev_month = today.month - 1
            prev_year = today.year

        prev_month_str = f"{prev_year:04d}{prev_month:02d}"

        # 預設開始和結束月份都是上個月
        return prev_month_str, prev_month_str

    def navigate_to_freight_page(self):
        """導航到運費查詢頁面 (2-7)運費(月結)結帳資料查詢"""
        safe_print("🧭 導航至運費查詢頁面...")

        try:
            # 等待主選單載入
            time.sleep(3)

            # 切換到datamain iframe（與wedi_selenium_scraper.py相同的邏輯）
            try:
                iframe = self.wait.until(
                    EC.presence_of_element_located((By.NAME, "datamain"))
                )
                self.driver.switch_to.frame(iframe)
                safe_print("✅ 已切換到 datamain iframe")
            except Exception as e:
                safe_print(f"❌ 無法切換到 datamain iframe: {e}")
                return False

            # 查找運費相關選項
            time.sleep(2)

            # 搜尋所有連結，找出運費相關項目
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            print(f"   找到 {len(all_links)} 個連結")

            freight_link = None
            for i, link in enumerate(all_links):
                try:
                    link_text = link.text.strip()
                    if link_text:
                        # 檢查運費(月結)結帳資料查詢相關關鍵字
                        if (("運費" in link_text and "月結" in link_text) or
                            ("2-7" in link_text and "運費" in link_text) or
                            ("結帳資料" in link_text and "運費" in link_text)):
                            freight_link = link
                            safe_print(f"   ✅ 找到運費查詢連結: {link_text}")
                            break
                        elif "運費" in link_text:
                            safe_print(f"   🔍 找到運費相關連結: {link_text}")
                except:
                    continue

            if freight_link:
                # 使用JavaScript點擊避免元素遮蔽問題
                self.driver.execute_script("arguments[0].click();", freight_link)
                time.sleep(3)
                safe_print("✅ 已點擊運費查詢連結")
                return True
            else:
                safe_print("❌ 未找到運費查詢連結")
                # 嘗試驗證頁面是否包含運費功能
                page_text = self.driver.page_source
                if "運費" in page_text and ("月結" in page_text or "結帳" in page_text):
                    safe_print("✅ 頁面包含運費查詢功能，繼續流程")
                    return True
                else:
                    safe_print("❌ 頁面不包含運費查詢功能")
                    return False

        except Exception as e:
            safe_print(f"❌ 導航到運費查詢頁面失敗: {e}")
            return False

    def set_date_range(self):
        """設定查詢月份範圍 - 基於wedi_selenium_scraper.py的邏輯但適配月份"""
        safe_print("📅 設定月份範圍...")

        # 使用指定的月份範圍，如果沒有指定則使用預設值
        if self.start_month and self.end_month:
            start_month = self.start_month
            end_month = self.end_month
        else:
            # 使用預設值（上個月）
            start_month_str, end_month_str = self.get_default_date_range()
            start_month = start_month_str
            end_month = end_month_str

        safe_print(f"📅 查詢月份範圍: {start_month} ~ {end_month}")

        try:
            # 已經在iframe中，嘗試尋找月份輸入框
            date_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')

            if len(date_inputs) >= 2:
                try:
                    # 填入開始月份
                    date_inputs[0].clear()
                    date_inputs[0].send_keys(start_month)
                    safe_print(f"✅ 已設定開始月份: {start_month}")

                    # 填入結束月份
                    date_inputs[1].clear()
                    date_inputs[1].send_keys(end_month)
                    safe_print(f"✅ 已設定結束月份: {end_month}")
                except Exception as date_error:
                    safe_print(f"⚠️ 填入月份失敗: {date_error}")

                # 嘗試點擊查詢按鈕（與wedi_selenium_scraper.py相同的邏輯）
                query_button_found = False
                button_selectors = [
                    'input[value*="查詢"]',
                    'button[title*="查詢"]',
                    'input[type="submit"]',
                    'button[type="submit"]',
                    'input[value*="搜尋"]'
                ]

                for selector in button_selectors:
                    try:
                        query_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        query_button.click()
                        safe_print(f"✅ 已點擊查詢按鈕")
                        time.sleep(2)
                        query_button_found = True
                        break
                    except:
                        continue

                if not query_button_found:
                    safe_print("⚠️ 未找到查詢按鈕，直接繼續流程")
            else:
                safe_print("⚠️ 未找到月份輸入框，可能不需要設定月份")

            return True

        except Exception as e:
            safe_print(f"⚠️ 月份範圍設定過程中出現問題，但繼續執行: {e}")
            return True  # 即使失敗也返回True，讓流程繼續

    def get_freight_records(self):
        """搜尋運費相關數據 - 基於wedi_selenium_scraper.py的邏輯但適配運費"""
        safe_print("📊 搜尋運費數據...")

        records = []
        try:
            # 此時已經在datamain iframe中，直接搜尋數據
            safe_print("🔍 分析當前頁面內容...")

            # 搜尋所有連結，找出運費相關項目
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            print(f"   找到 {len(all_links)} 個連結")

            # 定義運費相關關鍵字
            freight_keywords = [
                "運費", "月結", "結帳", "(2-7)"
            ]

            # 定義排除關鍵字
            excluded_keywords = [
                "語音取件", "三節加價", "系統公告", "操作說明", "維護通知",
                "Home", "首頁", "登出", "系統設定"
            ]

            for i, link in enumerate(all_links):
                try:
                    link_text = link.text.strip()
                    if link_text:
                        # 檢查是否需要排除
                        should_exclude = any(keyword in link_text for keyword in excluded_keywords)

                        # 匹配運費相關項目
                        is_freight_record = (("運費" in link_text and "月結" in link_text) or
                                           ("結帳資料" in link_text and "運費" in link_text) or
                                           "(2-7)" in link_text)

                        if is_freight_record and not should_exclude:
                            # 生成檔案ID
                            file_id = link_text.replace(" ", "_").replace("[", "").replace("]", "").replace("-", "_")
                            records.append({
                                "index": i + 1,
                                "title": link_text,
                                "record_id": file_id,
                                "link": link
                            })
                            safe_print(f"   ✅ 找到運費記錄: {link_text}")
                        elif should_exclude:
                            safe_print(f"   ⏭️ 跳過排除項目: {link_text}")
                        elif "運費" in link_text:
                            safe_print(f"   ⏭️ 跳過非目標運費項目: {link_text}")
                except:
                    continue

            # 如果沒有找到任何運費連結，嘗試搜尋表格數據
            if not records:
                safe_print("🔍 未找到運費連結，搜尋表格數據...")
                tables = self.driver.find_elements(By.TAG_NAME, "table")

                for table in tables:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    for row in rows:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        for cell in cells:
                            cell_text = cell.text.strip()
                            if any(keyword in cell_text for keyword in freight_keywords):
                                safe_print(f"   📋 找到表格中的運費數據: {cell_text}")

            safe_print(f"📊 總共找到 {len(records)} 筆運費相關記錄")
            return records

        except Exception as e:
            safe_print(f"❌ 搜尋運費數據失敗: {e}")
            return records

    def download_excel_for_record(self, record):
        """為特定運費記錄下載Excel檔案 - 簡化版本（沒有複雜的多視窗邏輯）"""
        safe_print(f"📥 下載記錄 {record['record_id']} 的Excel檔案...")

        try:
            # 點擊記錄連結
            found_link = record['link']
            if found_link:
                # 使用JavaScript點擊避免元素遮蔽問題
                self.driver.execute_script("arguments[0].click();", found_link)
                time.sleep(5)
            else:
                raise Exception(f"找不到連結")

            downloaded_files = []
            record_id = record['record_id']

            # 在詳細頁面填入查詢月份
            safe_print("📅 在詳細頁面填入查詢月份...")
            try:
                # 使用指定的月份範圍
                if self.start_month and self.end_month:
                    start_month = self.start_month
                    end_month = self.end_month
                else:
                    # 預設值（上個月）
                    start_month_str, end_month_str = self.get_default_date_range()
                    start_month = start_month_str
                    end_month = end_month_str

                # 找到月份輸入框
                date_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
                if len(date_inputs) >= 2:
                    # 填入開始月份
                    date_inputs[0].clear()
                    date_inputs[0].send_keys(start_month)
                    safe_print(f"✅ 已填入開始月份: {start_month}")

                    # 填入結束月份
                    date_inputs[1].clear()
                    date_inputs[1].send_keys(end_month)
                    safe_print(f"✅ 已填入結束月份: {end_month}")
                elif len(date_inputs) >= 1:
                    # 只有一個月份輸入框，填入查詢月份
                    date_inputs[0].clear()
                    date_inputs[0].send_keys(start_month)
                    safe_print(f"✅ 已填入查詢月份: {start_month}")

                # 點擊查詢按鈕
                try:
                    query_button = self.driver.find_element(By.CSS_SELECTOR, 'input[value*="查詢"]')
                    query_button.click()
                    safe_print("✅ 已點擊查詢按鈕")
                    time.sleep(5)
                except:
                    safe_print("⚠️ 未找到查詢按鈕，跳過此步驟")

            except Exception as date_e:
                safe_print(f"⚠️ 填入查詢月份失敗: {date_e}")

            # 尋找並點擊匯出xlsx按鈕（與wedi_selenium_scraper.py相同的邏輯）
            try:
                xlsx_selectors = [
                    "//button[contains(text(), '匯出xlsx')]",
                    "//input[@value*='匯出xlsx']",
                    "//a[contains(text(), '匯出xlsx')]",
                    "//button[contains(text(), 'Excel')]",
                    "//input[@value*='Excel']",
                    "//form//input[@type='submit'][contains(@value, '匯出')]"
                ]

                xlsx_button = None
                for selector in xlsx_selectors:
                    try:
                        xlsx_button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        break
                    except:
                        continue

                if xlsx_button:
                    # 獲取下載前的檔案列表
                    before_files = set(self.download_dir.glob("*"))

                    # 使用JavaScript點擊避免元素遮蔽問題
                    self.driver.execute_script("arguments[0].click();", xlsx_button)
                    safe_print(f"✅ 已點擊匯出xlsx按鈕")
                    time.sleep(5)

                    # 獲取新下載的檔案
                    after_files = set(self.download_dir.glob("*"))
                    new_files = after_files - before_files

                    # 重命名新下載的檔案
                    for new_file in new_files:
                        if new_file.suffix.lower() in ['.xlsx', '.xls']:
                            new_name = f"{self.username}_{record_id}{new_file.suffix}"
                            new_path = self.download_dir / new_name
                            
                            # 如果目標檔案已存在，直接覆蓋
                            if new_path.exists():
                                new_path.unlink()
                            
                            new_file.rename(new_path)
                            downloaded_files.append(str(new_path))
                            safe_print(f"✅ 已重命名為: {new_name}")
                else:
                    raise Exception("找不到xlsx匯出按鈕")

            except Exception as e:
                safe_print(f"⚠️ xlsx下載失敗: {e}")

            return downloaded_files

        except Exception as e:
            safe_print(f"❌ 下載記錄失敗: {e}")
            return []

    def run_full_process(self):
        """執行完整的自動化流程"""
        success = False
        all_downloads = []
        records = []

        try:
            print("=" * 60)
            safe_print(f"🚛 開始執行 WEDI 運費查詢流程 (帳號: {self.username})")
            print("=" * 60)

            # 1. 初始化瀏覽器
            self.init_browser()

            # 2. 登入
            login_success = self.login()
            if not login_success:
                safe_print(f"❌ 帳號 {self.username} 登入失敗")
                return {"success": False, "username": self.username, "error": "登入失敗", "downloads": [], "records": []}

            # 3. 導航到查詢頁面（基礎導航）
            nav_success = self.navigate_to_query()
            if not nav_success:
                safe_print(f"❌ 帳號 {self.username} 基礎導航失敗")
                return {"success": False, "username": self.username, "error": "導航失敗", "downloads": [], "records": []}

            # 4. 導航到運費查詢頁面
            freight_nav_success = self.navigate_to_freight_page()
            if not freight_nav_success:
                safe_print(f"❌ 帳號 {self.username} 運費頁面導航失敗")
                return {"success": False, "username": self.username, "error": "運費頁面導航失敗", "downloads": [], "records": []}

            # 5. 設定月份範圍
            self.set_date_range()

            # 6. 獲取運費記錄
            records = self.get_freight_records()

            if not records:
                safe_print(f"⚠️ 帳號 {self.username} 沒有找到運費記錄")
                return {"success": True, "username": self.username, "message": "無資料可下載", "downloads": [], "records": []}

            # 7. 下載每個記錄的Excel檔案
            for record in records:
                try:
                    downloads = self.download_excel_for_record(record)
                    all_downloads.extend(downloads)
                except Exception as download_e:
                    safe_print(f"⚠️ 帳號 {self.username} 下載記錄 {record.get('record_id', 'unknown')} 失敗: {download_e}")
                    continue

            safe_print(f"🎉 帳號 {self.username} 自動化流程完成！")
            success = True

            return {"success": True, "username": self.username, "downloads": all_downloads, "records": records}

        except Exception as e:
            safe_print(f"💥 帳號 {self.username} 流程執行失敗: {e}")
            return {"success": False, "username": self.username, "error": str(e), "downloads": all_downloads, "records": records}
        finally:
            self.close()


def main():
    """主程式入口"""
    parser = argparse.ArgumentParser(description='WEDI 運費查詢自動下載工具')
    parser.add_argument('--headless', action='store_true', help='使用無頭模式')
    parser.add_argument('--start-month', type=str, help='開始月份 (格式: YYYYMM，例如: 202411)')
    parser.add_argument('--end-month', type=str, help='結束月份 (格式: YYYYMM，例如: 202412)')

    args = parser.parse_args()

    # 月份參數驗證和處理
    start_month = None
    end_month = None

    if args.start_month:
        try:
            # 驗證月份格式
            year = int(args.start_month[:4])
            month = int(args.start_month[4:6])
            if not (1 <= month <= 12):
                raise ValueError("月份必須在01-12之間")
            start_month = args.start_month
        except (ValueError, IndexError) as e:
            print(f"⛔ 開始月份格式錯誤: {e}")
            print("💡 月份格式應為 YYYYMM，例如: 202411")
            return 1

    if args.end_month:
        try:
            # 驗證月份格式
            year = int(args.end_month[:4])
            month = int(args.end_month[4:6])
            if not (1 <= month <= 12):
                raise ValueError("月份必須在01-12之間")
            end_month = args.end_month
        except (ValueError, IndexError) as e:
            print(f"⛔ 結束月份格式錯誤: {e}")
            print("💡 月份格式應為 YYYYMM，例如: 202412")
            return 1

    # 如果沒有指定月份，使用預設值
    if not start_month:
        today = datetime.now()
        if today.month == 1:
            prev_month = 12
            prev_year = today.year - 1
        else:
            prev_month = today.month - 1
            prev_year = today.year
        
        start_month = f"{prev_year:04d}{prev_month:02d}"
        end_month = start_month  # 預設查詢單一月份
        
        safe_print(f"📅 查詢月份範圍: {start_month} ~ {end_month} (預設上個月)")
    elif not end_month:
        end_month = start_month  # 如果只指定開始月份，結束月份使用相同值
        safe_print(f"📅 查詢月份範圍: {start_month} ~ {end_month}")
    else:
        safe_print(f"📅 查詢月份範圍: {start_month} ~ {end_month}")

    try:
        # 使用多帳號管理器
        safe_print("🚛 WEDI 運費查詢自動下載工具")

        manager = MultiAccountManager("accounts.json")
        manager.run_all_accounts(
            scraper_class=FreightScraper,
            headless_override=args.headless if args.headless else None,
            start_month=start_month,
            end_month=end_month
        )

        return 0

    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"⛔ 錯誤: {e}")
        return 1
    except KeyboardInterrupt:
        print("\\n⛔ 使用者中斷執行")
        return 1
    except Exception as e:
        print(f"⛔ 未知錯誤: {e}")
        return 1


if __name__ == "__main__":
    main()