#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置檔案驗證模組

此模組提供配置檔案的 JSON Schema 驗證、結構檢查和安全性驗證功能。
支援 accounts.json 和 .env 檔案的完整性檢查。
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from jsonschema import ValidationError, validate

from ..utils.windows_encoding_utils import safe_print
from .logging_config import get_logger

# accounts.json JSON Schema 定義（新格式：純陣列）
ACCOUNTS_JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "username": {
                "type": "string",
                "minLength": 1,
                "description": "使用者帳號名稱",
            },
            "password": {
                "type": "string",
                "minLength": 1,
                "description": "使用者密碼",
            },
            "enabled": {"type": "boolean", "description": "帳號是否啟用"},
        },
        "required": ["username", "password", "enabled"],
        "additionalProperties": False,
    },
    "minItems": 1,
    "description": "帳號清單",
}

# 舊格式 JSON Schema（用於向後相容檢查）
OLD_ACCOUNTS_JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "accounts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "username": {"type": "string", "minLength": 1},
                    "password": {"type": "string", "minLength": 1},
                    "enabled": {"type": "boolean"},
                },
                "required": ["username", "password", "enabled"],
            },
            "minItems": 1,
        },
        "settings": {"type": "object"},
    },
    "required": ["accounts"],
}


class ConfigValidationError(Exception):
    """配置驗證錯誤異常類別"""


class ConfigValidator:
    """配置檔案驗證器"""

    def __init__(self, project_root: Optional[str] = None):
        """
        初始化配置驗證器

        Args:
            project_root: 專案根目錄路徑，若未提供則自動偵測
        """
        self.logger = get_logger("config_validator")
        if project_root:
            self.project_root = Path(project_root)
        else:
            # 自動偵測專案根目錄（尋找 pyproject.toml 或 .git）
            current_path = Path(__file__).resolve()
            for parent in current_path.parents:
                if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
                    self.project_root = parent
                    break
            else:
                self.project_root = Path.cwd()

        self.accounts_file = self.project_root / "accounts.json"
        self.accounts_example_file = self.project_root / "accounts.json.example"
        self.env_file = self.project_root / ".env"
        self.env_example_file = self.project_root / ".env.example"

    def validate_accounts_json(
        self, accounts_path: Optional[str] = None
    ) -> Tuple[bool, List[str]]:
        """
        驗證 accounts.json 檔案（支援新舊格式）

        Args:
            accounts_path: accounts.json 檔案路徑，若未提供則使用預設路徑

        Returns:
            tuple: (驗證是否成功, 錯誤訊息列表)
        """
        errors = []
        accounts_file = Path(accounts_path) if accounts_path else self.accounts_file

        # 檢查檔案是否存在
        if not accounts_file.exists():
            errors.append(f"檔案不存在: {accounts_file}")
            return False, errors

        try:
            # 讀取並解析 JSON 檔案
            with open(accounts_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 判斷是新格式還是舊格式
            is_old_format = isinstance(data, dict) and "accounts" in data

            # JSON Schema 驗證
            try:
                if is_old_format:
                    # 舊格式：顯示警告但允許通過
                    errors.append(
                        "⚠️ 偵測到舊格式的 accounts.json（包含 'accounts' 和 'settings' 鍵），"
                        "建議更新為新格式（純帳號陣列）。"
                        "請參考 accounts.json.example 或遷移指南。"
                    )
                    validate(instance=data, schema=OLD_ACCOUNTS_JSON_SCHEMA)
                else:
                    # 新格式
                    validate(instance=data, schema=ACCOUNTS_JSON_SCHEMA)
            except ValidationError as e:
                errors.append(f"JSON Schema 驗證失敗: {e.message}")
                if e.path:
                    errors.append(f"錯誤位置: {' -> '.join(str(p) for p in e.path)}")
                return False, errors

            # 額外的業務邏輯驗證
            business_errors = self._validate_accounts_business_logic(data, is_old_format)
            errors.extend(business_errors)

        except json.JSONDecodeError as e:
            errors.append(f"JSON 格式錯誤: {e}")
            return False, errors
        except Exception as e:
            errors.append(f"讀取檔案時發生錯誤: {e}")
            return False, errors

        return len(errors) == 0, errors

    def _validate_accounts_business_logic(self, data, is_old_format: bool = False) -> List[str]:
        """
        驗證 accounts.json 的業務邏輯（支援新舊格式）

        Args:
            data: 已解析的 JSON 資料（陣列或包含 accounts 鍵的字典）
            is_old_format: 是否為舊格式

        Returns:
            錯誤訊息列表
        """
        errors = []

        # 根據格式獲取帳號列表
        accounts = data["accounts"] if is_old_format else data

        # 檢查是否至少有一個啟用的帳號
        enabled_accounts = [
            acc for acc in accounts if acc.get("enabled", False)
        ]
        if not enabled_accounts:
            errors.append("至少需要一個啟用的帳號 (enabled: true)")

        # 檢查帳號名稱是否重複
        usernames = [acc["username"] for acc in accounts]
        if len(usernames) != len(set(usernames)):
            duplicates = []
            for username in set(usernames):
                if usernames.count(username) > 1:
                    duplicates.append(username)
            errors.append(f"發現重複的帳號名稱: {', '.join(duplicates)}")

        # 檢查密碼強度（基本檢查）
        for i, account in enumerate(accounts):
            password = account["password"]
            if len(password) < 6:
                errors.append(f"帳號 #{i+1} ({account['username']}) 的密碼過短，建議至少 6 個字元")

            # 檢查是否使用預設範例密碼
            if password in ["您的密碼1", "您的密碼2", "您的密碼3", "your_password"]:
                errors.append(f"帳號 #{i+1} ({account['username']}) 仍使用範例密碼，請更換為實際密碼")

        # 舊格式才檢查下載目錄設定（新格式改用環境變數）
        if is_old_format and "settings" in data:
            download_dir = data["settings"].get("download_base_dir", "downloads")
            if download_dir == "downloads":
                # 這是預設值，檢查是否為相對路徑
                abs_download_dir = self.project_root / download_dir
                if not abs_download_dir.exists():
                    errors.append(f"下載目錄不存在: {abs_download_dir}，將自動建立")
            elif not os.path.isabs(download_dir):
                # 相對路徑，轉換為絕對路徑檢查
                abs_download_dir = self.project_root / download_dir
                if not abs_download_dir.parent.exists():
                    errors.append(f"下載目錄的父目錄不存在: {abs_download_dir.parent}")

        return errors

    def validate_env_file(
        self, env_path: Optional[str] = None
    ) -> Tuple[bool, List[str]]:
        """
        驗證 .env 檔案

        Args:
            env_path: .env 檔案路徑，若未提供則使用預設路徑

        Returns:
            tuple: (驗證是否成功, 錯誤訊息列表)
        """
        errors = []
        env_file = Path(env_path) if env_path else self.env_file

        # 檢查檔案是否存在
        if not env_file.exists():
            errors.append(f"檔案不存在: {env_file}")
            return False, errors

        try:
            # 讀取 .env 檔案
            env_vars = {}
            with open(env_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # 跳過空行和註解
                    if not line or line.startswith("#"):
                        continue

                    # 解析 KEY=VALUE 格式
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip("\"'")  # 移除引號
                        env_vars[key] = value
                    else:
                        errors.append(f"行 {line_num}: 格式錯誤，應為 KEY=VALUE 格式")

            # 驗證必要的環境變數
            required_vars = ["CHROME_BINARY_PATH"]
            optional_vars = [
                "CHROMEDRIVER_PATH",
                "HEADLESS",
                "PAYMENT_DOWNLOAD_DIR",
                "UNPAID_DOWNLOAD_DIR",
                "FREIGHT_DOWNLOAD_DIR",
                "PYTHONUNBUFFERED",
                "LOG_LEVEL",
                "WAIT_TIMEOUT",
            ]

            for var in required_vars:
                if var not in env_vars:
                    errors.append(f"缺少必要的環境變數: {var}")
                elif not env_vars[var]:
                    errors.append(f"環境變數 {var} 不可為空")
                else:
                    # 檢查路徑是否存在
                    path = env_vars[var]
                    if not os.path.exists(path):
                        errors.append(f"環境變數 {var} 指向的路徑不存在: {path}")

            # 檢查可選環境變數
            for var in optional_vars:
                if var in env_vars and env_vars[var]:
                    # HEADLESS 是布林值，不需要檢查路徑
                    if var == "HEADLESS":
                        value = env_vars[var].lower()
                        if value not in ["true", "false"]:
                            errors.append(f"環境變數 HEADLESS 必須為 'true' 或 'false'，目前值: {env_vars[var]}")
                    # 下載目錄相關環境變數檢查目錄是否存在（或可以建立）
                    elif var.endswith("_DOWNLOAD_DIR"):
                        download_path = env_vars[var]
                        # 如果是相對路徑，轉換為絕對路徑
                        if not os.path.isabs(download_path):
                            abs_path = self.project_root / download_path
                        else:
                            abs_path = Path(download_path)

                        # 檢查父目錄是否存在
                        if not abs_path.parent.exists():
                            errors.append(
                                f"環境變數 {var} 指向的下載目錄父目錄不存在: {abs_path.parent}，"
                                "請確認路徑正確"
                            )
                    # ChromeDriver 路徑檢查
                    elif var == "CHROMEDRIVER_PATH":
                        path = env_vars[var]
                        if not os.path.exists(path):
                            errors.append(f"環境變數 {var} 指向的路徑不存在: {path}")
                    # PYTHONUNBUFFERED 檢查
                    elif var == "PYTHONUNBUFFERED":
                        value = env_vars[var]
                        if value not in ["0", "1"]:
                            errors.append(f"環境變數 PYTHONUNBUFFERED 必須為 '0' 或 '1'，目前值: {value}")
                    # LOG_LEVEL 檢查
                    elif var == "LOG_LEVEL":
                        value = env_vars[var].upper()
                        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                        if value not in valid_levels:
                            errors.append(
                                f"環境變數 LOG_LEVEL 必須為 {', '.join(valid_levels)} 之一，"
                                f"目前值: {env_vars[var]}"
                            )
                    # WAIT_TIMEOUT 檢查
                    elif var == "WAIT_TIMEOUT":
                        try:
                            timeout = int(env_vars[var])
                            if timeout <= 0:
                                errors.append(f"環境變數 WAIT_TIMEOUT 必須為正整數，目前值: {env_vars[var]}")
                        except ValueError:
                            errors.append(f"環境變數 WAIT_TIMEOUT 必須為整數，目前值: {env_vars[var]}")

        except Exception as e:
            errors.append(f"讀取 .env 檔案時發生錯誤: {e}")
            return False, errors

        return len(errors) == 0, errors

    def validate_all_configs(self) -> Tuple[bool, Dict[str, List[str]]]:
        """
        驗證所有配置檔案

        Returns:
            tuple: (全部驗證是否成功, 按檔案分組的錯誤訊息)
        """
        results = {}
        overall_success = True

        # 驗證 accounts.json
        success, errors = self.validate_accounts_json()
        results["accounts.json"] = errors
        if not success:
            overall_success = False

        # 驗證 .env
        success, errors = self.validate_env_file()
        results[".env"] = errors
        if not success:
            overall_success = False

        return overall_success, results

    def create_missing_config_files(self) -> Tuple[bool, List[str]]:
        """
        從範例檔案建立缺少的配置檔案

        Returns:
            tuple: (操作是否成功, 操作訊息列表)
        """
        messages = []
        success = True

        # 檢查並建立 accounts.json
        if not self.accounts_file.exists():
            if self.accounts_example_file.exists():
                try:
                    import shutil

                    shutil.copy2(self.accounts_example_file, self.accounts_file)
                    messages.append(f"✅ 已從範例建立 {self.accounts_file}")
                    messages.append(f"⚠️ 請編輯 {self.accounts_file} 並填入實際的帳號資訊")
                except Exception as e:
                    messages.append(f"❌ 無法建立 {self.accounts_file}: {e}")
                    success = False
            else:
                messages.append(f"❌ 範例檔案不存在: {self.accounts_example_file}")
                success = False
        else:
            messages.append(f"ℹ️ 配置檔案已存在: {self.accounts_file}")

        # 檢查並建立 .env
        if not self.env_file.exists():
            if self.env_example_file.exists():
                try:
                    import shutil

                    shutil.copy2(self.env_example_file, self.env_file)
                    messages.append(f"✅ 已從範例建立 {self.env_file}")
                    messages.append(
                        f"⚠️ 請編輯 {self.env_file} 並設定以下必要配置：\n"
                        "   1. CHROME_BINARY_PATH - Chrome 瀏覽器路徑（必要）\n"
                        "   2. CHROMEDRIVER_PATH - ChromeDriver 路徑（選用）\n"
                        "   3. HEADLESS - 無頭模式開關 true/false（選用，預設 false）\n"
                        "   4. 下載目錄設定（選用）：\n"
                        "      - PAYMENT_DOWNLOAD_DIR（代收貨款）\n"
                        "      - FREIGHT_DOWNLOAD_DIR（運費結帳）\n"
                        "      - UNPAID_DOWNLOAD_DIR（運費未請款）\n"
                        "   📝 提示：檔案中已包含各平台的快速設定範例"
                    )
                except Exception as e:
                    messages.append(f"❌ 無法建立 {self.env_file}: {e}")
                    success = False
            else:
                messages.append(f"❌ 範例檔案不存在: {self.env_example_file}")
                success = False
        else:
            messages.append(f"ℹ️ 配置檔案已存在: {self.env_file}")

        return success, messages

    def get_config_summary(self) -> Dict[str, Any]:
        """
        獲取配置檔案摘要資訊

        Returns:
            配置摘要字典
        """
        summary: Dict[str, Any] = {
            "project_root": str(self.project_root),
            "files": {},
            "validation_status": {},
        }

        # 檢查檔案存在狀態
        files_to_check = [
            ("accounts.json", self.accounts_file),
            ("accounts.json.example", self.accounts_example_file),
            (".env", self.env_file),
            (".env.example", self.env_example_file),
        ]

        for name, path in files_to_check:
            summary["files"][name] = {
                "exists": path.exists(),
                "path": str(path),
                "size": path.stat().st_size if path.exists() else 0,
            }

        # 執行驗證
        if self.accounts_file.exists():
            success, errors = self.validate_accounts_json()
            summary["validation_status"]["accounts.json"] = {
                "valid": success,
                "errors": errors,
            }

        if self.env_file.exists():
            success, errors = self.validate_env_file()
            summary["validation_status"][".env"] = {"valid": success, "errors": errors}

        return summary

    def print_validation_report(self, show_details: bool = True) -> bool:
        """
        列印詳細的驗證報告

        Args:
            show_details: 是否顯示詳細錯誤資訊

        Returns:
            整體驗證是否成功
        """
        self.logger.info("SeleniumPelican 配置檔案驗證報告", operation="validation_report")
        self.logger.info("=" * 50)

        overall_success, results = self.validate_all_configs()

        for config_file, errors in results.items():
            if not errors:
                self.logger.log_operation_success(
                    f"{config_file} 驗證", config_file=config_file
                )
            else:
                self.logger.error(
                    f"{config_file} 發現 {len(errors)} 個問題",
                    config_file=config_file,
                    error_count=len(errors),
                )
                if show_details:
                    for i, error in enumerate(errors, 1):
                        self.logger.error(
                            f"   {i}. {error}", error_detail=error, error_index=i
                        )

        self.logger.info("=" * 50)
        if overall_success:
            self.logger.log_operation_success("所有配置檔案驗證")
        else:
            self.logger.warning("發現配置問題，請檢查並修正上述錯誤", status="validation_failed")

        return overall_success


def validate_config_files(
    project_root: Optional[str] = None,
    create_missing: bool = False,
    show_report: bool = True,
) -> bool:
    """
    驗證配置檔案的便利函數

    Args:
        project_root: 專案根目錄路徑
        create_missing: 是否自動建立缺少的配置檔案
        show_report: 是否顯示驗證報告

    Returns:
        驗證是否成功
    """
    validator = ConfigValidator(project_root)

    # 建立缺少的配置檔案
    if create_missing:
        success, messages = validator.create_missing_config_files()
        for message in messages:
            safe_print(message)
        if not success:
            return False

    # 顯示驗證報告
    if show_report:
        return validator.print_validation_report()
    else:
        overall_success, _ = validator.validate_all_configs()
        return overall_success


if __name__ == "__main__":
    # 命令列執行時的測試
    import sys

    # 支援命令列參數
    create_missing = "--create" in sys.argv
    quiet = "--quiet" in sys.argv

    success = validate_config_files(
        create_missing=create_missing, show_report=not quiet
    )

    sys.exit(0 if success else 1)
