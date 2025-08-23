#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T8 与 T4/T5 集成示例
展示如何在真实采集流程中使用断点续采和失败重试功能
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from t8_resume_and_retry import T8ResumeAndRetry
from t8_config import get_config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MockT4ListCollector:
    """模拟T4列表采集器"""
    
    def __init__(self, t8: T8ResumeAndRetry):
        self.t8 = t8
        self.works_fetched = 0
        self.current_page = 1
        
        # 模拟采集状态
        self.is_running = False
        self.total_pages = 10
        
    async def run_collection(self, start_page: int = 1, max_pages: int = 10):
        """运行列表采集"""
        try:
            # 检查是否有断点续采点
            resume_point = self.t8.get_resume_point("LIST_COLLECTION")
            if resume_point:
                start_page = resume_point.current_page
                self.works_fetched = resume_point.total_processed
                logger.info(f"从断点续采点恢复：第{start_page}页，已处理{self.works_fetched}项")
            
            self.current_page = start_page
            self.is_running = True
            
            # 执行采集逻辑
            for page in range(start_page, max_pages + 1):
                try:
                    # 模拟采集逻辑
                    await self._collect_page(page)
                    
                    # 创建断点续采点
                    self.t8.create_resume_point(
                        task_type="LIST_COLLECTION",
                        current_page=page,
                        total_processed=self.works_fetched,
                        metadata={
                            "tag": "汽车交通",
                            "sort": "latest",
                            "batch": f"batch_{page//5 + 1}"
                        }
                    )
                    
                    logger.info(f"第{page}页采集完成，已处理{self.works_fetched}项")
                    
                    # 模拟中断（每3页中断一次）
                    if page % 3 == 0:
                        logger.info(f"模拟中断：第{page}页采集完成")
                        break
                    
                except Exception as e:
                    # 添加失败任务
                    self.t8.add_failed_task(
                        task_type="LIST_COLLECTION",
                        target=f"page_{page}",
                        error_message=str(e),
                        max_retries=3,
                        retry_delay=60
                    )
                    logger.error(f"第{page}页采集失败：{e}")
                    continue
                    
        except KeyboardInterrupt:
            logger.info("用户中断采集任务")
        except Exception as e:
            logger.error(f"采集任务异常：{e}")
        finally:
            self.is_running = False
    
    async def _collect_page(self, page: int):
        """模拟采集单页"""
        # 模拟网络延迟
        await asyncio.sleep(0.1)
        
        # 模拟采集结果
        works_per_page = 24
        self.works_fetched += works_per_page
        
        # 模拟偶尔失败
        if page == 3:
            raise Exception("模拟网络错误")
        
        logger.debug(f"采集第{page}页：{works_per_page}个作品")

class MockT5DetailCollector:
    """模拟T5详情采集器"""
    
    def __init__(self, t8: T8ResumeAndRetry):
        self.t8 = t8
        self.details_fetched = 0
        
        # 模拟slug列表
        self.slug_list = [
            f"car-model-{i:03d}" for i in range(1, 101)
        ]
    
    async def collect_details(self, start_slug: str = None):
        """采集详情"""
        try:
            # 检查是否有断点续采点
            resume_point = self.t8.get_resume_point("DETAIL_COLLECTION")
            if resume_point and resume_point.last_slug:
                # 从上次停止的slug继续
                try:
                    start_index = self.slug_list.index(resume_point.last_slug) + 1
                    slug_list = self.slug_list[start_index:]
                    logger.info(f"从断点续采点恢复：{resume_point.last_slug}")
                except ValueError:
                    slug_list = self.slug_list
                    logger.warning(f"断点续采点slug不存在，从头开始")
            else:
                slug_list = self.slug_list
            
            # 执行详情采集
            for i, slug in enumerate(slug_list):
                try:
                    # 模拟详情采集逻辑
                    await self._collect_work_detail(slug)
                    
                    # 更新断点续采点
                    self.t8.create_resume_point(
                        task_type="DETAIL_COLLECTION",
                        current_page=1,
                        last_slug=slug,
                        total_processed=self.details_fetched,
                        metadata={
                            "batch_size": 100,
                            "current_batch": i // 20 + 1
                        }
                    )
                    
                    # 模拟中断（每20个中断一次）
                    if (i + 1) % 20 == 0:
                        logger.info(f"模拟中断：已采集{self.details_fetched}个详情")
                        break
                    
                except Exception as e:
                    # 添加失败任务
                    self.t8.add_failed_task(
                        task_type="DETAIL_COLLECTION",
                        target=slug,
                        error_message=str(e),
                        max_retries=5,
                        retry_delay=120
                    )
                    logger.error(f"详情采集失败 {slug}：{e}")
                    continue
                    
        except Exception as e:
            logger.error(f"详情采集任务异常：{e}")
    
    async def _collect_work_detail(self, slug: str):
        """模拟采集单个作品详情"""
        # 模拟网络延迟
        await asyncio.sleep(0.05)
        
        # 模拟采集结果
        self.details_fetched += 1
        
        # 模拟偶尔失败
        if slug in ["car-model-005", "car-model-015", "car-model-025"]:
            raise Exception("模拟API错误")
        
        logger.debug(f"采集详情：{slug}")

class MockT6ImageDownloader:
    """模拟T6图片下载器"""
    
    def __init__(self, t8: T8ResumeAndRetry):
        self.t8 = t8
        self.images_downloaded = 0
        
        # 模拟图片URL列表
        self.image_urls = [
            f"https://example.com/images/car-model-{i:03d}.jpg" 
            for i in range(1, 51)
        ]
    
    async def download_images(self, start_url: str = None):
        """下载图片"""
        try:
            # 检查是否有断点续采点
            resume_point = self.t8.get_resume_point("IMAGE_DOWNLOAD")
            if resume_point and resume_point.last_slug:
                # 从上次停止的地方继续
                try:
                    start_index = self.image_urls.index(start_url) if start_url else 0
                    url_list = self.image_urls[start_index:]
                    logger.info(f"从断点续采点恢复：{start_url}")
                except ValueError:
                    url_list = self.image_urls
                    logger.warning(f"断点续采点URL不存在，从头开始")
            else:
                url_list = self.image_urls
            
            # 执行图片下载
            for i, url in enumerate(url_list):
                try:
                    # 模拟图片下载逻辑
                    await self._download_single_image(url)
                    
                    # 更新断点续采点
                    self.t8.create_resume_point(
                        task_type="IMAGE_DOWNLOAD",
                        current_page=1,
                        last_slug=url,
                        total_processed=self.images_downloaded,
                        metadata={
                            "batch_size": 50,
                            "current_batch": i // 10 + 1
                        }
                    )
                    
                    # 模拟中断（每10个中断一次）
                    if (i + 1) % 10 == 0:
                        logger.info(f"模拟中断：已下载{self.images_downloaded}张图片")
                        break
                    
                except Exception as e:
                    # 添加失败任务
                    self.t8.add_failed_task(
                        task_type="IMAGE_DOWNLOAD",
                        target=url,
                        error_message=str(e),
                        max_retries=3,
                        retry_delay=180
                    )
                    logger.error(f"图片下载失败 {url}：{e}")
                    continue
                    
        except Exception as e:
            logger.error(f"图片下载任务异常：{e}")
    
    async def _download_single_image(self, url: str):
        """模拟下载单张图片"""
        # 模拟网络延迟
        await asyncio.sleep(0.02)
        
        # 模拟下载结果
        self.images_downloaded += 1
        
        # 模拟偶尔失败
        if "car-model-010" in url or "car-model-020" in url:
            raise Exception("模拟网络错误")
        
        logger.debug(f"下载图片：{url}")

async def run_integration_example():
    """运行集成示例"""
    logger.info("T8 与 T4/T5 集成示例")
    logger.info("=" * 50)
    
    # 创建T8实例
    config = get_config('development')
    t8 = T8ResumeAndRetry(config)
    
    try:
        # 启动T8服务
        t8.start_service()
        logger.info("T8服务已启动")
        
        # 创建模拟采集器
        t4_collector = MockT4ListCollector(t8)
        t5_collector = MockT5DetailCollector(t8)
        t6_downloader = MockT6ImageDownloader(t8)
        
        # 第一阶段：列表采集
        logger.info("\n=== 第一阶段：列表采集 ===")
        await t4_collector.run_collection(start_page=1, max_pages=5)
        
        # 检查断点续采点
        list_resume = t8.get_resume_point("LIST_COLLECTION")
        if list_resume:
            logger.info(f"列表采集断点续采点：第{list_resume.current_page}页，已处理{list_resume.total_processed}项")
        
        # 检查失败任务
        failed_tasks = t8.get_retryable_tasks()
        logger.info(f"失败任务数量：{len(failed_tasks)}")
        
        # 第二阶段：详情采集
        logger.info("\n=== 第二阶段：详情采集 ===")
        await t5_collector.collect_details()
        
        # 检查详情采集断点续采点
        detail_resume = t8.get_resume_point("DETAIL_COLLECTION")
        if detail_resume:
            logger.info(f"详情采集断点续采点：最后slug {detail_resume.last_slug}，已处理{detail_resume.total_processed}项")
        
        # 第三阶段：图片下载
        logger.info("\n=== 第三阶段：图片下载 ===")
        await t6_downloader.download_images()
        
        # 检查图片下载断点续采点
        image_resume = t8.get_resume_point("IMAGE_DOWNLOAD")
        if image_resume:
            logger.info(f"图片下载断点续采点：最后URL {image_resume.last_slug}，已处理{image_resume.total_processed}项")
        
        # 等待一段时间让重试服务处理失败任务
        logger.info("\n等待重试服务处理失败任务...")
        await asyncio.sleep(5)
        
        # 最终统计
        logger.info("\n=== 最终统计 ===")
        logger.info(f"列表采集：{t4_collector.works_fetched}个作品")
        logger.info(f"详情采集：{t5_collector.details_fetched}个详情")
        logger.info(f"图片下载：{t6_downloader.images_downloaded}张图片")
        
        # 检查所有断点续采点
        all_resume_points = len([p for p in t8.state_manager.resume_points.values()])
        all_failed_tasks = len(t8.state_manager.failed_tasks)
        all_retryable_tasks = len(t8.get_retryable_tasks())
        
        logger.info(f"断点续采点总数：{all_resume_points}")
        logger.info(f"失败任务总数：{all_failed_tasks}")
        logger.info(f"可重试任务数：{all_retryable_tasks}")
        
        logger.info("\n✅ 集成示例完成")
        
    except Exception as e:
        logger.error(f"集成示例异常：{e}")
        raise
    finally:
        # 停止T8服务
        t8.stop_service()
        logger.info("T8服务已停止")

async def demonstrate_resume_capability():
    """演示断点续采能力"""
    logger.info("\n=== 演示断点续采能力 ===")
    
    # 创建T8实例
    config = get_config('development')
    t8 = T8ResumeAndRetry(config)
    
    try:
        # 启动服务
        t8.start_service()
        
        # 模拟第一次运行（采集前5页）
        logger.info("第一次运行：采集前5页")
        t4_collector = MockT4ListCollector(t8)
        await t4_collector.run_collection(start_page=1, max_pages=5)
        
        # 检查状态
        list_resume = t8.get_resume_point("LIST_COLLECTION")
        logger.info(f"第一次运行后断点续采点：第{list_resume.current_page}页，已处理{list_resume.works_fetched}项")
        
        # 模拟第二次运行（从断点续采点继续）
        logger.info("\n第二次运行：从断点续采点继续")
        await t4_collector.run_collection(start_page=1, max_pages=10)
        
        # 检查最终状态
        final_resume = t8.get_resume_point("LIST_COLLECTION")
        logger.info(f"第二次运行后断点续采点：第{final_resume.current_page}页，已处理{final_resume.works_fetched}项")
        
        logger.info("✅ 断点续采能力演示完成")
        
    except Exception as e:
        logger.error(f"断点续采能力演示异常：{e}")
    finally:
        t8.stop_service()

async def main():
    """主函数"""
    try:
        # 运行集成示例
        await run_integration_example()
        
        # 演示断点续采能力
        await demonstrate_resume_capability()
        
    except KeyboardInterrupt:
        logger.info("\n用户中断")
    except Exception as e:
        logger.error(f"运行异常：{e}")
        raise

if __name__ == "__main__":
    # 创建日志目录
    Path("logs").mkdir(exist_ok=True)
    
    # 运行主函数
    asyncio.run(main())
