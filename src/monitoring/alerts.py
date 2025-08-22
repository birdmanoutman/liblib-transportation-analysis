"""
阈值告警接口预留模块

提供可配置的阈值监控和多种告警方式，支持告警规则配置和告警历史记录
"""

import json
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from .logger import get_logger


class AlertLevel(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertRule:
    """告警规则"""
    
    def __init__(
        self,
        name: str,
        metric_name: str,
        threshold: Union[int, float],
        operator: str,  # ">", "<", ">=", "<=", "==", "!="
        level: AlertLevel = AlertLevel.WARNING,
        duration: int = 0,  # 持续时间（秒），0表示立即触发
        cooldown: int = 300,  # 冷却时间（秒），避免重复告警
        description: str = "",
        enabled: bool = True
    ):
        """
        初始化告警规则
        
        Args:
            name: 规则名称
            metric_name: 监控指标名称
            threshold: 阈值
            operator: 比较操作符
            level: 告警级别
            duration: 持续时间（秒）
            cooldown: 冷却时间（秒）
            description: 规则描述
            enabled: 是否启用
        """
        self.name = name
        self.metric_name = metric_name
        self.threshold = threshold
        self.operator = operator
        self.level = level
        self.duration = duration
        self.cooldown = cooldown
        self.description = description
        self.enabled = enabled
        
        self.last_triggered = None
        self.trigger_count = 0
        self.violation_start = None
    
    def check_condition(self, current_value: Union[int, float]) -> bool:
        """检查是否满足告警条件"""
        if not self.enabled:
            return False
        
        # 执行比较操作
        if self.operator == ">":
            condition_met = current_value > self.threshold
        elif self.operator == "<":
            condition_met = current_value < self.threshold
        elif self.operator == ">=":
            condition_met = current_value >= self.threshold
        elif self.operator == "<=":
            condition_met = current_value <= self.threshold
        elif self.operator == "==":
            condition_met = current_value == self.threshold
        elif self.operator == "!=":
            condition_met = current_value != self.threshold
        else:
            return False
        
        # 检查持续时间要求
        if condition_met and self.duration > 0:
            if self.violation_start is None:
                self.violation_start = datetime.now()
            elif (datetime.now() - self.violation_start).total_seconds() >= self.duration:
                return True
            else:
                return False
        elif not condition_met:
            self.violation_start = None
        
        return condition_met
    
    def can_trigger(self) -> bool:
        """检查是否可以触发告警（冷却时间检查）"""
        if self.last_triggered is None:
            return True
        
        return (datetime.now() - self.last_triggered).total_seconds() >= self.cooldown
    
    def trigger(self):
        """触发告警"""
        self.last_triggered = datetime.now()
        self.trigger_count += 1


class AlertChannel(ABC):
    """告警通道抽象基类"""
    
    @abstractmethod
    def send_alert(self, alert: Dict[str, Any]) -> bool:
        """发送告警"""
        pass


class ConsoleAlertChannel(AlertChannel):
    """控制台告警通道"""
    
    def __init__(self, logger=None):
        self.logger = logger or get_logger("alerts")
    
    def send_alert(self, alert: Dict[str, Any]) -> bool:
        """发送控制台告警"""
        try:
            level = alert.get('level', 'INFO')
            message = f"[{level.upper()}] {alert.get('message', '')}"
            
            if level == AlertLevel.CRITICAL.value:
                self.logger.critical(message)
            elif level == AlertLevel.ERROR.value:
                self.logger.error(message)
            elif level == AlertLevel.WARNING.value:
                self.logger.warning(message)
            else:
                self.logger.info(message)
            
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"发送控制台告警失败: {e}")
            return False


class FileAlertChannel(AlertChannel):
    """文件告警通道"""
    
    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def send_alert(self, alert: Dict[str, Any]) -> bool:
        """发送文件告警"""
        try:
            alert_line = json.dumps(alert, ensure_ascii=False, default=str) + "\n"
            
            with open(self.file_path, 'a', encoding='utf-8') as f:
                f.write(alert_line)
            
            return True
        except Exception:
            return False


class EmailAlertChannel(AlertChannel):
    """邮件告警通道（预留接口）"""
    
    def __init__(self, smtp_config: Dict[str, Any]):
        self.smtp_config = smtp_config
        # TODO: 实现SMTP配置和邮件发送逻辑
    
    def send_alert(self, alert: Dict[str, Any]) -> bool:
        """发送邮件告警（预留实现）"""
        # TODO: 实现邮件发送
        return False


class WebhookAlertChannel(AlertChannel):
    """Webhook告警通道（预留接口）"""
    
    def __init__(self, webhook_url: str, headers: Optional[Dict[str, str]] = None):
        self.webhook_url = webhook_url
        self.headers = headers or {}
        # TODO: 实现HTTP请求逻辑
    
    def send_alert(self, alert: Dict[str, Any]) -> bool:
        """发送Webhook告警（预留实现）"""
        # TODO: 实现HTTP POST请求
        return False


class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self.rules: List[AlertRule] = []
        self.channels: List[AlertChannel] = []
        self.alert_history: List[Dict[str, Any]] = []
        self.max_history = 1000
        
        # 默认添加控制台告警通道
        self.add_channel(ConsoleAlertChannel())
        
        self.logger = get_logger("alert_manager")
    
    def add_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.rules.append(rule)
        self.logger.info(f"添加告警规则: {rule.name}")
    
    def add_channel(self, channel: AlertChannel):
        """添加告警通道"""
        self.channels.append(channel)
        self.logger.info(f"添加告警通道: {channel.__class__.__name__}")
    
    def remove_rule(self, rule_name: str):
        """移除告警规则"""
        self.rules = [r for r in self.rules if r.name != rule_name]
        self.logger.info(f"移除告警规则: {rule_name}")
    
    def remove_channel(self, channel: AlertChannel):
        """移除告警通道"""
        self.channels.remove(channel)
        self.logger.info(f"移除告警通道: {channel.__class__.__name__}")
    
    def check_metrics(self, metrics: Dict[str, Union[int, float]]):
        """检查指标并触发告警"""
        for rule in self.rules:
            if rule.metric_name in metrics:
                current_value = metrics[rule.metric_name]
                
                if rule.check_condition(current_value) and rule.can_trigger():
                    self._trigger_alert(rule, current_value)
    
    def _trigger_alert(self, rule: AlertRule, current_value: Union[int, float]):
        """触发告警"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'rule_name': rule.name,
            'metric_name': rule.metric_name,
            'current_value': current_value,
            'threshold': rule.threshold,
            'operator': rule.operator,
            'level': rule.level.value,
            'message': f"指标 {rule.metric_name} 当前值 {current_value} {rule.operator} {rule.threshold}",
            'description': rule.description,
            'trigger_count': rule.trigger_count + 1
        }
        
        # 记录告警历史
        self.alert_history.append(alert)
        if len(self.alert_history) > self.max_history:
            self.alert_history.pop(0)
        
        # 发送到所有通道
        success_count = 0
        for channel in self.channels:
            try:
                if channel.send_alert(alert):
                    success_count += 1
            except Exception as e:
                self.logger.error(f"发送告警到通道 {channel.__class__.__name__} 失败: {e}")
        
        # 更新规则状态
        rule.trigger()
        
        self.logger.info(
            f"触发告警: {rule.name}，"
            f"指标: {rule.metric_name}，"
            f"当前值: {current_value}，"
            f"阈值: {rule.threshold}，"
            f"发送成功: {success_count}/{len(self.channels)}"
        )
    
    def get_alert_history(
        self,
        level: Optional[AlertLevel] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        max_count: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """获取告警历史"""
        filtered_history = self.alert_history
        
        if level:
            filtered_history = [a for a in filtered_history if a['level'] == level.value]
        
        if start_time:
            filtered_history = [a for a in filtered_history if datetime.fromisoformat(a['timestamp']) >= start_time]
        
        if end_time:
            filtered_history = [a for a in filtered_history if datetime.fromisoformat(a['timestamp']) <= end_time]
        
        if max_count:
            filtered_history = filtered_history[-max_count:]
        
        return filtered_history
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """获取告警汇总统计"""
        if not self.alert_history:
            return {}
        
        level_counts = {}
        rule_counts = {}
        
        for alert in self.alert_history:
            level = alert['level']
            rule_name = alert['rule_name']
            
            level_counts[level] = level_counts.get(level, 0) + 1
            rule_counts[rule_name] = rule_counts.get(rule_name, 0) + 1
        
        return {
            'total_alerts': len(self.alert_history),
            'level_distribution': level_counts,
            'rule_distribution': rule_counts,
            'last_alert': self.alert_history[-1]['timestamp'] if self.alert_history else None
        }
    
    def export_alerts_to_json(self, file_path: Union[str, Path]) -> Path:
        """导出告警历史到JSON文件"""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'alert_summary': self.get_alert_summary(),
            'alert_history': self.alert_history,
            'rules': [
                {
                    'name': rule.name,
                    'metric_name': rule.metric_name,
                    'threshold': rule.threshold,
                    'operator': rule.operator,
                    'level': rule.level.value,
                    'description': rule.description,
                    'enabled': rule.enabled,
                    'trigger_count': rule.trigger_count,
                    'last_triggered': rule.last_triggered.isoformat() if rule.last_triggered else None
                }
                for rule in self.rules
            ]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
        
        return file_path
    
    def load_rules_from_config(self, config_file: Union[str, Path]):
        """从配置文件加载告警规则"""
        config_file = Path(config_file)
        if not config_file.exists():
            self.logger.warning(f"配置文件不存在: {config_file}")
            return
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 清空现有规则
            self.rules.clear()
            
            for rule_config in config.get('rules', []):
                rule = AlertRule(
                    name=rule_config['name'],
                    metric_name=rule_config['metric_name'],
                    threshold=rule_config['threshold'],
                    operator=rule_config['operator'],
                    level=AlertLevel(rule_config.get('level', 'warning')),
                    duration=rule_config.get('duration', 0),
                    cooldown=rule_config.get('cooldown', 300),
                    description=rule_config.get('description', ''),
                    enabled=rule_config.get('enabled', True)
                )
                self.rules.append(rule)
            
            self.logger.info(f"从配置文件加载了 {len(self.rules)} 条告警规则")
            
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
    
    def save_rules_to_config(self, config_file: Union[str, Path]):
        """保存告警规则到配置文件"""
        config_file = Path(config_file)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        config = {
            'export_timestamp': datetime.now().isoformat(),
            'rules': [
                {
                    'name': rule.name,
                    'metric_name': rule.metric_name,
                    'threshold': rule.threshold,
                    'operator': rule.operator,
                    'level': rule.level.value,
                    'duration': rule.duration,
                    'cooldown': rule.cooldown,
                    'description': rule.description,
                    'enabled': rule.enabled
                }
                for rule in self.rules
            ]
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"告警规则已保存到配置文件: {config_file}")


# 预定义的告警规则
def get_default_alert_rules() -> List[AlertRule]:
    """获取默认的告警规则"""
    return [
        AlertRule(
            name="高错误率",
            metric_name="error_rate_percent",
            threshold=10.0,
            operator=">",
            level=AlertLevel.WARNING,
            description="错误率超过10%"
        ),
        AlertRule(
            name="低成功率",
            metric_name="success_rate_percent",
            threshold=90.0,
            operator="<",
            level=AlertLevel.WARNING,
            description="成功率低于90%"
        ),
        AlertRule(
            name="高响应时间",
            metric_name="avg_request_time_seconds",
            threshold=5.0,
            operator=">",
            level=AlertLevel.WARNING,
            description="平均响应时间超过5秒"
        ),
        AlertRule(
            name="系统资源紧张",
            metric_name="cpu_percent",
            threshold=80.0,
            operator=">",
            level=AlertLevel.WARNING,
            duration=60,  # 持续1分钟
            description="CPU使用率持续超过80%"
        ),
        AlertRule(
            name="磁盘空间不足",
            metric_name="disk_usage",
            threshold=90.0,
            operator=">",
            level=AlertLevel.CRITICAL,
            description="磁盘使用率超过90%"
        )
    ]


# 全局告警管理器实例
global_alert_manager = AlertManager()

# 添加默认告警规则
for rule in get_default_alert_rules():
    global_alert_manager.add_rule(rule)
