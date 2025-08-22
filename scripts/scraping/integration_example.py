#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T7 中间件集成示例
展示如何在T4和T5采集器中使用限速/重试中间件
"""

import asyncio
import time
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 直接导入模块
from rate_limit_middleware import (
    RateLimitMiddleware, SyncRateLimitMiddleware,
    RateLimitConfig, RetryConfig, CircuitBreakerConfig, ProxyConfig
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedT4Collector:
    """增强版T4采集器，集成T7中间件"""
    
    def __init__(self, middleware: RateLimitMiddleware = None):
        self.middleware = middleware or self._create_default_middleware()
        self.api_base = "https://api2.liblib.art"
        self.base_url = "https://www.liblib.art"
        
        # 采集状态
        self.current_page = 1
        self.total_pages = None
        self.works_fetched = 0
        
        logger.info("增强版T4采集器初始化完成")
    
    def _create_default_middleware(self) -> RateLimitMiddleware:
        """创建默认中间件"""
        rate_config = RateLimitConfig(
            max_requests_per_second=4.0,
            max_concurrent=5
        )
        
        retry_config = RetryConfig(
            max_retries=3,
            base_delay=1.0,
            backoff_factor=2.0
        )
        
        cb_config = CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=60.0
        )
        
        return RateLimitMiddleware(
            rate_limit_config=rate_config,
            retry_config=retry_config,
            circuit_breaker_config=cb_config
        )
    
    async def fetch_page(self, page: int, tag: str = "汽车交通") -> Dict[str, Any]:
        """获取单页数据"""
        url = f"{self.api_base}/img/group/search"
        params = {
            'tag': tag,
            'page': page,
            'page_size': 24,
            'sort': 'latest'
        }
        
        try:
            response = await self.middleware.make_request('GET', url, params=params)
            
            if response.status == 200:
                data = await response.json()
                logger.info(f"页面 {page} 获取成功，数据量: {len(data.get('data', []))}")
                return data
            else:
                logger.warning(f"页面 {page} 获取失败，状态码: {response.status}")
                return None
                
        except Exception as e:
            logger.error(f"页面 {page} 获取异常: {e}")
            return None
    
    async def collect_pages(self, start_page: int, end_page: int, tag: str = "汽车交通") -> List[Dict[str, Any]]:
        """批量采集页面"""
        all_data = []
        
        for page in range(start_page, end_page + 1):
            logger.info(f"开始采集页面 {page}")
            
            data = await self.fetch_page(page, tag)
            if data and 'data' in data:
                all_data.extend(data['data'])
                self.works_fetched += len(data['data'])
                
                # 显示进度
                logger.info(f"页面 {page} 完成，累计采集: {self.works_fetched}")
            
            # 页面间延迟（由中间件控制）
            await asyncio.sleep(0.1)
        
        return all_data
    
    def get_stats(self) -> Dict[str, Any]:
        """获取采集统计"""
        collector_stats = {
            'current_page': self.current_page,
            'total_pages': self.total_pages,
            'works_fetched': self.works_fetched
        }
        
        # 合并中间件统计
        middleware_stats = self.middleware.get_stats()
        
        return {
            'collector': collector_stats,
            'middleware': middleware_stats
        }

class EnhancedT5Collector:
    """增强版T5采集器，集成T7中间件"""
    
    def __init__(self, middleware: RateLimitMiddleware = None):
        self.middleware = middleware or self._create_default_middleware()
        self.api_base = "https://api2.liblib.art"
        
        # 采集统计
        self.details_fetched = 0
        self.comments_fetched = 0
        self.authors_fetched = 0
        
        logger.info("增强版T5采集器初始化完成")
    
    def _create_default_middleware(self) -> RateLimitMiddleware:
        """创建默认中间件"""
        rate_config = RateLimitConfig(
            max_requests_per_second=3.0,  # T5使用更保守的限速
            max_concurrent=3
        )
        
        retry_config = RetryConfig(
            max_retries=5,  # T5需要更多重试
            base_delay=2.0,
            backoff_factor=2.0
        )
        
        cb_config = CircuitBreakerConfig(
            failure_threshold=3,  # T5更敏感
            recovery_timeout=120.0
        )
        
        return RateLimitMiddleware(
            rate_limit_config=rate_config,
            retry_config=retry_config,
            circuit_breaker_config=cb_config
        )
    
    async def fetch_work_detail(self, slug: str) -> Dict[str, Any]:
        """获取作品详情"""
        url = f"{self.api_base}/group/get/{slug}"
        
        try:
            response = await self.middleware.make_request('GET', url)
            
            if response.status == 200:
                data = await response.json()
                self.details_fetched += 1
                logger.info(f"作品 {slug} 详情获取成功")
                return data
            else:
                logger.warning(f"作品 {slug} 详情获取失败，状态码: {response.status}")
                return None
                
        except Exception as e:
            logger.error(f"作品 {slug} 详情获取异常: {e}")
            return None
    
    async def fetch_author_info(self, author_slug: str) -> Dict[str, Any]:
        """获取作者信息"""
        url = f"{self.api_base}/author/{author_slug}"
        
        try:
            response = await self.middleware.make_request('GET', url)
            
            if response.status == 200:
                data = await response.json()
                self.authors_fetched += 1
                logger.info(f"作者 {author_slug} 信息获取成功")
                return data
            else:
                logger.warning(f"作者 {author_slug} 信息获取失败，状态码: {response.status}")
                return None
                
        except Exception as e:
            logger.error(f"作者 {author_slug} 信息获取异常: {e}")
            return None
    
    async def fetch_comments(self, slug: str, page: int = 1) -> Dict[str, Any]:
        """获取评论信息"""
        url = f"{self.api_base}/group/{slug}/comments"
        params = {'page': page, 'page_size': 20}
        
        try:
            response = await self.middleware.make_request('GET', url, params=params)
            
            if response.status == 200:
                data = await response.json()
                self.comments_fetched += 1
                logger.info(f"作品 {slug} 评论获取成功")
                return data
            else:
                logger.warning(f"作品 {slug} 评论获取失败，状态码: {response.status}")
                return None
                
        except Exception as e:
            logger.error(f"作品 {slug} 评论获取异常: {e}")
            return None
    
    async def collect_work_details(self, slugs: List[str]) -> List[Dict[str, Any]]:
        """批量获取作品详情"""
        all_details = []
        
        for i, slug in enumerate(slugs):
            logger.info(f"开始获取作品详情 {i+1}/{len(slugs)}: {slug}")
            
            # 获取作品详情
            detail = await self.fetch_work_detail(slug)
            if detail:
                all_details.append(detail)
                
                # 获取作者信息
                if 'author_slug' in detail:
                    author_info = await self.fetch_author_info(detail['author_slug'])
                    if author_info:
                        detail['author_info'] = author_info
                
                # 获取评论信息
                comments = await self.fetch_comments(slug)
                if comments:
                    detail['comments'] = comments
            
            # 显示进度
            logger.info(f"作品 {slug} 完成，累计详情: {self.details_fetched}")
        
        return all_details
    
    def get_stats(self) -> Dict[str, Any]:
        """获取采集统计"""
        collector_stats = {
            'details_fetched': self.details_fetched,
            'comments_fetched': self.comments_fetched,
            'authors_fetched': self.authors_fetched
        }
        
        # 合并中间件统计
        middleware_stats = self.middleware.get_stats()
        
        return {
            'collector': collector_stats,
            'middleware': middleware_stats
        }

class IntegratedScrapingPipeline:
    """集成采集流水线"""
    
    def __init__(self, 
                 t4_middleware: RateLimitMiddleware = None,
                 t5_middleware: RateLimitMiddleware = None):
        
        # 创建采集器
        self.t4_collector = EnhancedT4Collector(t4_middleware)
        self.t5_collector = EnhancedT5Collector(t5_middleware)
        
        logger.info("集成采集流水线初始化完成")
    
    async def run_pipeline(self, 
                          start_page: int = 1, 
                          end_page: int = 5, 
                          tag: str = "汽车交通") -> Dict[str, Any]:
        """运行完整采集流水线"""
        logger.info(f"开始运行采集流水线，标签: {tag}, 页数: {start_page}-{end_page}")
        
        start_time = time.time()
        
        # 第一阶段：T4列表采集
        logger.info("=== 第一阶段：T4列表采集 ===")
        list_data = await self.t4_collector.collect_pages(start_page, end_page, tag)
        
        if not list_data:
            logger.error("T4列表采集失败，流水线终止")
            return None
        
        # 提取slug列表
        slugs = [item.get('slug') for item in list_data if item.get('slug')]
        logger.info(f"T4采集完成，获得 {len(slugs)} 个slug")
        
        # 第二阶段：T5详情采集
        logger.info("=== 第二阶段：T5详情采集 ===")
        detail_data = await self.t5_collector.collect_work_details(slugs[:10])  # 限制数量用于演示
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 汇总结果
        result = {
            'pipeline_time': total_time,
            't4_stats': self.t4_collector.get_stats(),
            't5_stats': self.t5_collector.get_stats(),
            'list_data_count': len(list_data),
            'detail_data_count': len(detail_data),
            'success_rate': (len(detail_data) / min(len(slugs), 10)) * 100
        }
        
        logger.info(f"流水线完成，总耗时: {total_time:.2f}秒")
        logger.info(f"成功率: {result['success_rate']:.1f}%")
        
        return result

async def demo_integration():
    """演示集成功能"""
    print("=== T7中间件集成演示 ===")
    
    # 创建自定义中间件配置
    t4_middleware = RateLimitMiddleware(
        rate_limit_config=RateLimitConfig(
            max_requests_per_second=2.0,  # 保守的限速
            max_concurrent=3
        ),
        retry_config=RetryConfig(
            max_retries=3,
            base_delay=1.0
        )
    )
    
    t5_middleware = RateLimitMiddleware(
        rate_limit_config=RateLimitConfig(
            max_requests_per_second=1.5,  # 更保守的限速
            max_concurrent=2
        ),
        retry_config=RetryConfig(
            max_retries=5,
            base_delay=2.0
        )
    )
    
    # 创建流水线
    pipeline = IntegratedScrapingPipeline(t4_middleware, t5_middleware)
    
    try:
        # 运行流水线（限制页数用于演示）
        result = await pipeline.run_pipeline(start_page=1, end_page=2)
        
        if result:
            print("\n=== 流水线执行结果 ===")
            print(f"总耗时: {result['pipeline_time']:.2f}秒")
            print(f"T4采集数量: {result['list_data_count']}")
            print(f"T5采集数量: {result['detail_data_count']}")
            print(f"成功率: {result['success_rate']:.1f}%")
            
            print("\n=== T4中间件统计 ===")
            t4_stats = result['t4_stats']['middleware']
            print(f"总请求数: {t4_stats['total_requests']}")
            print(f"成功率: {t4_stats['success_rate']:.1f}%")
            print(f"熔断器状态: {t4_stats['circuit_breaker_state']}")
            
            print("\n=== T5中间件统计 ===")
            t5_stats = result['t5_stats']['middleware']
            print(f"总请求数: {t5_stats['total_requests']}")
            print(f"成功率: {t5_stats['success_rate']:.1f}%")
            print(f"熔断器状态: {t5_stats['circuit_breaker_state']}")
        
    except Exception as e:
        print(f"流水线执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 运行集成演示
    asyncio.run(demo_integration())
