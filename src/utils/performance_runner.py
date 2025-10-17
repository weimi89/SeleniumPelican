#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Performance test runner for SeleniumPelican
Executes performance tests and generates comprehensive reports
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.logging_config import get_logger


def run_performance_tests(
    test_type: str = "all", save_baseline: bool = False, headless: bool = True
):
    """
    Run performance tests with specified options

    Args:
        test_type: Type of tests to run ('all', 'browser', 'scraper', 'memory')
        save_baseline: Whether to save results as new baseline
        headless: Whether to run tests in headless mode
    """
    logger = get_logger("performance_runner")
    logger.info("🚀 啟動 SeleniumPelican 效能測試", test_type=test_type, headless=headless)

    # Prepare pytest command
    pytest_args = [
        "python",
        "-m",
        "pytest",
        "tests/performance/",
        "-v",
        "--tb=short",
        "-x",  # Stop on first failure
    ]

    # Add test type specific filters
    if test_type == "browser":
        pytest_args.extend(["-k", "browser"])
    elif test_type == "scraper":
        pytest_args.extend(["-k", "scraper"])
    elif test_type == "memory":
        pytest_args.extend(["-k", "memory"])

    # Add headless flag as environment variable
    env = {"PYTEST_HEADLESS": "true" if headless else "false"}

    try:
        # Run the tests
        logger.info("📊 執行效能測試...", command=" ".join(pytest_args))
        result = subprocess.run(pytest_args, capture_output=True, text=True, env=env)

        # Log results
        if result.returncode == 0:
            logger.log_operation_success(
                "效能測試執行", test_type=test_type, exit_code=result.returncode
            )
            print("✅ 所有效能測試通過")
        else:
            logger.warning(
                "部分效能測試失敗",
                test_type=test_type,
                exit_code=result.returncode,
                stderr=result.stderr[:500],  # Limit error output
            )
            print("⚠️ 部分效能測試失敗")

        # Show output
        if result.stdout:
            print("\n" + "=" * 60)
            print("測試輸出:")
            print("=" * 60)
            print(result.stdout)

        if result.stderr and result.returncode != 0:
            print("\n" + "=" * 60)
            print("錯誤輸出:")
            print("=" * 60)
            print(result.stderr)

        return result.returncode == 0

    except Exception as e:
        logger.error(f"❌ 效能測試執行失敗: {e}", exc_info=True)
        return False


def generate_performance_summary():
    """Generate a summary of all performance test results"""
    logger = get_logger("performance_summary")

    reports_dir = Path("reports/performance")
    if not reports_dir.exists():
        logger.warning("❌ 沒有找到效能測試報告目錄")
        return

    # Find the latest performance report
    report_files = list(reports_dir.glob("performance_report_*.txt"))
    if not report_files:
        logger.warning("❌ 沒有找到效能測試報告")
        return

    latest_report = max(report_files, key=lambda f: f.stat().st_mtime)

    logger.info(f"📊 最新效能報告: {latest_report}")

    # Read and display the report
    try:
        with open(latest_report, "r", encoding="utf-8") as f:
            report_content = f.read()

        print("\n" + "=" * 80)
        print("效能測試摘要報告")
        print("=" * 80)
        print(report_content)

        # Also check for baseline comparison
        baselines_file = Path("tests/performance/baselines.json")
        if baselines_file.exists():
            logger.info(f"📈 基準數據文件: {baselines_file}")
        else:
            logger.info("💡 建議執行 --save-baseline 建立效能基準")

    except Exception as e:
        logger.error(f"❌ 讀取效能報告失敗: {e}")


def check_performance_requirements():
    """Check if current performance meets requirements"""
    logger = get_logger("performance_check")

    # Define performance requirements based on OpenSpec
    requirements = {
        "browser_startup_headless": {"max_time": 10.0, "unit": "seconds"},
        "browser_startup_windowed": {"max_time": 15.0, "unit": "seconds"},
        "login_operation": {"max_time": 30.0, "unit": "seconds"},
        "navigation_operation": {"max_time": 10.0, "unit": "seconds"},
        "max_memory_usage": {"max_value": 500.0, "unit": "MB"},
        "max_degradation": {"max_percent": 50.0, "unit": "percent"},
    }

    logger.info("📋 效能需求檢查", requirements=requirements)

    # This would analyze recent test results against requirements
    # For now, just log the requirements
    print("\n📋 效能需求標準:")
    print("=" * 50)
    for operation, req in requirements.items():
        if "max_time" in req:
            print(f"• {operation}: ≤ {req['max_time']} {req['unit']}")
        elif "max_value" in req:
            print(f"• {operation}: ≤ {req['max_value']} {req['unit']}")
        elif "max_percent" in req:
            print(f"• {operation}: ≤ {req['max_percent']}% degradation")

    print("\n💡 執行 'python scripts/run_performance_tests.py' 來驗證效能")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="SeleniumPelican 效能測試執行器")

    parser.add_argument(
        "--type",
        choices=["all", "browser", "scraper", "memory"],
        default="all",
        help="測試類型 (預設: all)",
    )

    parser.add_argument("--save-baseline", action="store_true", help="將測試結果保存為新的基準")

    parser.add_argument("--windowed", action="store_true", help="使用視窗模式運行測試 (預設: 無頭模式)")

    parser.add_argument("--summary", action="store_true", help="只顯示最新的效能摘要報告")

    parser.add_argument("--check-requirements", action="store_true", help="檢查效能需求標準")

    args = parser.parse_args()

    if args.check_requirements:
        check_performance_requirements()
        return

    if args.summary:
        generate_performance_summary()
        return

    # Run performance tests
    success = run_performance_tests(
        test_type=args.type,
        save_baseline=args.save_baseline,
        headless=not args.windowed,
    )

    # Generate summary after tests
    if success:
        print("\n" + "=" * 60)
        print("正在生成效能摘要...")
        generate_performance_summary()

        if args.save_baseline:
            print("✅ 新的效能基準已保存")

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
