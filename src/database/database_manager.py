#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理器
为T4采集器提供异步数据库操作接口
"""

import os
import sys
import asyncio
import aiomysql
from typing import Dict, List, Optional, Any, Union
from dotenv import load_dotenv
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """异步数据库管理器"""
    
    def __init__(self):
        # 加载环境变量
        load_dotenv()
        
        # 数据库连接配置
        self.db_config = {
            'host': os.getenv('DB_HOST'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'db': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'charset': 'utf8mb4',
            'autocommit': True
        }
        
        # 验证必要的环境变量
        required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"缺少必要的环境变量: {missing_vars}")
        
        self.pool = None
        self.connection = None
    
    async def connect(self):
        """创建数据库连接池"""
        try:
            if not self.pool:
                self.pool = await aiomysql.create_pool(
                    **self.db_config,
                    minsize=1,
                    maxsize=10
                )
                logger.info("数据库连接池创建成功")
            
            # 获取连接
            self.connection = await self.pool.acquire()
            logger.info("数据库连接获取成功")
            
        except Exception as e:
            logger.error(f"连接数据库失败: {e}")
            raise
    
    async def disconnect(self):
        """关闭数据库连接"""
        try:
            if self.connection:
                self.pool.release(self.connection)
                self.connection = None
                logger.info("数据库连接已释放")
            
            if self.pool:
                self.pool.close()
                await self.pool.wait_closed()
                self.pool = None
                logger.info("数据库连接池已关闭")
                
        except Exception as e:
            logger.error(f"关闭数据库连接失败: {e}")
    
    async def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行查询语句"""
        try:
            if not self.connection:
                raise RuntimeError("数据库未连接")
            
            async with self.connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params)
                result = await cursor.fetchall()
                return result
                
        except Exception as e:
            logger.error(f"执行查询失败: {e}")
            logger.error(f"SQL: {query}")
            logger.error(f"参数: {params}")
            raise
    
    async def execute_insert(self, query: str, params: tuple = None) -> Optional[int]:
        """执行插入语句，返回插入的ID"""
        try:
            if not self.connection:
                raise RuntimeError("数据库未连接")
            
            async with self.connection.cursor() as cursor:
                await cursor.execute(query, params)
                insert_id = cursor.lastrowid
                return insert_id
                
        except Exception as e:
            logger.error(f"执行插入失败: {e}")
            logger.error(f"SQL: {query}")
            logger.error(f"参数: {params}")
            raise
    
    async def execute_update(self, query: str, params: tuple = None) -> int:
        """执行更新语句，返回影响的行数"""
        try:
            if not self.connection:
                raise RuntimeError("数据库未连接")
            
            async with self.connection.cursor() as cursor:
                await cursor.execute(query, params)
                affected_rows = cursor.rowcount
                return affected_rows
                
        except Exception as e:
            logger.error(f"执行更新失败: {e}")
            logger.error(f"SQL: {query}")
            logger.error(f"参数: {params}")
            raise
    
    async def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """批量执行语句"""
        try:
            if not self.connection:
                raise RuntimeError("数据库未连接")
            
            async with self.connection.cursor() as cursor:
                await cursor.executemany(query, params_list)
                affected_rows = cursor.rowcount
                return affected_rows
                
        except Exception as e:
            logger.error(f"批量执行失败: {e}")
            logger.error(f"SQL: {query}")
            raise
    
    async def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            await self.connect()
            
            # 执行简单查询
            result = await self.execute_query("SELECT 1 as test")
            if result and result[0]['test'] == 1:
                logger.info("数据库连接测试成功")
                return True
            else:
                logger.error("数据库连接测试失败")
                return False
                
        except Exception as e:
            logger.error(f"数据库连接测试异常: {e}")
            return False
        finally:
            await self.disconnect()
    
    async def get_table_count(self, table_name: str) -> int:
        """获取表的记录数"""
        try:
            query = f"SELECT COUNT(*) as count FROM {table_name}"
            result = await self.execute_query(query)
            return result[0]['count'] if result else 0
            
        except Exception as e:
            logger.error(f"获取表 {table_name} 记录数失败: {e}")
            return 0
    
    async def check_table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        try:
            query = """
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_schema = %s AND table_name = %s
            """
            result = await self.execute_query(query, (self.db_config['db'], table_name))
            return result[0]['count'] > 0 if result else False
            
        except Exception as e:
            logger.error(f"检查表 {table_name} 是否存在失败: {e}")
            return False
    
    async def get_works_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """根据slug获取作品信息"""
        try:
            query = "SELECT * FROM works WHERE slug = %s"
            result = await self.execute_query(query, (slug,))
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"获取作品 {slug} 失败: {e}")
            return None
    
    async def get_author_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据名称获取作者信息"""
        try:
            query = "SELECT * FROM authors WHERE name = %s"
            result = await self.execute_query(query, (name,))
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"获取作者 {name} 失败: {e}")
            return None
    
    async def insert_fetch_run(self, started_at: str, status: str = 'RUNNING') -> int:
        """插入采集运行记录"""
        try:
            query = """
                INSERT INTO fetch_runs (started_at, status, created_at) 
                VALUES (%s, %s, NOW())
            """
            return await self.execute_insert(query, (started_at, status))
            
        except Exception as e:
            logger.error(f"插入采集运行记录失败: {e}")
            raise
    
    async def update_fetch_run(self, run_id: int, **kwargs) -> bool:
        """更新采集运行记录"""
        try:
            set_clauses = []
            params = []
            
            for key, value in kwargs.items():
                if key in ['ended_at', 'status', 'pages_fetched', 'works_fetched', 
                          'details_fetched', 'images_downloaded', 'error_summary']:
                    set_clauses.append(f"{key} = %s")
                    params.append(value)
            
            if not set_clauses:
                return False
            
            query = f"UPDATE fetch_runs SET {', '.join(set_clauses)} WHERE id = %s"
            params.append(run_id)
            
            affected_rows = await self.execute_update(query, tuple(params))
            return affected_rows > 0
            
        except Exception as e:
            logger.error(f"更新采集运行记录失败: {e}")
            return False

# 测试函数
async def test_database_manager():
    """测试数据库管理器"""
    logger.info("开始测试数据库管理器...")
    
    try:
        db_manager = DatabaseManager()
        
        # 测试连接
        if await db_manager.test_connection():
            logger.info("数据库连接测试通过")
        else:
            logger.error("数据库连接测试失败")
            return False
        
        # 测试表存在性检查
        tables = ['authors', 'works', 'work_models', 'work_images']
        for table in tables:
            exists = await db_manager.check_table_exists(table)
            logger.info(f"表 {table} 存在: {exists}")
        
        # 测试记录数查询
        for table in tables:
            count = await db_manager.get_table_count(table)
            logger.info(f"表 {table} 记录数: {count}")
        
        logger.info("数据库管理器测试完成")
        return True
        
    except Exception as e:
        logger.error(f"测试过程中出现异常: {e}")
        return False

if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_database_manager())
