#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库状态检查脚本
检查数据库连接状态和已采集的数据统计
"""

import os
import sys
import mysql.connector
from dotenv import load_dotenv
import json
from datetime import datetime

# 加载环境变量
load_dotenv()

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 3306)),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            charset='utf8mb4'
        )
        return connection
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def check_table_status(connection):
    """检查表状态和数据统计"""
    if not connection:
        return
    
    cursor = connection.cursor()
    
    # 检查表是否存在
    tables_to_check = [
        'liblib_authors',
        'liblib_works', 
        'liblib_work_models',
        'liblib_work_images',
        'liblib_comments',
        'liblib_fetch_runs',
        'liblib_fetch_queue'
    ]
    
    print("=" * 60)
    print("数据库状态检查报告")
    print("=" * 60)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"数据库: {os.getenv('DB_NAME')} @ {os.getenv('DB_HOST')}")
    print()
    
    for table in tables_to_check:
        try:
            # 检查表是否存在
            cursor.execute(f"SHOW TABLES LIKE '{table}'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                # 获取记录数
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                
                # 获取表结构信息
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                column_count = len(columns)
                
                print(f"✓ {table}")
                print(f"  - 记录数: {count:,}")
                print(f"  - 字段数: {column_count}")
                
                # 如果是主要数据表，显示更多信息
                if table == 'liblib_works' and count > 0:
                    cursor.execute("""
                        SELECT 
                            MIN(published_at) as earliest_date,
                            MAX(published_at) as latest_date,
                            COUNT(DISTINCT author_id) as unique_authors
                        FROM liblib_works 
                        WHERE published_at IS NOT NULL
                    """)
                    work_stats = cursor.fetchone()
                    if work_stats[0]:
                        print(f"  - 时间范围: {work_stats[0]} 到 {work_stats[1]}")
                        print(f"  - 作者数量: {work_stats[2]}")
                
                elif table == 'liblib_work_images' and count > 0:
                    cursor.execute("""
                        SELECT 
                            COUNT(CASE WHEN status = 'OK' THEN 1 END) as downloaded,
                            COUNT(CASE WHEN status = 'PENDING' THEN 1 END) as pending,
                            COUNT(CASE WHEN status = 'FAILED' THEN 1 END) as failed
                        FROM liblib_work_images
                    """)
                    img_stats = cursor.fetchone()
                    print(f"  - 已下载: {img_stats[0]:,}")
                    print(f"  - 待下载: {img_stats[1]:,}")
                    print(f"  - 下载失败: {img_stats[2]:,}")
                
                elif table == 'liblib_fetch_runs' and count > 0:
                    cursor.execute("""
                        SELECT 
                            status,
                            COUNT(*) as count,
                            MAX(started_at) as last_run
                        FROM liblib_fetch_runs 
                        GROUP BY status
                    """)
                    run_stats = cursor.fetchall()
                    print(f"  - 运行状态统计:")
                    for status, count, last_run in run_stats:
                        print(f"    * {status}: {count} 次 (最后: {last_run})")
                
                print()
            else:
                print(f"✗ {table} - 表不存在")
                print()
                
        except Exception as e:
            print(f"✗ {table} - 检查失败: {e}")
            print()

def check_recent_data(connection):
    """检查最近采集的数据"""
    if not connection:
        return
    
    cursor = connection.cursor()
    
    print("=" * 60)
    print("最近采集数据概览")
    print("=" * 60)
    
    try:
        # 最近的作品
        cursor.execute("""
            SELECT id, title, published_at, author_id, like_count, favorite_count
            FROM liblib_works 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        recent_works = cursor.fetchall()
        
        if recent_works:
            print("最近采集的作品:")
            for work in recent_works:
                work_id, title, pub_date, author_id, likes, favorites = work
                title_display = title[:50] + "..." if title and len(title) > 50 else title or "无标题"
                print(f"  - ID: {work_id}, 标题: {title_display}")
                print(f"    发布时间: {pub_date}, 点赞: {likes}, 收藏: {favorites}")
                print()
        else:
            print("暂无作品数据")
            print()
        
        # 最近的采集运行
        cursor.execute("""
            SELECT started_at, ended_at, status, works_fetched, images_downloaded
            FROM liblib_fetch_runs 
            ORDER BY started_at DESC 
            LIMIT 3
        """)
        recent_runs = cursor.fetchall()
        
        if recent_runs:
            print("最近的采集运行:")
            for run in recent_runs:
                started, ended, status, works, images = run
                duration = "进行中" if not ended else f"{(ended - started).total_seconds():.0f}秒"
                print(f"  - 开始: {started}, 状态: {status}, 时长: {duration}")
                print(f"    采集作品: {works}, 下载图片: {images}")
                print()
        else:
            print("暂无采集运行记录")
            print()
            
    except Exception as e:
        print(f"检查最近数据失败: {e}")
        print()

def main():
    """主函数"""
    print("正在连接数据库...")
    connection = get_db_connection()
    
    if connection:
        print("数据库连接成功!")
        print()
        
        try:
            check_table_status(connection)
            check_recent_data(connection)
            
        except Exception as e:
            print(f"检查过程中发生错误: {e}")
        finally:
            connection.close()
            print("数据库连接已关闭")
    else:
        print("无法连接到数据库，请检查配置")

if __name__ == "__main__":
    main()
