#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
表验证脚本
检查工单T3创建的表是否存在
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def verify_tables():
    """验证表是否存在"""
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
    
    try:
        logger.info("正在连接数据库...")
        connection = mysql.connector.connect(**db_config)
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # 我们需要的表
            required_tables = [
                'liblib_authors', 'liblib_works', 'liblib_work_models', 'liblib_work_images', 
                'liblib_comments', 'liblib_fetch_runs', 'liblib_fetch_queue'
            ]
            
            # 检查表是否存在
            cursor.execute("SHOW TABLES")
            existing_tables = [table[0] for table in cursor.fetchall()]
            
            logger.info(f"数据库中共有 {len(existing_tables)} 个表")
            logger.info("现有表:")
            for table in existing_tables:
                logger.info(f"  - {table}")
            
            logger.info("\n检查我们需要的表:")
            missing_tables = []
            existing_required_tables = []
            
            for table in required_tables:
                if table in existing_tables:
                    logger.info(f"  ✅ {table} - 存在")
                    existing_required_tables.append(table)
                else:
                    logger.info(f"  ❌ {table} - 不存在")
                    missing_tables.append(table)
            
            # 检查表结构
            if existing_required_tables:
                logger.info(f"\n检查表结构:")
                for table in existing_required_tables:
                    try:
                        cursor.execute(f"DESCRIBE {table}")
                        columns = cursor.fetchall()
                        logger.info(f"\n表 {table} 的结构:")
                        for col in columns:
                            logger.info(f"  - {col[0]} {col[1]} {col[2]} {col[3]} {col[4]} {col[5]}")
                    except Error as e:
                        logger.error(f"检查表 {table} 结构时出错: {e}")
            
            # 检查索引
            if existing_required_tables:
                logger.info(f"\n检查索引:")
                for table in existing_required_tables:
                    try:
                        cursor.execute(f"SHOW INDEX FROM {table}")
                        indexes = cursor.fetchall()
                        logger.info(f"\n表 {table} 的索引:")
                        for idx in indexes:
                            logger.info(f"  - {idx[2]} ({idx[4]}) - 类型: {idx[10]}")
                    except Error as e:
                        logger.error(f"检查表 {table} 索引时出错: {e}")
            
            cursor.close()
            connection.close()
            
            if missing_tables:
                logger.error(f"\n❌ 缺少以下表: {missing_tables}")
                return False
            else:
                logger.info(f"\n🎉 所有需要的表都已创建成功！")
                return True
                
        else:
            logger.error("无法连接到数据库")
            return False
            
    except Error as e:
        logger.error(f"验证表时出错: {e}")
        return False

def main():
    """主函数"""
    logger.info("开始验证工单T3创建的表")
    logger.info("=" * 50)
    
    success = verify_tables()
    
    if success:
        logger.info("✅ 表验证完成，工单T3执行成功！")
    else:
        logger.error("❌ 表验证失败，工单T3执行有问题")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
