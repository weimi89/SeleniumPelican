#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日誌分析和監控機制

提供結構化日誌分析、模式檢測、異常監控和性能追蹤功能。
支援即時監控和歷史分析。
"""

import json
import re
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import statistics

from .logging_config import get_logger


class LogEntry:
    """日誌條目結構化表示"""

    def __init__(self, timestamp: datetime, level: str, message: str,
                 module: str = None, **extra_fields):
        self.timestamp = timestamp
        self.level = level
        self.message = message
        self.module = module
        self.extra_fields = extra_fields

    @classmethod
    def from_json_line(cls, line: str) -> Optional['LogEntry']:
        """從 JSON 日誌行建立 LogEntry"""
        try:
            data = json.loads(line)
            timestamp = datetime.fromisoformat(data.get('timestamp', '').replace('Z', '+00:00'))
            level = data.get('level', 'INFO')
            message = data.get('message', '')
            module = data.get('module')

            # 提取其他欄位
            extra_fields = {k: v for k, v in data.items()
                          if k not in ['timestamp', 'level', 'message', 'module']}

            return cls(timestamp, level, message, module, **extra_fields)
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            return None

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        result = {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level,
            'message': self.message,
        }
        if self.module:
            result['module'] = self.module
        result.update(self.extra_fields)
        return result


class LogPattern:
    """日誌模式定義"""

    def __init__(self, name: str, pattern: str, severity: str = 'info',
                 description: str = '', threshold: int = 1):
        self.name = name
        self.pattern = re.compile(pattern, re.IGNORECASE)
        self.severity = severity  # info, warning, error, critical
        self.description = description
        self.threshold = threshold  # 觸發警告的次數閾值
        self.matches = []

    def match(self, log_entry: LogEntry) -> bool:
        """檢查日誌條目是否匹配模式"""
        if self.pattern.search(log_entry.message):
            self.matches.append(log_entry)
            return True
        return False

    def is_triggered(self) -> bool:
        """檢查是否觸發警告閾值"""
        return len(self.matches) >= self.threshold

    def reset(self):
        """重置匹配記錄"""
        self.matches.clear()


class PerformanceMetrics:
    """性能指標收集器"""

    def __init__(self):
        self.operation_times = defaultdict(list)
        self.error_counts = Counter()
        self.success_counts = Counter()
        self.start_times = {}

    def record_operation_start(self, operation: str, operation_id: str = None):
        """記錄操作開始時間"""
        key = f"{operation}:{operation_id}" if operation_id else operation
        self.start_times[key] = datetime.now()

    def record_operation_end(self, operation: str, operation_id: str = None,
                           success: bool = True):
        """記錄操作結束時間"""
        key = f"{operation}:{operation_id}" if operation_id else operation

        if key in self.start_times:
            duration = (datetime.now() - self.start_times[key]).total_seconds()
            self.operation_times[operation].append(duration)
            del self.start_times[key]

            if success:
                self.success_counts[operation] += 1
            else:
                self.error_counts[operation] += 1

    def get_operation_stats(self, operation: str) -> Dict[str, Any]:
        """取得操作統計"""
        times = self.operation_times.get(operation, [])
        if not times:
            return {
                'operation': operation,
                'count': 0,
                'success_rate': 0.0,
                'avg_duration': 0.0
            }

        return {
            'operation': operation,
            'count': len(times),
            'success_count': self.success_counts[operation],
            'error_count': self.error_counts[operation],
            'success_rate': self.success_counts[operation] /
                          (self.success_counts[operation] + self.error_counts[operation])
                          if (self.success_counts[operation] + self.error_counts[operation]) > 0 else 0.0,
            'avg_duration': statistics.mean(times),
            'min_duration': min(times),
            'max_duration': max(times),
            'median_duration': statistics.median(times),
            'p95_duration': self._percentile(times, 95) if len(times) >= 5 else max(times)
        }

    def _percentile(self, data: List[float], percentile: int) -> float:
        """計算百分位數"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


class LogAnalyzer:
    """日誌分析主類別"""

    def __init__(self, log_dir: Union[str, Path] = "logs"):
        self.logger = get_logger("log_analyzer")
        self.log_dir = Path(log_dir)
        self.patterns = self._initialize_patterns()
        self.metrics = PerformanceMetrics()
        self.analysis_cache = {}

    def _initialize_patterns(self) -> List[LogPattern]:
        """初始化預設日誌模式"""
        return [
            # 錯誤模式
            LogPattern(
                "login_failures",
                r"登入失敗|login.*failed|authentication.*failed",
                "error",
                "登入失敗檢測",
                threshold=3
            ),
            LogPattern(
                "navigation_errors",
                r"導航.*失敗|navigation.*failed|element.*not.*found",
                "warning",
                "導航錯誤檢測",
                threshold=5
            ),
            LogPattern(
                "timeout_errors",
                r"timeout|超時|等待.*超時",
                "warning",
                "超時錯誤檢測",
                threshold=3
            ),
            LogPattern(
                "critical_errors",
                r"critical|fatal|crashed|崩潰",
                "critical",
                "嚴重錯誤檢測",
                threshold=1
            ),

            # 性能模式
            LogPattern(
                "slow_operations",
                r"duration.*[5-9]\d{3,}|執行時間.*[5-9]\d+秒",
                "warning",
                "慢操作檢測",
                threshold=2
            ),

            # 成功模式
            LogPattern(
                "successful_downloads",
                r"下載.*成功|已生成.*Excel|successfully.*downloaded",
                "info",
                "成功下載追蹤"
            ),
        ]

    def add_pattern(self, pattern: LogPattern):
        """添加自定義模式"""
        self.patterns.append(pattern)

    def analyze_log_file(self, log_file: Path,
                        time_range: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, Any]:
        """分析單個日誌檔案"""
        if not log_file.exists():
            self.logger.warning(f"日誌檔案不存在: {log_file}")
            return {}

        # 檢查快取
        cache_key = f"{log_file}_{log_file.stat().st_mtime}"
        if cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]

        entries = []
        invalid_lines = 0

        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue

                    entry = LogEntry.from_json_line(line)
                    if entry:
                        # 檢查時間範圍
                        if time_range:
                            start_time, end_time = time_range
                            if not (start_time <= entry.timestamp <= end_time):
                                continue
                        entries.append(entry)
                    else:
                        invalid_lines += 1

        except Exception as e:
            self.logger.error(f"讀取日誌檔案失敗 {log_file}: {e}")
            return {}

        # 分析日誌條目
        analysis = self._analyze_entries(entries)
        analysis['file_info'] = {
            'path': str(log_file),
            'total_entries': len(entries),
            'invalid_lines': invalid_lines,
            'size_bytes': log_file.stat().st_size,
        }

        # 快取結果
        self.analysis_cache[cache_key] = analysis
        return analysis

    def analyze_directory(self, time_range: Optional[Tuple[datetime, datetime]] = None,
                         file_pattern: str = "*.json") -> Dict[str, Any]:
        """分析整個日誌目錄"""
        log_files = list(self.log_dir.glob(file_pattern))
        if not log_files:
            self.logger.warning(f"在 {self.log_dir} 中找不到符合 {file_pattern} 的日誌檔案")
            return {}

        # 按修改時間排序
        log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        all_entries = []
        file_analyses = {}

        for log_file in log_files:
            file_analysis = self.analyze_log_file(log_file, time_range)
            if file_analysis:
                file_analyses[str(log_file)] = file_analysis
                # 收集所有條目進行整體分析
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                entry = LogEntry.from_json_line(line)
                                if entry:
                                    if time_range:
                                        start_time, end_time = time_range
                                        if start_time <= entry.timestamp <= end_time:
                                            all_entries.append(entry)
                                    else:
                                        all_entries.append(entry)
                except Exception as e:
                    self.logger.warning(f"處理檔案 {log_file} 時發生錯誤: {e}")

        # 整體分析
        overall_analysis = self._analyze_entries(all_entries)
        overall_analysis['file_analyses'] = file_analyses
        overall_analysis['analyzed_files'] = len(log_files)

        return overall_analysis

    def _analyze_entries(self, entries: List[LogEntry]) -> Dict[str, Any]:
        """分析日誌條目列表"""
        if not entries:
            return {}

        # 重置模式匹配
        for pattern in self.patterns:
            pattern.reset()

        # 基本統計
        level_counts = Counter(entry.level for entry in entries)
        module_counts = Counter(entry.module for entry in entries if entry.module)
        hourly_counts = defaultdict(int)

        # 模式匹配和時間分布
        triggered_patterns = []
        for entry in entries:
            # 檢查模式
            for pattern in self.patterns:
                if pattern.match(entry):
                    continue  # 模式已在 match 方法中記錄

            # 時間分布統計
            hour_key = entry.timestamp.strftime('%Y-%m-%d %H:00')
            hourly_counts[hour_key] += 1

            # 性能指標提取
            self._extract_performance_metrics(entry)

        # 檢查觸發的模式
        for pattern in self.patterns:
            if pattern.is_triggered():
                triggered_patterns.append({
                    'name': pattern.name,
                    'severity': pattern.severity,
                    'description': pattern.description,
                    'match_count': len(pattern.matches),
                    'threshold': pattern.threshold,
                    'recent_matches': [
                        {
                            'timestamp': match.timestamp.isoformat(),
                            'message': match.message
                        }
                        for match in pattern.matches[-5:]  # 最近 5 個匹配
                    ]
                })

        # 異常檢測
        anomalies = self._detect_anomalies(entries)

        # 性能分析
        performance_summary = self._analyze_performance()

        return {
            'summary': {
                'total_entries': len(entries),
                'time_range': {
                    'start': min(entries, key=lambda e: e.timestamp).timestamp.isoformat(),
                    'end': max(entries, key=lambda e: e.timestamp).timestamp.isoformat(),
                } if entries else None,
                'level_distribution': dict(level_counts),
                'module_distribution': dict(module_counts),
            },
            'triggered_patterns': triggered_patterns,
            'anomalies': anomalies,
            'performance': performance_summary,
            'time_distribution': dict(hourly_counts),
            'analysis_timestamp': datetime.now().isoformat(),
        }

    def _extract_performance_metrics(self, entry: LogEntry):
        """從日誌條目提取性能指標"""
        # 檢查操作成功/失敗
        if '成功' in entry.message or 'success' in entry.message.lower():
            # 嘗試提取操作類型
            if 'operation' in entry.extra_fields:
                operation = entry.extra_fields['operation']
                self.metrics.success_counts[operation] += 1

        elif '失敗' in entry.message or 'failed' in entry.message.lower() or 'error' in entry.message.lower():
            if 'operation' in entry.extra_fields:
                operation = entry.extra_fields['operation']
                self.metrics.error_counts[operation] += 1

        # 提取持續時間
        if 'duration' in entry.extra_fields:
            try:
                duration = float(entry.extra_fields['duration'])
                operation = entry.extra_fields.get('operation', 'unknown')
                self.metrics.operation_times[operation].append(duration)
            except (ValueError, TypeError):
                pass

    def _detect_anomalies(self, entries: List[LogEntry]) -> List[Dict[str, Any]]:
        """異常檢測"""
        anomalies = []

        if len(entries) < 10:  # 數據不足，無法進行異常檢測
            return anomalies

        # 時間間隔異常檢測
        time_intervals = []
        for i in range(1, len(entries)):
            interval = (entries[i].timestamp - entries[i-1].timestamp).total_seconds()
            time_intervals.append(interval)

        if time_intervals:
            avg_interval = statistics.mean(time_intervals)
            std_interval = statistics.stdev(time_intervals) if len(time_intervals) > 1 else 0

            # 檢測異常間隔（超過平均值 + 3*標準差）
            threshold = avg_interval + 3 * std_interval
            for i, interval in enumerate(time_intervals):
                if interval > threshold and interval > 300:  # 超過 5 分鐘且異常
                    anomalies.append({
                        'type': 'time_gap',
                        'description': f'日誌時間間隔異常：{interval:.1f}秒',
                        'timestamp': entries[i+1].timestamp.isoformat(),
                        'severity': 'warning',
                        'details': {
                            'interval_seconds': interval,
                            'average_interval': avg_interval,
                            'threshold': threshold
                        }
                    })

        # 錯誤爆發檢測
        error_entries = [e for e in entries if e.level in ['ERROR', 'CRITICAL']]
        if len(error_entries) > 5:  # 至少 5 個錯誤才檢測
            # 檢查 5 分鐘內的錯誤密度
            window_size = timedelta(minutes=5)
            for i, entry in enumerate(error_entries[:-2]):  # 至少需要 3 個錯誤
                window_end = entry.timestamp + window_size
                errors_in_window = sum(1 for e in error_entries[i:]
                                     if e.timestamp <= window_end)

                if errors_in_window >= 5:  # 5 分鐘內 5 個錯誤
                    anomalies.append({
                        'type': 'error_burst',
                        'description': f'錯誤爆發：5分鐘內{errors_in_window}個錯誤',
                        'timestamp': entry.timestamp.isoformat(),
                        'severity': 'error',
                        'details': {
                            'error_count': errors_in_window,
                            'window_minutes': 5
                        }
                    })
                    break  # 只報告第一個爆發

        return anomalies

    def _analyze_performance(self) -> Dict[str, Any]:
        """分析性能指標"""
        performance_data = {}

        for operation in self.metrics.operation_times.keys():
            stats = self.metrics.get_operation_stats(operation)
            performance_data[operation] = stats

        # 整體統計
        all_operations = list(self.metrics.operation_times.keys())
        total_successes = sum(self.metrics.success_counts.values())
        total_errors = sum(self.metrics.error_counts.values())

        return {
            'operations': performance_data,
            'summary': {
                'total_operations': len(all_operations),
                'total_successes': total_successes,
                'total_errors': total_errors,
                'overall_success_rate': total_successes / (total_successes + total_errors)
                                      if (total_successes + total_errors) > 0 else 0.0
            }
        }

    def generate_report(self, time_range: Optional[Tuple[datetime, datetime]] = None,
                       output_format: str = 'json') -> str:
        """生成分析報告"""
        analysis = self.analyze_directory(time_range)

        if output_format.lower() == 'json':
            return json.dumps(analysis, indent=2, ensure_ascii=False, default=str)

        elif output_format.lower() == 'markdown':
            return self._generate_markdown_report(analysis)

        else:
            raise ValueError(f"不支援的輸出格式: {output_format}")

    def _generate_markdown_report(self, analysis: Dict[str, Any]) -> str:
        """生成 Markdown 格式報告"""
        lines = [
            "# 日誌分析報告",
            "",
            f"**分析時間**: {analysis.get('analysis_timestamp', '')}",
            "",
        ]

        # 摘要
        summary = analysis.get('summary', {})
        if summary:
            lines.extend([
                "## 摘要",
                "",
                f"- **總條目數**: {summary.get('total_entries', 0):,}",
                f"- **分析檔案數**: {analysis.get('analyzed_files', 0)}",
                "",
            ])

            # 時間範圍
            time_range = summary.get('time_range')
            if time_range:
                lines.extend([
                    f"- **時間範圍**: {time_range['start']} 至 {time_range['end']}",
                    "",
                ])

            # 層級分布
            level_dist = summary.get('level_distribution', {})
            if level_dist:
                lines.extend([
                    "### 日誌層級分布",
                    "",
                ])
                for level, count in sorted(level_dist.items()):
                    lines.append(f"- **{level}**: {count:,}")
                lines.append("")

        # 觸發的模式
        triggered = analysis.get('triggered_patterns', [])
        if triggered:
            lines.extend([
                "## 觸發的警告模式",
                "",
            ])
            for pattern in triggered:
                severity_emoji = {
                    'critical': '🔴',
                    'error': '❌',
                    'warning': '⚠️',
                    'info': 'ℹ️'
                }.get(pattern['severity'], '•')

                lines.extend([
                    f"### {severity_emoji} {pattern['name']}",
                    "",
                    f"- **描述**: {pattern['description']}",
                    f"- **嚴重性**: {pattern['severity']}",
                    f"- **匹配次數**: {pattern['match_count']} (閾值: {pattern['threshold']})",
                    "",
                ])

                if pattern.get('recent_matches'):
                    lines.extend([
                        "**最近匹配**:",
                        "",
                    ])
                    for match in pattern['recent_matches']:
                        lines.append(f"- `{match['timestamp']}`: {match['message']}")
                    lines.append("")

        # 異常檢測
        anomalies = analysis.get('anomalies', [])
        if anomalies:
            lines.extend([
                "## 檢測到的異常",
                "",
            ])
            for anomaly in anomalies:
                severity_emoji = {
                    'critical': '🔴',
                    'error': '❌',
                    'warning': '⚠️'
                }.get(anomaly['severity'], '•')

                lines.extend([
                    f"### {severity_emoji} {anomaly['type']}",
                    "",
                    f"- **描述**: {anomaly['description']}",
                    f"- **時間**: {anomaly['timestamp']}",
                    f"- **嚴重性**: {anomaly['severity']}",
                    "",
                ])

        # 性能分析
        performance = analysis.get('performance', {})
        if performance and performance.get('operations'):
            lines.extend([
                "## 性能分析",
                "",
            ])

            perf_summary = performance.get('summary', {})
            if perf_summary:
                lines.extend([
                    f"- **總成功操作**: {perf_summary.get('total_successes', 0):,}",
                    f"- **總失敗操作**: {perf_summary.get('total_errors', 0):,}",
                    f"- **整體成功率**: {perf_summary.get('overall_success_rate', 0):.1%}",
                    "",
                ])

            operations = performance.get('operations', {})
            if operations:
                lines.extend([
                    "### 操作詳細統計",
                    "",
                    "| 操作 | 次數 | 成功率 | 平均時間 | 最短時間 | 最長時間 |",
                    "|------|------|--------|----------|----------|----------|",
                ])

                for op_name, stats in operations.items():
                    lines.append(
                        f"| {op_name} | {stats['count']:,} | "
                        f"{stats['success_rate']:.1%} | "
                        f"{stats['avg_duration']:.2f}s | "
                        f"{stats['min_duration']:.2f}s | "
                        f"{stats['max_duration']:.2f}s |"
                    )
                lines.append("")

        return "\n".join(lines)

    def monitor_realtime(self, callback_func, check_interval: int = 30):
        """即時監控日誌（示例實作）"""
        # 這是一個示例方法，實際實作可能需要使用檔案監控庫如 watchdog
        last_analysis_time = datetime.now()

        while True:
            try:
                # 分析最近的日誌
                current_time = datetime.now()
                time_range = (last_analysis_time, current_time)

                analysis = self.analyze_directory(time_range)

                # 檢查觸發的模式和異常
                alerts = []
                for pattern in analysis.get('triggered_patterns', []):
                    if pattern['severity'] in ['error', 'critical']:
                        alerts.append(pattern)

                for anomaly in analysis.get('anomalies', []):
                    alerts.append(anomaly)

                # 呼叫回調函數
                if alerts:
                    callback_func(alerts)

                last_analysis_time = current_time

                # 等待下次檢查
                import time
                time.sleep(check_interval)

            except KeyboardInterrupt:
                self.logger.info("即時監控已停止")
                break
            except Exception as e:
                self.logger.error(f"即時監控錯誤: {e}")
                import time
                time.sleep(check_interval)


def create_monitoring_dashboard_data(analyzer: LogAnalyzer,
                                   hours_back: int = 24) -> Dict[str, Any]:
    """建立監控儀表板數據"""
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours_back)

    analysis = analyzer.analyze_directory((start_time, end_time))

    # 為儀表板準備數據
    dashboard_data = {
        'status': 'healthy',  # healthy, warning, error
        'last_updated': end_time.isoformat(),
        'time_range_hours': hours_back,
        'metrics': {
            'total_logs': analysis.get('summary', {}).get('total_entries', 0),
            'error_rate': 0.0,
            'warning_count': 0,
            'critical_alerts': 0,
        },
        'trends': {},
        'alerts': [],
        'performance': analysis.get('performance', {}),
    }

    # 計算狀態和指標
    level_dist = analysis.get('summary', {}).get('level_distribution', {})
    total_logs = sum(level_dist.values()) if level_dist else 0
    error_logs = level_dist.get('ERROR', 0) + level_dist.get('CRITICAL', 0)

    if total_logs > 0:
        dashboard_data['metrics']['error_rate'] = error_logs / total_logs

    # 警告和嚴重問題
    triggered_patterns = analysis.get('triggered_patterns', [])
    critical_count = sum(1 for p in triggered_patterns if p['severity'] == 'critical')
    warning_count = sum(1 for p in triggered_patterns if p['severity'] in ['warning', 'error'])

    dashboard_data['metrics']['warning_count'] = warning_count
    dashboard_data['metrics']['critical_alerts'] = critical_count

    # 決定整體狀態
    if critical_count > 0:
        dashboard_data['status'] = 'error'
    elif warning_count > 0 or dashboard_data['metrics']['error_rate'] > 0.1:
        dashboard_data['status'] = 'warning'

    # 活躍警告
    dashboard_data['alerts'] = triggered_patterns + analysis.get('anomalies', [])

    return dashboard_data


if __name__ == "__main__":
    # 測試程式碼
    analyzer = LogAnalyzer("logs")

    # 分析最近 24 小時的日誌
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)

    report = analyzer.generate_report((start_time, end_time), 'markdown')
    print(report)