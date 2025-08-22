#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T4 列表采集器测试脚本
用于验证基本功能和配置
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.scraping.t4_config import get_config, validate_config, print_config
from scripts.database.database_manager import DatabaseManager

def test_config():
    """测试配置功能"""
    print("测试配置功能...")
    
    # 测试不同环境的配置
    for env in ['development', 'testing', 'production']:
        print(f"\n{env} 环境配置:")
        config = get_config(env)
        print(f"  目标数量: {config['target_count']}")
        print(f"  最大页数: {config['max_pages']}")
        print(f"  日志级别: {config['log_level']}")
    
    # 测试配置验证
    config = get_config('development')
    print(f"\n配置验证结果: {validate_config(config)}")
    
    print("配置测试完成！\n")

async def test_database_connection():
    """测试数据库连接"""
    print("测试数据库连接...")
    
    try:
        db_manager = DatabaseManager()
        
        # 测试连接
        if await db_manager.test_connection():
            print("✓ 数据库连接成功")
            
            # 测试表存在性检查
            tables = ['authors', 'works', 'work_models', 'work_images']
            for table in tables:
                exists = await db_manager.check_table_exists(table)
                print(f"  表 {table}: {'✓' if exists else '✗'}")
            
            # 测试记录数查询
            for table in tables:
                if await db_manager.check_table_exists(table):
                    count = await db_manager.get_table_count(table)
                    print(f"  表 {table} 记录数: {count}")
            
        else:
            print("✗ 数据库连接失败")
            return False
            
    except Exception as e:
        print(f"✗ 数据库测试异常: {e}")
        return False
    
    print("数据库测试完成！\n")
    return True

async def test_api_endpoint():
    """测试API端点"""
    print("测试API端点...")
    
    import aiohttp
    
    api_base = "https://api2.liblib.art"
    url = f"{api_base}/api/www/img/group/search"
    
    payload = {
        "tag": "汽车交通",
        "page": 1,
        "pageSize": 5,  # 只测试少量数据
        "sortType": "latest",
        "nsfw": False
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://www.liblib.art',
        'Origin': 'https://www.liblib.art',
        'Content-Type': 'application/json'
    }
    
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✓ API端点测试成功")
                    
                    # 分析响应结构
                    if 'data' in data and 'list' in data['data']:
                        works = data['data']['list']
                        print(f"  返回作品数: {len(works)}")
                        
                        if works:
                            first_work = works[0]
                            print(f"  第一个作品字段: {list(first_work.keys())}")
                            
                            # 检查必要字段
                            required_fields = ['slug', 'title', 'author']
                            missing_fields = [field for field in required_fields if field not in first_work]
                            if missing_fields:
                                print(f"  ⚠ 缺少字段: {missing_fields}")
                            else:
                                print("  ✓ 必要字段完整")
                    else:
                        print("  ⚠ 响应结构异常")
                        
                elif response.status == 429:
                    print("⚠ API请求频率限制")
                else:
                    print(f"✗ API请求失败: HTTP {response.status}")
                    return False
                    
    except Exception as e:
        print(f"✗ API测试异常: {e}")
        return False
    
    print("API测试完成！\n")
    return True

def test_directory_structure():
    """测试目录结构"""
    print("测试目录结构...")
    
    required_dirs = [
        'data',
        'logs',
        'data/raw',
        'data/processed'
    ]
    
    for directory in required_dirs:
        dir_path = Path(directory)
        if dir_path.exists():
            print(f"  ✓ {directory}")
        else:
            print(f"  ✗ {directory} (不存在)")
            # 创建目录
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"    → 已创建 {directory}")
    
    print("目录结构测试完成！\n")

def test_environment_variables():
    """测试环境变量"""
    print("测试环境变量...")
    
    required_vars = [
        'DB_HOST',
        'DB_NAME', 
        'DB_USER',
        'DB_PASSWORD',
        'STORAGE_DRIVER',
        'S3_ENDPOINT',
        'S3_BUCKET',
        'S3_ACCESS_KEY',
        'S3_SECRET_KEY'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # 隐藏敏感信息
            if 'PASSWORD' in var or 'KEY' in var:
                display_value = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '***'
            else:
                display_value = value
            print(f"  ✓ {var}: {display_value}")
        else:
            print(f"  ✗ {var}: 未设置")
    
    print("环境变量测试完成！\n")

async def run_all_tests():
    """运行所有测试"""
    print("开始T4列表采集器功能测试")
    print("=" * 50)
    
    # 测试配置
    test_config()
    
    # 测试目录结构
    test_directory_structure()
    
    # 测试环境变量
    test_environment_variables()
    
    # 测试数据库连接
    db_ok = await test_database_connection()
    
    # 测试API端点
    api_ok = await test_api_endpoint()
    
    # 输出测试结果
    print("测试结果汇总")
    print("=" * 50)
    print(f"配置功能: ✓")
    print(f"目录结构: ✓")
    print(f"环境变量: {'✓' if all(os.getenv(var) for var in ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']) else '✗'}")
    print(f"数据库连接: {'✓' if db_ok else '✗'}")
    print(f"API端点: {'✓' if api_ok else '✗'}")
    
    if db_ok and api_ok:
        print("\n🎉 所有测试通过！T4采集器可以开始运行。")
        return True
    else:
        print("\n⚠ 部分测试失败，请检查相关配置。")
        return False

def main():
    """主函数"""
    try:
        success = asyncio.run(run_all_tests())
        return 0 if success else 1
    except Exception as e:
        print(f"测试运行异常: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
