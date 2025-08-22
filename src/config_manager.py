#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
支持配置文件加载、命令行参数覆盖和配置验证

功能特性：
- 📁 多级配置文件支持
- 🔧 命令行参数覆盖
- ✅ 配置验证和默认值
- 🌍 环境变量支持
- 📝 配置模板生成
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
import argparse

@dataclass
class ConfigManager:
    """配置管理器"""
    
    config_file: Optional[str] = None
    config_data: Dict[str, Any] = field(default_factory=dict)
    logger: Optional[logging.Logger] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.logger:
            self.logger = logging.getLogger(__name__)
    
    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """加载配置文件
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
            
        Returns:
            配置字典
        """
        if config_path:
            self.config_file = config_path
        elif not self.config_file:
            # 查找配置文件
            self.config_file = self._find_config_file()
        
        defaults = self._get_default_config()
        if self.config_file and os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                # 深度合并：以 loaded 覆盖 defaults
                self.config_data = self._merge_config(defaults, loaded)
                self.logger.info(f"配置文件加载成功: {self.config_file}")
            except Exception as e:
                self.logger.error(f"配置文件加载失败: {e}")
                self.config_data = defaults
        else:
            self.logger.info("使用默认配置")
            self.config_data = defaults
        
        # 应用环境变量覆盖
        self._apply_environment_overrides()
        # 同步扁平派生键，确保覆盖后也生效
        self._sync_derived_keys()
        
        return self.config_data

    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """深度合并配置，override 覆盖 base。"""
        result = base.copy()
        for key, value in (override or {}).items():
            if isinstance(value, dict) and isinstance(result.get(key), dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        # 维护派生扁平键，确保 Analyzer 可用
        result["api_base"] = result.get("api_base") or result.get("api", {}).get("base_url")
        result["base_url"] = result.get("base_url") or "https://www.liblib.art"
        result["page_size"] = result.get("page_size") or result.get("scraping", {}).get("page_size", 24)
        result["max_workers"] = result.get("max_workers") or result.get("scraping", {}).get("max_workers", 4)
        if not result.get("car_keywords"):
            result["car_keywords"] = result.get("tags", {}).get("enabled", [])
        return result

    def _sync_derived_keys(self) -> None:
        """从嵌套配置同步生成 Analyzer 使用的扁平键。"""
        api = self.config_data.get("api", {}) or {}
        scraping = self.config_data.get("scraping", {}) or {}
        tags = self.config_data.get("tags", {}) or {}
        if api.get("base_url"):
            self.config_data["api_base"] = api.get("base_url")
        if not self.config_data.get("base_url"):
            self.config_data["base_url"] = "https://www.liblib.art"
        if scraping.get("page_size") and not self.config_data.get("page_size"):
            self.config_data["page_size"] = scraping.get("page_size")
        if scraping.get("max_workers") and not self.config_data.get("max_workers"):
            self.config_data["max_workers"] = scraping.get("max_workers")
        if not self.config_data.get("car_keywords"):
            self.config_data["car_keywords"] = tags.get("enabled", [])
    
    def _find_config_file(self) -> Optional[str]:
        """查找配置文件
        
        优先级：
        1. 当前目录的 config.json
        2. 当前目录的 config/default.json
        3. 用户主目录的 .liblib/config.json
        """
        search_paths = [
            "config.json",
            "config/default.json",
            os.path.expanduser("~/.liblib/config.json")
        ]
        
        for path in search_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        cfg = {
            "api": {
                "base_url": "https://api2.liblib.art",
                "timeout": 30,
                "retry_times": 3,
                "retry_delay": 2
            },
            "scraping": {
                "page_size": 48,
                "max_pages": 10,
                "delay_between_pages": 1,
                "max_workers": 4
            },
            "tags": {
                "enabled": ["汽车", "车", "跑车", "超跑", "轿车", "SUV"],
                "disabled": [],
                "custom_keywords": []
            },
            "sorting": {
                "field": "downloads",
                "order": "desc",
                "available_fields": ["downloads", "likes", "created_at", "updated_at", "name"]
            },
            "download": {
                "concurrent_downloads": 5,
                "image_formats": ["jpg", "png", "webp"],
                "retry_times": 3,
                "skip_existing": True
            },
            "storage": {
                "output_dir": "liblib_analysis_output",
                "images_dir": "images",
                "data_dir": "data",
                "reports_dir": "reports",
                "logs_dir": "logs"
            },
            "analysis": {
                "include_charts": True,
                "report_format": "markdown",
                "language": "zh"
            },
            "logging": {
                "level": "INFO",
                "file_logging": True,
                "console_logging": True
            }
        }

        # 兼容 Analyzer 直接访问的扁平键
        cfg["api_base"] = cfg["api"]["base_url"]
        cfg["base_url"] = "https://www.liblib.art"
        cfg["page_size"] = cfg["scraping"]["page_size"]
        cfg["max_workers"] = cfg["scraping"]["max_workers"]
        cfg["car_keywords"] = cfg["tags"]["enabled"]

        return cfg
    
    def _apply_environment_overrides(self):
        """应用环境变量覆盖"""
        env_mappings = {
            "LIBLIB_API_BASE_URL": ("api", "base_url"),
            "LIBLIB_TIMEOUT": ("api", "timeout"),
            "LIBLIB_COOKIE": ("api", "cookie"),
            "LIBLIB_MAX_WORKERS": ("scraping", "max_workers"),
            "LIBLIB_OUTPUT_DIR": ("storage", "output_dir"),
            "LIBLIB_CONCURRENT_DOWNLOADS": ("download", "concurrent_downloads"),
            "LIBLIB_LOG_LEVEL": ("logging", "level")
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                self._set_nested_value(config_path, env_value)
                self.logger.debug(f"环境变量覆盖: {env_var} = {env_value}")
    
    def _set_nested_value(self, path: tuple, value: Any):
        """设置嵌套配置值"""
        current = self.config_data
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # 类型转换
        if isinstance(current.get(path[-1]), bool):
            if isinstance(value, str):
                value = value.lower() in ('true', '1', 'yes', 'on')
        elif isinstance(current.get(path[-1]), int):
            try:
                value = int(value)
            except (ValueError, TypeError):
                pass
        elif isinstance(current.get(path[-1]), float):
            try:
                value = float(value)
            except (ValueError, TypeError):
                pass
        
        current[path[-1]] = value
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """获取配置值
        
        Args:
            key_path: 配置键路径，如 "api.base_url"
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key_path.split('.')
        current = self.config_data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current
    
    def set(self, key_path: str, value: Any):
        """设置配置值
        
        Args:
            key_path: 配置键路径，如 "api.base_url"
            value: 配置值
        """
        keys = key_path.split('.')
        current = self.config_data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def update_from_args(self, args: argparse.Namespace):
        """从命令行参数更新配置
        
        Args:
            args: 解析后的命令行参数
        """
        # 标签相关
        if hasattr(args, 'tags') and args.tags:
            self.set('tags.enabled', args.tags.split(','))
        
        if hasattr(args, 'exclude_tags') and args.exclude_tags:
            self.set('tags.disabled', args.exclude_tags.split(','))
        
        if hasattr(args, 'custom_keywords') and args.custom_keywords:
            self.set('tags.custom_keywords', args.custom_keywords.split(','))
        
        # 排序相关
        if hasattr(args, 'sort_by') and args.sort_by:
            if args.sort_by in self.get('sorting.available_fields', []):
                self.set('sorting.field', args.sort_by)
            else:
                self.logger.warning(f"不支持的排序字段: {args.sort_by}")
        
        if hasattr(args, 'sort_order') and args.sort_order:
            if args.sort_order in ['asc', 'desc']:
                self.set('sorting.order', args.sort_order)
            else:
                self.logger.warning(f"不支持的排序顺序: {args.sort_order}")
        
        # 页范围相关
        if hasattr(args, 'max_pages') and args.max_pages:
            self.set('scraping.max_pages', args.max_pages)
        
        if hasattr(args, 'page_size') and args.page_size:
            self.set('scraping.page_size', args.page_size)
        
        # 并发相关
        if hasattr(args, 'max_workers') and args.max_workers:
            self.set('scraping.max_workers', args.max_workers)
        
        if hasattr(args, 'concurrent_downloads') and args.concurrent_downloads:
            self.set('download.concurrent_downloads', args.concurrent_downloads)
        
        # 存储路径相关
        if hasattr(args, 'output_dir') and args.output_dir:
            self.set('storage.output_dir', args.output_dir)
        
        if hasattr(args, 'images_dir') and args.images_dir:
            self.set('storage.images_dir', args.images_dir)
        
        # 日志相关
        if hasattr(args, 'log_level') and args.log_level:
            self.set('logging.level', args.log_level.upper())
        
        if hasattr(args, 'verbose') and args.verbose:
            self.set('logging.level', 'DEBUG')
    
    def validate_config(self) -> List[str]:
        """验证配置
        
        Returns:
            错误信息列表
        """
        errors = []
        
        # 验证API配置
        if not self.get('api.base_url'):
            errors.append("API基础URL不能为空")
        
        if self.get('api.timeout', 0) <= 0:
            errors.append("API超时时间必须大于0")
        
        # 验证爬取配置
        if self.get('scraping.max_pages', 0) <= 0:
            errors.append("最大页数必须大于0")
        
        if self.get('scraping.page_size', 0) <= 0:
            errors.append("页大小必须大于0")
        
        if self.get('scraping.max_workers', 0) <= 0:
            errors.append("最大工作线程数必须大于0")
        
        # 验证下载配置
        if self.get('download.concurrent_downloads', 0) <= 0:
            errors.append("并发下载数必须大于0")
        
        # 验证标签配置
        enabled_tags = self.get('tags.enabled', [])
        if not enabled_tags:
            errors.append("至少需要启用一个标签")
        
        # 验证排序配置
        sort_field = self.get('sorting.field')
        available_fields = self.get('sorting.available_fields', [])
        if sort_field and sort_field not in available_fields:
            errors.append(f"不支持的排序字段: {sort_field}")
        
        return errors
    
    def save_config(self, file_path: Optional[str] = None) -> bool:
        """保存配置到文件
        
        Args:
            file_path: 文件路径，如果为None则使用当前配置文件路径
            
        Returns:
            是否保存成功
        """
        if not file_path:
            file_path = self.config_file or "config.json"
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"配置已保存到: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"配置保存失败: {e}")
            return False
    
    def create_config_template(self, file_path: str = "config_template.json") -> bool:
        """创建配置模板文件
        
        Args:
            file_path: 模板文件路径
            
        Returns:
            是否创建成功
        """
        template_config = self._get_default_config()
        
        # 添加注释说明
        template_config["_comment"] = {
            "api": "API相关配置",
            "scraping": "数据采集配置",
            "tags": "标签和关键词配置",
            "sorting": "排序配置",
            "download": "下载配置",
            "storage": "存储路径配置",
            "analysis": "分析配置",
            "logging": "日志配置"
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(template_config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"配置模板已创建: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"配置模板创建失败: {e}")
            return False
    
    def get_effective_config(self) -> Dict[str, Any]:
        """获取有效配置（包含所有默认值）"""
        return self.config_data.copy()
    
    def print_config_summary(self):
        """打印配置摘要"""
        print("\n📋 当前配置摘要:")
        print("=" * 50)
        
        # API配置
        print(f"🌐 API基础URL: {self.get('api.base_url')}")
        print(f"⏱️  超时时间: {self.get('api.timeout')}秒")
        
        # 爬取配置
        print(f"📄 最大页数: {self.get('scraping.max_pages')}")
        print(f"📊 页大小: {self.get('scraping.page_size')}")
        print(f"🔄 最大工作线程: {self.get('scraping.max_workers')}")
        
        # 标签配置
        enabled_tags = self.get('tags.enabled', [])
        print(f"🏷️  启用标签: {', '.join(enabled_tags[:5])}{'...' if len(enabled_tags) > 5 else ''}")
        
        # 排序配置
        print(f"📈 排序字段: {self.get('sorting.field')}")
        print(f"📊 排序顺序: {self.get('sorting.order')}")
        
        # 下载配置
        print(f"⬇️  并发下载: {self.get('download.concurrent_downloads')}")
        
        # 存储配置
        print(f"📁 输出目录: {self.get('storage.output_dir')}")
        
        print("=" * 50)
