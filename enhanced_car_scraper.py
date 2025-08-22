#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版汽车交通模型数据采集器
支持多种策略获取大量模型数据
"""

import requests
import json
import time
import logging
import os
from typing import Dict, List, Any
from datetime import datetime
import re

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_car_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedCarModelScraper:
    def __init__(self):
        self.api_base = "https://api2.liblib.art"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.liblib.art/',
            'Origin': 'https://www.liblib.art'
        })
        self.collected_models = []
        self.model_ids = set()  # 避免重复
        
        # 汽车交通相关关键词
        self.car_keywords = [
            "汽车", "车", "跑车", "超跑", "轿车", "SUV", "卡车", "货车", "客车", "巴士",
            "内饰", "外饰", "车身", "车型", "车展", "轮毂", "方向盘", "仪表盘",
            "保时捷", "法拉利", "兰博基尼", "奔驰", "宝马", "奥迪", "大众", "丰田", "本田",
            "特斯拉", "比亚迪", "蔚来", "小鹏", "理想", "吉利", "长城", "奇瑞",
            "电车", "电动车", "混动", "新能源", "充电", "电池",
            "概念车", "未来车", "科幻车", "赛车", "F1", "勒芒", "拉力赛",
            "摩托车", "电动车", "自行车", "三轮车", "房车", "露营车",
            "火车", "动车", "高铁", "地铁", "轻轨", "有轨电车",
            "飞机", "客机", "战斗机", "直升机", "无人机", "航空",
            "船", "轮船", "游艇", "帆船", "潜艇", "舰艇", "航母",
            "交通工具", "载具", "交通", "运输", "物流", "配送"
        ]

    def safe_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """安全的HTTP请求"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.request(method, url, timeout=30, **kwargs)
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"请求失败，状态码: {response.status_code}")
                    time.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"请求异常 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
        return {}

    def get_models_by_category(self, page: int = 1, page_size: int = 48) -> List[Dict]:
        """通过分类获取汽车交通模型"""
        url = f"{self.api_base}/api/www/model/list"
        
        payload = {
            "categories": ["汽车交通"],
            "page": page,
            "pageSize": page_size,
            "sortType": "recommend",
            "modelType": "",
            "nsfw": False
        }
        
        logger.info(f"获取分类模型 - 第 {page} 页...")
        response = self.safe_request('POST', url, json=payload)
        
        if response and 'data' in response and 'list' in response['data']:
            models = response['data']['list']
            logger.info(f"分类搜索获取到 {len(models)} 个模型")
            return models
        return []

    def get_models_by_search(self, keyword: str, page: int = 1, page_size: int = 48) -> List[Dict]:
        """通过搜索关键词获取模型"""
        url = f"{self.api_base}/api/www/model/list"
        
        payload = {
            "keyword": keyword,
            "page": page,
            "pageSize": page_size,
            "sortType": "recommend",
            "modelType": "",
            "nsfw": False
        }
        
        logger.info(f"搜索关键词 '{keyword}' - 第 {page} 页...")
        response = self.safe_request('POST', url, json=payload)
        
        if response and 'data' in response and 'list' in response['data']:
            models = response['data']['list']
            # 过滤汽车交通相关的模型
            filtered_models = []
            for model in models:
                title = (model.get('title') or '').lower()
                description = (model.get('description') or '').lower()
                if title and description and any(kw in title or kw in description for kw in self.car_keywords):
                    filtered_models.append(model)
            
            logger.info(f"关键词 '{keyword}' 搜索获取到 {len(filtered_models)} 个相关模型")
            return filtered_models
        return []

    def get_models_by_feed(self, page: int = 1) -> List[Dict]:
        """通过推荐流获取模型"""
        url = f"{self.api_base}/api/www/model/feed/stream"
        
        payload = {
            "page": page,
            "pageSize": 48
        }
        
        logger.info(f"获取推荐流 - 第 {page} 页...")
        response = self.safe_request('POST', url, json=payload)
        
        if response and 'data' in response and 'list' in response['data']:
            models = response['data']['list']
            # 过滤汽车交通相关的模型
            filtered_models = []
            for model in models:
                title = (model.get('title') or '').lower()
                description = (model.get('description') or '').lower()
                tags = model.get('tags', []) or []
                tag_text = ' '.join([tag.get('name', '') for tag in tags if tag and tag.get('name')]).lower()
                
                if title and any(kw in title or kw in description or kw in tag_text for kw in self.car_keywords):
                    filtered_models.append(model)
            
            logger.info(f"推荐流获取到 {len(filtered_models)} 个相关模型")
            return filtered_models
        return []

    def process_model(self, model: Dict) -> Dict:
        """处理模型数据"""
        try:
            model_id = model.get('id', '')
            if model_id in self.model_ids:
                return None  # 跳过重复模型
            
            self.model_ids.add(model_id)
            
            # 提取模型基本信息
            processed_model = {
                'id': model_id,
                'title': model.get('title') or '',
                'description': model.get('description') or '',
                'type': model.get('modelType', ''),
                'baseModel': model.get('baseModel', ''),
                'author': model.get('createdBy', {}).get('nickName', ''),
                'authorId': model.get('createdBy', {}).get('id', ''),
                'views': model.get('viewCount', 0),
                'likes': model.get('likeCount', 0),
                'downloads': model.get('downloadCount', 0),
                'createTime': model.get('createTime', ''),
                'updateTime': model.get('updateTime', ''),
                'isExclusive': model.get('isExclusive', False),
                'isVip': model.get('isVip', False),
                'url': f"https://www.liblib.art/modelinfo/{model_id}",
                'images': []
            }
            
            # 提取图片信息
            images = model.get('images', [])
            for img in images:
                if isinstance(img, dict):
                    processed_model['images'].append({
                        'url': img.get('url', ''),
                        'type': img.get('type', ''),
                        'width': img.get('width', 0),
                        'height': img.get('height', 0)
                    })
            
            # 提取标签
            tags = model.get('tags', [])
            processed_model['tags'] = [tag.get('name', '') for tag in tags if isinstance(tag, dict)]
            
            return processed_model
            
        except Exception as e:
            logger.error(f"处理模型数据时出错: {e}")
            return None

    def collect_models_comprehensive(self, target_count: int = 200) -> List[Dict]:
        """综合采集模型数据"""
        logger.info(f"开始综合采集，目标: {target_count} 个模型")
        
        # 策略1: 分类搜索
        logger.info("=== 策略1: 分类搜索 ===")
        page = 1
        while len(self.collected_models) < target_count:
            models = self.get_models_by_category(page, 48)
            if not models:
                break
                
            for model in models:
                processed = self.process_model(model)
                if processed:
                    self.collected_models.append(processed)
                    logger.info(f"采集进度: {len(self.collected_models)}/{target_count}")
                    
                    if len(self.collected_models) >= target_count:
                        break
            
            page += 1
            time.sleep(1)  # 避免请求过快
            
            if page > 20:  # 避免无限循环
                break
        
        # 策略2: 关键词搜索
        if len(self.collected_models) < target_count:
            logger.info("=== 策略2: 关键词搜索 ===")
            priority_keywords = ["汽车", "跑车", "内饰", "车型", "概念车", "超跑", "电动车", "未来车"]
            
            for keyword in priority_keywords:
                if len(self.collected_models) >= target_count:
                    break
                    
                page = 1
                while len(self.collected_models) < target_count and page <= 5:
                    models = self.get_models_by_search(keyword, page, 48)
                    if not models:
                        break
                        
                    for model in models:
                        processed = self.process_model(model)
                        if processed:
                            self.collected_models.append(processed)
                            logger.info(f"采集进度: {len(self.collected_models)}/{target_count}")
                            
                            if len(self.collected_models) >= target_count:
                                break
                    
                    page += 1
                    time.sleep(1)
        
        # 策略3: 推荐流搜索
        if len(self.collected_models) < target_count:
            logger.info("=== 策略3: 推荐流搜索 ===")
            page = 1
            while len(self.collected_models) < target_count and page <= 10:
                models = self.get_models_by_feed(page)
                if not models:
                    break
                    
                for model in models:
                    processed = self.process_model(model)
                    if processed:
                        self.collected_models.append(processed)
                        logger.info(f"采集进度: {len(self.collected_models)}/{target_count}")
                        
                        if len(self.collected_models) >= target_count:
                            break
                
                page += 1
                time.sleep(1)
        
        logger.info(f"采集完成！共获取 {len(self.collected_models)} 个模型")
        return self.collected_models

    def save_results(self, filename: str = None):
        """保存采集结果"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'enhanced_car_models_{timestamp}.json'
        
        # 计算统计信息
        total_models = len(self.collected_models)
        if total_models == 0:
            logger.warning("没有采集到任何模型数据")
            return
        
        total_views = sum(model.get('views', 0) for model in self.collected_models)
        total_likes = sum(model.get('likes', 0) for model in self.collected_models)
        total_downloads = sum(model.get('downloads', 0) for model in self.collected_models)
        
        exclusive_models = sum(1 for model in self.collected_models if model.get('isExclusive', False))
        vip_models = sum(1 for model in self.collected_models if model.get('isVip', False))
        
        summary = {
            'collection_time': datetime.now().isoformat(),
            'total_models': total_models,
            'exclusive_models': exclusive_models,
            'vip_models': vip_models,
            'regular_models': total_models - exclusive_models - vip_models,
            'total_views': total_views,
            'total_likes': total_likes,
            'total_downloads': total_downloads,
            'avg_views': total_views / total_models if total_models > 0 else 0,
            'avg_likes': total_likes / total_models if total_models > 0 else 0,
            'avg_downloads': total_downloads / total_models if total_models > 0 else 0
        }
        
        result = {
            'summary': summary,
            'models': self.collected_models
        }
        
        # 保存到文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"结果已保存到: {filename}")
        logger.info(f"采集统计:")
        logger.info(f"  总模型数: {total_models}")
        logger.info(f"  独家模型: {exclusive_models}")
        logger.info(f"  VIP模型: {vip_models}")
        logger.info(f"  普通模型: {summary['regular_models']}")
        logger.info(f"  总浏览量: {total_views:,}")
        logger.info(f"  总点赞数: {total_likes:,}")
        logger.info(f"  总下载量: {total_downloads:,}")
        
        return filename

def main():
    """主函数"""
    logger.info("启动增强版汽车交通模型采集器")
    
    scraper = EnhancedCarModelScraper()
    
    try:
        # 采集模型，目标200+
        models = scraper.collect_models_comprehensive(target_count=250)
        
        if models:
            # 保存结果
            filename = scraper.save_results()
            logger.info(f"采集任务完成！数据已保存到 {filename}")
        else:
            logger.error("采集失败，未获取到任何数据")
            
    except KeyboardInterrupt:
        logger.info("用户中断采集")
        if scraper.collected_models:
            filename = scraper.save_results('interrupted_car_models.json')
            logger.info(f"已保存当前采集的 {len(scraper.collected_models)} 个模型到 {filename}")
    except Exception as e:
        logger.error(f"采集过程中发生错误: {e}")
        if scraper.collected_models:
            filename = scraper.save_results('error_car_models.json')
            logger.info(f"已保存当前采集的 {len(scraper.collected_models)} 个模型到 {filename}")

if __name__ == "__main__":
    main()
