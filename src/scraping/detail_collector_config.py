#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T5 详情采集器配置文件
包含各种参数和配置选项
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class CollectorConfig:
    """详情采集器配置"""
    
    # 数据库配置
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    
    # API配置
    api_base: str = 'https://api2.liblib.art'
    api_timeout: int = 30
    api_retry_count: int = 3
    api_retry_delay: float = 2.0
    
    # 并发配置
    max_workers: int = 5
    max_concurrent_requests: int = 10
    
    # 限速配置
    requests_per_second: float = 4.0
    delay_between_requests: float = 0.25
    
    # 数据采集配置
    collect_comments: bool = True
    collect_author_info: bool = True
    collect_model_references: bool = True
    
    # 字段校验配置
    strict_validation: bool = False
    skip_invalid_works: bool = True
    
    # 日志配置
    log_level: str = 'INFO'
    log_file: str = 'detail_collector.log'
    log_format: str = '%(asctime)s - %(levelname)s - %(message)s'
    
    # 输出配置
    save_raw_data: bool = True
    raw_data_dir: str = 'raw_data'
    
    @classmethod
    def from_env(cls) -> 'CollectorConfig':
        """从环境变量创建配置"""
        load_dotenv()
        
        return cls(
            db_host=os.getenv('DB_HOST', 'localhost'),
            db_port=int(os.getenv('DB_PORT', '3306')),
            db_name=os.getenv('DB_NAME', 'cardesignspace'),
            db_user=os.getenv('DB_USER', 'root'),
            db_password=os.getenv('DB_PASSWORD', ''),
        )
    
    @classmethod
    def from_file(cls, config_file: str) -> 'CollectorConfig':
        """从配置文件创建配置"""
        import json
        
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"配置文件不存在: {config_file}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        return cls(**config_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'db_host': self.db_host,
            'db_port': self.db_port,
            'db_name': self.db_name,
            'db_user': self.db_user,
            'db_password': self.db_password,
            'api_base': self.api_base,
            'api_timeout': self.api_timeout,
            'api_retry_count': self.api_retry_count,
            'api_retry_delay': self.api_retry_delay,
            'max_workers': self.max_workers,
            'max_concurrent_requests': self.max_concurrent_requests,
            'requests_per_second': self.requests_per_second,
            'delay_between_requests': self.delay_between_requests,
            'collect_comments': self.collect_comments,
            'collect_author_info': self.collect_author_info,
            'collect_model_references': self.collect_model_references,
            'strict_validation': self.strict_validation,
            'skip_invalid_works': self.skip_invalid_works,
            'log_level': self.log_level,
            'log_file': self.log_file,
            'log_format': self.log_format,
            'save_raw_data': self.save_raw_data,
            'raw_data_dir': self.raw_data_dir,
        }
    
    def save_to_file(self, config_file: str):
        """保存配置到文件"""
        import json
        
        # 如果是相对路径，直接创建文件
        if not os.path.dirname(config_file):
            pass
        else:
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        
        print(f"配置已保存到: {config_file}")
    
    def validate(self) -> List[str]:
        """验证配置"""
        errors = []
        
        # 数据库配置验证
        if not self.db_host:
            errors.append("数据库主机地址不能为空")
        if not self.db_name:
            errors.append("数据库名称不能为空")
        if not self.db_user:
            errors.append("数据库用户名不能为空")
        if not self.db_password:
            errors.append("数据库密码不能为空")
        
        # API配置验证
        if self.api_timeout <= 0:
            errors.append("API超时时间必须大于0")
        if self.api_retry_count < 0:
            errors.append("API重试次数不能为负数")
        if self.api_retry_delay < 0:
            errors.append("API重试延迟不能为负数")
        
        # 并发配置验证
        if self.max_workers <= 0:
            errors.append("最大工作线程数必须大于0")
        if self.max_concurrent_requests <= 0:
            errors.append("最大并发请求数必须大于0")
        
        # 限速配置验证
        if self.requests_per_second <= 0:
            errors.append("每秒请求数必须大于0")
        if self.delay_between_requests < 0:
            errors.append("请求间延迟不能为负数")
        
        return errors

# 默认配置
DEFAULT_CONFIG = CollectorConfig(
    db_host='localhost',
    db_port=3306,
    db_name='cardesignspace',
    db_user='root',
    db_password='',
    max_workers=5,
    requests_per_second=4.0,
    collect_comments=True,
    collect_author_info=True,
    strict_validation=False
)

# 开发环境配置
DEV_CONFIG = CollectorConfig(
    db_host='localhost',
    db_port=3306,
    db_name='cardesignspace',
    db_user='root',
    db_password='',
    max_workers=3,
    requests_per_second=2.0,
    collect_comments=True,
    collect_author_info=True,
    strict_validation=False,
    log_level='DEBUG'
)

# 生产环境配置
PROD_CONFIG = CollectorConfig(
    db_host='localhost',
    db_port=3306,
    db_name='cardesignspace',
    db_user='root',
    db_password='',
    max_workers=10,
    requests_per_second=4.0,
    collect_comments=True,
    collect_author_info=True,
    strict_validation=True,
    log_level='INFO'
)

def create_config_file(config_file: str = 'detail_collector_config.json'):
    """创建默认配置文件"""
    config = DEFAULT_CONFIG
    config.save_to_file(config_file)
    return config

def load_config(config_file: str = None) -> CollectorConfig:
    """加载配置"""
    if config_file and os.path.exists(config_file):
        return CollectorConfig.from_file(config_file)
    else:
        return CollectorConfig.from_env()

if __name__ == "__main__":
    # 创建默认配置文件
    config = create_config_file()
    print("✅ 默认配置文件已创建")
    
    # 验证配置
    errors = config.validate()
    if errors:
        print("❌ 配置验证失败:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("✅ 配置验证通过")
    
    # 显示配置信息
    print("\n📋 当前配置:")
    for key, value in config.to_dict().items():
        print(f"   {key}: {value}")
