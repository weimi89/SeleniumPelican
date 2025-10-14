"""
SeleniumPelican 專案常數定義
集中管理所有硬編碼值和設定常數
"""

from typing import Any, Dict


class Timeouts:
    """等待時間常數"""

    # WebDriverWait 超時設定
    DEFAULT_WAIT = 10
    LONG_WAIT = 30
    SHORT_WAIT = 5

    # 頁面載入等待
    PAGE_LOAD = 5
    IFRAME_SWITCH = 2
    QUERY_SUBMIT = 3

    # 下載相關等待
    DOWNLOAD_WAIT = 5
    FILE_CHECK_INTERVAL = 1
    MAX_DOWNLOAD_TIME = 60

    # 登入相關等待
    LOGIN_SUBMIT = 3
    CAPTCHA_INPUT_WAIT = 20  # 手動輸入驗證碼等待時間
    LOGIN_RETRY_DELAY = 2


class Selectors:
    """CSS/XPath 選擇器常數"""

    # 登入頁面選擇器 (WEDI 系統特定)
    LOGIN_USERNAME = "input[name='CUST_ID']"
    LOGIN_PASSWORD = "input[name='CUST_PASSWORD']"
    LOGIN_CAPTCHA = "input[name='KEY_RND']"
    LOGIN_SUBMIT = "input[type='submit']"

    # iframe 選擇器
    DATA_MAIN_IFRAME = "iframe[name='datamain']"

    # 導航選擇器
    QUERY_OPERATIONS = "查詢作業"
    QUERY_PAGE_LINK = "查件"

    # 表格和數據選擇器
    TABLE_ROWS = "tr"
    TABLE_CELLS = "td"
    DOWNLOAD_LINKS = "a"

    # 日期輸入選擇器
    START_DATE_INPUT = "input[name*='start'], input[id*='start'], input[name*='begin']"
    END_DATE_INPUT = "input[name*='end'], input[id*='end']"
    QUERY_BUTTON = "input[value*='查詢'], button[text*='查詢'], input[type='submit']"


class Messages:
    """訊息文字常數"""

    # 登入相關訊息
    LOGIN_SUCCESS = "✅ 登入成功"
    LOGIN_FAILED = "❌ 登入失敗"
    LOGIN_RETRY = "🔄 登入失敗，正在重試..."
    CAPTCHA_DETECTED = "🔍 自動偵測到驗證碼"
    CAPTCHA_MANUAL = "⚠️ 無法自動偵測驗證碼，請手動輸入"

    # 操作相關訊息
    NAVIGATING_TO_QUERY = "🧭 導航至查詢頁面..."
    SETTING_DATE_RANGE = "📅 設定日期範圍"
    SEARCHING_RECORDS = "🔍 搜尋記錄中..."
    DOWNLOADING_FILE = "📥 下載檔案"

    # 完成狀態訊息
    PROCESS_COMPLETE = "🎉 處理完成"
    NO_RECORDS_FOUND = "📭 未找到符合條件的記錄"
    DOWNLOAD_SUCCESS = "✅ 下載成功"
    DOWNLOAD_FAILED = "❌ 下載失敗"


class ErrorMessages:
    """錯誤訊息常數"""

    # 登入錯誤
    LOGIN_ELEMENT_NOT_FOUND = "找不到登入表單元素"
    LOGIN_MAX_RETRIES = "登入重試次數已達上限"
    CAPTCHA_RECOGNITION_FAILED = "驗證碼識別失敗"

    # 導航錯誤
    IFRAME_NOT_FOUND = "找不到目標 iframe"
    QUERY_PAGE_NOT_FOUND = "找不到查詢頁面"
    NAVIGATION_FAILED = "頁面導航失敗"

    # 數據錯誤
    NO_DATA_FOUND = "未找到數據"
    TABLE_PARSING_FAILED = "表格解析失敗"
    RECORD_PROCESSING_FAILED = "記錄處理失敗"

    # 下載錯誤
    DOWNLOAD_LINK_NOT_FOUND = "找不到下載連結"
    FILE_DOWNLOAD_FAILED = "檔案下載失敗"
    FILE_MOVE_FAILED = "檔案移動失敗"


class RetryConfig:
    """重試機制設定"""

    MAX_LOGIN_RETRIES = 3
    MAX_DOWNLOAD_RETRIES = 2
    MAX_NAVIGATION_RETRIES = 2

    RETRY_DELAY = 2  # 秒
    EXPONENTIAL_BACKOFF = True











class LoggingConfig:
    """日誌設定"""

    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    LOG_LEVEL = "INFO"
    LOG_FILE_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5



