#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WEDI 運費未請款明細下載工具
使用基礎類別實作運費未請款明細查詢功能
直接抓取HTML表格並轉換為Excel檔案
"""

import sys
import os
import time
import re
import argparse
import json
import openpyxl
from datetime import datetime, timedelta
from pathlib import Path
from bs4 import BeautifulSoup

# 使用共用的模組和基礎類別
from src.utils.windows_encoding_utils import safe_print, check_pythonunbuffered
from src.core.base_scraper import BaseScraper
from src.core.multi_account_manager import MultiAccountManager

# 檢查 PYTHONUNBUFFERED 環境變數
check_pythonunbuffered()

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class UnpaidScraper(BaseScraper):
    """
    WEDI 運費未請款明細下載工具
    繼承 BaseScraper 實作運費未請款明細查詢
    """

    def __init__(self, username, password, headless=False, download_base_dir="downloads"):
        # 調用父類構造函數
        super().__init__(username, password, headless, download_base_dir)

        # 設定結束時間為當日
        self.end_date = datetime.now().strftime("%Y%m%d")

    def navigate_to_unpaid_freight_page(self):
        """導航到運費未請款明細頁面"""
        safe_print("🧭 導航至運費未請款明細頁面...")

        try:
            # 已經在 datamain iframe 中（由 BaseScraper.navigate_to_query() 切換），直接進行操作
            time.sleep(2)

            # 搜尋所有連結，找出運費未請款相關項目
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            print(f"   找到 {len(all_links)} 個連結")

            unpaid_freight_link = None
            for i, link in enumerate(all_links):
                try:
                    link_text = link.text.strip()
                    if link_text:
                        # 檢查運費未請款明細相關關鍵字
                        if (("運費" in link_text and "未請款" in link_text) or
                            ("未請款" in link_text and "明細" in link_text) or
                            ("運費" in link_text and "明細" in link_text and "請款" in link_text)):
                            unpaid_freight_link = link
                            safe_print(f"   ✅ 找到運費未請款明細連結: {link_text}")
                            break
                        elif "運費" in link_text and "明細" in link_text:
                            safe_print(f"   🔍 找到運費相關連結: {link_text}")
                except:
                    continue

            if unpaid_freight_link:
                # 使用JavaScript點擊避免元素遮蔽問題
                self.driver.execute_script("arguments[0].click();", unpaid_freight_link)
                time.sleep(3)
                safe_print("✅ 已點擊運費未請款明細連結")
                return True
            else:
                safe_print("❌ 未找到運費未請款明細連結")
                # 嘗試驗證頁面是否包含運費未請款功能
                page_text = self.driver.page_source
                if "運費" in page_text and ("未請款" in page_text or "明細" in page_text):
                    safe_print("✅ 頁面包含運費未請款功能，繼續流程")
                    return True
                else:
                    safe_print("❌ 頁面不包含運費未請款功能")
                    return False

        except Exception as e:
            safe_print(f"❌ 導航到運費未請款明細頁面失敗: {e}")
            return False

    def set_end_date(self):
        """設定結束時間為當日 - 不需要使用者輸入"""
        safe_print("📅 設定結束時間為當日...")

        safe_print(f"📅 結束時間: {self.end_date}")

        try:
            # 已經在iframe中，嘗試尋找日期輸入框
            date_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')

            if len(date_inputs) >= 1:
                try:
                    # 填入結束時間（當日）
                    # 通常運費未請款明細只需要一個結束時間
                    date_inputs[-1].clear()  # 使用最後一個輸入框作為結束時間
                    date_inputs[-1].send_keys(self.end_date)
                    safe_print(f"✅ 已設定結束時間: {self.end_date}")
                except Exception as date_error:
                    safe_print(f"⚠️ 填入結束時間失敗: {date_error}")

                # 嘗試點擊查詢按鈕
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
                        time.sleep(3)
                        query_button_found = True
                        break
                    except:
                        continue

                if not query_button_found:
                    safe_print("⚠️ 未找到查詢按鈕，直接繼續流程")
            else:
                safe_print("⚠️ 未找到日期輸入框，可能不需要設定日期")

            return True

        except Exception as e:
            safe_print(f"⚠️ 結束時間設定過程中出現問題，但繼續執行: {e}")
            return True  # 即使失敗也返回True，讓流程繼續

    def extract_table_data_to_excel(self):
        """直接從HTML表格提取數據並轉換為Excel檔案"""
        safe_print("📊 提取表格數據並轉換為Excel...")

        try:
            # 等待頁面完全載入
            time.sleep(3)

            # 獲取頁面HTML
            page_html = self.driver.page_source
            soup = BeautifulSoup(page_html, 'html.parser')

            # 尋找包含數據的表格
            tables = soup.find_all('table')
            safe_print(f"   找到 {len(tables)} 個表格")

            main_table = None
            max_rows = 0

            # 找到最大的表格（通常是包含數據的主表格）
            for table in tables:
                rows = table.find_all('tr')
                if len(rows) > max_rows:
                    max_rows = len(rows)
                    main_table = table

            if not main_table or max_rows < 2:  # 至少要有表頭和一行數據
                safe_print("❌ 未找到包含數據的表格")
                return None

            safe_print(f"✅ 找到主要數據表格，共 {max_rows} 行")

            # 提取表格數據
            table_data = []
            rows = main_table.find_all('tr')

            for row_index, row in enumerate(rows):
                row_data = []
                cells = row.find_all(['td', 'th'])

                for cell in cells:
                    # 清理單元格內容
                    cell_text = cell.get_text(strip=True)
                    # 移除HTML實體和多餘空白
                    cell_text = cell_text.replace('\u00a0', ' ').replace('\xa0', ' ')
                    cell_text = re.sub(r'\s+', ' ', cell_text).strip()
                    row_data.append(cell_text)

                if row_data:  # 只添加非空行
                    table_data.append(row_data)
                    if row_index < 5:  # 只顯示前5行的內容用於調試
                        safe_print(f"   行 {row_index + 1}: {row_data[:5]}...")  # 只顯示前5個欄位

            if not table_data:
                safe_print("❌ 表格中沒有找到數據")
                return None

            safe_print(f"✅ 成功提取 {len(table_data)} 行數據")

            # 創建Excel檔案
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "運費未請款明細"

            # 將數據寫入工作表
            for row_index, row_data in enumerate(table_data, 1):
                for col_index, cell_value in enumerate(row_data, 1):
                    ws.cell(row=row_index, column=col_index, value=cell_value)

            # 設定表頭樣式（如果有表頭）
            if len(table_data) > 0:
                from openpyxl.styles import Font, PatternFill

                # 第一行設為表頭樣式
                for col_index in range(1, len(table_data[0]) + 1):
                    cell = ws.cell(row=1, column=col_index)
                    cell.font = Font(bold=True)
                    cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")

            # 自動調整欄寬
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)  # 最大寬度限制
                ws.column_dimensions[column_letter].width = adjusted_width

            # 生成檔案名稱：{帳號}_FREIGHT_{結束時間}.xlsx
            filename = f"{self.username}_FREIGHT_{self.end_date}.xlsx"
            file_path = self.download_dir / filename

            # 保存檔案
            wb.save(file_path)
            wb.close()

            safe_print(f"✅ 成功生成運費未請款明細Excel: {filename}")
            safe_print(f"📁 檔案大小: {file_path.stat().st_size:,} bytes")
            safe_print(f"📋 數據行數: {len(table_data)} 行，欄數: {len(table_data[0]) if table_data else 0} 欄")

            return str(file_path)

        except Exception as e:
            safe_print(f"❌ 提取表格數據失敗: {e}")
            return None

    def run_full_process(self):
        """執行完整的自動化流程"""
        success = False
        all_downloads = []

        try:
            print("=" * 60)
            safe_print(f"📊 開始執行 WEDI 運費未請款明細下載流程 (帳號: {self.username})")
            print("=" * 60)

            # 1. 初始化瀏覽器
            self.init_browser()

            # 2. 登入
            login_success = self.login()
            if not login_success:
                safe_print(f"❌ 帳號 {self.username} 登入失敗")
                return {"success": False, "username": self.username, "error": "登入失敗", "downloads": []}

            # 3. 導航到查詢頁面（基礎導航）
            nav_success = self.navigate_to_query()
            if not nav_success:
                safe_print(f"❌ 帳號 {self.username} 基礎導航失敗")
                return {"success": False, "username": self.username, "error": "導航失敗", "downloads": []}

            # 4. 導航到運費未請款明細頁面
            unpaid_nav_success = self.navigate_to_unpaid_freight_page()
            if not unpaid_nav_success:
                safe_print(f"❌ 帳號 {self.username} 運費未請款明細頁面導航失敗")
                return {"success": False, "username": self.username, "error": "運費未請款明細頁面導航失敗", "downloads": []}

            # 5. 設定結束時間（當日）
            self.set_end_date()

            # 6. 直接提取表格數據並轉換為Excel
            excel_file = self.extract_table_data_to_excel()

            if excel_file:
                all_downloads.append(excel_file)
                safe_print(f"🎉 帳號 {self.username} 運費未請款明細下載完成！")
                success = True
            else:
                safe_print(f"⚠️ 帳號 {self.username} 沒有找到可下載的數據")
                return {"success": True, "username": self.username, "message": "無資料可下載", "downloads": []}

            return {"success": True, "username": self.username, "downloads": all_downloads}

        except Exception as e:
            safe_print(f"💥 帳號 {self.username} 流程執行失敗: {e}")
            return {"success": False, "username": self.username, "error": str(e), "downloads": all_downloads}
        finally:
            self.close()


def main():
    """主程式入口"""
    parser = argparse.ArgumentParser(description='WEDI 運費未請款明細下載工具')
    parser.add_argument('--headless', action='store_true', help='使用無頭模式')

    args = parser.parse_args()

    # 顯示結束時間（當日）
    end_date = datetime.now().strftime("%Y%m%d")
    safe_print(f"📅 結束時間: {end_date} (當日)")

    try:
        # 使用多帳號管理器
        safe_print("📊 WEDI 運費未請款明細下載工具")

        manager = MultiAccountManager("accounts.json")
        manager.run_all_accounts(
            scraper_class=UnpaidScraper,
            headless_override=args.headless if args.headless else None
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