#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Liblib 汽车交通模型完整分析器
整合数据采集、图片下载、数据分析和报告生成的统一工具

功能特性：
- 🚗 智能数据采集（API + 浏览器自动化）
- 🖼️ 批量图片下载（支持多种格式）
- 📊 深度数据分析（多维度统计）
- 📝 专业报告生成（Markdown + 图表）
- ⚡ 高性能并发处理
- 🛡️ 完善的错误处理和重试机制

使用方法：
    python liblib_car_analyzer.py [选项]

选项：
    --collect    执行数据采集
    --download  执行图片下载
    --analyze   执行数据分析
    --report    生成分析报告
    --all       执行完整流程
    --config    指定配置文件
    --output    指定输出目录
    --help      显示帮助信息

示例：
    python liblib_car_analyzer.py --all
    python liblib_car_analyzer.py --collect --download
    python liblib_car_analyzer.py --config config.json
"""

import os
import sys
import json
import time
import logging
import argparse
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import requests
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
from urllib.parse import urlparse, urljoin
import re

# 导入配置管理模块
try:
    from config_manager import ConfigManager
except ImportError:
    # 如果导入失败，创建一个简单的配置管理器
    class ConfigManager:
        def __init__(self):
            self.config_data = {}
        def get(self, key_path, default=None):
            return default
        def load_config(self):
            return {}

# 尝试导入Playwright（可选依赖）
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Playwright未安装，浏览器自动化功能将不可用")
    print("   安装命令: pip install playwright && playwright install")

class LiblibCarModelsAnalyzer:
    """Liblib汽车交通模型完整分析器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化分析器"""
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        
        # 加载配置
        if config:
            self.config_manager.config_data = config
        else:
            self.config_manager.load_config()
        
        self.config = self.config_manager.get_effective_config()
        self._setup_logging()
        self._setup_directories()
        self._setup_session()
        
        # 数据存储
        self.models_data = []
        self.collected_models = set()
        self.analysis_results = {}
        
        # 统计信息
        self.stats = {
            'total_models': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'start_time': time.time()
        }
    
    def _get_default_config(self) -> Dict:
        """获取默认配置（兼容性方法）"""
        return self.config_manager.get_effective_config()
    
    def _setup_logging(self):
        """设置日志系统"""
        # 获取日志配置
        log_level = getattr(logging, self.config_manager.get('logging.level', 'INFO').upper(), logging.INFO)
        file_logging = self.config_manager.get('logging.file_logging', True)
        console_logging = self.config_manager.get('logging.console_logging', True)
        
        # 设置日志格式
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        # 清除现有的处理器
        logging.getLogger().handlers.clear()
        
        # 设置根日志器级别
        logging.getLogger().setLevel(log_level)
        
        # 创建格式化器
        formatter = logging.Formatter(log_format)
        
        # 添加文件处理器
        if file_logging:
            log_dir = Path(self.config['storage']['output_dir']) / self.config['storage']['logs_dir']
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f"liblib_analyzer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logging.getLogger().addHandler(file_handler)
        
        # 添加控制台处理器
        if console_logging:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logging.getLogger().addHandler(console_handler)
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Liblib汽车交通模型分析器启动")
    
    def _setup_directories(self):
        """设置输出目录"""
        self.output_dir = Path(self.config['storage']['output_dir'])
        self.images_dir = self.output_dir / self.config['storage']['images_dir']
        self.data_dir = self.output_dir / self.config['storage']['data_dir']
        self.reports_dir = self.output_dir / self.config['storage']['reports_dir']
        
        for dir_path in [self.output_dir, self.images_dir, self.data_dir, self.reports_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"输出目录: {self.output_dir.absolute()}")
    
    def _setup_session(self):
        """设置HTTP会话"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.liblib.art/',
            'Origin': 'https://www.liblib.art'
        })
        
        # 设置超时和重试配置
        self.timeout = self.config_manager.get('api.timeout', 30)
        self.retry_times = self.config_manager.get('api.retry_times', 3)
        self.retry_delay = self.config_manager.get('api.retry_delay', 2)
    
    def safe_request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """安全的HTTP请求，支持重试"""
        for attempt in range(self.retry_times):
            try:
                response = self.session.request(
                    method, url, 
                    timeout=self.timeout,
                    **kwargs
                )
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                self.logger.warning(f"请求失败 (尝试 {attempt + 1}/{self.retry_times}) {url}: {e}")
                if attempt < self.retry_times - 1:
                    time.sleep(self.retry_delay ** attempt)
        return None
    
    def get_timestamp(self) -> int:
        """获取当前时间戳"""
        return int(time.time() * 1000)
    
    async def collect_data_api(self) -> List[Dict]:
        """通过API采集数据"""
        self.logger.info("开始API数据采集...")
        all_models = []
        
        max_pages = self.config_manager.get('scraping.max_pages', 10)
        delay_between_pages = self.config_manager.get('scraping.delay_between_pages', 1)
        
        for page in range(1, max_pages + 1):
            models = self._get_models_by_page(page)
            if not models:
                self.logger.info(f"第{page}页无数据，停止采集")
                break
            
            all_models.extend(models)
            self.logger.info(f"第{page}页采集到{len(models)}个模型")
            
            # 避免请求过快
            if page < max_pages:
                time.sleep(delay_between_pages)
        
        self.logger.info(f"API采集完成，共获取{len(all_models)}个模型")
        return all_models
    
    def _get_models_by_page(self, page: int) -> List[Dict]:
        """获取指定页的模型数据"""
        url = f"{self.config['api_base']}/api/www/model/list"
        
        payload = {
            "categories": ["汽车交通"],
            "page": page,
            "pageSize": self.config['page_size'],
            "sortType": "recommend",
            "modelType": "",
            "nsfw": False
        }
        
        response = self.safe_request('POST', url, json=payload)
        if response:
            try:
                data = response.json()
                if data.get('data', {}).get('list'):
                    return data['data']['list']
            except json.JSONDecodeError:
                self.logger.error("响应JSON解析失败")
        
        return []
    
    async def collect_data_browser(self) -> List[Dict]:
        """通过浏览器自动化采集数据"""
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.warning("Playwright不可用，跳过浏览器采集")
            return []
        
        self.logger.info("开始浏览器数据采集...")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # 访问页面
                await page.goto(f"{self.config['base_url']}/models?category=汽车交通")
                await page.wait_for_load_state('networkidle')
                
                # 滚动页面加载更多内容
                models = await self._scroll_and_extract(page)
                
                await browser.close()
                self.logger.info(f"浏览器采集完成，共获取{len(models)}个模型")
                return models
                
        except Exception as e:
            self.logger.error(f"浏览器采集失败: {e}")
            return []
    
    async def _scroll_and_extract(self, page) -> List[Dict]:
        """滚动页面并提取数据"""
        models = []
        last_height = await page.evaluate("document.body.scrollHeight")
        
        while len(models) < 200:  # 最大200个模型
            # 滚动到底部
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)
            
            # 提取当前页面的模型数据
            new_models = await page.evaluate("""
                () => {
                    const models = [];
                    const cards = document.querySelectorAll('div[role="gridcell"]');
                    
                    cards.forEach(card => {
                        try {
                            const link = card.querySelector('a');
                            if (!link || !link.href) return;
                            
                            const modelId = link.href.match(/modelinfo\/([^/?]+)/)?.[1];
                            if (!modelId) return;
                            
                            const title = card.querySelector('h6')?.textContent?.trim() || '';
                            const author = card.querySelector('div:last-child div:last-child')?.textContent?.trim() || '';
                            const imageUrl = card.querySelector('img')?.src || '';
                            
                            if (title && author) {
                                models.push({
                                    id: modelId,
                                    title: title,
                                    author: author,
                                    imageUrl: imageUrl,
                                    url: link.href
                                });
                            }
                        } catch (e) {}
                    });
                    
                    return models;
                }
            """)
            
            # 去重
            for model in new_models:
                if model['id'] not in [m['id'] for m in models]:
                    models.append(model)
            
            # 检查是否到达底部
            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            
            self.logger.info(f"已采集{len(models)}个模型，继续滚动...")
        
        return models
    
    async def collect_data_enhanced(self) -> List[Dict]:
        """增强搜索策略采集数据"""
        self.logger.info("开始增强搜索数据采集...")
        all_models = []
        
        # 通过关键词搜索
        for keyword in self.config['car_keywords'][:10]:  # 限制关键词数量
            models = self._search_models_by_keyword(keyword)
            all_models.extend(models)
            self.logger.info(f"关键词'{keyword}'搜索到{len(models)}个模型")
            time.sleep(1)
        
        # 去重
        unique_models = []
        seen_ids = set()
        for model in all_models:
            if model.get('id') not in seen_ids:
                unique_models.append(model)
                seen_ids.add(model.get('id'))
        
        self.logger.info(f"增强搜索完成，共获取{len(unique_models)}个唯一模型")
        return unique_models
    
    def _search_models_by_keyword(self, keyword: str) -> List[Dict]:
        """通过关键词搜索模型"""
        url = f"{self.config['api_base']}/api/www/model/list"
        
        payload = {
            "keyword": keyword,
            "page": 1,
            "pageSize": 24,
            "sortType": "recommend",
            "modelType": "",
            "nsfw": False
        }
        
        response = self.safe_request('POST', url, json=payload)
        if response:
            try:
                data = response.json()
                if data.get('data', {}).get('list'):
                    return data['data']['list']
            except json.JSONDecodeError:
                self.logger.error("搜索响应JSON解析失败")
        
        return []
    
    async def collect_all_data(self) -> List[Dict]:
        """采集所有数据（多种策略结合）"""
        self.logger.info("开始综合数据采集...")
        
        # 1. API采集（主要方式）
        api_models = await self.collect_data_api()
        
        # 2. 浏览器采集（补充）
        browser_models = await self.collect_data_browser()
        
        # 3. 增强搜索（补充）
        enhanced_models = await self.collect_data_enhanced()
        
        # 合并所有数据
        all_models = []
        seen_ids = set()
        
        for model_list in [api_models, browser_models, enhanced_models]:
            for model in model_list:
                model_id = model.get('id') or model.get('uuid')
                if model_id and model_id not in seen_ids:
                    all_models.append(model)
                    seen_ids.add(model_id)
        
        # 获取详细信息
        detailed_models = []
        with ThreadPoolExecutor(max_workers=self.config['max_workers']) as executor:
            future_to_model = {
                executor.submit(self._get_model_detail, model): model 
                for model in all_models[:50]  # 限制数量
            }
            
            for future in as_completed(future_to_model):
                model = future_to_model[future]
                try:
                    detail = future.result()
                    if detail:
                        detailed_models.append(detail)
                except Exception as e:
                    self.logger.error(f"获取模型详情失败: {e}")
        
        self.logger.info(f"综合采集完成，共获取{len(detailed_models)}个详细模型")
        return detailed_models
    
    def _get_model_detail(self, model: Dict) -> Optional[Dict]:
        """获取模型详细信息"""
        model_id = model.get('id') or model.get('uuid')
        if not model_id:
            return None
        
        url = f"{self.config['api_base']}/api/www/model/getByUuid/{model_id}"
        params = {"timestamp": self.get_timestamp()}
        
        response = self.safe_request('POST', url, params=params)
        if response:
            try:
                data = response.json()
                if data.get('data'):
                    return data['data']
            except json.JSONDecodeError:
                self.logger.error("模型详情JSON解析失败")
        
        return None
    
    async def download_images(self, models: List[Dict]) -> Dict:
        """批量下载图片"""
        self.logger.info("开始批量图片下载...")
        
        download_results = {
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'total': len(models)
        }
        
        def download_single_image(model):
            """下载单个图片"""
            try:
                image_url = model.get('coverUrl') or model.get('imageUrl')
                if not image_url:
                    return 'skipped'
                
                # 生成文件名
                title = model.get('title', 'unknown')
                safe_title = re.sub(r'[^\w\s-]', '', title)[:50]
                filename = f"{safe_title}_{model.get('id', 'unknown')}"
                
                # 获取文件扩展名
                parsed_url = urlparse(image_url)
                path = parsed_url.path
                if '.' in path:
                    ext = path.split('.')[-1]
                    if ext.lower() in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                        filename = f"{filename}.{ext}"
                    else:
                        filename = f"{filename}.jpg"
                else:
                    filename = f"{filename}.jpg"
                
                filepath = self.images_dir / filename
                
                # 检查文件是否已存在
                if filepath.exists():
                    return 'skipped'
                
                # 下载图片
                response = self.safe_request('GET', image_url)
                if response:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    return 'success'
                else:
                    return 'failed'
                    
            except Exception as e:
                self.logger.error(f"下载图片失败: {e}")
                return 'failed'
        
        # 并发下载
        with ThreadPoolExecutor(max_workers=self.config['max_workers']) as executor:
            future_to_model = {
                executor.submit(download_single_image, model): model 
                for model in models
            }
            
            for future in as_completed(future_to_model):
                result = future.result()
                if result == 'success':
                    download_results['successful'] += 1
                elif result == 'failed':
                    download_results['failed'] += 1
                else:
                    download_results['skipped'] += 1
                
                # 显示进度
                total_processed = download_results['successful'] + download_results['failed'] + download_results['skipped']
                if total_processed % 5 == 0:
                    self.logger.info(f"下载进度: {total_processed}/{download_results['total']}")
        
        self.logger.info(f"图片下载完成: 成功{download_results['successful']}, 失败{download_results['failed']}, 跳过{download_results['skipped']}")
        return download_results
    
    def analyze_data(self, models: List[Dict]) -> Dict:
        """分析数据"""
        self.logger.info("开始数据分析...")
        
        if not models:
            self.logger.warning("没有数据可分析")
            return {}
        
        # 数据预处理
        df = pd.DataFrame(models)
        
        # 解析数值字段
        numeric_fields = ['views', 'likes', 'downloads']
        for field in numeric_fields:
            if field in df.columns:
                df[field] = df[field].apply(self._parse_number)
        
        # 基础统计
        basic_stats = {
            'total_models': len(models),
            'unique_authors': df['author'].nunique() if 'author' in df.columns else 0,
            'model_types': df['type'].value_counts().to_dict() if 'type' in df.columns else {},
            'total_views': df['views'].sum() if 'views' in df.columns else 0,
            'total_likes': df['likes'].sum() if 'likes' in df.columns else 0,
            'total_downloads': df['downloads'].sum() if 'downloads' in df.columns else 0
        }
        
        # 计算平均值
        if 'views' in df.columns:
            basic_stats['avg_views'] = df['views'].mean()
        if 'likes' in df.columns:
            basic_stats['avg_likes'] = df['likes'].mean()
        if 'downloads' in df.columns:
            basic_stats['avg_downloads'] = df['downloads'].mean()
        
        # 作者分析
        author_stats = {}
        if 'author' in df.columns and 'views' in df.columns:
            author_stats = df.groupby('author').agg({
                'views': 'sum',
                'likes': 'sum',
                'downloads': 'sum'
            }).sort_values('views', ascending=False).head(10).to_dict('index')
        
        # 模型类型分析
        type_stats = {}
        if 'type' in df.columns and 'views' in df.columns:
            type_stats = df.groupby('type').agg({
                'views': 'sum',
                'likes': 'sum',
                'downloads': 'sum',
                'id': 'count'
            }).rename(columns={'id': 'count'}).to_dict('index')
        
        # 参与度分析
        engagement_stats = {}
        if 'views' in df.columns and 'likes' in df.columns and 'downloads' in df.columns:
            df['engagement_rate'] = (df['likes'] + df['downloads']) / df['views']
            engagement_stats = {
                'avg_engagement_rate': df['engagement_rate'].mean(),
                'top_engagement_models': df.nlargest(5, 'engagement_rate')[['title', 'author', 'engagement_rate']].to_dict('records')
            }
        
        analysis_results = {
            'basic_stats': basic_stats,
            'author_stats': author_stats,
            'type_stats': type_stats,
            'engagement_stats': engagement_stats,
            'raw_data': models
        }
        
        self.logger.info("数据分析完成")
        return analysis_results
    
    def _parse_number(self, value) -> Union[int, float]:
        """解析数字字符串"""
        if pd.isna(value) or value is None:
            return 0
        
        if isinstance(value, (int, float)):
            return value
        
        if isinstance(value, str):
            # 处理k, w等后缀
            value = value.lower().strip()
            if 'k' in value:
                return float(value.replace('k', '')) * 1000
            elif 'w' in value:
                return float(value.replace('w', '')) * 10000
            elif value.isdigit():
                return int(value)
            else:
                # 尝试提取数字
                numbers = re.findall(r'\d+\.?\d*', value)
                if numbers:
                    return float(numbers[0])
        
        return 0
    
    def generate_report(self, analysis_results: Dict) -> str:
        """生成分析报告"""
        self.logger.info("开始生成分析报告...")
        
        if not analysis_results:
            return "无数据可生成报告"
        
        # 生成Markdown报告
        report_content = self._generate_markdown_report(analysis_results)
        
        # 保存报告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.reports_dir / f"liblib_car_analysis_{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.info(f"报告已保存: {report_file}")
        return str(report_file)
    
    def _generate_markdown_report(self, analysis_results: Dict) -> str:
        """生成Markdown格式报告"""
        basic_stats = analysis_results.get('basic_stats', {})
        author_stats = analysis_results.get('author_stats', {})
        type_stats = analysis_results.get('type_stats', {})
        engagement_stats = analysis_results.get('engagement_stats', {})
        
        report = f"""# Liblib 汽车交通模型分析报告

## 📊 基础统计

- **总模型数量**: {basic_stats.get('total_models', 0)}
- **唯一作者数**: {basic_stats.get('unique_authors', 0)}
- **总浏览量**: {basic_stats.get('total_views', 0):,}
- **总点赞数**: {basic_stats.get('total_likes', 0):,}
- **总下载量**: {basic_stats.get('total_downloads', 0):,}
- **平均浏览量**: {basic_stats.get('avg_views', 0):,.1f}
- **平均点赞数**: {basic_stats.get('avg_likes', 0):,.1f}
- **平均下载量**: {basic_stats.get('avg_downloads', 0):,.1f}

## 🏆 模型类型分布

"""
        
        for model_type, stats in type_stats.items():
            report += f"- **{model_type}**: {stats.get('count', 0)}个模型\n"
        
        report += "\n## 👥 作者排行榜 (Top 10)\n\n"
        
        for i, (author, stats) in enumerate(author_stats.items(), 1):
            report += f"{i}. **{author}**\n"
            report += f"   - 浏览量: {stats.get('views', 0):,}\n"
            report += f"   - 点赞数: {stats.get('likes', 0):,}\n"
            report += f"   - 下载量: {stats.get('downloads', 0):,}\n\n"
        
        if engagement_stats:
            report += f"## 📈 参与度分析\n\n"
            report += f"- **平均参与率**: {engagement_stats.get('avg_engagement_rate', 0):.2%}\n\n"
            report += f"- **参与度最高的模型**:\n"
            for model in engagement_stats.get('top_engagement_models', []):
                report += f"  - {model.get('title', 'Unknown')} (作者: {model.get('author', 'Unknown')})\n"
                report += f"    参与率: {model.get('engagement_rate', 0):.2%}\n\n"
        
        report += f"\n---\n\n*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        report += f"*数据来源: Liblib.art 汽车交通板块*\n"
        
        return report
    
    def save_data(self, models: List[Dict], analysis_results: Dict):
        """保存数据到文件"""
        self.logger.info("保存数据到文件...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存原始数据
        data_file = self.data_dir / f"models_data_{timestamp}.json"
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(models, f, ensure_ascii=False, indent=2)
        
        # 保存分析结果
        analysis_file = self.data_dir / f"analysis_results_{timestamp}.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"数据已保存: {data_file}, {analysis_file}")
    
    async def run_full_analysis(self):
        """运行完整分析流程"""
        self.logger.info("开始运行完整分析流程...")
        
        try:
            # 1. 数据采集
            self.logger.info("=== 第一阶段: 数据采集 ===")
            models = await self.collect_all_data()
            if not models:
                self.logger.error("数据采集失败，无法继续")
                return False
            
            # 2. 图片下载
            self.logger.info("=== 第二阶段: 图片下载 ===")
            download_results = await self.download_images(models)
            
            # 3. 数据分析
            self.logger.info("=== 第三阶段: 数据分析 ===")
            analysis_results = self.analyze_data(models)
            
            # 4. 生成报告
            self.logger.info("=== 第四阶段: 生成报告 ===")
            report_file = self.generate_report(analysis_results)
            
            # 5. 保存数据
            self.logger.info("=== 第五阶段: 保存数据 ===")
            self.save_data(models, analysis_results)
            
            # 6. 统计信息
            elapsed_time = time.time() - self.stats['start_time']
            self.logger.info(f"=== 分析完成 ===")
            self.logger.info(f"总耗时: {elapsed_time:.2f}秒")
            self.logger.info(f"采集模型: {len(models)}个")
            self.logger.info(f"图片下载: 成功{download_results['successful']}个")
            self.logger.info(f"报告文件: {report_file}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"分析流程执行失败: {e}")
            return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Liblib 汽车交通模型完整分析器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # 基本功能参数
    parser.add_argument('--collect', action='store_true', help='执行数据采集')
    parser.add_argument('--download', action='store_true', help='执行图片下载')
    parser.add_argument('--analyze', action='store_true', help='执行数据分析')
    parser.add_argument('--report', action='store_true', help='生成分析报告')
    parser.add_argument('--all', action='store_true', help='执行完整流程')
    
    # 配置相关参数
    parser.add_argument('--config', type=str, help='指定配置文件')
    parser.add_argument('--create-config', action='store_true', help='创建配置模板文件')
    parser.add_argument('--show-config', action='store_true', help='显示当前配置摘要')
    
    # T10工单要求的参数化配置
    # 标签相关
    parser.add_argument('--tags', type=str, help='指定要采集的标签，用逗号分隔')
    parser.add_argument('--exclude-tags', type=str, help='指定要排除的标签，用逗号分隔')
    parser.add_argument('--custom-keywords', type=str, help='自定义关键词，用逗号分隔')
    
    # 排序相关
    parser.add_argument('--sort-by', type=str, choices=['downloads', 'likes', 'created_at', 'updated_at', 'name'], 
                       help='指定排序字段')
    parser.add_argument('--sort-order', type=str, choices=['asc', 'desc'], help='指定排序顺序')
    
    # 页范围相关
    parser.add_argument('--max-pages', type=int, help='最大采集页数')
    parser.add_argument('--page-size', type=int, help='每页模型数量')
    
    # 并发相关
    parser.add_argument('--max-workers', type=int, help='最大工作线程数')
    parser.add_argument('--concurrent-downloads', type=int, help='并发下载数量')
    
    # 存储路径相关
    parser.add_argument('--output-dir', type=str, help='指定输出目录')
    parser.add_argument('--images-dir', type=str, help='指定图片存储目录')
    
    # 日志相关
    parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       help='指定日志级别')
    parser.add_argument('--verbose', action='store_true', help='详细日志输出')
    
    args = parser.parse_args()
    
    # 创建配置管理器
    config_manager = ConfigManager()
    
    # 加载配置文件
    if args.config:
        config_manager.load_config(args.config)
    else:
        config_manager.load_config()
    
    # 从命令行参数更新配置
    config_manager.update_from_args(args)
    
    # 验证配置
    validation_errors = config_manager.validate_config()
    if validation_errors:
        print("❌ 配置验证失败:")
        for error in validation_errors:
            print(f"  - {error}")
        return
    
    # 显示配置摘要
    if args.show_config:
        config_manager.print_config_summary()
        return
    
    # 创建配置模板
    if args.create_config:
        if config_manager.create_config_template():
            print("✅ 配置模板创建成功")
        else:
            print("❌ 配置模板创建失败")
        return
    
    # 创建分析器
    analyzer = LiblibCarModelsAnalyzer(config_manager.get_effective_config())
    
    try:
        if args.all or (not any([args.collect, args.download, args.analyze, args.report])):
            # 运行完整流程
            asyncio.run(analyzer.run_full_analysis())
        else:
            # 运行指定功能
            if args.collect:
                print("数据采集功能需要完整流程支持")
            if args.download:
                print("图片下载功能需要完整流程支持")
            if args.analyze:
                print("数据分析功能需要完整流程支持")
            if args.report:
                print("报告生成功能需要完整流程支持")
            print("建议使用 --all 参数运行完整流程")
    
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"程序执行失败: {e}")
        analyzer.logger.error(f"程序执行失败: {e}")

if __name__ == "__main__":
    main()
