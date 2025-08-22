#!/usr/bin/env python3
"""
T4 列表采集器 - Liblib 汽车交通数据采集系统
实现按标签=汽车交通调用 img/group/search 的分页采集
包含断点续采、速率限制、slug队列功能
"""

import os
import sys
import json
import time
import logging
import asyncio
import aiohttp
import aiofiles
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import sqlite3
from contextlib import asynccontextmanager

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.database.database_manager import DatabaseManager
from scripts.scraping.t4_config import get_config, validate_config

# 配置日志
logger = logging.getLogger(__name__)

@dataclass
class ListItem:
    """列表项数据结构"""
    slug: str
    title: str
    author_name: str
    published_at: Optional[str]
    tags: List[str]
    like_count: int
    favorite_count: int
    comment_count: int
    source_url: str
    created_at: datetime

@dataclass
class FetchState:
    """采集状态记录"""
    current_page: int
    total_pages: Optional[int]
    last_cursor: Optional[str]
    works_fetched: int
    last_fetch_time: datetime
    status: str  # RUNNING, SUCCESS, FAILED, PAUSED

class RateLimiter:
    """速率限制器"""
    def __init__(self, max_requests: int, time_window: float):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def acquire(self):
        """获取请求许可"""
        now = time.time()
        # 清理过期的请求记录
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < self.time_window]
        
        if len(self.requests) >= self.max_requests:
            # 需要等待
            wait_time = self.time_window - (now - self.requests[0])
            if wait_time > 0:
                logger.info(f"速率限制：等待 {wait_time:.2f} 秒")
                await asyncio.sleep(wait_time)
        
        self.requests.append(time.time())

class T4ListCollector:
    """T4 列表采集器主类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        # 加载配置
        if config is None:
            config = get_config()
        
        # 验证配置
        if not validate_config(config):
            raise ValueError("配置验证失败")
        
        self.config = config
        self.api_base = "https://api2.liblib.art"
        self.base_url = "https://www.liblib.art"
        
        # 速率限制：从配置读取
        self.rate_limiter = RateLimiter(
            max_requests=config['max_requests_per_second'], 
            time_window=1.0
        )
        self.max_concurrent = config['max_concurrent']
        
        # 数据存储
        self.db_manager = DatabaseManager()
        self.state_file = config['state_file']
        self.slug_queue_file = config['slug_queue_file']
        
        # 采集状态
        self.fetch_state = FetchState(
            current_page=1,
            total_pages=None,
            last_cursor=None,
            works_fetched=0,
            last_fetch_time=datetime.now(),
            status="RUNNING"
        )
        
        # 已采集的slug集合（用于去重）
        self.collected_slugs: Set[str] = set()
        
        # 创建必要的目录
        self._create_directories()
        
        # 加载历史状态
        self._load_state()
    
    def _create_directories(self):
        """创建必要的目录"""
        directories = [
            "data",
            "logs", 
            "data/raw",
            "data/processed"
        ]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _load_state(self):
        """加载历史采集状态"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                    self.fetch_state.current_page = state_data.get('current_page', 1)
                    self.fetch_state.works_fetched = state_data.get('works_fetched', 0)
                    self.fetch_state.last_cursor = state_data.get('last_cursor')
                    self.fetch_state.status = state_data.get('status', 'RUNNING')
                    logger.info(f"加载历史状态：第{self.fetch_state.current_page}页，已采集{self.fetch_state.works_fetched}个作品")
            
            if os.path.exists(self.slug_queue_file):
                with open(self.slug_queue_file, 'r', encoding='utf-8') as f:
                    slug_data = json.load(f)
                    self.collected_slugs = set(slug_data.get('collected_slugs', []))
                    logger.info(f"加载历史slug队列：{len(self.collected_slugs)}个已采集")
        except Exception as e:
            logger.warning(f"加载历史状态失败：{e}")
    
    def _save_state(self):
        """保存当前采集状态"""
        try:
            state_data = {
                'current_page': self.fetch_state.current_page,
                'total_pages': self.fetch_state.total_pages,
                'last_cursor': self.fetch_state.last_cursor,
                'works_fetched': self.fetch_state.works_fetched,
                'last_fetch_time': self.fetch_state.last_fetch_time.isoformat(),
                'status': self.fetch_state.status
            }
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存状态失败：{e}")
    
    def _save_slug_queue(self):
        """保存slug队列"""
        try:
            slug_data = {
                'collected_slugs': list(self.collected_slugs),
                'updated_at': datetime.now().isoformat()
            }
            with open(self.slug_queue_file, 'w', encoding='utf-8') as f:
                json.dump(slug_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存slug队列失败：{e}")
    
    async def _make_request(self, session: aiohttp.ClientSession, url: str, 
                           payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """发送HTTP请求"""
        try:
            await self.rate_limiter.acquire()
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Referer': self.base_url,
                'Origin': self.base_url,
                'Content-Type': 'application/json'
            }
            
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    logger.warning("请求频率过高，等待重试")
                    await asyncio.sleep(5)
                    return None
                else:
                    logger.error(f"请求失败 {url}: HTTP {response.status}")
                    return None
        except Exception as e:
            logger.error(f"请求异常 {url}: {e}")
            return None
    
    async def fetch_list_page(self, session: aiohttp.ClientSession, 
                             page: int, page_size: int = 24) -> Optional[Dict[str, Any]]:
        """获取列表页数据"""
        url = f"{self.api_base}/api/www/img/group/search"
        
        payload = {
            "tag": self.config['target_tag'],  # 按标签筛选
            "page": page,
            "pageSize": page_size,
            "sortType": self.config['sort_type'],  # 排序方式
            "nsfw": False
        }
        
        logger.info(f"获取第 {page} 页列表数据...")
        
        response = await self._make_request(session, url, payload)
        if response:
            logger.info(f"第 {page} 页获取成功")
            return response
        else:
            logger.error(f"第 {page} 页获取失败")
            return None
    
    def parse_list_response(self, response: Dict[str, Any]) -> List[ListItem]:
        """解析列表响应数据"""
        items = []
        
        try:
            data = response.get('data', {})
            works = data.get('list', [])
            
            for work in works:
                try:
                    item = ListItem(
                        slug=work.get('slug', ''),
                        title=work.get('title', ''),
                        author_name=work.get('author', {}).get('name', ''),
                        published_at=work.get('publishedAt'),
                        tags=work.get('tags', []),
                        like_count=work.get('likeCount', 0),
                        favorite_count=work.get('favoriteCount', 0),
                        comment_count=work.get('commentCount', 0),
                        source_url=work.get('sourceUrl', ''),
                        created_at=datetime.now()
                    )
                    
                    if item.slug:  # 只处理有slug的作品
                        items.append(item)
                        
                except Exception as e:
                    logger.warning(f"解析作品数据失败：{e}")
                    continue
            
            logger.info(f"解析完成：{len(items)}个有效作品")
            
        except Exception as e:
            logger.error(f"解析响应数据失败：{e}")
        
        return items
    
    async def save_to_database(self, items: List[ListItem]) -> int:
        """保存数据到数据库"""
        saved_count = 0
        
        try:
            # 连接数据库
            await self.db_manager.connect()
            
            for item in items:
                try:
                    # 检查是否已存在
                    if item.slug in self.collected_slugs:
                        logger.debug(f"作品 {item.slug} 已存在，跳过")
                        continue
                    
                    # 保存作者信息
                    author_id = await self._save_author(item.author_name)
                    
                    # 保存作品信息
                    work_id = await self._save_work(item, author_id)
                    
                    if work_id:
                        self.collected_slugs.add(item.slug)
                        saved_count += 1
                        
                        # 添加到采集队列（为T5详情采集器准备）
                        await self._add_to_fetch_queue(item.slug)
                        
                except Exception as e:
                    logger.error(f"保存作品 {item.slug} 失败：{e}")
                    continue
            
            logger.info(f"数据库保存完成：{saved_count}个新作品")
            
        except Exception as e:
            logger.error(f"数据库操作失败：{e}")
        finally:
            await self.db_manager.disconnect()
        
        return saved_count
    
    async def _save_author(self, author_name: str) -> Optional[int]:
        """保存作者信息"""
        try:
            # 检查作者是否已存在
            query = "SELECT id FROM authors WHERE name = %s"
            result = await self.db_manager.execute_query(query, (author_name,))
            
            if result:
                return result[0]['id']
            
            # 插入新作者
            insert_query = """
                INSERT INTO authors (name, created_at, updated_at) 
                VALUES (%s, NOW(), NOW())
            """
            author_id = await self.db_manager.execute_insert(insert_query, (author_name,))
            return author_id
            
        except Exception as e:
            logger.error(f"保存作者 {author_name} 失败：{e}")
            return None
    
    async def _save_work(self, item: ListItem, author_id: Optional[int]) -> Optional[int]:
        """保存作品信息"""
        try:
            # 解析发布时间
            published_at = None
            if item.published_at:
                try:
                    published_at = datetime.fromisoformat(item.published_at.replace('Z', '+00:00'))
                except:
                    published_at = datetime.now()
            
            # 插入作品
            insert_query = """
                INSERT INTO works (
                    slug, title, published_at, tags_json, like_count, 
                    favorite_count, comment_count, source_url, author_id, 
                    created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            
            work_id = await self.db_manager.execute_insert(insert_query, (
                item.slug, item.title, published_at, json.dumps(item.tags), 
                item.like_count, item.favorite_count, item.comment_count, 
                item.source_url, author_id
            ))
            
            return work_id
            
        except Exception as e:
            logger.error(f"保存作品 {item.slug} 失败：{e}")
            return None
    
    async def _add_to_fetch_queue(self, slug: str):
        """添加到采集队列（为T5详情采集器准备）"""
        try:
            # 这里可以添加到队列表或文件
            # 暂时保存到文件，后续T5会读取
            queue_file = self.config['fetch_queue_file']
            with open(queue_file, 'a', encoding='utf-8') as f:
                f.write(f"{slug}\n")
                
        except Exception as e:
            logger.error(f"添加到队列失败 {slug}: {e}")
    
    async def run_collection(self, start_page: int = 1, max_pages: Optional[int] = None, 
                           target_count: int = 1000) -> Dict[str, Any]:
        """运行采集任务"""
        logger.info(f"开始T4列表采集任务：目标{target_count}个作品，起始页{start_page}")
        
        self.fetch_state.current_page = start_page
        self.fetch_state.status = "RUNNING"
        self.fetch_state.last_fetch_time = datetime.now()
        
        # 创建HTTP会话
        timeout = aiohttp.ClientTimeout(total=self.config['request_timeout'])
        connector = aiohttp.TCPConnector(limit=self.max_concurrent)
        
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            page = start_page
            
            while True:
                try:
                    # 检查是否达到目标
                    if self.fetch_state.works_fetched >= target_count:
                        logger.info(f"已达到目标数量：{self.fetch_state.works_fetched}")
                        break
                    
                    # 检查页数限制
                    if max_pages and page > max_pages:
                        logger.info(f"已达到最大页数限制：{max_pages}")
                        break
                    
                    # 获取列表页
                    response = await self.fetch_list_page(session, page)
                    if not response:
                        logger.error(f"第 {page} 页获取失败，尝试下一页")
                        page += 1
                        continue
                    
                    # 解析数据
                    items = self.parse_list_response(response)
                    if not items:
                        logger.warning(f"第 {page} 页无有效数据，可能已到末尾")
                        break
                    
                    # 保存到数据库
                    saved_count = await self.save_to_database(items)
                    self.fetch_state.works_fetched += saved_count
                    self.fetch_state.current_page = page
                    
                    # 保存状态
                    self._save_state()
                    self._save_slug_queue()
                    
                    logger.info(f"第 {page} 页处理完成：{saved_count}个新作品，总计{self.fetch_state.works_fetched}个")
                    
                    # 检查是否还有更多数据
                    data = response.get('data', {})
                    if not data.get('hasMore', True):
                        logger.info("已到达最后一页")
                        break
                    
                    page += 1
                    
                    # 短暂休息，避免过于频繁的请求
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"处理第 {page} 页时发生错误：{e}")
                    page += 1
                    continue
        
        # 完成采集
        self.fetch_state.status = "SUCCESS"
        self.fetch_state.last_fetch_time = datetime.now()
        self._save_state()
        
        result = {
            'status': 'success',
            'total_works': self.fetch_state.works_fetched,
            'pages_processed': self.fetch_state.current_page - start_page + 1,
            'start_page': start_page,
            'end_page': self.fetch_state.current_page,
            'collected_slugs': len(self.collected_slugs)
        }
        
        logger.info(f"T4列表采集任务完成：{result}")
        return result

async def main():
    """主函数"""
    # 加载配置
    config = get_config()
    
    # 创建采集器
    collector = T4ListCollector(config)
    
    try:
        # 运行采集任务
        result = await collector.run_collection(
            start_page=config['start_page'],
            max_pages=config['max_pages'],
            target_count=config['target_count']
        )
        
        print(f"采集完成：{result}")
        
    except KeyboardInterrupt:
        logger.info("用户中断采集任务")
        collector.fetch_state.status = "PAUSED"
        collector._save_state()
    except Exception as e:
        logger.error(f"采集任务异常：{e}")
        collector.fetch_state.status = "FAILED"
        collector._save_state()

if __name__ == "__main__":
    # 创建日志目录
    Path("logs").mkdir(exist_ok=True)
    
    # 运行异步主函数
    asyncio.run(main())
