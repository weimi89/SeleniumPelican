#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
監控服務

提供日誌監控、警報通知和健康檢查功能。
支援多種通知方式和自定義監控規則。
"""

import asyncio
import json
import smtplib
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
import threading

from .log_analyzer import LogAnalyzer, create_monitoring_dashboard_data
from .logging_config import get_logger


class AlertChannel:
    """警報通道基礎類別"""

    def __init__(self, name: str):
        self.name = name
        self.enabled = True

    async def send_alert(self, alert: Dict[str, Any]) -> bool:
        """發送警報（需要子類實作）"""
        raise NotImplementedError

    def format_alert_message(self, alert: Dict[str, Any]) -> str:
        """格式化警報訊息"""
        severity_emoji = {
            'critical': '🔴',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        }.get(alert.get('severity', 'info'), '•')

        timestamp = alert.get('timestamp', datetime.now().isoformat())
        name = alert.get('name', alert.get('type', 'Unknown'))
        description = alert.get('description', '')

        return f"{severity_emoji} **{name}**\n時間: {timestamp}\n描述: {description}"


class EmailAlertChannel(AlertChannel):
    """電子郵件警報通道"""

    def __init__(self, smtp_host: str, smtp_port: int, username: str,
                 password: str, from_email: str, to_emails: List[str]):
        super().__init__("email")
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails

    async def send_alert(self, alert: Dict[str, Any]) -> bool:
        """發送電子郵件警報"""
        try:
            msg = MimeMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = f"SeleniumPelican 警報: {alert.get('name', 'Alert')}"

            body = self._format_email_body(alert)
            msg.attach(MimeText(body, 'plain', 'utf-8'))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            return True
        except Exception as e:
            print(f"Failed to send email alert: {e}")
            return False

    def _format_email_body(self, alert: Dict[str, Any]) -> str:
        """格式化電子郵件內容"""
        lines = [
            "SeleniumPelican 系統警報",
            "=" * 40,
            "",
            f"警報名稱: {alert.get('name', 'Unknown')}",
            f"嚴重性: {alert.get('severity', 'info')}",
            f"時間: {alert.get('timestamp', datetime.now().isoformat())}",
            f"描述: {alert.get('description', '')}",
            "",
        ]

        if 'details' in alert:
            lines.extend([
                "詳細資訊:",
                json.dumps(alert['details'], indent=2, ensure_ascii=False),
                "",
            ])

        if 'recent_matches' in alert:
            lines.extend([
                "最近匹配:",
            ])
            for match in alert['recent_matches']:
                lines.append(f"  - {match.get('timestamp', '')}: {match.get('message', '')}")
            lines.append("")

        lines.extend([
            "",
            "此警報由 SeleniumPelican 監控系統自動生成。",
        ])

        return "\n".join(lines)


class WebhookAlertChannel(AlertChannel):
    """Webhook 警報通道"""

    def __init__(self, webhook_url: str, headers: Optional[Dict[str, str]] = None):
        super().__init__("webhook")
        self.webhook_url = webhook_url
        self.headers = headers or {}

    async def send_alert(self, alert: Dict[str, Any]) -> bool:
        """發送 Webhook 警報"""
        try:
            import aiohttp

            payload = {
                'alert': alert,
                'timestamp': datetime.now().isoformat(),
                'source': 'SeleniumPelican'
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers=self.headers
                ) as response:
                    return response.status < 400
        except Exception as e:
            print(f"Failed to send webhook alert: {e}")
            return False


class FileAlertChannel(AlertChannel):
    """檔案警報通道"""

    def __init__(self, alert_file: Union[str, Path]):
        super().__init__("file")
        self.alert_file = Path(alert_file)
        self.alert_file.parent.mkdir(parents=True, exist_ok=True)

    async def send_alert(self, alert: Dict[str, Any]) -> bool:
        """將警報寫入檔案"""
        try:
            alert_entry = {
                'timestamp': datetime.now().isoformat(),
                'alert': alert
            }

            with open(self.alert_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(alert_entry, ensure_ascii=False) + '\n')

            return True
        except Exception as e:
            print(f"Failed to write alert to file: {e}")
            return False


class MonitoringRule:
    """監控規則"""

    def __init__(self, name: str, condition_func: Callable[[Dict[str, Any]], bool],
                 severity: str = 'warning', description: str = '',
                 cooldown_minutes: int = 30):
        self.name = name
        self.condition_func = condition_func
        self.severity = severity
        self.description = description
        self.cooldown_minutes = cooldown_minutes
        self.last_triggered = None

    def check(self, analysis_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """檢查規則是否觸發"""
        # 檢查冷卻時間
        if self.last_triggered:
            cooldown_end = self.last_triggered + timedelta(minutes=self.cooldown_minutes)
            if datetime.now() < cooldown_end:
                return None

        # 檢查條件
        if self.condition_func(analysis_data):
            self.last_triggered = datetime.now()
            return {
                'name': self.name,
                'severity': self.severity,
                'description': self.description,
                'timestamp': self.last_triggered.isoformat(),
                'type': 'monitoring_rule',
                'triggered_by': 'custom_rule'
            }

        return None


class MonitoringService:
    """監控服務主類別"""

    def __init__(self, log_analyzer: LogAnalyzer, config_file: Optional[str] = None):
        self.logger = get_logger("monitoring_service")
        self.analyzer = log_analyzer
        self.alert_channels: List[AlertChannel] = []
        self.monitoring_rules: List[MonitoringRule] = []
        self.is_running = False
        self.monitoring_thread = None
        self.check_interval = 300  # 5 分鐘
        self.config = self._load_config(config_file)

        # 初始化預設規則
        self._initialize_default_rules()

    def _load_config(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """載入監控配置"""
        default_config = {
            'check_interval_seconds': 300,
            'alert_channels': [],
            'rules': [],
            'dashboard': {
                'enabled': True,
                'update_interval_seconds': 60
            }
        }

        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                default_config.update(config)
            except Exception as e:
                self.logger.warning(f"載入監控配置失敗: {e}")

        return default_config

    def _initialize_default_rules(self):
        """初始化預設監控規則"""

        # 高錯誤率規則
        def high_error_rate(data):
            metrics = data.get('metrics', {})
            return metrics.get('error_rate', 0) > 0.15  # 超過 15% 錯誤率

        self.add_rule(MonitoringRule(
            "high_error_rate",
            high_error_rate,
            "error",
            "錯誤率過高（超過15%）",
            cooldown_minutes=15
        ))

        # 嚴重錯誤規則
        def critical_alerts(data):
            metrics = data.get('metrics', {})
            return metrics.get('critical_alerts', 0) > 0

        self.add_rule(MonitoringRule(
            "critical_alerts",
            critical_alerts,
            "critical",
            "檢測到嚴重錯誤",
            cooldown_minutes=5
        ))

        # 長時間無日誌規則
        def no_recent_logs(data):
            last_updated = data.get('last_updated')
            if last_updated:
                try:
                    last_time = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                    return (datetime.now() - last_time) > timedelta(hours=2)
                except ValueError:
                    return True
            return True

        self.add_rule(MonitoringRule(
            "no_recent_logs",
            no_recent_logs,
            "warning",
            "超過2小時無新日誌",
            cooldown_minutes=60
        ))

    def add_alert_channel(self, channel: AlertChannel):
        """添加警報通道"""
        self.alert_channels.append(channel)
        self.logger.info(f"已添加警報通道: {channel.name}")

    def add_rule(self, rule: MonitoringRule):
        """添加監控規則"""
        self.monitoring_rules.append(rule)
        self.logger.info(f"已添加監控規則: {rule.name}")

    async def send_alert(self, alert: Dict[str, Any]):
        """發送警報到所有通道"""
        self.logger.warning(f"發送警報: {alert.get('name', 'Unknown')}")

        for channel in self.alert_channels:
            if channel.enabled:
                try:
                    success = await channel.send_alert(alert)
                    if success:
                        self.logger.info(f"警報已發送到 {channel.name}")
                    else:
                        self.logger.error(f"發送警報到 {channel.name} 失敗")
                except Exception as e:
                    self.logger.error(f"發送警報到 {channel.name} 時發生錯誤: {e}")

    def start_monitoring(self):
        """開始監控"""
        if self.is_running:
            self.logger.warning("監控服務已在運行")
            return

        self.is_running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("監控服務已啟動")

    def stop_monitoring(self):
        """停止監控"""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        self.logger.info("監控服務已停止")

    def _monitoring_loop(self):
        """監控主循環"""
        while self.is_running:
            try:
                # 執行監控檢查
                asyncio.run(self._perform_monitoring_check())

                # 等待下次檢查
                time.sleep(self.check_interval)

            except Exception as e:
                self.logger.error(f"監控循環錯誤: {e}")
                time.sleep(60)  # 錯誤後等待 1 分鐘

    async def _perform_monitoring_check(self):
        """執行一次監控檢查"""
        try:
            # 獲取儀表板數據
            dashboard_data = create_monitoring_dashboard_data(self.analyzer, hours_back=1)

            # 檢查所有規則
            alerts_to_send = []

            for rule in self.monitoring_rules:
                alert = rule.check(dashboard_data)
                if alert:
                    alerts_to_send.append(alert)

            # 檢查分析器產生的警報
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=self.check_interval // 60)

            analysis = self.analyzer.analyze_directory((start_time, end_time))

            # 添加觸發的模式警報
            for pattern in analysis.get('triggered_patterns', []):
                if pattern['severity'] in ['error', 'critical']:
                    alerts_to_send.append(pattern)

            # 添加異常檢測警報
            for anomaly in analysis.get('anomalies', []):
                alerts_to_send.append(anomaly)

            # 發送所有警報
            for alert in alerts_to_send:
                await self.send_alert(alert)

            # 記錄監控狀態
            if alerts_to_send:
                self.logger.warning(f"監控檢查完成，發現 {len(alerts_to_send)} 個警報")
            else:
                self.logger.debug("監控檢查完成，一切正常")

        except Exception as e:
            self.logger.error(f"執行監控檢查時發生錯誤: {e}")

    def get_monitoring_status(self) -> Dict[str, Any]:
        """取得監控狀態"""
        return {
            'is_running': self.is_running,
            'check_interval': self.check_interval,
            'alert_channels': [
                {
                    'name': channel.name,
                    'enabled': channel.enabled
                }
                for channel in self.alert_channels
            ],
            'monitoring_rules': [
                {
                    'name': rule.name,
                    'severity': rule.severity,
                    'description': rule.description,
                    'last_triggered': rule.last_triggered.isoformat() if rule.last_triggered else None
                }
                for rule in self.monitoring_rules
            ],
            'last_check': datetime.now().isoformat(),
        }

    def create_dashboard_html(self, output_file: str = "monitoring_dashboard.html"):
        """建立監控儀表板 HTML 檔案"""
        dashboard_data = create_monitoring_dashboard_data(self.analyzer)

        html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SeleniumPelican 監控儀表板</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .dashboard {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 14px;
            font-weight: 500;
        }}
        .status-healthy {{ background-color: #d4edda; color: #155724; }}
        .status-warning {{ background-color: #fff3cd; color: #856404; }}
        .status-error {{ background-color: #f8d7da; color: #721c24; }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        .metric-label {{
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }}
        .alerts-section {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .alert-item {{
            padding: 12px;
            margin: 8px 0;
            border-left: 4px solid #ddd;
            background: #f8f9fa;
        }}
        .alert-critical {{ border-left-color: #dc3545; }}
        .alert-error {{ border-left-color: #fd7e14; }}
        .alert-warning {{ border-left-color: #ffc107; }}
        .refresh-info {{
            color: #666;
            font-size: 12px;
            text-align: center;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>SeleniumPelican 監控儀表板</h1>
            <div class="status-badge status-{dashboard_data['status']}">{dashboard_data['status'].upper()}</div>
            <p>最後更新: {dashboard_data['last_updated']}</p>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{dashboard_data['metrics']['total_logs']:,}</div>
                <div class="metric-label">總日誌數量</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{dashboard_data['metrics']['error_rate']:.1%}</div>
                <div class="metric-label">錯誤率</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{dashboard_data['metrics']['warning_count']}</div>
                <div class="metric-label">警告數量</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{dashboard_data['metrics']['critical_alerts']}</div>
                <div class="metric-label">嚴重警報</div>
            </div>
        </div>

        <div class="alerts-section">
            <h2>活躍警報</h2>
            {self._generate_alerts_html(dashboard_data.get('alerts', []))}
        </div>
    </div>

    <div class="refresh-info">
        頁面每 30 秒自動重新整理
    </div>

    <script>
        setTimeout(() => {{
            location.reload();
        }}, 30000);
    </script>
</body>
</html>
        """

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        self.logger.info(f"儀表板已生成: {output_file}")

    def _generate_alerts_html(self, alerts: List[Dict[str, Any]]) -> str:
        """生成警報 HTML"""
        if not alerts:
            return "<p>目前沒有活躍警報</p>"

        html_parts = []
        for alert in alerts[:10]:  # 只顯示前 10 個警報
            severity = alert.get('severity', 'info')
            name = alert.get('name', alert.get('type', 'Unknown'))
            description = alert.get('description', '')
            timestamp = alert.get('timestamp', '')

            html_parts.append(f"""
            <div class="alert-item alert-{severity}">
                <strong>{name}</strong>
                <p>{description}</p>
                <small>{timestamp}</small>
            </div>
            """)

        return "\n".join(html_parts)


def create_monitoring_service_from_config(config_file: str) -> MonitoringService:
    """從配置檔案建立監控服務"""
    analyzer = LogAnalyzer()
    service = MonitoringService(analyzer, config_file)

    # 根據配置添加警報通道（這裡需要根據實際配置實作）
    # 示例：添加檔案警報通道
    file_channel = FileAlertChannel("logs/alerts.jsonl")
    service.add_alert_channel(file_channel)

    return service


if __name__ == "__main__":
    # 測試程式碼
    analyzer = LogAnalyzer("logs")
    service = MonitoringService(analyzer)

    # 添加檔案警報通道
    file_channel = FileAlertChannel("logs/alerts.jsonl")
    service.add_alert_channel(file_channel)

    # 執行一次檢查
    import asyncio
    asyncio.run(service._perform_monitoring_check())

    # 生成儀表板
    service.create_dashboard_html()

    print("監控服務測試完成")