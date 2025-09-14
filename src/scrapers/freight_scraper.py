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
import requests
import json
import openpyxl
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
            # 已經在 datamain iframe 中（由 BaseScraper.navigate_to_query() 切換），直接進行操作
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

            # 先搜尋表格中的發票數據（運費查詢結果為表格格式）
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            safe_print(f"   找到 {len(tables)} 個表格")

            for table_index, table in enumerate(tables):
                try:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    safe_print(f"   表格 {table_index + 1} 有 {len(rows)} 行")
                    
                    # 詳細分析每一行的內容
                    for row_index, row in enumerate(rows):
                        try:
                            cells = row.find_elements(By.TAG_NAME, "td")
                            th_cells = row.find_elements(By.TAG_NAME, "th")
                            total_cells = len(cells) + len(th_cells)
                            
                            if total_cells > 0:
                                safe_print(f"   行 {row_index + 1}: {len(cells)} 個 td, {len(th_cells)} 個 th")
                                
                                # 檢查每個欄位的內容
                                all_cells = cells if cells else th_cells
                                for cell_index, cell in enumerate(all_cells):
                                    cell_text = cell.text.strip()
                                    if cell_text:
                                        safe_print(f"     欄位 {cell_index + 1}: '{cell_text}'")
                                        
                                        # 檢查這個欄位是否包含發票號碼（英數字組合，長度 > 8）
                                        if (len(cell_text) > 8 and 
                                            any(c.isdigit() for c in cell_text) and 
                                            any(c.isalpha() for c in cell_text) and
                                            cell_text not in ["發票號碼", "小計", "總計"]):
                                            
                                            safe_print(f"     🔍 可能的發票號碼: '{cell_text}'")
                                            
                                            # 檢查是否有可點擊的連結
                                            invoice_link = None
                                            try:
                                                # 嘗試在該欄位中尋找連結
                                                invoice_link = cell.find_element(By.TAG_NAME, "a")
                                                safe_print(f"     ✅ 在欄位中找到連結")
                                            except:
                                                # 如果該欄位沒有連結，嘗試整行是否可點擊
                                                try:
                                                    invoice_link = row.find_element(By.TAG_NAME, "a")
                                                    safe_print(f"     ✅ 在整行中找到連結")
                                                except:
                                                    # 如果沒有連結，使用整個 cell 作為點擊目標
                                                    invoice_link = cell
                                                    safe_print(f"     ⚠️ 沒有連結，使用欄位本身")

                                            if invoice_link:
                                                # 嘗試獲取發票日期（通常在前一個或後一個欄位）
                                                invoice_date = ""
                                                try:
                                                    # 檢查前後欄位是否有日期格式（8位數字）
                                                    for check_index in [cell_index - 1, cell_index + 1]:
                                                        if 0 <= check_index < len(all_cells):
                                                            check_text = all_cells[check_index].text.strip()
                                                            if len(check_text) == 8 and check_text.isdigit():
                                                                invoice_date = check_text
                                                                break
                                                except:
                                                    pass
                                                
                                                records.append({
                                                    "index": len(records) + 1,
                                                    "title": f"發票號碼: {cell_text}",
                                                    "invoice_no": cell_text,
                                                    "invoice_date": invoice_date,
                                                    "record_id": f"{invoice_date}_{cell_text}" if invoice_date else cell_text,
                                                    "link": invoice_link
                                                })
                                                safe_print(f"   ✅ 找到發票記錄: {cell_text} (日期: {invoice_date})")
                                                
                        except Exception as row_e:
                            safe_print(f"   ⚠️ 處理行 {row_index + 1} 時出錯: {row_e}")
                            continue
                            
                except Exception as table_e:
                    safe_print(f"   ⚠️ 處理表格 {table_index + 1} 時出錯: {table_e}")
                    continue

            # 如果表格中沒有找到發票數據，嘗試搜尋連結
            if not records:
                safe_print("🔍 表格中未找到發票數據，搜尋連結...")
                all_links = self.driver.find_elements(By.TAG_NAME, "a")
                safe_print(f"   找到 {len(all_links)} 個連結")

                # 定義運費相關關鍵字
                freight_keywords = ["運費", "月結", "結帳", "(2-7)", "發票"]

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

                            # 匹配運費相關項目或發票號碼格式
                            is_freight_record = (("運費" in link_text and "月結" in link_text) or
                                               ("結帳資料" in link_text and "運費" in link_text) or
                                               "(2-7)" in link_text or
                                               (len(link_text) > 8 and any(c.isdigit() for c in link_text) and any(c.isalpha() for c in link_text)))

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
                    except:
                        continue

            safe_print(f"📊 總共找到 {len(records)} 筆運費相關記錄")
            return records

        except Exception as e:
            safe_print(f"❌ 搜尋運費數據失敗: {e}")
            return records

    def download_excel_for_record(self, record):
        """為特定運費記錄下載Excel檔案 - 修正stale element問題"""
        safe_print(f"📥 下載記錄 {record['record_id']} 的Excel檔案...")

        try:
            # 重新搜尋發票連結（避免 stale element reference）
            invoice_no = record['invoice_no']
            safe_print(f"🔍 重新搜尋發票號碼 {invoice_no} 的連結...")
            
            found_link = None
            # 方法1：直接用發票號碼搜尋連結
            try:
                found_link = self.driver.find_element(By.XPATH, f"//a[contains(text(), '{invoice_no}')]")
                safe_print("✅ 通過文字內容找到連結")
            except:
                # 方法2：通過 href 屬性搜尋
                try:
                    found_link = self.driver.find_element(By.XPATH, f"//a[contains(@href, '{invoice_no}')]")
                    safe_print("✅ 通過href屬性找到連結")
                except:
                    # 方法3：重新搜尋表格中的連結
                    try:
                        tables = self.driver.find_elements(By.TAG_NAME, "table")
                        for table in tables:
                            links = table.find_elements(By.TAG_NAME, "a")
                            for link in links:
                                if invoice_no in link.text:
                                    found_link = link
                                    safe_print("✅ 在表格中重新找到連結")
                                    break
                            if found_link:
                                break
                    except Exception as e:
                        safe_print(f"⚠️ 重新搜尋連結失敗: {e}")

            if found_link:
                # 使用JavaScript點擊避免元素遮蔽問題
                self.driver.execute_script("arguments[0].click();", found_link)
                safe_print(f"✅ 已點擊發票號碼 {invoice_no} 的連結")
                time.sleep(5)
            else:
                raise Exception(f"重新搜尋後仍找不到發票號碼 {invoice_no} 的連結")

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

            # 直接從頁面提取 data-fileblob 數據並生成 Excel
            try:
                safe_print("🚀 嘗試從頁面提取 data-fileblob 數據...")
                
                # 尋找包含 data-fileblob 屬性的按鈕
                fileblob_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[data-fileblob]")
                
                if not fileblob_buttons:
                    # 如果找不到，嘗試其他可能的選擇器
                    fileblob_buttons = self.driver.find_elements(By.XPATH, "//*[@data-fileblob]")
                
                if fileblob_buttons:
                    safe_print(f"✅ 找到 {len(fileblob_buttons)} 個包含 data-fileblob 的元素")
                    
                    # 通常第一個就是我們要的匯出按鈕
                    fileblob_button = fileblob_buttons[0]
                    fileblob_data = fileblob_button.get_attribute("data-fileblob")
                    
                    if fileblob_data:
                        safe_print("✅ 成功獲取 data-fileblob 數據")
                        
                        try:
                            # 解析 JSON 數據
                            blob_json = json.loads(fileblob_data)
                            data_array = blob_json.get("data", [])
                            filename_base = blob_json.get("fileName", "Excel")
                            mime_type = blob_json.get("mimeType", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                            file_extension = blob_json.get("fileExtension", ".xlsx")
                            
                            safe_print(f"📊 數據信息:")
                            safe_print(f"   檔名: {filename_base}{file_extension}")
                            safe_print(f"   MIME類型: {mime_type}")
                            safe_print(f"   數據行數: {len(data_array)}")
                            
                            if data_array:
                                # 使用 openpyxl 創建 Excel 檔案
                                wb = openpyxl.Workbook()
                                ws = wb.active
                                ws.title = "運費明細"
                                
                                # 將數據寫入工作表
                                for row_index, row_data in enumerate(data_array, 1):
                                    for col_index, cell_value in enumerate(row_data, 1):
                                        # 清理數據（移除HTML空格等）
                                        if isinstance(cell_value, str):
                                            cell_value = cell_value.replace("&nbsp;", "").strip()
                                        
                                        ws.cell(row=row_index, column=col_index, value=cell_value)
                                
                                # 設定表頭樣式
                                if len(data_array) > 0:
                                    from openpyxl.styles import Font, PatternFill, Border, Side
                                    
                                    # 表頭加粗
                                    for col_index in range(1, len(data_array[0]) + 1):
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
                                
                                # 生成檔案名稱
                                invoice_no = record.get('invoice_no', record_id)
                                invoice_date = record.get('invoice_date', '')
                                if invoice_date:
                                    filename = f"{self.username}_{invoice_date}_{invoice_no}.xlsx"
                                else:
                                    filename = f"{self.username}_{invoice_no}.xlsx"
                                
                                # 保存檔案
                                file_path = self.download_dir / filename
                                wb.save(file_path)
                                wb.close()
                                
                                downloaded_files = [str(file_path)]
                                safe_print(f"✅ 成功從 data-fileblob 生成 Excel: {filename}")
                                safe_print(f"📁 檔案大小: {file_path.stat().st_size:,} bytes")
                                safe_print(f"📋 數據行數: {len(data_array)} 行，欄數: {len(data_array[0]) if data_array else 0} 欄")
                                
                                return downloaded_files
                            
                            else:
                                safe_print("❌ data-fileblob 中沒有找到數據陣列")
                                
                        except json.JSONDecodeError as json_e:
                            safe_print(f"❌ 解析 data-fileblob JSON 失敗: {json_e}")
                            safe_print(f"   原始數據前500字元: {fileblob_data[:500]}")
                        
                        except Exception as excel_e:
                            safe_print(f"❌ 生成 Excel 檔案失敗: {excel_e}")
                    
                    else:
                        safe_print("❌ data-fileblob 屬性為空")
                        
                else:
                    safe_print("⚠️ 未找到包含 data-fileblob 的元素")
                    raise Exception("未找到 data-fileblob 元素")
                    
            except Exception as blob_e:
                safe_print(f"❌ data-fileblob 提取失敗: {blob_e}")
                safe_print("🔄 程式無法提取數據，請檢查頁面是否正確載入")
                return []

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