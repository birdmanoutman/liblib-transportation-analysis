#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T6 媒体下载器配置文件
支持开发、测试、生产环境配置
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class MediaConfig:
    """媒体下载器配置基类"""
    
    def __init__(self):
        # S3/MinIO配置
        self.storage_driver = os.getenv('STORAGE_DRIVER', 's3')
        self.s3_endpoint = os.getenv('S3_ENDPOINT')
        self.s3_bucket = os.getenv('S3_BUCKET')
        self.s3_region = os.getenv('S3_REGION', 'us-east-1')
        self.s3_access_key = os.getenv('S3_ACCESS_KEY')
        self.s3_secret_key = os.getenv('S3_SECRET_KEY')
        
        # 数据库配置
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_port = int(os.getenv('DB_PORT', '3306'))
        self.db_name = os.getenv('DB_NAME', 'cardesignspace')
        self.db_user = os.getenv('DB_USER', 'root')
        self.db_password = os.getenv('DB_PASSWORD', '')
        
        # 下载配置
        self.max_workers = int(os.getenv('MEDIA_MAX_WORKERS', '10'))
        self.requests_per_second = float(os.getenv('MEDIA_RPS', '5.0'))
        self.max_retries = int(os.getenv('MEDIA_MAX_RETRIES', '3'))
        self.timeout = int(os.getenv('MEDIA_TIMEOUT', '30'))
        
        # 图片处理配置
        self.target_width = int(os.getenv('MEDIA_TARGET_WIDTH', '1024'))
        self.target_format = os.getenv('MEDIA_TARGET_FORMAT', 'webp')
        self.quality = int(os.getenv('MEDIA_QUALITY', '85'))
        
        # 验证配置
        self.verify_size = os.getenv('MEDIA_VERIFY_SIZE', 'true').lower() == 'true'
        self.verify_hash = os.getenv('MEDIA_VERIFY_HASH', 'true').lower() == 'true'
        self.min_file_size = int(os.getenv('MEDIA_MIN_SIZE', '1024'))  # 1KB
        
        # 日志配置
        self.log_level = os.getenv('MEDIA_LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('MEDIA_LOG_FILE', 't6_media_downloader.log')
        
        # 重试配置
        self.retry_delay = float(os.getenv('MEDIA_RETRY_DELAY', '1.0'))
        self.exponential_backoff = os.getenv('MEDIA_EXPONENTIAL_BACKOFF', 'true').lower() == 'true'
        
        # 监控配置
        self.enable_monitoring = os.getenv('MEDIA_ENABLE_MONITORING', 'true').lower() == 'true'
        self.metrics_interval = int(os.getenv('MEDIA_METRICS_INTERVAL', '60'))  # 秒

class DevConfig(MediaConfig):
    """开发环境配置"""
    
    def __init__(self):
        super().__init__()
        
        # 开发环境特定配置
        self.max_workers = 5
        self.requests_per_second = 2.0
        self.max_retries = 2
        self.timeout = 15
        
        # 开发环境日志级别
        self.log_level = 'DEBUG'
        
        # 开发环境验证配置
        self.verify_size = True
        self.verify_hash = True
        self.min_file_size = 512  # 512B
        
        # 开发环境监控
        self.enable_monitoring = False

class TestConfig(MediaConfig):
    """测试环境配置"""
    
    def __init__(self):
        super().__init__()
        
        # 测试环境特定配置
        self.max_workers = 8
        self.requests_per_second = 3.0
        self.max_retries = 3
        self.timeout = 20
        
        # 测试环境日志级别
        self.log_level = 'INFO'
        
        # 测试环境验证配置
        self.verify_size = True
        self.verify_hash = True
        self.min_file_size = 1024  # 1KB
        
        # 测试环境监控
        self.enable_monitoring = True
        self.metrics_interval = 30

class ProdConfig(MediaConfig):
    """生产环境配置"""
    
    def __init__(self):
        super().__init__()
        
        # 生产环境特定配置
        self.max_workers = 20
        self.requests_per_second = 8.0
        self.max_retries = 5
        self.timeout = 45
        
        # 生产环境日志级别
        self.log_level = 'WARNING'
        
        # 生产环境验证配置
        self.verify_size = True
        self.verify_hash = True
        self.min_file_size = 2048  # 2KB
        
        # 生产环境监控
        self.enable_monitoring = True
        self.metrics_interval = 60

def load_media_config(env: str = None) -> MediaConfig:
    """加载媒体下载器配置"""
    if not env:
        env = os.getenv('MEDIA_ENV', 'dev').lower()
    
    config_map = {
        'dev': DevConfig,
        'test': TestConfig,
        'prod': ProdConfig,
        'production': ProdConfig
    }
    
    config_class = config_map.get(env, DevConfig)
    return config_class()

def validate_config(config: MediaConfig) -> Dict[str, Any]:
    """验证配置有效性"""
    validation_results = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    # 检查S3配置
    if not config.s3_endpoint:
        validation_results['valid'] = False
        validation_results['errors'].append('S3_ENDPOINT 未配置')
    
    if not config.s3_bucket:
        validation_results['valid'] = False
        validation_results['errors'].append('S3_BUCKET 未配置')
    
    if not config.s3_access_key:
        validation_results['valid'] = False
        validation_results['errors'].append('S3_ACCESS_KEY 未配置')
    
    if not config.s3_secret_key:
        validation_results['valid'] = False
        validation_results['errors'].append('S3_SECRET_KEY 未配置')
    
    # 检查数据库配置
    if not config.db_host:
        validation_results['warnings'].append('DB_HOST 未配置，使用默认值 localhost')
    
    if not config.db_name:
        validation_results['warnings'].append('DB_NAME 未配置，使用默认值 cardesignspace')
    
    # 检查下载配置
    if config.max_workers <= 0:
        validation_results['valid'] = False
        validation_results['errors'].append('MEDIA_MAX_WORKERS 必须大于0')
    
    if config.requests_per_second <= 0:
        validation_results['valid'] = False
        validation_results['errors'].append('MEDIA_RPS 必须大于0')
    
    if config.max_retries < 0:
        validation_results['valid'] = False
        validation_results['errors'].append('MEDIA_MAX_RETRIES 不能为负数')
    
    # 检查图片处理配置
    if config.target_width <= 0:
        validation_results['valid'] = False
        validation_results['errors'].append('MEDIA_TARGET_WIDTH 必须大于0')
    
    if config.quality < 1 or config.quality > 100:
        validation_results['valid'] = False
        validation_results['errors'].append('MEDIA_QUALITY 必须在1-100之间')
    
    return validation_results

def print_config_summary(config: MediaConfig):
    """打印配置摘要"""
    print("=" * 60)
    print("T6 媒体下载器配置摘要")
    print("=" * 60)
    
    print(f"环境: {os.getenv('MEDIA_ENV', 'dev')}")
    print(f"存储驱动: {config.storage_driver}")
    print(f"S3端点: {config.s3_endpoint}")
    print(f"S3存储桶: {config.s3_bucket}")
    print(f"最大工作线程: {config.max_workers}")
    print(f"请求速率: {config.requests_per_second} RPS")
    print(f"最大重试次数: {config.max_retries}")
    print(f"目标图片宽度: {config.target_width}")
    print(f"目标图片格式: {config.target_format}")
    print(f"图片质量: {config.quality}")
    print(f"验证文件大小: {config.verify_size}")
    print(f"验证文件哈希: {config.verify_hash}")
    print(f"最小文件大小: {config.min_file_size} bytes")
    print(f"日志级别: {config.log_level}")
    print(f"启用监控: {config.enable_monitoring}")
    print("=" * 60)

if __name__ == "__main__":
    # 测试配置加载
    env = os.getenv('MEDIA_ENV', 'dev')
    config = load_media_config(env)
    
    # 打印配置摘要
    print_config_summary(config)
    
    # 验证配置
    validation = validate_config(config)
    if validation['valid']:
        print("✅ 配置验证通过")
    else:
        print("❌ 配置验证失败:")
        for error in validation['errors']:
            print(f"   - {error}")
    
    if validation['warnings']:
        print("⚠️  配置警告:")
        for warning in validation['warnings']:
            print(f"   - {warning}")
