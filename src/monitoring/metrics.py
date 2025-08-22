"""
阶段性统计和指标收集模块

提供爬虫运行过程中的各种统计指标收集和导出功能
"""

import json
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, max_history: int = 1000):
        """
        初始化指标收集器
        
        Args:
            max_history: 最大历史记录数量
        """
        self.max_history = max_history
        self.start_time = None
        self.end_time = None
        
        # 基础统计
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_items = 0
        
        # 时间统计
        self.request_times = deque(maxlen=max_history)
        self.processing_times = deque(maxlen=max_history)
        
        # 错误统计
        self.error_counts = defaultdict(int)
        self.error_details = deque(maxlen=max_history)
        
        # 速率统计
        self.requests_per_minute = deque(maxlen=60)  # 最近60分钟
        self.items_per_minute = deque(maxlen=60)
        
        # 阶段统计
        self.stage_stats = defaultdict(lambda: {
            'start_time': None,
            'end_time': None,
            'total_items': 0,
            'success_count': 0,
            'error_count': 0,
            'duration': 0
        })
        
        # 系统资源统计
        self.system_metrics = deque(maxlen=max_history)
        
        # 限速统计
        self.rate_limit_events = deque(maxlen=max_history)
        
        # 断点统计
        self.checkpoint_stats = {
            'total_checkpoints': 0,
            'successful_resumes': 0,
            'failed_resumes': 0,
            'last_checkpoint': None
        }
    
    def start_session(self):
        """开始新的统计会话"""
        self.start_time = datetime.now()
        self.start_time = datetime.now()
    
    def end_session(self):
        """结束统计会话"""
        self.end_time = datetime.now()
    
    def record_request(self, success: bool, duration: float, items_count: int = 0, error: Optional[Exception] = None):
        """
        记录请求统计
        
        Args:
            success: 请求是否成功
            duration: 请求耗时（秒）
            items_count: 获取的数据项数量
            error: 错误信息
        """
        self.total_requests += 1
        if success:
            self.successful_requests += 1
            self.total_items += items_count
        else:
            self.failed_requests += 1
            if error:
                self.error_counts[type(error).__name__] += 1
                self.error_details.append({
                    'timestamp': datetime.now().isoformat(),
                    'error_type': type(error).__name__,
                    'error_message': str(error),
                    'duration': duration
                })
        
        self.request_times.append(duration)
        
        # 更新速率统计
        current_time = datetime.now()
        self._update_rate_stats(current_time, items_count)
    
    def record_processing_time(self, duration: float):
        """记录处理耗时"""
        self.processing_times.append(duration)
    
    def start_stage(self, stage_name: str):
        """开始一个阶段"""
        self.stage_stats[stage_name]['start_time'] = datetime.now()
    
    def end_stage(self, stage_name: str, success_count: int, error_count: int, total_items: int):
        """结束一个阶段"""
        stage = self.stage_stats[stage_name]
        stage['end_time'] = datetime.now()
        stage['success_count'] = success_count
        stage['error_count'] = error_count
        stage['total_items'] = total_items
        
        if stage['start_time']:
            stage['duration'] = (stage['end_time'] - stage['start_time']).total_seconds()
    
    def record_rate_limit(self, endpoint: str, retry_after: int):
        """记录限速事件"""
        self.rate_limit_events.append({
            'timestamp': datetime.now().isoformat(),
            'endpoint': endpoint,
            'retry_after': retry_after
        })
    
    def record_checkpoint(self, success: bool):
        """记录断点状态"""
        self.checkpoint_stats['total_checkpoints'] += 1
        if success:
            self.checkpoint_stats['successful_resumes'] += 1
        else:
            self.checkpoint_stats['failed_resumes'] += 1
        self.checkpoint_stats['last_checkpoint'] = datetime.now().isoformat()
    
    def record_system_metrics(self, cpu_percent: float, memory_percent: float, disk_usage: float):
        """记录系统资源指标"""
        self.system_metrics.append({
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'disk_usage': disk_usage
        })
    
    def _update_rate_stats(self, current_time: datetime, items_count: int):
        """更新速率统计"""
        minute_key = current_time.replace(second=0, microsecond=0)
        
        # 找到当前分钟的统计
        current_minute_stats = None
        for stats in self.requests_per_minute:
            if stats['minute'] == minute_key:
                current_minute_stats = stats
                break
        
        if current_minute_stats is None:
            current_minute_stats = {
                'minute': minute_key,
                'requests': 0,
                'items': 0
            }
            self.requests_per_minute.append(current_minute_stats)
        
        current_minute_stats['requests'] += 1
        current_minute_stats['items'] += items_count
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """获取汇总统计"""
        if not self.start_time:
            return {}
        
        duration = (self.end_time or datetime.now()) - self.start_time
        duration_seconds = duration.total_seconds()
        
        # 计算平均响应时间
        avg_request_time = sum(self.request_times) / len(self.request_times) if self.request_times else 0
        avg_processing_time = sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
        
        # 计算成功率
        success_rate = (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0
        
        # 计算速率
        requests_per_second = self.total_requests / duration_seconds if duration_seconds > 0 else 0
        items_per_second = self.total_items / duration_seconds if duration_seconds > 0 else 0
        
        return {
            'session_duration_seconds': duration_seconds,
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'total_items': self.total_items,
            'success_rate_percent': round(success_rate, 2),
            'avg_request_time_seconds': round(avg_request_time, 3),
            'avg_processing_time_seconds': round(avg_processing_time, 3),
            'requests_per_second': round(requests_per_second, 2),
            'items_per_second': round(items_per_second, 2),
            'error_distribution': dict(self.error_counts),
            'checkpoint_stats': self.checkpoint_stats.copy()
        }
    
    def get_stage_stats(self) -> Dict[str, Any]:
        """获取阶段统计"""
        return {
            stage: {
                'start_time': stats['start_time'].isoformat() if stats['start_time'] else None,
                'end_time': stats['end_time'].isoformat() if stats['end_time'] else None,
                'duration_seconds': stats['duration'],
                'total_items': stats['total_items'],
                'success_count': stats['success_count'],
                'error_count': stats['error_count'],
                'success_rate_percent': round(
                    stats['success_count'] / (stats['success_count'] + stats['error_count']) * 100, 2
                ) if (stats['success_count'] + stats['error_count']) > 0 else 0
            }
            for stage, stats in self.stage_stats.items()
        }
    
    def get_rate_limit_stats(self) -> Dict[str, Any]:
        """获取限速统计"""
        if not self.rate_limit_events:
            return {}
        
        endpoints = defaultdict(int)
        total_wait_time = 0
        
        for event in self.rate_limit_events:
            endpoints[event['endpoint']] += 1
            total_wait_time += event['retry_after']
        
        return {
            'total_rate_limit_events': len(self.rate_limit_events),
            'endpoint_distribution': dict(endpoints),
            'total_wait_time_seconds': total_wait_time,
            'avg_wait_time_seconds': round(total_wait_time / len(self.rate_limit_events), 2) if self.rate_limit_events else 0
        }
    
    def get_system_metrics_summary(self) -> Dict[str, Any]:
        """获取系统指标汇总"""
        if not self.system_metrics:
            return {}
        
        cpu_values = [m['cpu_percent'] for m in self.system_metrics]
        memory_values = [m['memory_percent'] for m in self.system_metrics]
        disk_values = [m['disk_usage'] for m in self.system_metrics]
        
        return {
            'cpu_percent': {
                'min': min(cpu_values),
                'max': max(cpu_values),
                'avg': round(sum(cpu_values) / len(cpu_values), 2)
            },
            'memory_percent': {
                'min': min(memory_values),
                'max': max(memory_values),
                'avg': round(sum(memory_values) / len(memory_values), 2)
            },
            'disk_usage_percent': {
                'min': min(disk_values),
                'max': max(disk_values),
                'avg': round(sum(disk_values) / len(disk_values), 2)
            }
        }
    
    def export_to_json(self, file_path: Union[str, Path]) -> Path:
        """导出统计到JSON文件"""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'session_info': {
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'end_time': self.end_time.isoformat() if self.end_time else None
            },
            'summary_stats': self.get_summary_stats(),
            'stage_stats': self.get_stage_stats(),
            'rate_limit_stats': self.get_rate_limit_stats(),
            'system_metrics_summary': self.get_system_metrics_summary()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
        
        return file_path
    
    def export_to_excel(self, file_path: Union[str, Path]) -> Path:
        """导出统计到Excel文件"""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # 汇总统计
            summary_df = pd.DataFrame([self.get_summary_stats()])
            summary_df.to_excel(writer, sheet_name='汇总统计', index=False)
            
            # 阶段统计
            stage_df = pd.DataFrame(self.get_stage_stats()).T.reset_index()
            stage_df.rename(columns={'index': '阶段名称'}, inplace=True)
            stage_df.to_excel(writer, sheet_name='阶段统计', index=False)
            
            # 错误详情
            if self.error_details:
                error_df = pd.DataFrame(self.error_details)
                error_df.to_excel(writer, sheet_name='错误详情', index=False)
            
            # 限速事件
            if self.rate_limit_events:
                rate_limit_df = pd.DataFrame(self.rate_limit_events)
                rate_limit_df.to_excel(writer, sheet_name='限速事件', index=False)
            
            # 系统指标
            if self.system_metrics:
                system_df = pd.DataFrame(self.system_metrics)
                system_df.to_excel(writer, sheet_name='系统指标', index=False)
        
        return file_path
    
    def generate_report(self) -> str:
        """生成文本报告"""
        if not self.start_time:
            return "未开始统计会话"
        
        summary = self.get_summary_stats()
        stage_stats = self.get_stage_stats()
        
        report_lines = [
            "=" * 60,
            "Liblib 交通数据采集统计报告",
            "=" * 60,
            f"会话开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"会话结束时间: {self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else '进行中'}",
            f"会话持续时间: {summary.get('session_duration_seconds', 0):.2f} 秒",
            "",
            "汇总统计:",
            f"  总请求数: {summary.get('total_requests', 0)}",
            f"  成功请求: {summary.get('successful_requests', 0)}",
            f"  失败请求: {summary.get('failed_requests', 0)}",
            f"  成功率: {summary.get('success_rate_percent', 0)}%",
            f"  总数据项: {summary.get('total_items', 0)}",
            f"  平均响应时间: {summary.get('avg_request_time_seconds', 0):.3f} 秒",
            f"  请求速率: {summary.get('requests_per_second', 0):.2f} 请求/秒",
            "",
            "阶段统计:"
        ]
        
        for stage, stats in stage_stats.items():
            report_lines.extend([
                f"  {stage}:",
                f"    成功: {stats['success_count']}, 失败: {stats['error_count']}, "
                f"成功率: {stats['success_rate_percent']}%",
                f"    耗时: {stats['duration']:.2f} 秒, 数据项: {stats['total_items']}"
            ])
        
        if self.error_counts:
            report_lines.extend([
                "",
                "错误分布:"
            ])
            for error_type, count in self.error_counts.items():
                report_lines.append(f"  {error_type}: {count}")
        
        report_lines.extend([
            "",
            "=" * 60
        ])
        
        return "\n".join(report_lines)


# 全局指标收集器实例
global_metrics = MetricsCollector()
