#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SeleniumPelican 日誌監控命令列工具

提供日誌分析、監控和報告生成功能。
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.log_analyzer import LogAnalyzer, create_monitoring_dashboard_data
from src.core.monitoring_service import FileAlertChannel, MonitoringService
from src.utils.windows_encoding_utils import safe_print


def setup_argument_parser():
    """設定命令列參數解析器"""
    parser = argparse.ArgumentParser(
        description="SeleniumPelican 日誌監控工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  # 分析最近 24 小時的日誌
  python scripts/log_monitor.py analyze --hours 24 --format markdown

  # 生成 JSON 報告
  python scripts/log_monitor.py analyze --output report.json

  # 啟動即時監控
  python scripts/log_monitor.py monitor --interval 60

  # 生成儀表板
  python scripts/log_monitor.py dashboard --output dashboard.html

  # 檢查特定日期範圍
  python scripts/log_monitor.py analyze --start "2024-12-01 00:00:00" --end "2024-12-02 00:00:00"
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 分析命令
    analyze_parser = subparsers.add_parser("analyze", help="分析日誌檔案")
    analyze_parser.add_argument("--log-dir", default="logs", help="日誌目錄路徑 (預設: logs)")
    analyze_parser.add_argument("--hours", type=int, help="分析最近 N 小時的日誌")
    analyze_parser.add_argument("--start", help='開始時間 (格式: "YYYY-MM-DD HH:MM:SS")')
    analyze_parser.add_argument("--end", help='結束時間 (格式: "YYYY-MM-DD HH:MM:SS")')
    analyze_parser.add_argument(
        "--format", choices=["json", "markdown"], default="json", help="輸出格式 (預設: json)"
    )
    analyze_parser.add_argument("--output", help="輸出檔案路徑 (若未指定則輸出到標準輸出)")
    analyze_parser.add_argument(
        "--pattern", default="*.json", help="日誌檔案模式 (預設: *.json)"
    )

    # 監控命令
    monitor_parser = subparsers.add_parser("monitor", help="啟動即時監控")
    monitor_parser.add_argument("--log-dir", default="logs", help="日誌目錄路徑 (預設: logs)")
    monitor_parser.add_argument(
        "--interval", type=int, default=300, help="檢查間隔秒數 (預設: 300)"
    )
    monitor_parser.add_argument(
        "--alert-file",
        default="logs/alerts.jsonl",
        help="警報輸出檔案 (預設: logs/alerts.jsonl)",
    )
    monitor_parser.add_argument("--dashboard", help="儀表板 HTML 檔案路徑 (若指定則定期更新)")

    # 儀表板命令
    dashboard_parser = subparsers.add_parser("dashboard", help="生成監控儀表板")
    dashboard_parser.add_argument("--log-dir", default="logs", help="日誌目錄路徑 (預設: logs)")
    dashboard_parser.add_argument(
        "--output",
        default="monitoring_dashboard.html",
        help="儀表板檔案路徑 (預設: monitoring_dashboard.html)",
    )
    dashboard_parser.add_argument(
        "--hours", type=int, default=24, help="分析最近 N 小時的數據 (預設: 24)"
    )

    # 統計命令
    stats_parser = subparsers.add_parser("stats", help="顯示日誌統計")
    stats_parser.add_argument("--log-dir", default="logs", help="日誌目錄路徑 (預設: logs)")
    stats_parser.add_argument(
        "--hours", type=int, default=24, help="統計最近 N 小時的數據 (預設: 24)"
    )

    return parser


def parse_time_range(args):
    """解析時間範圍參數"""
    if args.hours:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=args.hours)
        return start_time, end_time

    if args.start and args.end:
        try:
            start_time = datetime.strptime(args.start, "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(args.end, "%Y-%m-%d %H:%M:%S")
            return start_time, end_time
        except ValueError as e:
            safe_print(f"❌ 時間格式錯誤: {e}")
            safe_print("請使用格式: YYYY-MM-DD HH:MM:SS")
            return None, None

    return None, None


def command_analyze(args):
    """執行分析命令"""
    safe_print(f"🔍 開始分析日誌目錄: {args.log_dir}")

    # 檢查日誌目錄
    log_dir = Path(args.log_dir)
    if not log_dir.exists():
        safe_print(f"❌ 日誌目錄不存在: {log_dir}")
        return 1

    # 解析時間範圍
    start_time, end_time = parse_time_range(args)
    if args.hours or (args.start and args.end):
        if start_time is None or end_time is None:
            return 1
        safe_print(f"📅 分析時間範圍: {start_time} 至 {end_time}")

    # 建立分析器
    analyzer = LogAnalyzer(log_dir)

    try:
        # 執行分析
        if start_time and end_time:
            report = analyzer.generate_report((start_time, end_time), args.format)
        else:
            report = analyzer.generate_report(output_format=args.format)

        # 輸出結果
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)
            safe_print(f"✅ 分析報告已儲存至: {output_path}")
        else:
            print(report)

        return 0

    except Exception as e:
        safe_print(f"❌ 分析失敗: {e}")
        return 1


def command_monitor(args):
    """執行監控命令"""
    safe_print(f"🖥️ 啟動日誌監控服務")
    safe_print(f"   日誌目錄: {args.log_dir}")
    safe_print(f"   檢查間隔: {args.interval} 秒")
    safe_print(f"   警報檔案: {args.alert_file}")

    # 檢查日誌目錄
    log_dir = Path(args.log_dir)
    if not log_dir.exists():
        safe_print(f"❌ 日誌目錄不存在: {log_dir}")
        return 1

    # 建立監控服務
    analyzer = LogAnalyzer(log_dir)
    service = MonitoringService(analyzer)
    service.check_interval = args.interval

    # 添加檔案警報通道
    alert_file = Path(args.alert_file)
    alert_file.parent.mkdir(parents=True, exist_ok=True)
    file_channel = FileAlertChannel(alert_file)
    service.add_alert_channel(file_channel)

    try:
        # 啟動監控
        service.start_monitoring()
        safe_print("✅ 監控服務已啟動")
        safe_print("按 Ctrl+C 停止監控")

        # 如果指定了儀表板，定期更新
        if args.dashboard:
            import time

            dashboard_path = Path(args.dashboard)
            dashboard_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                while service.is_running:
                    service.create_dashboard_html(str(dashboard_path))
                    time.sleep(60)  # 每分鐘更新一次儀表板
            except KeyboardInterrupt:
                pass
        else:
            # 等待中斷信號
            try:
                while service.is_running:
                    import time

                    time.sleep(1)
            except KeyboardInterrupt:
                pass

        return 0

    except KeyboardInterrupt:
        safe_print("\n⏹️ 監控服務正在停止...")
        return 0
    except Exception as e:
        safe_print(f"❌ 監控失敗: {e}")
        return 1
    finally:
        service.stop_monitoring()
        safe_print("✅ 監控服務已停止")


def command_dashboard(args):
    """執行儀表板命令"""
    safe_print(f"📊 生成監控儀表板")
    safe_print(f"   日誌目錄: {args.log_dir}")
    safe_print(f"   輸出檔案: {args.output}")
    safe_print(f"   分析時間: 最近 {args.hours} 小時")

    # 檢查日誌目錄
    log_dir = Path(args.log_dir)
    if not log_dir.exists():
        safe_print(f"❌ 日誌目錄不存在: {log_dir}")
        return 1

    try:
        # 建立分析器和監控服務
        analyzer = LogAnalyzer(log_dir)
        service = MonitoringService(analyzer)

        # 生成儀表板
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        service.create_dashboard_html(str(output_path))

        safe_print(f"✅ 儀表板已生成: {output_path}")
        safe_print(f"🌐 在瀏覽器中開啟: file://{output_path.absolute()}")

        return 0

    except Exception as e:
        safe_print(f"❌ 生成儀表板失敗: {e}")
        return 1


def command_stats(args):
    """執行統計命令"""
    safe_print(f"📈 顯示日誌統計")
    safe_print(f"   日誌目錄: {args.log_dir}")
    safe_print(f"   統計時間: 最近 {args.hours} 小時")

    # 檢查日誌目錄
    log_dir = Path(args.log_dir)
    if not log_dir.exists():
        safe_print(f"❌ 日誌目錄不存在: {log_dir}")
        return 1

    try:
        # 建立分析器
        analyzer = LogAnalyzer(log_dir)

        # 獲取儀表板數據
        dashboard_data = create_monitoring_dashboard_data(analyzer, args.hours)

        # 顯示統計
        safe_print("\n" + "=" * 50)
        safe_print("📊 日誌統計摘要")
        safe_print("=" * 50)

        metrics = dashboard_data.get("metrics", {})
        safe_print(f"整體狀態: {dashboard_data.get('status', 'unknown').upper()}")
        safe_print(f"總日誌數量: {metrics.get('total_logs', 0):,}")
        safe_print(f"錯誤率: {metrics.get('error_rate', 0):.1%}")
        safe_print(f"警告數量: {metrics.get('warning_count', 0)}")
        safe_print(f"嚴重警報: {metrics.get('critical_alerts', 0)}")

        # 顯示性能統計
        performance = dashboard_data.get("performance", {})
        operations = performance.get("operations", {})
        if operations:
            safe_print("\n📈 操作性能統計:")
            for op_name, stats in operations.items():
                safe_print(f"  {op_name}:")
                safe_print(f"    次數: {stats.get('count', 0):,}")
                safe_print(f"    成功率: {stats.get('success_rate', 0):.1%}")
                safe_print(f"    平均時間: {stats.get('avg_duration', 0):.2f}s")

        # 顯示活躍警報
        alerts = dashboard_data.get("alerts", [])
        if alerts:
            safe_print(f"\n⚠️ 活躍警報 ({len(alerts)}):")
            for alert in alerts[:5]:  # 只顯示前 5 個
                severity_emoji = {
                    "critical": "🔴",
                    "error": "❌",
                    "warning": "⚠️",
                    "info": "ℹ️",
                }.get(alert.get("severity", "info"), "•")
                name = alert.get("name", alert.get("type", "Unknown"))
                description = alert.get("description", "")
                safe_print(f"  {severity_emoji} {name}: {description}")

        safe_print("\n" + "=" * 50)

        return 0

    except Exception as e:
        safe_print(f"❌ 統計失敗: {e}")
        return 1


def main():
    """主函數"""
    parser = setup_argument_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # 執行對應命令
    if args.command == "analyze":
        return command_analyze(args)
    elif args.command == "monitor":
        return command_monitor(args)
    elif args.command == "dashboard":
        return command_dashboard(args)
    elif args.command == "stats":
        return command_stats(args)
    else:
        safe_print(f"❌ 未知命令: {args.command}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        safe_print("\n⏹️ 程式已中止")
        sys.exit(0)
    except Exception as e:
        safe_print(f"❌ 程式執行錯誤: {e}")
        sys.exit(1)
