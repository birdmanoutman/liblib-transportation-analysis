#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T5 增强版详情采集器
集成配置管理、更好的错误处理和限速控制
"""

import os
import sys
import json
import time
import logging
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
from urllib.parse import urlparse
import re
import threading
from queue import Queue
import signal

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# 导入配置
try:
    from detail_collector_config import CollectorConfig, load_config
except ImportError:
    # 如果配置文件不存在，使用默认配置
    class CollectorConfig:
        def __init__(self):
            load_dotenv()
            self.db_host = os.getenv('DB_HOST', 'localhost')
            self.db_port = int(os.getenv('DB_PORT', '3306'))
            self.db_name = os.getenv('DB_NAME', 'cardesignspace')
            self.db_user = os.getenv('DB_USER', 'root')
            self.db_password = os.getenv('DB_PASSWORD', '')
            self.max_workers = 5
            self.requests_per_second = 4.0
            self.collect_comments = True
            self.collect_author_info = True
            self.strict_validation = False
            self.log_level = 'INFO'
    
    def load_config():
        return CollectorConfig()

class RateLimiter:
    """请求限速器"""
    
    def __init__(self, requests_per_second: float):
        self.requests_per_second = requests_per_second
        self.delay = 1.0 / requests_per_second
        self.last_request_time = 0
        self.lock = threading.Lock()
    
    def wait_if_needed(self):
        """等待如果需要限速"""
        with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            if time_since_last < self.delay:
                sleep_time = self.delay - time_since_last
                time.sleep(sleep_time)
            
            self.last_request_time = time.time()

class EnhancedDetailCollector:
    """T5 增强版详情采集器"""
    
    def __init__(self, config: CollectorConfig = None):
        # 加载配置
        self.config = config or load_config()
        
        # 设置日志
        self.setup_logging()
        
        # 初始化限速器
        self.rate_limiter = RateLimiter(self.config.requests_per_second)
        
        # 数据库连接配置
        self.db_config = {
            'host': self.config.db_host,
            'port': self.config.db_port,
            'database': self.config.db_name,
            'user': self.config.db_user,
            'password': self.config.db_password,
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci'
        }
        
        # API配置
        self.api_base = self.config.api_base
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.liblib.art/',
            'Origin': 'https://www.liblib.art'
        })
        
        # 统计信息
        self.stats = {
            'total_processed': 0,
            'success_count': 0,
            'failed_count': 0,
            'authors_created': 0,
            'works_created': 0,
            'comments_created': 0,
            'start_time': datetime.now(),
            'errors': []
        }
        
        # 数据库连接
        self.connection = None
        self.connect_database()
        
        # 信号处理
        self.setup_signal_handlers()
        
        # 原始数据保存
        if self.config.save_raw_data:
            os.makedirs(self.config.raw_data_dir, exist_ok=True)
    
    def setup_logging(self):
        """设置日志"""
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        
        logging.basicConfig(
            level=log_level,
            format=self.config.log_format,
            handlers=[
                logging.FileHandler(self.config.log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            self.logger.info(f"收到信号 {signum}，正在优雅关闭...")
            self.close()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def connect_database(self):
        """连接数据库"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            if self.connection.is_connected():
                self.logger.info("数据库连接成功")
            else:
                self.logger.error("数据库连接失败")
                raise Exception("数据库连接失败")
        except Error as e:
            self.logger.error(f"数据库连接错误: {e}")
            raise
    
    def get_timestamp(self) -> int:
        """获取当前时间戳"""
        return int(time.time() * 1000)
    
    def safe_request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """安全的HTTP请求（带限速和重试）"""
        # 限速控制
        self.rate_limiter.wait_if_needed()
        
        for attempt in range(self.config.api_retry_count + 1):
            try:
                response = self.session.request(
                    method, url, 
                    timeout=self.config.api_timeout,
                    **kwargs
                )
                response.raise_for_status()
                return response
                
            except requests.RequestException as e:
                self.logger.warning(f"请求失败 {url} (尝试 {attempt + 1}/{self.config.api_retry_count + 1}): {e}")
                
                if attempt < self.config.api_retry_count:
                    time.sleep(self.config.api_retry_delay * (2 ** attempt))  # 指数退避
                else:
                    self.logger.error(f"请求最终失败 {url}: {e}")
                    self.stats['errors'].append({
                        'url': url,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
                    return None
        
        return None
    
    def get_work_detail(self, slug: str) -> Optional[Dict[str, Any]]:
        """获取作品详情 - group/get/{slug}"""
        url = f"{self.api_base}/api/www/img/group/get/{slug}"
        
        payload = {
            "timestamp": self.get_timestamp()
        }
        
        self.logger.debug(f"获取作品详情: {slug}")
        
        response = self.safe_request('POST', url, json=payload)
        if response:
            try:
                data = response.json()
                if data.get('code') == 0:
                    work_data = data.get('data', {})
                    
                    # 保存原始数据
                    if self.config.save_raw_data:
                        raw_file = os.path.join(self.config.raw_data_dir, f'work_detail_{slug}.json')
                        with open(raw_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    return work_data
                else:
                    self.logger.warning(f"作品详情接口返回错误: {data.get('message', 'Unknown error')}")
            except json.JSONDecodeError:
                self.logger.error(f"作品详情响应格式错误: {slug}")
        
        return None
    
    def get_author_detail(self, author_slug: str) -> Optional[Dict[str, Any]]:
        """获取作者详情 - author/{slug}"""
        url = f"{self.api_base}/api/www/img/author/{author_slug}"
        
        params = {
            "timestamp": self.get_timestamp()
        }
        
        self.logger.debug(f"获取作者详情: {author_slug}")
        
        response = self.safe_request('POST', url, params=params)
        if response:
            try:
                data = response.json()
                if data.get('code') == 0:
                    author_data = data.get('data', {})
                    
                    # 保存原始数据
                    if self.config.save_raw_data:
                        raw_file = os.path.join(self.config.raw_data_dir, f'author_{author_slug}.json')
                        with open(raw_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    return author_data
                else:
                    self.logger.warning(f"作者详情接口返回错误: {data.get('message', 'Unknown error')}")
            except json.JSONDecodeError:
                self.logger.error(f"作者详情响应格式错误: {author_slug}")
        
        return None
    
    def get_work_comments(self, work_id: int, slug: str) -> List[Dict[str, Any]]:
        """获取作品评论（可选）"""
        if not self.config.collect_comments:
            return []
        
        url = f"{self.api_base}/api/www/community/commentList"
        
        payload = {
            "workId": work_id,
            "page": 1,
            "pageSize": 50,
            "sortType": "hot",
            "timestamp": self.get_timestamp()
        }
        
        self.logger.debug(f"获取作品评论: {slug}")
        
        response = self.safe_request('POST', url, json=payload)
        if response:
            try:
                data = response.json()
                if data.get('code') == 0:
                    comments = data.get('data', {}).get('list', [])
                    
                    # 保存原始数据
                    if self.config.save_raw_data:
                        raw_file = os.path.join(self.config.raw_data_dir, f'comments_{slug}.json')
                        with open(raw_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    return comments
                else:
                    self.logger.warning(f"评论接口返回错误: {data.get('message', 'Unknown error')}")
            except json.JSONDecodeError:
                self.logger.error(f"评论响应格式错误: {slug}")
        
        return []
    
    def validate_and_default_work_data(self, work_data: Dict[str, Any]) -> Dict[str, Any]:
        """字段校验与缺省策略 - 作品数据"""
        validated = {}
        
        # 必填字段校验
        required_fields = ['slug', 'title']
        for field in required_fields:
            if not work_data.get(field):
                if self.config.strict_validation:
                    self.logger.error(f"作品缺少必填字段: {field}")
                    return {}
                else:
                    self.logger.warning(f"作品缺少必填字段: {field}，使用默认值")
        
        # 基础字段
        validated['slug'] = work_data.get('slug', '')
        validated['title'] = work_data.get('title', '')
        validated['published_at'] = self.parse_datetime(work_data.get('publishedAt'))
        
        # 标签处理
        tags = work_data.get('tags', [])
        if isinstance(tags, list):
            validated['tags_json'] = json.dumps(tags, ensure_ascii=False)
        else:
            validated['tags_json'] = json.dumps([], ensure_ascii=False)
        
        # 提示词处理
        validated['prompt'] = work_data.get('prompt', '') or ''
        validated['negative_prompt'] = work_data.get('negativePrompt', '') or ''
        
        # 生成参数
        validated['sampler'] = work_data.get('sampler', '') or ''
        validated['steps'] = work_data.get('steps', 0) or 0
        validated['cfg_scale'] = float(work_data.get('cfgScale', 0)) or 0.0
        validated['width'] = work_data.get('width', 0) or 0
        validated['height'] = work_data.get('height', 0) or 0
        validated['seed'] = str(work_data.get('seed', '')) or ''
        
        # 统计数据
        validated['like_count'] = work_data.get('likeCount', 0) or 0
        validated['favorite_count'] = work_data.get('favoriteCount', 0) or 0
        validated['comment_count'] = work_data.get('commentCount', 0) or 0
        
        # 源URL
        validated['source_url'] = work_data.get('sourceUrl', '') or ''
        
        return validated
    
    def validate_and_default_author_data(self, author_data: Dict[str, Any]) -> Dict[str, Any]:
        """字段校验与缺省策略 - 作者数据"""
        validated = {}
        
        # 必填字段校验
        if not author_data.get('name'):
            if self.config.strict_validation:
                self.logger.error("作者缺少必填字段: name")
                return {}
            else:
                self.logger.warning("作者缺少必填字段: name，使用默认值")
                validated['name'] = 'Unknown'
        
        # 基础字段
        validated['external_author_id'] = author_data.get('id', '') or ''
        validated['name'] = author_data.get('name', 'Unknown')
        validated['avatar_url'] = author_data.get('avatar', '') or ''
        validated['profile_url'] = author_data.get('profileUrl', '') or ''
        validated['created_at'] = self.parse_datetime(author_data.get('createdAt'))
        
        return validated
    
    def parse_datetime(self, timestamp: Any) -> Optional[datetime]:
        """解析时间戳"""
        if not timestamp:
            return None
        
        try:
            if isinstance(timestamp, (int, float)):
                # 毫秒时间戳
                if timestamp > 1e10:  # 毫秒
                    timestamp = timestamp / 1000
                return datetime.fromtimestamp(timestamp, tz=timezone.utc)
            elif isinstance(timestamp, str):
                # ISO格式字符串
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            self.logger.warning(f"无法解析时间戳: {timestamp}")
        
        return None
    
    def create_author(self, author_data: Dict[str, Any]) -> Optional[int]:
        """创建作者记录"""
        try:
            cursor = self.connection.cursor()
            
            # 检查作者是否已存在
            check_sql = "SELECT id FROM authors WHERE name = %s"
            cursor.execute(check_sql, (author_data['name'],))
            existing = cursor.fetchone()
            
            if existing:
                self.logger.debug(f"作者已存在: {author_data['name']} (ID: {existing[0]})")
                return existing[0]
            
            # 插入新作者
            insert_sql = """
                INSERT INTO authors (external_author_id, name, avatar_url, profile_url, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (
                author_data['external_author_id'],
                author_data['name'],
                author_data['avatar_url'],
                author_data['profile_url'],
                author_data['created_at']
            ))
            
            author_id = cursor.lastrowid
            self.connection.commit()
            
            self.logger.info(f"创建作者成功: {author_data['name']} (ID: {author_id})")
            self.stats['authors_created'] += 1
            
            return author_id
            
        except Error as e:
            self.logger.error(f"创建作者失败: {e}")
            self.connection.rollback()
            return None
    
    def create_work(self, work_data: Dict[str, Any], author_id: Optional[int]) -> Optional[int]:
        """创建作品记录"""
        try:
            cursor = self.connection.cursor()
            
            # 检查作品是否已存在
            check_sql = "SELECT id FROM works WHERE slug = %s"
            cursor.execute(check_sql, (work_data['slug'],))
            existing = cursor.fetchone()
            
            if existing:
                self.logger.debug(f"作品已存在: {work_data['slug']} (ID: {existing[0]})")
                return existing[0]
            
            # 插入新作品
            insert_sql = """
                INSERT INTO works (
                    slug, title, published_at, tags_json, prompt, negative_prompt,
                    sampler, steps, cfg_scale, width, height, seed,
                    like_count, favorite_count, comment_count, source_url, author_id
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            cursor.execute(insert_sql, (
                work_data['slug'],
                work_data['title'],
                work_data['published_at'],
                work_data['tags_json'],
                work_data['prompt'],
                work_data['negative_prompt'],
                work_data['sampler'],
                work_data['steps'],
                work_data['cfg_scale'],
                work_data['width'],
                work_data['height'],
                work_data['seed'],
                work_data['like_count'],
                work_data['favorite_count'],
                work_data['comment_count'],
                work_data['source_url'],
                author_id
            ))
            
            work_id = cursor.lastrowid
            self.connection.commit()
            
            self.logger.info(f"创建作品成功: {work_data['title']} (ID: {work_id})")
            self.stats['works_created'] += 1
            
            return work_id
            
        except Error as e:
            self.logger.error(f"创建作品失败: {e}")
            self.connection.rollback()
            return None
    
    def create_comments(self, work_id: int, comments: List[Dict[str, Any]]) -> int:
        """创建评论记录"""
        if not comments:
            return 0
        
        created_count = 0
        
        try:
            cursor = self.connection.cursor()
            
            for comment in comments:
                # 检查评论是否已存在（基于内容和时间）
                comment_content = comment.get('content', '')
                comment_time = self.parse_datetime(comment.get('commentedAt'))
                
                if not comment_content or not comment_time:
                    continue
                
                # 简单的重复检查
                check_sql = """
                    SELECT id FROM comments 
                    WHERE work_id = %s AND content = %s AND commented_at = %s
                """
                cursor.execute(check_sql, (work_id, comment_content, comment_time))
                existing = cursor.fetchone()
                
                if existing:
                    continue
                
                # 插入新评论
                insert_sql = """
                    INSERT INTO comments (work_id, commenter_name, commenter_avatar_url, content, commented_at)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (
                    work_id,
                    comment.get('commenterName', ''),
                    comment.get('commenterAvatar', ''),
                    comment_content,
                    comment_time
                ))
                
                created_count += 1
            
            self.connection.commit()
            
            if created_count > 0:
                self.logger.info(f"创建评论成功: {created_count} 条")
                self.stats['comments_created'] += created_count
            
        except Error as e:
            self.logger.error(f"创建评论失败: {e}")
            self.connection.rollback()
        
        return created_count
    
    def process_single_work(self, slug: str) -> bool:
        """处理单个作品的详情采集"""
        try:
            self.logger.info(f"开始处理作品: {slug}")
            
            # 1. 获取作品详情
            work_detail = self.get_work_detail(slug)
            if not work_detail:
                self.logger.error(f"无法获取作品详情: {slug}")
                return False
            
            # 2. 字段校验与缺省
            validated_work = self.validate_and_default_work_data(work_detail)
            if not validated_work:
                if self.config.skip_invalid_works:
                    self.logger.warning(f"跳过无效作品: {slug}")
                    return False
                else:
                    self.logger.error(f"作品数据验证失败: {slug}")
                    return False
            
            # 3. 获取作者信息
            author_id = None
            if self.config.collect_author_info:
                author_slug = work_detail.get('authorSlug', '')
                if author_slug:
                    author_detail = self.get_author_detail(author_slug)
                    if author_detail:
                        validated_author = self.validate_and_default_author_data(author_detail)
                        if validated_author:
                            author_id = self.create_author(validated_author)
            
            # 4. 创建作品记录
            work_id = self.create_work(validated_work, author_id)
            if not work_id:
                self.logger.error(f"创建作品记录失败: {slug}")
                return False
            
            # 5. 获取并创建评论（可选）
            if self.config.collect_comments and work_detail.get('commentCount', 0) > 0:
                comments = self.get_work_comments(work_id, slug)
                if comments:
                    self.create_comments(work_id, comments)
            
            # 6. 处理模型引用（如果有）
            if self.config.collect_model_references:
                self.process_model_references(work_id, work_detail)
            
            self.logger.info(f"作品处理完成: {slug}")
            return True
            
        except Exception as e:
            self.logger.error(f"处理作品异常 {slug}: {e}")
            self.stats['errors'].append({
                'slug': slug,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            return False
    
    def process_model_references(self, work_id: int, work_detail: Dict[str, Any]):
        """处理模型引用"""
        try:
            # 这里可以根据实际API响应结构来提取模型引用信息
            # 目前先预留接口
            pass
        except Exception as e:
            self.logger.error(f"处理模型引用失败: {e}")
    
    def collect_details_batch(self, slugs: List[str]) -> Dict[str, Any]:
        """批量采集详情"""
        self.logger.info(f"开始批量采集详情，共 {len(slugs)} 个作品")
        
        self.stats['total_processed'] = len(slugs)
        self.stats['start_time'] = datetime.now()
        
        # 并发处理
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_slug = {
                executor.submit(self.process_single_work, slug): slug 
                for slug in slugs
            }
            
            for future in as_completed(future_to_slug):
                slug = future_to_slug[future]
                try:
                    success = future.result()
                    if success:
                        self.stats['success_count'] += 1
                    else:
                        self.stats['failed_count'] += 1
                except Exception as e:
                    self.logger.error(f"处理作品异常 {slug}: {e}")
                    self.stats['failed_count'] += 1
                    self.stats['errors'].append({
                        'slug': slug,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
        
        # 计算成功率
        success_rate = (self.stats['success_count'] / self.stats['total_processed']) * 100 if self.stats['total_processed'] > 0 else 0
        
        self.logger.info(f"批量采集完成，成功率: {success_rate:.2f}%")
        self.logger.info(f"成功: {self.stats['success_count']}, 失败: {self.stats['failed_count']}")
        
        return self.stats
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """获取采集统计"""
        return {
            'total_processed': self.stats['total_processed'],
            'success_count': self.stats['success_count'],
            'failed_count': self.stats['failed_count'],
            'success_rate': (self.stats['success_count'] / self.stats['total_processed']) * 100 if self.stats['total_processed'] > 0 else 0,
            'authors_created': self.stats['authors_created'],
            'works_created': self.stats['works_created'],
            'comments_created': self.stats['comments_created'],
            'start_time': self.stats['start_time'].isoformat(),
            'duration': (datetime.now() - self.stats['start_time']).total_seconds(),
            'error_count': len(self.stats['errors']),
            'errors': self.stats['errors']
        }
    
    def save_stats_to_file(self, filename: str = 'collection_stats.json'):
        """保存统计信息到文件"""
        stats = self.get_collection_stats()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"统计信息已保存到: {filename}")
    
    def close(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.logger.info("数据库连接已关闭")

def main():
    """主函数 - 测试增强版详情采集器"""
    # 测试用的slug列表
    test_slugs = [
        "test-slug-1",
        "test-slug-2"
    ]
    
    try:
        # 加载配置
        config = load_config()
        
        # 验证配置
        errors = config.validate()
        if errors:
            print("❌ 配置验证失败:")
            for error in errors:
                print(f"   - {error}")
            return
        
        # 创建采集器
        collector = EnhancedDetailCollector(config)
        
        # 批量采集详情
        stats = collector.collect_details_batch(test_slugs)
        
        # 输出统计信息
        print("\n✅ 详情采集完成！")
        print(f"📊 采集统计:")
        print(f"   总处理数: {stats['total_processed']}")
        print(f"   成功数: {stats['success_count']}")
        print(f"   失败数: {stats['failed_count']}")
        print(f"   成功率: {stats.get('success_rate', 0):.2f}%")
        print(f"   创建作者: {stats['authors_created']}")
        print(f"   创建作品: {stats['works_created']}")
        print(f"   创建评论: {stats['comments_created']}")
        print(f"   错误数: {len(stats['errors'])}")
        
        # 保存统计信息
        collector.save_stats_to_file()
        
    except KeyboardInterrupt:
        print("\n❌ 用户中断采集")
    except Exception as e:
        print(f"\n❌ 采集过程中发生错误: {e}")
    finally:
        if 'collector' in locals():
            collector.close()

if __name__ == "__main__":
    main()
