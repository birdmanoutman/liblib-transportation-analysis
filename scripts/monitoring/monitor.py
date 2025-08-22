"""
监控系统核心模块

整合结构化日志、指标收集和阈值告警功能，提供统一的监控接口
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import psutil

from .alerts import global_alert_manager, AlertLevel
from .logger import get_logger, StructuredLogger
from .metrics import global_metrics, MetricsCollector


class MonitoringSystem:
    """监控系统核心类"""
    
    def __init__(
        self,
        system_name: str = "liblib_transportation",
        log_file: Optional[Union[str, Path]] = None,
        metrics_file: Optional[Union[str, Path]] = None,
        alerts_file: Optional[Union[str, Path]] = None,
        enable_system_monitoring: bool = True,
        system_monitoring_interval: int = 30  # 秒
    ):
        """
        初始化监控系统
        
        Args:
            system_name: 系统名称
            log_file: 日志文件路径
            metrics_file: 指标文件路径
            alerts_file: 告警文件路径
            enable_system_monitoring: 是否启用系统资源监控
            system_monitoring_interval: 系统监控间隔（秒）
        """
        self.system_name = system_name
        self.log_file = Path(log_file) if log_file else None
        self.metrics_file = Path(metrics_file) if metrics_file else None
        self.alerts_file = Path(alerts_file) if alerts_file else None
        
        # 初始化日志记录器
        self.logger = get_logger(
            name=system_name,
            log_file=log_file,
            console_output=True,
            log_level="INFO"
        )
        
        # 初始化指标收集器
        self.metrics = global_metrics
        self.metrics.start_session()
        
        # 初始化告警管理器
        self.alerts = global_alert_manager
        
        # 系统监控相关
        self.enable_system_monitoring = enable_system_monitoring
        self.system_monitoring_interval = system_monitoring_interval
        self.last_system_check = None
        
        # 监控状态
        self.is_monitoring = False
        self.monitoring_start_time = None
        
        self.logger.info(f"监控系统 {system_name} 初始化完成")
    
    def start_monitoring(self):
        """开始监控"""
        if self.is_monitoring:
            self.logger.warning("监控系统已在运行中")
            return
        
        self.is_monitoring = True
        self.monitoring_start_time = datetime.now()
        self.metrics.start_session()
        
        self.logger.info("监控系统已启动")
        
        # 启动系统资源监控
        if self.enable_system_monitoring:
            self._start_system_monitoring()
    
    def stop_monitoring(self):
        """停止监控"""
        if not self.is_monitoring:
            self.logger.warning("监控系统未在运行")
            return
        
        self.is_monitoring = False
        self.metrics.end_session()
        
        # 记录最终统计
        self._record_final_stats()
        
        self.logger.info("监控系统已停止")
    
    def _start_system_monitoring(self):
        """启动系统资源监控"""
        if not self.enable_system_monitoring:
            return
        
        try:
            # 记录初始系统状态
            self._record_system_metrics()
            self.last_system_check = datetime.now()
            
            self.logger.info("系统资源监控已启动")
        except Exception as e:
            self.logger.error(f"启动系统资源监控失败: {e}")
    
    def _record_system_metrics(self):
        """记录系统资源指标"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage('/').percent
            
            self.metrics.record_system_metrics(cpu_percent, memory_percent, disk_usage)
            
            # 检查是否需要触发告警
            current_metrics = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_usage': disk_usage
            }
            
            self.alerts.check_metrics(current_metrics)
            
        except Exception as e:
            self.logger.error(f"记录系统指标失败: {e}")
    
    def _record_final_stats(self):
        """记录最终统计信息"""
        try:
            summary = self.metrics.get_summary_stats()
            stage_stats = self.metrics.get_stage_stats()
            
            self.logger.info("监控会话统计汇总", extra_fields={
                'event_type': 'monitoring_summary',
                'summary': summary,
                'stage_stats': stage_stats
            })
            
        except Exception as e:
            self.logger.error(f"记录最终统计失败: {e}")
    
    def log_scraping_event(self, event_type: str, **kwargs):
        """记录爬虫事件"""
        if event_type == "start":
            self.metrics.start_stage(kwargs.get('stage_name', 'scraping'))
            self.logger.log_scraping_start(
                target=kwargs.get('target', 'unknown'),
                total_pages=kwargs.get('total_pages', 0)
            )
        elif event_type == "progress":
            self.logger.log_scraping_progress(
                current_page=kwargs.get('current_page', 0),
                total_pages=kwargs.get('total_pages', 0),
                success_count=kwargs.get('success_count', 0),
                error_count=kwargs.get('error_count', 0)
            )
        elif event_type == "complete":
            stage_name = kwargs.get('stage_name', 'scraping')
            self.metrics.end_stage(
                stage_name=stage_name,
                success_count=kwargs.get('success_count', 0),
                error_count=kwargs.get('error_count', 0),
                total_items=kwargs.get('total_items', 0)
            )
            
            duration = kwargs.get('duration', 0)
            self.logger.log_scraping_complete(
                target=kwargs.get('target', 'unknown'),
                total_pages=kwargs.get('total_pages', 0),
                success_count=kwargs.get('success_count', 0),
                error_count=kwargs.get('error_count', 0),
                duration=duration
            )
    
    def record_request(self, success: bool, duration: float, items_count: int = 0, error: Optional[Exception] = None):
        """记录请求统计"""
        self.metrics.record_request(success, duration, items_count, error)
        
        if error:
            self.logger.log_error(error, "请求处理")
    
    def record_rate_limit(self, endpoint: str, retry_after: int):
        """记录限速事件"""
        self.metrics.record_rate_limit(endpoint, retry_after)
        self.logger.log_rate_limit(endpoint, retry_after)
    
    def record_checkpoint(self, success: bool):
        """记录断点状态"""
        self.metrics.record_checkpoint(success)
    
    def add_alert_rule(self, rule):
        """添加告警规则"""
        self.alerts.add_rule(rule)
    
    def add_alert_channel(self, channel):
        """添加告警通道"""
        self.alerts.add_channel(channel)
    
    def check_alerts(self, metrics: Dict[str, Union[int, float]]):
        """检查指标并触发告警"""
        self.alerts.check_metrics(metrics)
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """获取监控汇总信息"""
        return {
            'system_name': self.system_name,
            'is_monitoring': self.is_monitoring,
            'monitoring_start_time': self.monitoring_start_time.isoformat() if self.monitoring_start_time else None,
            'metrics_summary': self.metrics.get_summary_stats(),
            'stage_stats': self.metrics.get_stage_stats(),
            'alert_summary': self.alerts.get_alert_summary(),
            'system_metrics': self.metrics.get_system_metrics_summary()
        }
    
    def export_all_data(
        self,
        export_dir: Union[str, Path],
        include_logs: bool = True,
        include_metrics: bool = True,
        include_alerts: bool = True
    ) -> Dict[str, Path]:
        """导出所有监控数据"""
        export_dir = Path(export_dir)
        export_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exported_files = {}
        
        try:
            # 导出指标数据
            if include_metrics:
                metrics_file = export_dir / f"{self.system_name}_metrics_{timestamp}.json"
                exported_files['metrics'] = self.metrics.export_to_json(metrics_file)
                
                metrics_excel = export_dir / f"{self.system_name}_metrics_{timestamp}.xlsx"
                exported_files['metrics_excel'] = self.metrics.export_to_excel(metrics_excel)
            
            # 导出告警数据
            if include_alerts:
                alerts_file = export_dir / f"{self.system_name}_alerts_{timestamp}.json"
                exported_files['alerts'] = self.alerts.export_alerts_to_json(alerts_file)
            
            # 导出监控汇总
            summary_file = export_dir / f"{self.system_name}_summary_{timestamp}.json"
            summary_data = {
                'export_timestamp': datetime.now().isoformat(),
                'monitoring_summary': self.get_monitoring_summary()
            }
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, ensure_ascii=False, indent=2, default=str)
            
            exported_files['summary'] = summary_file
            
            # 生成文本报告
            report_file = export_dir / f"{self.system_name}_report_{timestamp}.txt"
            report_content = self.metrics.generate_report()
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            exported_files['report'] = report_file
            
            self.logger.info(f"监控数据导出完成，共导出 {len(exported_files)} 个文件到 {export_dir}")
            
        except Exception as e:
            self.logger.error(f"导出监控数据失败: {e}")
            raise
        
        return exported_files
    
    def periodic_system_check(self):
        """定期系统检查（应在主循环中调用）"""
        if not self.is_monitoring or not self.enable_system_monitoring:
            return
        
        current_time = datetime.now()
        if (self.last_system_check is None or 
            (current_time - self.last_system_check).total_seconds() >= self.system_monitoring_interval):
            
            self._record_system_metrics()
            self.last_system_check = current_time
    
    def cleanup(self):
        """清理资源"""
        try:
            if self.is_monitoring:
                self.stop_monitoring()
            
            # 清理日志处理器
            if hasattr(self.logger, 'logger'):
                for handler in self.logger.logger.handlers[:]:
                    handler.close()
                    self.logger.logger.removeHandler(handler)
            
            self.logger.info("监控系统资源清理完成")
            
        except Exception as e:
            print(f"清理监控系统资源时出错: {e}")


class MonitoringContext:
    """监控上下文管理器"""
    
    def __init__(self, monitoring_system: MonitoringSystem):
        self.monitoring_system = monitoring_system
    
    def __enter__(self):
        self.monitoring_system.start_monitoring()
        return self.monitoring_system
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.monitoring_system.logger.error(f"监控会话异常退出: {exc_val}")
        self.monitoring_system.stop_monitoring()


def create_monitoring_system(
    system_name: str = "liblib_transportation",
    config: Optional[Dict[str, Any]] = None
) -> MonitoringSystem:
    """
    创建监控系统实例
    
    Args:
        system_name: 系统名称
        config: 配置字典
    
    Returns:
        MonitoringSystem实例
    """
    if config is None:
        config = {}
    
    # 设置默认配置
    default_config = {
        'log_file': f"logs/{system_name}.log",
        'metrics_file': f"data/monitoring/{system_name}_metrics.json",
        'alerts_file': f"data/monitoring/{system_name}_alerts.json",
        'enable_system_monitoring': True,
        'system_monitoring_interval': 30
    }
    
    # 合并配置
    final_config = {**default_config, **config}
    
    # 创建监控系统
    monitoring_system = MonitoringSystem(
        system_name=system_name,
        log_file=final_config['log_file'],
        metrics_file=final_config['metrics_file'],
        alerts_file=final_config['alerts_file'],
        enable_system_monitoring=final_config['enable_system_monitoring'],
        system_monitoring_interval=final_config['system_monitoring_interval']
    )
    
    return monitoring_system


# 全局监控系统实例
global_monitoring_system = create_monitoring_system()


def get_global_monitoring() -> MonitoringSystem:
    """获取全局监控系统实例"""
    return global_monitoring_system
