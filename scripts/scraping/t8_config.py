#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T8 断点续采与失败补偿模块配置文件
"""

import os
from typing import Dict, Any

# 基础配置
BASE_CONFIG = {
    # 状态管理配置
    'state_dir': 'data/state',           # 状态文件目录
    'max_workers': 5,                    # 最大重试工作线程数
    
    # 重试配置
    'retry_check_interval': 30,          # 重试检查间隔（秒）
    'max_retry_delay': 3600,            # 最大重试延迟（秒）
    'enable_auto_retry': True,           # 启用自动重试
    'enable_integrity_check': True,      # 启用完整性检查
    
    # 断点续采配置
    'resume_point_ttl': 86400 * 7,      # 断点续采点TTL（7天）
    'max_resume_points': 100,            # 最大断点续采点数量
    
    # 失败任务配置
    'max_failed_tasks': 1000,            # 最大失败任务数量
    'failed_task_ttl': 86400 * 30,      # 失败任务TTL（30天）
    
    # 数据完整性配置
    'integrity_check_interval': 300,     # 完整性检查间隔（秒）
    'enable_duplicate_detection': True,  # 启用重复检测
    'enable_missing_detection': True,    # 启用缺失检测
    
    # 日志配置
    'log_level': 'INFO',
    'log_file': 'logs/t8_resume_retry.log',
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    
    # 监控配置
    'enable_metrics': True,              # 启用指标收集
    'metrics_interval': 60,              # 指标收集间隔（秒）
    'alert_thresholds': {
        'failed_task_ratio': 0.1,        # 失败任务比例阈值
        'retry_success_rate': 0.8,       # 重试成功率阈值
        'data_integrity_score': 0.95     # 数据完整性分数阈值
    }
}

# 环境特定配置
ENV_CONFIGS = {
    'development': {
        'max_workers': 3,
        'retry_check_interval': 60,
        'enable_metrics': False,
        'log_level': 'DEBUG'
    },
    'testing': {
        'max_workers': 2,
        'retry_check_interval': 120,
        'enable_metrics': True,
        'log_level': 'INFO'
    },
    'production': {
        'max_workers': 10,
        'retry_check_interval': 15,
        'enable_metrics': True,
        'log_level': 'WARNING'
    }
}

def get_config(env: str = None) -> Dict[str, Any]:
    """获取配置"""
    if env is None:
        env = os.getenv('T8_ENV', 'development')
    
    config = BASE_CONFIG.copy()
    
    if env in ENV_CONFIGS:
        config.update(ENV_CONFIGS[env])
    
    # 环境变量覆盖
    for key in config:
        env_key = f'T8_{key.upper()}'
        if env_key in os.environ:
            value = os.environ[env_key]
            # 类型转换
            if isinstance(config[key], bool):
                config[key] = value.lower() in ('true', '1', 'yes', 'on')
            elif isinstance(config[key], int):
                config[key] = int(value)
            elif isinstance(config[key], float):
                config[key] = float(value)
            else:
                config[key] = value
    
    return config

def validate_config(config: Dict[str, Any]) -> bool:
    """验证配置"""
    try:
        # 验证必要字段
        required_fields = ['state_dir', 'max_workers', 'retry_check_interval']
        for field in required_fields:
            if field not in config:
                print(f"配置验证失败：缺少必要字段 {field}")
                return False
        
        # 验证数值范围
        if config['max_workers'] < 1 or config['max_workers'] > 50:
            print(f"配置验证失败：max_workers 必须在 1-50 范围内")
            return False
        
        if config['retry_check_interval'] < 5 or config['retry_check_interval'] > 3600:
            print(f"配置验证失败：retry_check_interval 必须在 5-3600 秒范围内")
            return False
        
        if config['max_retry_delay'] < 60 or config['max_retry_delay'] > 86400:
            print(f"配置验证失败：max_retry_delay 必须在 60-86400 秒范围内")
            return False
        
        return True
        
    except Exception as e:
        print(f"配置验证异常：{e}")
        return False

def print_config(config: Dict[str, Any]):
    """打印配置信息"""
    print("T8 断点续采与失败补偿模块配置：")
    print("=" * 50)
    
    for key, value in config.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for sub_key, sub_value in value.items():
                print(f"  {sub_key}: {sub_value}")
        else:
            print(f"{key}: {value}")
    
    print("=" * 50)

if __name__ == "__main__":
    # 测试配置
    config = get_config()
    print_config(config)
    
    if validate_config(config):
        print("配置验证通过")
    else:
        print("配置验证失败")
