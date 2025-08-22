#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试脚本
直接执行CREATE TABLE语句
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

def test_simple_create():
    """测试简单的CREATE TABLE语句"""
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
            logger.info("✅ 数据库连接成功")
            
            cursor = connection.cursor()
            
            # 检查当前表数量
            cursor.execute("SHOW TABLES")
            before_tables = cursor.fetchall()
            logger.info(f"执行前表数量: {len(before_tables)}")
            
            # 测试创建一个简单的表
            test_sql = """
            CREATE TABLE IF NOT EXISTS liblib_test_table (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            logger.info("执行测试SQL:")
            logger.info(test_sql)
            
            try:
                cursor.execute(test_sql)
                logger.info("✅ 测试表创建成功")
                
                # 提交事务
                connection.commit()
                logger.info("✅ 事务提交成功")
                
                # 检查执行后的表数量
                cursor.execute("SHOW TABLES")
                after_tables = cursor.fetchall()
                logger.info(f"执行后表数量: {len(after_tables)}")
                
                # 显示新增的表
                before_table_names = {table[0] for table in before_tables}
                after_table_names = {table[0] for table in after_tables}
                new_tables = after_table_names - before_table_names
                
                if new_tables:
                    logger.info(f"✅ 新增的表: {list(new_tables)}")
                else:
                    logger.warning("⚠️  没有新增表")
                
                # 删除测试表
                cursor.execute("DROP TABLE IF EXISTS liblib_test_table")
                connection.commit()
                logger.info("✅ 测试表已删除")
                
            except Error as e:
                logger.error(f"❌ 创建测试表时出错: {e}")
                logger.error(f"   错误代码: {e.errno}")
                logger.error(f"   错误消息: {e.msg}")
                return False
            
            cursor.close()
            connection.close()
            logger.info("数据库连接已关闭")
            
            return True
            
        else:
            logger.error("无法连接到数据库")
            return False
            
    except Error as e:
        logger.error(f"连接数据库时出错: {e}")
        return False

def main():
    """主函数"""
    logger.info("开始测试简单的CREATE TABLE语句")
    logger.info("=" * 50)
    
    success = test_simple_create()
    
    if success:
        logger.info("✅ 测试完成")
    else:
        logger.error("❌ 测试失败")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
