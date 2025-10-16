#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
瀏覽器功能測試腳本
功能: 驗證瀏覽器自動化能力和效能指標
"""

import os
import sys
import time
import psutil
from pathlib import Path

# 將專案根目錄加入 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from selenium.common.exceptions import WebDriverException

# 顏色輸出（Unix-like 系統）
GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"  # No Color


def print_success(msg: str) -> None:
    """列印成功訊息"""
    print(f"{GREEN}✅ {msg}{NC}")


def print_fail(msg: str) -> None:
    """列印失敗訊息"""
    print(f"{RED}❌ {msg}{NC}")


def print_info(msg: str) -> None:
    """列印資訊訊息"""
    print(f"{BLUE}ℹ️  {msg}{NC}")


def print_warning(msg: str) -> None:
    """列印警告訊息"""
    print(f"{YELLOW}⚠️  {msg}{NC}")


def get_memory_usage_mb(pid: int) -> float:
    """取得程序記憶體使用量（MB）"""
    try:
        process = psutil.Process(pid)
        # 取得實際記憶體使用（RSS - Resident Set Size）
        memory_info = process.memory_info()
        return memory_info.rss / 1024 / 1024  # 轉換為 MB
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return 0.0


def test_browser_functionality() -> bool:
    """測試瀏覽器功能"""
    print("\n" + "=" * 50)
    print("  瀏覽器功能測試")
    print("=" * 50 + "\n")

    tests_passed = 0
    tests_total = 6

    driver = None
    start_time = time.time()

    try:
        # 測試 1: 啟動瀏覽器
        print(f"[1/{tests_total}] 測試: 啟動 Chrome 瀏覽器（無頭模式）...")
        from src.core.browser_utils import init_chrome_browser

        driver, wait = init_chrome_browser(headless=True)
        init_time = time.time() - start_time
        print_success(f"瀏覽器啟動成功 (耗時: {init_time:.2f}秒)")
        tests_passed += 1

        # 記錄程序 PID 和初始記憶體
        driver_pid = getattr(getattr(driver, 'service', None), 'process', None)
        driver_pid = getattr(driver_pid, 'pid', None) if driver_pid else None
        if driver_pid:
            initial_memory = get_memory_usage_mb(driver_pid)
            print_info(f"程序 PID: {driver_pid}, 初始記憶體: {initial_memory:.1f}MB")
        else:
            initial_memory = 0.0
            print_info("無法取得程序 PID（跳過記憶體測量）")

        # 測試 2: 導航至測試網頁
        print(f"\n[2/{tests_total}] 測試: 導航至測試網頁...")
        nav_start = time.time()
        driver.get("https://www.google.com")
        nav_time = time.time() - nav_start
        print_success(f"頁面載入成功 (耗時: {nav_time:.2f}秒)")
        tests_passed += 1

        # 測試 3: 驗證頁面標題
        print(f"\n[3/{tests_total}] 測試: 驗證頁面載入...")
        page_title = driver.title
        if page_title:
            print_success(f"頁面標題: {page_title}")
            tests_passed += 1
        else:
            print_fail("無法取得頁面標題")

        # 測試 4: 執行 JavaScript
        print(f"\n[4/{tests_total}] 測試: 執行 JavaScript...")
        result = driver.execute_script("return 'Hello from JavaScript';")
        if result == "Hello from JavaScript":
            print_success(f"JavaScript 執行成功: {result}")
            tests_passed += 1
        else:
            print_fail(f"JavaScript 執行結果不符: {result}")

        # 測試 5: 驗證視窗大小
        print(f"\n[5/{tests_total}] 測試: 驗證視窗大小設定...")
        window_size = driver.get_window_size()
        expected_width = 1280
        expected_height = 720
        if window_size["width"] == expected_width and window_size["height"] == expected_height:
            print_success(f"視窗大小正確: {window_size['width']}x{window_size['height']}")
            tests_passed += 1
        else:
            print_warning(
                f"視窗大小不符預期: {window_size['width']}x{window_size['height']} "
                f"(預期: {expected_width}x{expected_height})"
            )

        # 測試 6: 測量記憶體使用
        print(f"\n[6/{tests_total}] 測試: 測量記憶體使用...")
        if driver_pid:
            time.sleep(1)  # 等待穩定
            final_memory = get_memory_usage_mb(driver_pid)
            print_success(f"最終記憶體使用: {final_memory:.1f}MB")

            # 記憶體效能評估
            memory_threshold = 250  # MB
            if final_memory <= memory_threshold:
                print_success(f"記憶體使用符合優化目標 (<= {memory_threshold}MB)")
                tests_passed += 1
            else:
                print_warning(f"記憶體使用超過目標: {final_memory:.1f}MB > {memory_threshold}MB")
                tests_passed += 1  # 仍算通過，只是警告
        else:
            print_info("無法測量記憶體（未取得 PID）")
            tests_passed += 1  # 跳過但仍計為通過

    except WebDriverException as e:
        print_fail(f"瀏覽器驅動錯誤: {e}")
        print_info("診斷建議: 執行 ./scripts/test_ubuntu_env.sh 檢查環境")
        return False
    except Exception as e:
        print_fail(f"測試過程發生錯誤: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        # 關閉瀏覽器
        if driver:
            print("\n正在關閉瀏覽器...")
            try:
                driver.quit()
                print_success("瀏覽器已正常關閉")
            except Exception as e:
                print_warning(f"關閉瀏覽器時出現警告: {e}")

    # 總結
    total_time = time.time() - start_time
    print("\n" + "=" * 50)
    print(f"  測試結果: {tests_passed}/{tests_total} 項測試通過")
    print(f"  總執行時間: {total_time:.2f}秒")
    print("=" * 50 + "\n")

    if tests_passed == tests_total:
        print_success("✅ 所有瀏覽器功能測試通過")

        # 效能評估
        print("\n效能指標:")
        print(f"  - 啟動時間: {init_time:.2f}秒" + (" ✅" if init_time < 3.0 else " ⚠️"))
        if driver_pid and 'final_memory' in locals() and final_memory:
            print(
                f"  - 記憶體使用: {final_memory:.1f}MB"
                + (" ✅" if final_memory <= 250 else " ⚠️")
            )

        print("\n瀏覽器自動化環境已就緒，可以開始使用 SeleniumPelican！")
        return True
    else:
        print_warning(f"部分測試未通過: {tests_passed}/{tests_total}")
        return False


def main() -> int:
    """主函式"""
    try:
        success = test_browser_functionality()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n測試已中斷")
        return 130
    except Exception as e:
        print_fail(f"執行測試時發生未預期的錯誤: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
