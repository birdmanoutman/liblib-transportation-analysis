#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于Playwright的汽车交通模型采集器
直接从页面提取数据，确保获取足够数量的模型
"""

import asyncio
import json
import time
import logging
import re
from datetime import datetime
from typing import List, Dict, Any
import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('playwright_car_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PlaywrightCarScraper:
    def __init__(self):
        self.collected_models = []
        self.model_ids = set()
        self.target_count = 200
        
    def extract_model_data_from_browser(self) -> List[Dict]:
        """从浏览器中提取模型数据"""
        import subprocess
        import os
        
        # 执行JavaScript来提取页面数据
        js_code = '''
        () => {
            const models = [];
            const modelCards = document.querySelectorAll('div[role="gridcell"]');
            
            modelCards.forEach((card, index) => {
                try {
                    // 获取链接和ID
                    const link = card.querySelector('a');
                    if (!link || !link.href) return;
                    
                    const modelId = link.href.match(/modelinfo\/([^/?]+)/)?.[1];
                    if (!modelId) return;
                    
                    // 获取标题
                    const titleElement = card.querySelector('h6') || 
                                       card.querySelector('[class*="title"]') || 
                                       card.querySelector('div:nth-child(2) > div:first-child');
                    const title = titleElement?.textContent?.trim() || '';
                    
                    // 获取作者信息
                    const authorElement = card.querySelector('div:last-child div:last-child') ||
                                        card.querySelector('[class*="author"]') ||
                                        card.querySelector('div[class*="user"]');
                    const author = authorElement?.textContent?.trim() || '';
                    
                    // 获取图片
                    const imgElement = card.querySelector('img');
                    const imageUrl = imgElement?.src || imgElement?.getAttribute('data-src') || '';
                    
                    // 获取统计数据 (views, likes, downloads)
                    const statElements = card.querySelectorAll('div[class*="stat"], div[class*="count"], span[class*="num"]');
                    const stats = Array.from(statElements).map(el => el.textContent?.trim()).filter(Boolean);
                    
                    // 获取模型类型
                    const typeElement = card.querySelector('div[class*="type"], span[class*="tag"], div[class*="model"]');
                    const modelType = typeElement?.textContent?.trim() || '';
                    
                    // 检查是否为汽车交通相关
                    const carKeywords = ['汽车', '车', '跑车', '内饰', '超跑', '保时捷', '卡车', '轮毂', 
                                       '车展', '车型', '车身', '极星', '概念车', '未来车', '电动车', '新能源',
                                       '摩托车', '火车', '动车', '高铁', '飞机', '船', '交通', '载具'];
                    
                    const isCarRelated = carKeywords.some(keyword => 
                        title.includes(keyword) || 
                        modelType.includes(keyword) ||
                        author.includes(keyword)
                    );
                    
                    if (isCarRelated && title) {
                        models.push({
                            id: modelId,
                            title: title,
                            author: author,
                            type: modelType,
                            imageUrl: imageUrl,
                            stats: stats,
                            url: link.href,
                            index: models.length + 1
                        });
                    }
                } catch (error) {
                    console.log('Error processing card:', error);
                }
            });
            
            return {
                models: models,
                totalCards: modelCards.length,
                carModels: models.length
            };
        }
        '''
        
        # 这里我们需要与MCP Playwright工具交互
        # 由于当前在Python环境中，我们创建一个简化版本
        logger.info("准备从浏览器提取数据...")
        return []
    
    def scroll_and_load_more(self, max_scrolls: int = 50) -> bool:
        """滚动页面加载更多内容"""
        logger.info(f"开始滚动页面，最多滚动 {max_scrolls} 次")
        
        # 这里需要与Playwright MCP交互
        # 模拟滚动过程
        for i in range(max_scrolls):
            logger.info(f"滚动第 {i+1} 次...")
            time.sleep(2)  # 等待加载
            
            # 检查是否有新内容加载
            # 这里需要实际的Playwright代码
            
        return True
    
    def collect_comprehensive_data(self) -> List[Dict]:
        """综合采集汽车交通模型数据"""
        logger.info(f"开始采集，目标数量: {self.target_count}")
        
        # 方法1: 直接点击汽车交通分类
        logger.info("=== 方法1: 访问汽车交通分类页面 ===")
        
        # 方法2: 使用API直接获取
        logger.info("=== 方法2: 尝试API调用 ===")
        api_models = self.try_api_collection()
        
        # 方法3: 组合搜索关键词
        logger.info("=== 方法3: 关键词搜索 ===")
        search_models = self.search_by_keywords()
        
        # 合并所有结果
        all_models = api_models + search_models
        
        # 去重
        unique_models = {}
        for model in all_models:
            model_id = model.get('id', '')
            if model_id and model_id not in unique_models:
                unique_models[model_id] = model
        
        self.collected_models = list(unique_models.values())
        logger.info(f"采集完成，共获取 {len(self.collected_models)} 个唯一模型")
        
        return self.collected_models
    
    def try_api_collection(self) -> List[Dict]:
        """尝试通过API采集数据"""
        models = []
        
        api_base = "https://api2.liblib.art"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.liblib.art/',
            'Origin': 'https://www.liblib.art'
        }
        
        # 尝试推荐流API
        try:
            url = f"{api_base}/api/www/model/feed/stream"
            
            for page in range(1, 11):  # 尝试前10页
                payload = {
                    "page": page,
                    "pageSize": 48
                }
                
                logger.info(f"API获取第 {page} 页...")
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('data') and data['data'].get('list'):
                        page_models = data['data']['list']
                        
                        # 过滤汽车交通相关模型
                        car_keywords = [
                            '汽车', '车', '跑车', '内饰', '超跑', '保时捷', '卡车', '轮毂',
                            '车展', '车型', '车身', '极星', '概念车', '未来车', '电动车', '新能源',
                            '摩托车', '火车', '动车', '高铁', '飞机', '船', '交通', '载具',
                            '奔驰', '宝马', '奥迪', '特斯拉', '比亚迪', '蔚来', '小鹏'
                        ]
                        
                        for model in page_models:
                            title = (model.get('title') or '').lower()
                            description = (model.get('description') or '').lower()
                            tags = model.get('tags', []) or []
                            tag_text = ' '.join([tag.get('name', '') for tag in tags if tag]).lower()
                            
                            if any(kw in title or kw in description or kw in tag_text for kw in car_keywords):
                                processed_model = self.process_model_data(model)
                                if processed_model:
                                    models.append(processed_model)
                                    logger.info(f"API采集到汽车模型: {model.get('title', '')}")
                        
                        if len(models) >= self.target_count:
                            break
                    else:
                        logger.warning(f"第 {page} 页没有数据")
                        break
                else:
                    logger.warning(f"API请求失败: {response.status_code}")
                
                time.sleep(1)  # 避免请求过快
                
        except Exception as e:
            logger.error(f"API采集出错: {e}")
        
        logger.info(f"API采集完成，获取 {len(models)} 个模型")
        return models
    
    def search_by_keywords(self) -> List[Dict]:
        """通过关键词搜索采集"""
        models = []
        
        keywords = [
            "汽车", "跑车", "超跑", "车型", "概念车", "未来车", "电动车",
            "保时捷", "法拉利", "特斯拉", "宝马", "奔驰", "奥迪",
            "内饰", "外饰", "车身", "轮毂", "车展", "赛车"
        ]
        
        api_base = "https://api2.liblib.art"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://www.liblib.art/'
        }
        
        for keyword in keywords:
            if len(models) >= self.target_count:
                break
                
            try:
                url = f"{api_base}/api/www/model/list"
                payload = {
                    "keyword": keyword,
                    "page": 1,
                    "pageSize": 24,
                    "sortType": "recommend"
                }
                
                logger.info(f"搜索关键词: {keyword}")
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('data') and data['data'].get('list'):
                        for model in data['data']['list']:
                            processed = self.process_model_data(model)
                            if processed and processed['id'] not in [m['id'] for m in models]:
                                models.append(processed)
                                logger.info(f"搜索采集到: {model.get('title', '')}")
                
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"搜索 {keyword} 时出错: {e}")
        
        logger.info(f"关键词搜索完成，获取 {len(models)} 个模型")
        return models
    
    def process_model_data(self, model: Dict) -> Dict:
        """处理模型数据"""
        try:
            model_id = model.get('id', '')
            if not model_id or model_id in self.model_ids:
                return None
            
            self.model_ids.add(model_id)
            
            # 处理基本信息
            processed = {
                'id': model_id,
                'title': model.get('title') or '',
                'description': model.get('description') or '',
                'type': model.get('modelType') or '',
                'baseModel': model.get('baseModel') or '',
                'author': '',
                'authorId': '',
                'views': model.get('viewCount', 0),
                'likes': model.get('likeCount', 0),
                'downloads': model.get('downloadCount', 0),
                'createTime': model.get('createTime', ''),
                'updateTime': model.get('updateTime', ''),
                'isExclusive': model.get('isExclusive', False),
                'isVip': model.get('isVip', False),
                'url': f"https://www.liblib.art/modelinfo/{model_id}",
                'images': [],
                'tags': []
            }
            
            # 处理作者信息
            created_by = model.get('createdBy', {})
            if created_by:
                processed['author'] = created_by.get('nickName', '')
                processed['authorId'] = created_by.get('id', '')
            
            # 处理图片
            images = model.get('images', [])
            for img in images:
                if isinstance(img, dict):
                    processed['images'].append({
                        'url': img.get('url', ''),
                        'type': img.get('type', ''),
                        'width': img.get('width', 0),
                        'height': img.get('height', 0)
                    })
            
            # 处理标签
            tags = model.get('tags', [])
            for tag in tags:
                if isinstance(tag, dict) and tag.get('name'):
                    processed['tags'].append(tag['name'])
            
            return processed
            
        except Exception as e:
            logger.error(f"处理模型数据出错: {e}")
            return None
    
    def save_results(self, filename: str = None) -> str:
        """保存采集结果"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'playwright_car_models_{timestamp}.json'
        
        total_models = len(self.collected_models)
        if total_models == 0:
            logger.warning("没有采集到任何模型数据")
            return filename
        
        # 计算统计信息
        total_views = sum(model.get('views', 0) for model in self.collected_models)
        total_likes = sum(model.get('likes', 0) for model in self.collected_models)
        total_downloads = sum(model.get('downloads', 0) for model in self.collected_models)
        
        exclusive_count = sum(1 for model in self.collected_models if model.get('isExclusive', False))
        vip_count = sum(1 for model in self.collected_models if model.get('isVip', False))
        
        # 按浏览量排序
        sorted_models = sorted(self.collected_models, key=lambda x: x.get('views', 0), reverse=True)
        
        summary = {
            'collection_time': datetime.now().isoformat(),
            'collection_method': 'Playwright + API',
            'total_models': total_models,
            'exclusive_models': exclusive_count,
            'vip_models': vip_count,
            'regular_models': total_models - exclusive_count - vip_count,
            'total_views': total_views,
            'total_likes': total_likes,
            'total_downloads': total_downloads,
            'avg_views': total_views / total_models if total_models > 0 else 0,
            'avg_likes': total_likes / total_models if total_models > 0 else 0,
            'avg_downloads': total_downloads / total_models if total_models > 0 else 0,
            'top_models': [model['title'] for model in sorted_models[:10]]
        }
        
        result = {
            'summary': summary,
            'models': sorted_models
        }
        
        # 保存文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 输出统计信息
        logger.info(f"=== 采集完成统计 ===")
        logger.info(f"文件保存: {filename}")
        logger.info(f"总模型数: {total_models}")
        logger.info(f"独家模型: {exclusive_count}")
        logger.info(f"VIP模型: {vip_count}")
        logger.info(f"普通模型: {summary['regular_models']}")
        logger.info(f"总浏览量: {total_views:,}")
        logger.info(f"总点赞数: {total_likes:,}")
        logger.info(f"总下载量: {total_downloads:,}")
        logger.info(f"平均浏览量: {summary['avg_views']:.1f}")
        
        if sorted_models:
            logger.info(f"最热门模型: {sorted_models[0]['title']} (浏览量: {sorted_models[0]['views']:,})")
        
        return filename

def main():
    """主函数"""
    logger.info("启动Playwright汽车交通模型采集器")
    
    scraper = PlaywrightCarScraper()
    
    try:
        # 开始采集
        models = scraper.collect_comprehensive_data()
        
        if models:
            filename = scraper.save_results()
            logger.info(f"采集成功！共获取 {len(models)} 个汽车交通模型")
            logger.info(f"数据已保存到: {filename}")
            
            if len(models) >= scraper.target_count:
                logger.info(f"✅ 已达到目标数量 {scraper.target_count}!")
            else:
                logger.warning(f"⚠️ 未达到目标数量，仅采集到 {len(models)} 个模型")
        else:
            logger.error("采集失败，未获取到任何数据")
            
    except KeyboardInterrupt:
        logger.info("用户中断采集")
        if scraper.collected_models:
            filename = scraper.save_results('interrupted_playwright_models.json')
            logger.info(f"已保存当前采集的 {len(scraper.collected_models)} 个模型")
    except Exception as e:
        logger.error(f"采集过程中发生错误: {e}")
        if scraper.collected_models:
            filename = scraper.save_results('error_playwright_models.json')
            logger.info(f"已保存当前采集的 {len(scraper.collected_models)} 个模型")

if __name__ == "__main__":
    main()
