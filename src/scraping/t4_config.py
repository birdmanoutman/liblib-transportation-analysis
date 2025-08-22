#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T4 列表采集器配置文件
"""

import os
from typing import Dict, Any

# 基础配置
BASE_CONFIG = {
    # 采集目标
    'target_count': 1000,        # 目标采集数量
    'start_page': 1,             # 起始页
    'max_pages': None,           # 最大页数限制（None表示无限制）
    'page_size': 24,             # 每页大小
    
    # 速率限制
    'max_requests_per_second': 4,  # 最大请求频率（RPS）
    'max_concurrent': 5,           # 最大并发数
    
    # 重试配置
    'max_retries': 3,            # 最大重试次数
    'retry_delay': 5,            # 重试延迟（秒）
    'backoff_factor': 2,         # 退避因子
    
    # 请求配置
    'request_timeout': 30,       # 请求超时时间（秒）
    'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
    
    # 标签配置
    'target_tag': '汽车交通',     # 目标标签
    'sort_type': 'latest',       # 排序方式：latest, popular, random
    
    # 数据存储
    'state_file': 'data/fetch_state.json',
    'slug_queue_file': 'data/slug_queue.json',
    'fetch_queue_file': 'data/fetch_queue.txt',
    
    # 日志配置
    'log_level': 'INFO',
    'log_file': 'logs/t4_list_collector.log',
    
    # 断点续采配置
    'enable_resume': True,       # 启用断点续采
    'resume_threshold': 100,     # 断点续采阈值（页数）
    
    # 数据验证
    'min_slug_length': 5,        # 最小slug长度
    'required_fields': ['slug', 'title', 'author_name'],  # 必填字段
}

# 环境特定配置
ENV_CONFIGS = {
    'development': {
        'target_count': 100,     # 开发环境减少目标数量
        'max_pages': 5,          # 限制页数
        'log_level': 'DEBUG',
    },
    'testing': {
        'target_count': 50,      # 测试环境更少数量
        'max_pages': 3,
        'log_level': 'DEBUG',
    },
    'production': {
        'target_count': 1000,    # 生产环境完整数量
        'max_pages': None,
        'log_level': 'INFO',
    }
}

def get_config(env: str = None) -> Dict[str, Any]:
    """获取配置"""
    if not env:
        env = os.getenv('ENV', 'development')
    
    config = BASE_CONFIG.copy()
    
    if env in ENV_CONFIGS:
        config.update(ENV_CONFIGS[env])
    
    # 环境变量覆盖
    for key in config:
        env_key = f'T4_{key.upper()}'
        if os.getenv(env_key):
            try:
                # 尝试转换类型
                if isinstance(config[key], bool):
                    config[key] = os.getenv(env_key).lower() in ('true', '1', 'yes')
                elif isinstance(config[key], int):
                    config[key] = int(os.getenv(env_key))
                elif isinstance(config[key], float):
                    config[key] = float(os.getenv(env_key))
                else:
                    config[key] = os.getenv(env_key)
            except (ValueError, TypeError):
                logger.warning(f"环境变量 {env_key} 类型转换失败，使用默认值")
    
    return config

def validate_config(config: Dict[str, Any]) -> bool:
    """验证配置有效性"""
    errors = []
    
    # 检查必要字段
    if config['target_count'] <= 0:
        errors.append("target_count 必须大于0")
    
    if config['start_page'] < 1:
        errors.append("start_page 必须大于等于1")
    
    if config['max_pages'] is not None and config['max_pages'] < config['start_page']:
        errors.append("max_pages 必须大于等于 start_page")
    
    if config['page_size'] <= 0 or config['page_size'] > 100:
        errors.append("page_size 必须在1-100之间")
    
    if config['max_requests_per_second'] <= 0:
        errors.append("max_requests_per_second 必须大于0")
    
    if config['max_concurrent'] <= 0:
        errors.append("max_concurrent 必须大于0")
    
    if errors:
        print("配置验证失败:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True

def print_config(config: Dict[str, Any]):
    """打印配置信息"""
    print("T4 列表采集器配置:")
    print("=" * 50)
    
    categories = {
        '采集目标': ['target_count', 'start_page', 'max_pages', 'page_size'],
        '速率限制': ['max_requests_per_second', 'max_concurrent'],
        '重试配置': ['max_retries', 'retry_delay', 'backoff_factor'],
        '请求配置': ['request_timeout', 'target_tag', 'sort_type'],
        '数据存储': ['state_file', 'slug_queue_file', 'fetch_queue_file'],
        '断点续采': ['enable_resume', 'resume_threshold']
    }
    
    for category, keys in categories.items():
        print(f"\n{category}:")
        for key in keys:
            if key in config:
                value = config[key]
                if isinstance(value, str) and len(value) > 50:
                    value = value[:47] + "..."
                print(f"  {key}: {value}")

if __name__ == "__main__":
    # 测试配置
    config = get_config()
    print_config(config)
    
    if validate_config(config):
        print("\n配置验证通过！")
    else:
        print("\n配置验证失败！")
