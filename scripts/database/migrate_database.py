#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本
执行工单T3：数据模型与迁移
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
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_migration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    def __init__(self):
        # 加载环境变量
        load_dotenv()
        
        # 数据库连接配置
        self.db_config = {
            'host': os.getenv('DB_HOST'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci'
        }
        
        # 验证必要的环境变量
        required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"缺少必要的环境变量: {missing_vars}")
        
        self.connection = None
    
    def test_connection(self):
        """测试数据库连接"""
        try:
            logger.info("正在测试数据库连接...")
            self.connection = mysql.connector.connect(**self.db_config)
            
            if self.connection.is_connected():
                db_info = self.connection.get_server_info()
                logger.info(f"成功连接到MySQL服务器，版本: {db_info}")
                
                cursor = self.connection.cursor()
                cursor.execute("SELECT DATABASE();")
                database = cursor.fetchone()
                logger.info(f"当前数据库: {database[0]}")
                
                return True
            else:
                logger.error("无法连接到数据库")
                return False
                
        except Error as e:
            logger.error(f"连接数据库时出错: {e}")
            return False
    
    def create_tables(self):
        """创建数据库表"""
        try:
            if not self.connection or not self.connection.is_connected():
                logger.error("数据库未连接")
                return False
            
            # 读取DDL脚本
            ddl_file = Path(__file__).parent / 'create_tables.sql'
            if not ddl_file.exists():
                logger.error(f"DDL文件不存在: {ddl_file}")
                return False
            
            with open(ddl_file, 'r', encoding='utf-8') as f:
                ddl_script = f.read()
            
            # 分割SQL语句 - 改进的分割逻辑
            statements = []
            current_statement = ""
            
            for line in ddl_script.split('\n'):
                line = line.strip()
                if line.startswith('--') or not line:  # 跳过注释和空行
                    continue
                
                current_statement += line + " "
                
                if line.endswith(';'):
                    # 完整的SQL语句
                    statements.append(current_statement.strip())
                    current_statement = ""
            
            # 添加最后一个语句（如果没有分号结尾）
            if current_statement.strip():
                statements.append(current_statement.strip())
            
            cursor = self.connection.cursor()
            
            for i, statement in enumerate(statements, 1):
                if statement and not statement.startswith('--'):
                    try:
                        logger.info(f"执行SQL语句 {i}/{len(statements)}: {statement[:50]}...")
                        cursor.execute(statement)
                        logger.info(f"SQL语句 {i} 执行成功")
                    except Error as e:
                        logger.error(f"执行SQL语句 {i} 时出错: {e}")
                        return False
            
            # 提交事务
            self.connection.commit()
            logger.info("所有表创建完成")
            return True
            
        except Error as e:
            logger.error(f"创建表时出错: {e}")
            return False
    
    def verify_tables(self):
        """验证表是否创建成功"""
        try:
            if not self.connection or not self.connection.is_connected():
                logger.error("数据库未连接")
                return False
            
            cursor = self.connection.cursor()
            
            # 检查表是否存在
            expected_tables = [
                'liblib_authors', 'liblib_works', 'liblib_work_models', 'liblib_work_images', 
                'liblib_comments', 'liblib_fetch_runs', 'liblib_fetch_queue'
            ]
            
            cursor.execute("SHOW TABLES")
            existing_tables = [table[0] for table in cursor.fetchall()]
            
            logger.info("现有表:")
            for table in existing_tables:
                logger.info(f"  - {table}")
            
            # 检查索引
            for table in expected_tables:
                if table in existing_tables:
                    cursor.execute(f"SHOW INDEX FROM {table}")
                    indexes = cursor.fetchall()
                    logger.info(f"\n表 {table} 的索引:")
                    for idx in indexes:
                        logger.info(f"  - {idx[2]} ({idx[4]})")
            
            return True
            
        except Error as e:
            logger.error(f"验证表时出错: {e}")
            return False
    
    def close_connection(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("数据库连接已关闭")

def main():
    """主函数"""
    logger.info("开始执行工单T3：数据模型与迁移")
    
    try:
        migrator = DatabaseMigrator()
        
        # 测试连接
        if not migrator.test_connection():
            logger.error("数据库连接测试失败")
            return False
        
        # 创建表
        if not migrator.create_tables():
            logger.error("创建表失败")
            return False
        
        # 验证表
        if not migrator.verify_tables():
            logger.error("验证表失败")
            return False
        
        logger.info("工单T3执行成功！")
        return True
        
    except Exception as e:
        logger.error(f"执行过程中出现异常: {e}")
        return False
    
    finally:
        if 'migrator' in locals():
            migrator.close_connection()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
