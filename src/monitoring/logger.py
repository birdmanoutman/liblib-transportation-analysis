"""
结构化日志记录器

提供JSON格式的结构化日志，支持多种输出目标和日志级别
"""

import json
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

import psutil


class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器，输出JSON格式"""
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为JSON字符串"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": record.process,
            "thread_id": record.thread,
        }
        
        # 添加异常信息
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # 添加额外字段
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)
        
        # 添加系统信息
        if hasattr(record, "include_system_info") and record.include_system_info:
            log_entry["system_info"] = self._get_system_info()
        
        return json.dumps(log_entry, ensure_ascii=False, default=str)
    
    def _get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
            }
        except Exception:
            return {"error": "Failed to get system info"}


class StructuredLogger:
    """结构化日志记录器"""
    
    def __init__(
        self,
        name: str,
        log_file: Optional[Union[str, Path]] = None,
        console_output: bool = True,
        log_level: str = "INFO",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        include_system_info: bool = False
    ):
        """
        初始化结构化日志记录器
        
        Args:
            name: 日志记录器名称
            log_file: 日志文件路径，None表示不输出到文件
            console_output: 是否输出到控制台
            log_level: 日志级别
            max_bytes: 单个日志文件最大字节数
            backup_count: 保留的备份文件数量
            include_system_info: 是否包含系统信息
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # 避免重复添加处理器
        if self.logger.handlers:
            return
        
        formatter = StructuredFormatter()
        
        # 控制台输出
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # 文件输出
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_path,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def _log_with_extra(
        self,
        level: int,
        message: str,
        extra_fields: Optional[Dict[str, Any]] = None,
        include_system_info: bool = False,
        **kwargs
    ):
        """记录带额外字段的日志"""
        extra = kwargs.copy()
        if extra_fields:
            extra["extra_fields"] = extra_fields
        if include_system_info:
            extra["include_system_info"] = True
        
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """记录DEBUG级别日志"""
        self._log_with_extra(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """记录INFO级别日志"""
        self._log_with_extra(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """记录WARNING级别日志"""
        self._log_with_extra(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """记录ERROR级别日志"""
        self._log_with_extra(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """记录CRITICAL级别日志"""
        self._log_with_extra(logging.CRITICAL, message, **kwargs)
    
    def log_scraping_start(self, target: str, total_pages: int, **kwargs):
        """记录爬虫开始日志"""
        extra_fields = {
            "event_type": "scraping_start",
            "target": target,
            "total_pages": total_pages,
            "start_time": datetime.now().isoformat()
        }
        self.info(f"开始爬取 {target}，共 {total_pages} 页", extra_fields=extra_fields, **kwargs)
    
    def log_scraping_progress(self, current_page: int, total_pages: int, success_count: int, error_count: int, **kwargs):
        """记录爬虫进度日志"""
        extra_fields = {
            "event_type": "scraping_progress",
            "current_page": current_page,
            "total_pages": total_pages,
            "success_count": success_count,
            "error_count": error_count,
            "progress_percent": round(current_page / total_pages * 100, 2)
        }
        self.info(
            f"爬取进度: {current_page}/{total_pages} ({extra_fields['progress_percent']}%)，"
            f"成功: {success_count}，失败: {error_count}",
            extra_fields=extra_fields, **kwargs
        )
    
    def log_scraping_complete(self, target: str, total_pages: int, success_count: int, error_count: int, duration: float, **kwargs):
        """记录爬虫完成日志"""
        extra_fields = {
            "event_type": "scraping_complete",
            "target": target,
            "total_pages": total_pages,
            "success_count": success_count,
            "error_count": error_count,
            "duration_seconds": duration,
            "success_rate": round(success_count / (success_count + error_count) * 100, 2) if (success_count + error_count) > 0 else 0
        }
        self.info(
            f"爬取完成: {target}，成功: {success_count}，失败: {error_count}，"
            f"成功率: {extra_fields['success_rate']}%，耗时: {duration:.2f}秒",
            extra_fields=extra_fields, **kwargs
        )
    
    def log_error(self, error: Exception, context: str, **kwargs):
        """记录错误日志"""
        extra_fields = {
            "event_type": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }
        self.error(f"错误: {context} - {error}", extra_fields=extra_fields, **kwargs)
    
    def log_rate_limit(self, endpoint: str, retry_after: int, **kwargs):
        """记录限速日志"""
        extra_fields = {
            "event_type": "rate_limit",
            "endpoint": endpoint,
            "retry_after": retry_after
        }
        self.warning(f"触发限速: {endpoint}，等待 {retry_after} 秒", extra_fields=extra_fields, **kwargs)


def get_logger(
    name: str,
    log_file: Optional[Union[str, Path]] = None,
    console_output: bool = True,
    log_level: str = "INFO"
) -> StructuredLogger:
    """
    获取结构化日志记录器
    
    Args:
        name: 日志记录器名称
        log_file: 日志文件路径
        console_output: 是否输出到控制台
        log_level: 日志级别
    
    Returns:
        StructuredLogger实例
    """
    return StructuredLogger(name, log_file, console_output, log_level)


# 默认日志记录器
default_logger = get_logger("liblib_transportation")
