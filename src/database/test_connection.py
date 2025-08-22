#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接测试脚本
验证本地/远程MySQL连接
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_database_connection():
    """测试数据库连接"""
    # 加载环境变量
    load_dotenv()
    
    # 数据库连接配置
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    
    # 显示连接信息（隐藏密码）
    safe_config = db_config.copy()
    safe_config['password'] = '***' if safe_config['password'] else 'None'
    logger.info(f"数据库连接配置: {safe_config}")
    
    try:
        logger.info("正在连接数据库...")
        connection = mysql.connector.connect(**db_config)
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            logger.info(f"✅ 成功连接到MySQL服务器")
            logger.info(f"   服务器版本: {db_info}")
            
            cursor = connection.cursor()
            
            # 获取数据库信息
            cursor.execute("SELECT DATABASE();")
            database = cursor.fetchone()
            logger.info(f"   当前数据库: {database[0]}")
            
            # 获取MySQL版本信息
            cursor.execute("SELECT VERSION();")
            version = cursor.fetchone()
            logger.info(f"   MySQL版本: {version[0]}")
            
            # 测试基本查询
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = %s", (db_config['database'],))
            table_count = cursor.fetchone()
            logger.info(f"   数据库中的表数量: {table_count[0]}")
            
            # 显示现有表
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            if tables:
                logger.info("   现有表:")
                for table in tables:
                    logger.info(f"     - {table[0]}")
            else:
                logger.info("   数据库中没有表")
            
            cursor.close()
            connection.close()
            logger.info("✅ 数据库连接测试成功")
            return True
            
        else:
            logger.error("❌ 无法连接到数据库")
            return False
            
    except Error as e:
        logger.error(f"❌ 连接数据库时出错: {e}")
        return False

def test_s3_connection():
    """测试S3连接（可选）"""
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        # 加载环境变量
        load_dotenv()
        
        s3_config = {
            'endpoint_url': os.getenv('S3_ENDPOINT'),
            'aws_access_key_id': os.getenv('S3_ACCESS_KEY'),
            'aws_secret_access_key': os.getenv('S3_SECRET_KEY'),
            'region_name': os.getenv('S3_REGION', 'us-east-1')
        }
        
        logger.info("正在测试S3连接...")
        
        # 创建S3客户端
        s3_client = boto3.client('s3', **s3_config)
        
        # 测试列出bucket
        response = s3_client.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        
        logger.info(f"✅ S3连接测试成功")
        logger.info(f"   可用bucket: {buckets}")
        
        # 测试指定bucket
        target_bucket = os.getenv('S3_BUCKET')
        if target_bucket:
            try:
                s3_client.head_bucket(Bucket=target_bucket)
                logger.info(f"   ✅ 目标bucket '{target_bucket}' 可访问")
            except ClientError as e:
                logger.warning(f"   ⚠️  目标bucket '{target_bucket}' 不可访问: {e}")
        
        return True
        
    except ImportError:
        logger.warning("⚠️  boto3未安装，跳过S3连接测试")
        return False
    except Exception as e:
        logger.error(f"❌ S3连接测试失败: {e}")
        return False

def main():
    """主函数"""
    logger.info("开始数据库连接测试")
    logger.info("=" * 50)
    
    # 测试数据库连接
    db_success = test_database_connection()
    
    logger.info("=" * 50)
    
    # 测试S3连接
    s3_success = test_s3_connection()
    
    logger.info("=" * 50)
    
    if db_success:
        logger.info("🎉 数据库连接测试完成！")
        logger.info("   可以继续执行数据库迁移脚本")
    else:
        logger.error("💥 数据库连接测试失败！")
        logger.error("   请检查环境变量和网络连接")
    
    return db_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
