#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代收貨款查詢工具
使用基礎類別實作代收貨款匯款明細查詢功能
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

# 使用共用的模組和基礎類別
from src.utils.windows_encoding_utils import safe_print, check_pythonunbuffered
from src.core.base_scraper import BaseScraper
from src.core.multi_account_manager import MultiAccountManager

# 檢查 PYTHONUNBUFFERED 環境變數
check_pythonunbuffered()

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class PaymentScraper(BaseScraper):
    """
    代收貨款查詢工具
    繼承 BaseScraper 實作代收貨款匯款明細查詢
    """

    def __init__(self, username, password, headless=False, download_base_dir="downloads", start_date=None, end_date=None):
        # 調用父類構造函數
        super().__init__(username, password, headless, download_base_dir)

        # 子類特有的屬性
        self.start_date = start_date
        self.end_date = end_date

    def set_date_range(self):
        """設定查詢日期範圍 - 使用wedi_selenium_scraper.py的邏輯"""
        safe_print("📅 設定日期範圍...")

        # 使用指定的日期範圍，如果沒有指定則使用預設值（當日）
        if self.start_date and self.end_date:
            start_date = self.start_date.strftime("%Y%m%d")
            end_date = self.end_date.strftime("%Y%m%d")
        else:
            # 預設值：當日
            today = datetime.now()
            start_date = today.strftime("%Y%m%d")
            end_date = today.strftime("%Y%m%d")

        safe_print(f"📅 查詢日期範圍: {start_date} ~ {end_date}")

        try:
            # 已經在iframe中，嘗試尋找日期輸入框
            date_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')

            if len(date_inputs) >= 2:
                try:
                    # 填入開始日期
                    date_inputs[0].clear()
                    date_inputs[0].send_keys(start_date)
                    safe_print(f"✅ 已設定開始日期: {start_date}")

                    # 填入結束日期
                    date_inputs[1].clear()
                    date_inputs[1].send_keys(end_date)
                    safe_print(f"✅ 已設定結束日期: {end_date}")
                except Exception as date_error:
                    safe_print(f"⚠️ 填入日期失敗: {date_error}")

                # 嘗試多種方式尋找查詢按鈕
                query_button_found = False
                button_selectors = [
                    'input[value*="查詢"]',
                    'button[title*="查詢"]',
                    'input[type="submit"]',
                    'button[type="submit"]',
                    'input[value*="搜尋"]',
                    'button:contains("查詢")'
                ]

                for selector in button_selectors:
                    try:
                        query_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        query_button.click()
                        safe_print(f"✅ 已點擊查詢按鈕 (使用選擇器: {selector})")
                        time.sleep(2)
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
            safe_print(f"⚠️ 日期範圍設定過程中出現問題，但繼續執行: {e}")
            return True  # 即使失敗也返回True，讓流程繼續

    def get_payment_records(self):
        """直接在iframe中搜尋代收貨款相關數據 - 使用wedi_selenium_scraper.py的邏輯"""
        safe_print("📊 搜尋當前頁面中的代收貨款數據...")

        records = []
        try:
            # 此時已經在datamain iframe中，直接搜尋數據
            safe_print("🔍 分析當前頁面內容...")

            # 搜尋所有連結，找出代收貨款相關項目
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            print(f"   找到 {len(all_links)} 個連結")

            # 定義代收貨款匯款明細相關關鍵字（更精確）
            payment_keywords = [
                "代收貨款", "匯款明細", "(2-1)"
            ]

            # 定義排除關鍵字（增加不需要的項目）
            excluded_keywords = [
                "語音取件", "三節加價", "系統公告", "操作說明", "維護通知",
                "Home", "首頁", "登出", "系統設定",
                "代收款已收未結帳明細", "已收未結帳", "未結帳明細"  # 不需要下載的項目
            ]

            for i, link in enumerate(all_links):
                try:
                    link_text = link.text.strip()
                    if link_text:
                        # 檢查是否需要排除
                        should_exclude = any(keyword in link_text for keyword in excluded_keywords)

                        # 更精確的匹配：必須包含「代收貨款」和「匯款明細」
                        is_payment_remittance = ("代收貨款" in link_text and "匯款明細" in link_text) or "(2-1)" in link_text

                        if is_payment_remittance and not should_exclude:
                            # 生成檔案ID
                            file_id = link_text.replace(" ", "_").replace("[", "").replace("]", "").replace("-", "_")
                            records.append({
                                "index": i + 1,
                                "title": link_text,
                                "payment_no": file_id,
                                "link": link
                            })
                            safe_print(f"   ✅ 找到代收貨款匯款明細: {link_text}")
                        elif should_exclude:
                            safe_print(f"   ⏭️ 跳過排除項目: {link_text}")
                        elif "代收" in link_text:
                            safe_print(f"   ⏭️ 跳過非匯款明細項目: {link_text}")
                except:
                    continue

            # 如果沒有找到任何代收貨款連結，嘗試搜尋表格數據
            if not records:
                safe_print("🔍 未找到代收貨款連結，搜尋表格數據...")
                tables = self.driver.find_elements(By.TAG_NAME, "table")

                for table in tables:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    for row in rows:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        for cell in cells:
                            cell_text = cell.text.strip()
                            if any(keyword in cell_text for keyword in payment_keywords):
                                safe_print(f"   📋 找到表格中的代收貨款數據: {cell_text}")

            safe_print(f"📊 總共找到 {len(records)} 筆代收貨款相關記錄")
            return records

        except Exception as e:
            safe_print(f"❌ 搜尋代收貨款數據失敗: {e}")
            return records

    def download_excel_for_record(self, record):
        """為特定記錄下載Excel檔案 - 使用wedi_selenium_scraper.py的完整邏輯"""
        safe_print(f"📥 下載記錄 {record['payment_no']} 的Excel檔案...")

        try:
            # 已經在iframe中，直接查找連結
            links = self.driver.find_elements(By.TAG_NAME, "a")
            found_link = None

            # 尋找匹配的連結
            for link in links:
                try:
                    if record['title'] in link.text:
                        found_link = link
                        break
                except:
                    continue

            if found_link:
                # 使用JavaScript點擊避免元素遮蔽問題
                self.driver.execute_script("arguments[0].click();", found_link)
                time.sleep(5)
            else:
                raise Exception(f"找不到標題為 '{record['title']}' 的可點擊連結")

            downloaded_files = []
            payment_no = record['payment_no']

            # 調試：查看頁面上的所有按鈕和表單元素
            safe_print("🔍 頁面調試資訊:")
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            forms = self.driver.find_elements(By.TAG_NAME, "form")

            print(f"   找到 {len(buttons)} 個按鈕:")
            for i, btn in enumerate(buttons[:10]):  # 只顯示前10個
                try:
                    text = btn.text or btn.get_attribute('value') or btn.get_attribute('title')
                    print(f"     按鈕 {i+1}: {text}")
                except:
                    pass

            print(f"   找到 {len(inputs)} 個input元素:")
            for i, inp in enumerate(inputs[:10]):  # 只顯示前10個
                try:
                    inp_type = inp.get_attribute('type')
                    value = inp.get_attribute('value') or inp.text
                    print(f"     Input {i+1}: type='{inp_type}' value='{value}'")
                except:
                    pass

            print(f"   找到 {len(forms)} 個表單")

            # 在詳細頁面填入查詢日期範圍
            safe_print("📅 在詳細頁面填入查詢日期...")
            try:
                # 使用指定的日期範圍
                if self.start_date and self.end_date:
                    start_date = self.start_date.strftime("%Y%m%d")
                    end_date = self.end_date.strftime("%Y%m%d")
                else:
                    # 預設值：當日
                    today = datetime.now()
                    start_date = today.strftime("%Y%m%d")
                    end_date = today.strftime("%Y%m%d")

                # 找到日期輸入框
                date_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
                if len(date_inputs) >= 2:
                    # 填入開始日期
                    date_inputs[0].clear()
                    date_inputs[0].send_keys(start_date)
                    safe_print(f"✅ 已填入開始日期: {start_date}")

                    # 填入結束日期
                    date_inputs[1].clear()
                    date_inputs[1].send_keys(end_date)
                    safe_print(f"✅ 已填入結束日期: {end_date}")
                elif len(date_inputs) >= 1:
                    # 只有一個日期輸入框，填入結束日期
                    date_inputs[0].clear()
                    date_inputs[0].send_keys(end_date)
                    safe_print(f"✅ 已填入查詢日期: {end_date}")

                # 嘗試點擊查詢按鈕
                try:
                    query_button = self.driver.find_element(By.CSS_SELECTOR, 'input[value*="查詢"]')
                    query_button.click()
                    safe_print("✅ 已點擊查詢按鈕")
                    time.sleep(5)  # 等待查詢結果
                except:
                    safe_print("⚠️ 未找到查詢按鈕，跳過此步驟")

                # 查詢後再次檢查頁面元素
                safe_print("🔍 查詢後頁面調試資訊:")
                buttons_after = self.driver.find_elements(By.TAG_NAME, "button")
                inputs_after = self.driver.find_elements(By.TAG_NAME, "input")
                links_after = self.driver.find_elements(By.TAG_NAME, "a")

                print(f"   查詢後找到 {len(buttons_after)} 個按鈕:")
                for i, btn in enumerate(buttons_after[:10]):
                    try:
                        text = btn.text or btn.get_attribute('value') or btn.get_attribute('title')
                        print(f"     按鈕 {i+1}: {text}")
                    except:
                        pass

                print(f"   查詢後找到 {len(inputs_after)} 個input元素:")
                for i, inp in enumerate(inputs_after[:15]):
                    try:
                        inp_type = inp.get_attribute('type')
                        value = inp.get_attribute('value') or inp.text
                        print(f"     Input {i+1}: type='{inp_type}' value='{value}'")
                    except:
                        pass

                print(f"   查詢後找到 {len(links_after)} 個連結:")
                for i, link in enumerate(links_after[:10]):
                    try:
                        text = link.text.strip()
                        if text and ("匯出" in text or "Excel" in text or "下載" in text):
                            print(f"     重要連結 {i+1}: {text}")
                    except:
                        pass

                # 查詢結果頁面載入完成

                # 查找查詢結果中的匯款編號連結
                safe_print("🔍 尋找查詢結果中的匯款編號連結...")
                payment_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'javascript:') or starts-with(text(), '4')]")

                if payment_links:
                    print(f"   找到 {len(payment_links)} 個匯款編號連結")
                    for i, link in enumerate(payment_links):
                        try:
                            link_text = link.text.strip()
                            print(f"   連結 {i+1}: {link_text}")
                        except:
                            pass

                    # 收集所有匯款編號
                    payment_numbers = []
                    for i, link in enumerate(payment_links):
                        try:
                            link_text = link.text.strip()
                            if link_text and len(link_text) > 10:
                                payment_numbers.append(link_text)
                                print(f"   收集匯款編號: {link_text}")
                        except:
                            pass

                    # 分別處理每個匯款編號 - 使用多視窗方式
                    for i, payment_no in enumerate(payment_numbers):
                        safe_print(f"🔗 正在處理匯款編號 ({i+1}/{len(payment_numbers)}): {payment_no}")

                        try:
                            # 保存當前主視窗handle
                            main_window = self.driver.current_window_handle

                            # 重新找到所有連結
                            current_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'javascript:') or starts-with(text(), '4')]")
                            target_link = None

                            for link in current_links:
                                if link.text.strip() == payment_no:
                                    target_link = link
                                    break

                            if target_link:
                                # 獲取連結的href屬性
                                link_href = target_link.get_attribute('href')
                                safe_print(f"🔗 連結href: {link_href}")

                                if 'javascript:' in link_href:
                                    # JavaScript連結需要在新視窗中執行
                                    # 使用Ctrl+Click或者執行JavaScript來開新視窗
                                    self.driver.execute_script("window.open('about:blank', '_blank');")

                                    # 切換到新視窗
                                    new_windows = [handle for handle in self.driver.window_handles if handle != main_window]
                                    if new_windows:
                                        new_window = new_windows[-1]
                                        self.driver.switch_to.window(new_window)

                                        # 在新視窗中重新導航到相同頁面
                                        self.driver.get(self.driver.current_url if hasattr(self, 'current_url') else "about:blank")
                                        time.sleep(2)

                                        # 切換回原始iframe
                                        try:
                                            iframe = WebDriverWait(self.driver, 10).until(
                                                EC.presence_of_element_located((By.NAME, "datamain"))
                                            )
                                            self.driver.switch_to.frame(iframe)
                                        except:
                                            pass

                                        # 重新執行查詢和點擊目標連結
                                        try:
                                            # 重新填入查詢條件
                                            self.refill_query_conditions()

                                            # 重新尋找並點擊目標連結
                                            new_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'javascript:') or starts-with(text(), '4')]")
                                            for link in new_links:
                                                if link.text.strip() == payment_no:
                                                    self.driver.execute_script("arguments[0].click();", link)
                                                    time.sleep(3)
                                                    break

                                        except Exception as nav_e:
                                            safe_print(f"⚠️ 新視窗導航失敗: {nav_e}")
                                            # 如果新視窗導航失敗，切換回主視窗並使用原方法
                                            self.driver.close()
                                            self.driver.switch_to.window(main_window)
                                            continue
                                else:
                                    # 普通連結可以直接在新視窗中開啟
                                    self.driver.execute_script("window.open(arguments[0], '_blank');", link_href)
                                    new_windows = [handle for handle in self.driver.window_handles if handle != main_window]
                                    if new_windows:
                                        new_window = new_windows[-1]
                                        self.driver.switch_to.window(new_window)
                                        time.sleep(3)

                                # 匯款詳細頁面載入完成

                                # 下載這個匯款記錄的Excel檔案
                                download_success = self.download_excel_for_payment(payment_no)
                                if download_success:
                                    downloaded_files.append(f"{self.username}_{payment_no}.xlsx")

                                # 關閉新視窗並回到主視窗
                                self.driver.close()
                                self.driver.switch_to.window(main_window)

                                # 切換回iframe
                                try:
                                    iframe = WebDriverWait(self.driver, 5).until(
                                        EC.presence_of_element_located((By.NAME, "datamain"))
                                    )
                                    self.driver.switch_to.frame(iframe)
                                except:
                                    pass

                                safe_print(f"✅ 已關閉新視窗，回到主查詢頁面")

                            else:
                                safe_print(f"⚠️ 找不到匯款編號 {payment_no} 的連結")

                        except Exception as link_e:
                            safe_print(f"⚠️ 處理匯款編號 {payment_no} 時發生錯誤: {link_e}")

                            # 確保回到主視窗
                            try:
                                if len(self.driver.window_handles) > 1:
                                    self.driver.close()
                                    self.driver.switch_to.window(main_window)
                            except:
                                pass
                            continue

                    # 處理完所有連結後返回
                    return downloaded_files

                else:
                    safe_print("❌ 沒有找到匯款編號連結")

            except Exception as date_e:
                safe_print(f"⚠️ 填入查詢日期失敗: {date_e}")

            # 尋找並點擊匯出xlsx按鈕
            try:
                # 嘗試多種可能的匯出按鈕選擇器
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
                    time.sleep(5)  # 增加等待時間
                else:
                    raise Exception("找不到xlsx匯出按鈕")

                # 獲取新下載的檔案
                after_files = set(self.download_dir.glob("*"))
                new_files = after_files - before_files

                # 重命名新下載的檔案
                for new_file in new_files:
                    if new_file.suffix.lower() in ['.xlsx', '.xls']:
                        new_name = f"{self.username}_{payment_no}{new_file.suffix}"
                        new_path = self.download_dir / new_name
                        new_file.rename(new_path)
                        downloaded_files.append(str(new_path))
                        safe_print(f"✅ 已重命名為: {new_name}")

            except Exception as e:
                safe_print(f"⚠️ xlsx下載失敗: {e}")

            # 保持在iframe中，不切換回主frame
            return downloaded_files

        except Exception as e:
            safe_print(f"❌ 下載記錄失敗: {e}")
            return []

    def refill_query_conditions(self):
        """在新視窗中重新填入查詢條件"""
        safe_print("📅 重新填入查詢條件...")

        try:
            # 使用指定的日期範圍
            if self.start_date and self.end_date:
                start_date = self.start_date.strftime("%Y%m%d")
                end_date = self.end_date.strftime("%Y%m%d")
            else:
                # 預設值：當日
                today = datetime.now()
                start_date = today.strftime("%Y%m%d")
                end_date = today.strftime("%Y%m%d")

            # 尋找日期輸入框
            date_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')

            if len(date_inputs) >= 2:
                # 填入開始日期
                date_inputs[0].clear()
                date_inputs[0].send_keys(start_date)

                # 填入結束日期
                date_inputs[1].clear()
                date_inputs[1].send_keys(end_date)

                safe_print(f"✅ 已重新填入日期範圍: {start_date} ~ {end_date}")

                # 點擊查詢按鈕
                try:
                    query_button = self.driver.find_element(By.CSS_SELECTOR, 'input[value*="查詢"]')
                    query_button.click()
                    time.sleep(3)
                    safe_print("✅ 已執行查詢")
                except:
                    safe_print("⚠️ 找不到查詢按鈕")
            else:
                safe_print("⚠️ 找不到足夠的日期輸入框")

        except Exception as e:
            safe_print(f"⚠️ 重新填入查詢條件失敗: {e}")

    def download_excel_for_payment(self, payment_no):
        """為單個匯款記錄下載Excel檔案 - 使用 data-fileblob 提取"""
        safe_print(f"📥 下載匯款編號 {payment_no} 的Excel檔案...")

        try:
            # 直接從頁面提取 data-fileblob 數據並生成 Excel
            safe_print("🚀 嘗試從頁面提取 data-fileblob 數據...")
            
            # 尋找包含 data-fileblob 屬性的按鈕
            fileblob_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[data-fileblob]")
            
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
                            ws.title = "代收貨款匯款明細"
                            
                            # 將數據寫入工作表
                            for row_index, row_data in enumerate(data_array, 1):
                                for col_index, cell_value in enumerate(row_data, 1):
                                    # 清理 HTML 實體和空白字符
                                    if isinstance(cell_value, str):
                                        cell_value = cell_value.replace("&nbsp;", "").strip()
                                    
                                    cell = ws.cell(row=row_index, column=col_index, value=cell_value)
                                    
                                    # 設定標題行格式
                                    if row_index == 1:
                                        cell.font = openpyxl.styles.Font(bold=True)
                            
                            # 自動調整欄寬
                            for column in ws.columns:
                                max_length = 0
                                column_letter = column[0].column_letter
                                for cell in column:
                                    try:
                                        if cell.value:
                                            max_length = max(max_length, len(str(cell.value)))
                                    except:
                                        pass
                                adjusted_width = min(max_length + 2, 50)
                                ws.column_dimensions[column_letter].width = adjusted_width
                            
                            # 生成檔案名稱
                            new_name = f"{self.username}_{payment_no}.xlsx"
                            new_path = self.download_dir / new_name
                            
                            # 如果目標檔案已存在，直接覆蓋
                            if new_path.exists():
                                safe_print(f"⚠️ 檔案已存在，將覆蓋: {new_name}")
                                new_path.unlink()
                            
                            # 保存 Excel 檔案
                            wb.save(new_path)
                            safe_print(f"✅ 已生成 Excel 檔案: {new_name} (共 {len(data_array)} 行數據)")
                            
                            return True
                            
                        else:
                            safe_print("❌ data-fileblob 中沒有找到數據陣列")
                            return False
                            
                    except json.JSONDecodeError as json_e:
                        safe_print(f"❌ 解析 data-fileblob JSON 失敗: {json_e}")
                        safe_print(f"   原始數據前500字元: {fileblob_data[:500]}")
                        return False
                    
                    except Exception as excel_e:
                        safe_print(f"❌ 生成 Excel 檔案失敗: {excel_e}")
                        return False
                
                else:
                    safe_print("❌ data-fileblob 屬性為空")
                    return False
                    
            else:
                safe_print("⚠️ 未找到包含 data-fileblob 的元素，嘗試傳統下載方式...")
                return self._fallback_download_excel(payment_no)
                
        except Exception as blob_e:
            safe_print(f"❌ data-fileblob 提取失敗: {blob_e}")
            safe_print("🔄 嘗試傳統下載方式...")
            return self._fallback_download_excel(payment_no)

    def _fallback_download_excel(self, payment_no):
        """備用的傳統下載方式"""
        try:
            # 尋找並點擊匯出xlsx按鈕
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
                    xlsx_button = WebDriverWait(self.driver, 3).until(
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
                time.sleep(5)  # 等待下載完成

                # 獲取新下載的檔案
                after_files = set(self.download_dir.glob("*"))
                new_files = after_files - before_files

                # 重命名新下載的檔案
                for new_file in new_files:
                    if new_file.suffix.lower() in ['.xlsx', '.xls']:
                        new_name = f"{self.username}_{payment_no}{new_file.suffix}"
                        new_path = self.download_dir / new_name

                        # 如果目標檔案已存在，直接覆蓋
                        if new_path.exists():
                            safe_print(f"⚠️ 檔案已存在，將覆蓋: {new_name}")
                            new_path.unlink()  # 刪除舊檔案

                        new_file.rename(new_path)
                        safe_print(f"✅ 已重命名為: {new_name}")
                        return True

                # 處理.crdownload檔案（Chrome下載中的檔案）
                crdownload_files = list(self.download_dir.glob("*.crdownload"))
                if crdownload_files:
                    crdownload_file = crdownload_files[0]
                    new_name = f"{self.username}_{payment_no}.xlsx"
                    new_path = self.download_dir / new_name

                    if new_path.exists():
                        safe_print(f"⚠️ 檔案已存在，將覆蓋: {new_name}")
                        new_path.unlink()  # 刪除舊檔案

                    crdownload_file.rename(new_path)
                    safe_print(f"✅ 已重命名.crdownload檔案為: {new_name}")
                    return True

                return len(new_files) > 0
            else:
                safe_print("⚠️ 找不到xlsx匯出按鈕")
                return False

        except Exception as e:
            safe_print(f"⚠️ 傳統下載方式失敗: {e}")
            return False

    def run_full_process(self):
        """執行完整的自動化流程"""
        success = False
        all_downloads = []
        records = []

        try:
            print("=" * 60)
            safe_print(f"🤖 開始執行代收貨款查詢流程 (帳號: {self.username})")
            print("=" * 60)

            # 1. 初始化瀏覽器
            self.init_browser()

            # 2. 登入
            login_success = self.login()
            if not login_success:
                safe_print(f"❌ 帳號 {self.username} 登入失敗")
                return {"success": False, "username": self.username, "error": "登入失敗", "downloads": [], "records": []}

            # 3. 導航到查詢頁面
            nav_success = self.navigate_to_query()
            if not nav_success:
                safe_print(f"❌ 帳號 {self.username} 導航失敗")
                return {"success": False, "username": self.username, "error": "導航失敗", "downloads": [], "records": []}

            # 4. 先設定日期範圍（雖然可能找不到輸入框）
            self.set_date_range()

            # 5. 獲取付款記錄
            records = self.get_payment_records()

            if not records:
                safe_print(f"⚠️ 帳號 {self.username} 沒有找到付款記錄")
                return {"success": True, "username": self.username, "message": "無資料可下載", "downloads": [], "records": []}

            # 6. 下載每個記錄的Excel檔案
            for record in records:
                try:
                    downloads = self.download_excel_for_record(record)
                    all_downloads.extend(downloads)
                except Exception as download_e:
                    safe_print(f"⚠️ 帳號 {self.username} 下載記錄 {record.get('payment_no', 'unknown')} 失敗: {download_e}")
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
    import argparse
    from datetime import datetime, timedelta

    parser = argparse.ArgumentParser(description='代收貨款自動下載工具')
    parser.add_argument('--headless', action='store_true', help='使用無頭模式')
    parser.add_argument('--start-date', type=str, help='開始日期 (格式: YYYYMMDD，例如: 20241201)')
    parser.add_argument('--end-date', type=str, help='結束日期 (格式: YYYYMMDD，例如: 20241208)')

    args = parser.parse_args()

    # 日期參數驗證和處理
    try:
        today = datetime.now()

        # 處理開始日期：如果未指定則使用往前7天
        if args.start_date:
            start_date = datetime.strptime(args.start_date, '%Y%m%d')
        else:
            start_date = today - timedelta(days=7)

        # 處理結束日期：如果未指定則使用當日
        if args.end_date:
            end_date = datetime.strptime(args.end_date, '%Y%m%d')
        else:
            end_date = today

        # 驗證日期範圍
        if start_date > end_date:
            print("⛔ 錯誤: 開始日期不能晚於結束日期")
            return 1

        # 顯示查詢範圍
        if args.start_date and args.end_date:
            safe_print(f"📅 使用指定日期範圍: {start_date.strftime('%Y%m%d')} ~ {end_date.strftime('%Y%m%d')}")
        elif args.start_date:
            safe_print(f"📅 從指定日期到當日: {start_date.strftime('%Y%m%d')} ~ {end_date.strftime('%Y%m%d')}")
        elif args.end_date:
            safe_print(f"📅 從7天前到指定日期: {start_date.strftime('%Y%m%d')} ~ {end_date.strftime('%Y%m%d')}")
        else:
            safe_print(f"📅 查詢日期範圍: {start_date.strftime('%Y%m%d')} ~ {end_date.strftime('%Y%m%d')} (預設7天)")

    except ValueError as e:
        print(f"⛔ 日期格式錯誤: {e}")
        print("💡 日期格式應為 YYYYMMDD，例如: 20241201")
        return 1

    try:
        # 統一使用多帳號管理模式
        safe_print("🏢 代收貨款自動下載工具")

        manager = MultiAccountManager("accounts.json")
        manager.run_all_accounts(
            scraper_class=PaymentScraper,
            headless_override=args.headless if args.headless else None,
            start_date=start_date,
            end_date=end_date
        )

        return 0

    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"⛔ 錯誤: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n⛔ 使用者中斷執行")
        return 1
    except Exception as e:
        print(f"⛔ 未知錯誤: {e}")
        return 1


if __name__ == "__main__":
    main()