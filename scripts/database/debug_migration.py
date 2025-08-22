#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试版数据库迁移脚本
显示详细的SQL执行过程
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

def debug_migration():
    """调试迁移过程"""
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
            
            # 读取DDL脚本
            ddl_file = 'scripts/database/create_tables.sql'
            if not os.path.exists(ddl_file):
                logger.error(f"DDL文件不存在: {ddl_file}")
                return False
            
            with open(ddl_file, 'r', encoding='utf-8') as f:
                ddl_script = f.read()
            
            logger.info(f"DDL脚本内容长度: {len(ddl_script)} 字符")
            
            # 分割SQL语句
            statements = [stmt.strip() for stmt in ddl_script.split(';') if stmt.strip()]
            logger.info(f"分割后的SQL语句数量: {len(statements)}")
            
            cursor = connection.cursor()
            
            # 检查当前表数量
            cursor.execute("SHOW TABLES")
            before_tables = cursor.fetchall()
            logger.info(f"执行前表数量: {len(before_tables)}")
            
            for i, statement in enumerate(statements, 1):
                if statement and not statement.startswith('--'):
                    try:
                        logger.info(f"\n执行SQL语句 {i}/{len(statements)}:")
                        logger.info(f"SQL: {statement[:100]}...")
                        
                        cursor.execute(statement)
                        logger.info(f"✅ SQL语句 {i} 执行成功")
                        
                        # 检查是否有错误
                        if cursor.with_rows:
                            result = cursor.fetchall()
                            logger.info(f"   结果: {result}")
                        
                    except Error as e:
                        logger.error(f"❌ 执行SQL语句 {i} 时出错: {e}")
                        logger.error(f"   错误代码: {e.errno}")
                        logger.error(f"   错误消息: {e.msg}")
                        return False
            
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
    logger.info("开始调试数据库迁移过程")
    logger.info("=" * 50)
    
    success = debug_migration()
    
    if success:
        logger.info("✅ 调试完成")
    else:
        logger.error("❌ 调试过程中发现问题")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
