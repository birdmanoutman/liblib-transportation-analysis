#!/usr/bin/env python3
"""
LiblibAI 汽车交通模型完整采集器
为设计师提供趋势洞察的专业采集工具
"""

import requests
import json
import time
import os
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse, urljoin
import re
from datetime import datetime, timezone
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('car_models_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LiblibCarModelsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.liblib.art/',
            'Origin': 'https://www.liblib.art'
        })
        
        self.base_url = 'https://www.liblib.art'
        self.api_base = 'https://api2.liblib.art'
        self.image_base = 'https://liblibai-online.liblib.cloud'
        
        # 创建输出目录
        self.output_dir = 'car_models_complete'
        self.images_dir = os.path.join(self.output_dir, 'images')
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
        
        self.models_data = []
        self.collected_models = set()
        
    def get_timestamp(self) -> int:
        """获取当前时间戳"""
        return int(time.time() * 1000)
    
    def safe_request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """安全的HTTP请求"""
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"请求失败 {url}: {e}")
            time.sleep(2)
            return None
    
    def get_car_models_list(self, page: int = 1, page_size: int = 24) -> Dict[str, Any]:
        """获取汽车交通分类模型列表"""
        url = f"{self.api_base}/api/www/model/list"
        
        payload = {
            "categories": ["汽车交通"],  # 汽车交通分类
            "page": page,
            "pageSize": page_size,
            "sortType": "recommend",  # 推荐排序
            "modelType": "",
            "nsfw": False
        }
        
        logger.info(f"获取第 {page} 页汽车交通模型列表...")
        
        response = self.safe_request('POST', url, json=payload)
        if response:
            try:
                return response.json()
            except json.JSONDecodeError:
                logger.error("响应不是有效的JSON格式")
        
        return {}
    
    def get_model_detail(self, model_uuid: str) -> Optional[Dict[str, Any]]:
        """获取模型详细信息"""
        url = f"{self.api_base}/api/www/model/getByUuid/{model_uuid}"
        params = {"timestamp": self.get_timestamp()}
        
        response = self.safe_request('POST', url, params=params)
        if response:
            try:
                return response.json()
            except json.JSONDecodeError:
                logger.error(f"模型 {model_uuid} 详情响应格式错误")
        
        return None
    
    def get_model_versions(self, model_uuid: str) -> List[Dict[str, Any]]:
        """获取模型版本信息"""
        url = f"{self.api_base}/api/www/model-version/modelVersion/listByIds"
        payload = {
            "modelIds": [model_uuid],
            "timestamp": self.get_timestamp()
        }
        
        response = self.safe_request('POST', url, json=payload)
        if response:
            try:
                data = response.json()
                return data.get('data', [])
            except json.JSONDecodeError:
                logger.error(f"模型版本 {model_uuid} 响应格式错误")
        
        return []
    
    def get_model_author(self, model_uuid: str) -> Optional[Dict[str, Any]]:
        """获取模型作者信息"""
        url = f"{self.api_base}/api/www/model/author/{model_uuid}"
        params = {"timestamp": self.get_timestamp()}
        
        response = self.safe_request('POST', url, params=params)
        if response:
            try:
                return response.json()
            except json.JSONDecodeError:
                logger.error(f"作者信息 {model_uuid} 响应格式错误")
        
        return None
    
    def get_model_comments(self, model_uuid: str) -> List[Dict[str, Any]]:
        """获取模型评论"""
        url = f"{self.api_base}/api/www/community/commentList"
        payload = {
            "modelId": model_uuid,
            "page": 1,
            "pageSize": 50,
            "sortType": "hot",
            "timestamp": self.get_timestamp()
        }
        
        response = self.safe_request('POST', url, json=payload)
        if response:
            try:
                data = response.json()
                return data.get('data', {}).get('list', [])
            except json.JSONDecodeError:
                logger.error(f"评论 {model_uuid} 响应格式错误")
        
        return []
    
    def get_model_returns(self, model_uuid: str) -> List[Dict[str, Any]]:
        """获取模型返图（用户作品）"""
        url = f"{self.api_base}/api/www/community/returnPicList"
        payload = {
            "modelId": model_uuid,
            "page": 1,
            "pageSize": 20,
            "sortType": "hot",
            "timestamp": self.get_timestamp()
        }
        
        response = self.safe_request('POST', url, json=payload)
        if response:
            try:
                data = response.json()
                return data.get('data', {}).get('list', [])
            except json.JSONDecodeError:
                logger.error(f"返图 {model_uuid} 响应格式错误")
        
        return []
    
    def download_image(self, image_url: str, filename: str) -> bool:
        """下载图片"""
        if not image_url:
            return False
            
        try:
            # 添加图片处理参数以获取高质量图片
            if '?' in image_url:
                image_url = image_url.split('?')[0]
            
            image_url += '?x-oss-process=image/resize,w_1024,m_lfit/format,webp'
            
            response = self.safe_request('GET', image_url, timeout=30)
            if response:
                filepath = os.path.join(self.images_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return True
        except Exception as e:
            logger.error(f"下载图片失败 {image_url}: {e}")
        
        return False
    
    def extract_tags_and_keywords(self, model_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """提取标签和关键词"""
        tags = []
        keywords = []
        
        # 从模型名称提取关键词
        title = model_data.get('title', '')
        if title:
            # 提取中文关键词
            chinese_words = re.findall(r'[\u4e00-\u9fff]+', title)
            keywords.extend(chinese_words)
            
            # 提取英文关键词
            english_words = re.findall(r'[A-Za-z]+', title)
            keywords.extend(english_words)
        
        # 从标签列表提取
        tag_list = model_data.get('tagList', [])
        for tag in tag_list:
            if isinstance(tag, dict):
                tag_name = tag.get('name', '')
                if tag_name:
                    tags.append(tag_name)
            elif isinstance(tag, str):
                tags.append(tag)
        
        # 从描述中提取关键词
        description = model_data.get('description', '')
        if description:
            desc_keywords = re.findall(r'[\u4e00-\u9fff]+|[A-Za-z]+', description)
            keywords.extend(desc_keywords)
        
        return {
            'tags': list(set(tags)),
            'keywords': list(set(keywords))
        }
    
    def analyze_car_style(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析汽车风格和类型"""
        title = model_data.get('title', '').lower()
        description = model_data.get('description', '').lower()
        text = f"{title} {description}"
        
        style_analysis = {
            'vehicle_types': [],
            'design_styles': [],
            'render_styles': [],
            'use_cases': []
        }
        
        # 车辆类型识别
        vehicle_keywords = {
            '跑车': ['跑车', 'sports car', 'supercar'],
            '轿车': ['轿车', 'sedan', '轿车'],
            'SUV': ['suv', '越野', 'off-road'],
            '卡车': ['卡车', 'truck', '货车'],
            '巴士': ['巴士', 'bus', '公交'],
            '摩托车': ['摩托', 'motorcycle', '机车'],
            '概念车': ['概念', 'concept', '未来'],
            '赛车': ['赛车', 'racing', 'f1', 'formula'],
            '皮卡': ['皮卡', 'pickup'],
            '面包车': ['面包车', 'van', '商务车']
        }
        
        for vehicle_type, keywords in vehicle_keywords.items():
            if any(keyword in text for keyword in keywords):
                style_analysis['vehicle_types'].append(vehicle_type)
        
        # 设计风格识别
        design_keywords = {
            '科幻': ['科幻', 'sci-fi', '未来', 'future'],
            '复古': ['复古', 'vintage', 'retro', '经典'],
            '现代': ['现代', 'modern', '简约'],
            '豪华': ['豪华', 'luxury', '高端'],
            '运动': ['运动', 'sport', '动感'],
            '工业': ['工业', 'industrial', '机械'],
            '极简': ['极简', 'minimal', '简洁']
        }
        
        for style, keywords in design_keywords.items():
            if any(keyword in text for keyword in keywords):
                style_analysis['design_styles'].append(style)
        
        # 渲染风格识别
        render_keywords = {
            '写实': ['写实', 'realistic', '真实'],
            '插画': ['插画', 'illustration', '手绘'],
            '3D渲染': ['3d', 'render', '渲染'],
            '概念图': ['概念', 'concept', '草图'],
            '技术图': ['技术', 'technical', '工程图'],
            '海报': ['海报', 'poster', '广告']
        }
        
        for style, keywords in render_keywords.items():
            if any(keyword in text for keyword in keywords):
                style_analysis['render_styles'].append(style)
        
        # 使用场景识别
        use_case_keywords = {
            '游戏': ['游戏', 'game', '游戏设计'],
            '广告': ['广告', 'advertising', '营销'],
            '电影': ['电影', 'movie', '影视'],
            '工业设计': ['工业设计', 'industrial design'],
            '汽车设计': ['汽车设计', 'automotive design'],
            '概念设计': ['概念设计', 'concept design']
        }
        
        for use_case, keywords in use_case_keywords.items():
            if any(keyword in text for keyword in keywords):
                style_analysis['use_cases'].append(use_case)
        
        return style_analysis
    
    def process_single_model(self, model_basic: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """处理单个模型的完整信息"""
        model_uuid = model_basic.get('uuid')
        if not model_uuid or model_uuid in self.collected_models:
            return None
        
        logger.info(f"处理模型: {model_basic.get('title', 'Unknown')} ({model_uuid})")
        
        try:
            # 获取详细信息
            detail = self.get_model_detail(model_uuid)
            if not detail or detail.get('code') != 0:
                logger.warning(f"无法获取模型详情: {model_uuid}")
                return None
            
            model_data = detail.get('data', {})
            
            # 获取版本信息
            versions = self.get_model_versions(model_uuid)
            
            # 获取作者信息
            author_info = self.get_model_author(model_uuid)
            author_data = author_info.get('data', {}) if author_info else {}
            
            # 获取评论
            comments = self.get_model_comments(model_uuid)
            
            # 获取返图
            returns = self.get_model_returns(model_uuid)
            
            # 提取标签和关键词
            tags_keywords = self.extract_tags_and_keywords(model_data)
            
            # 分析汽车风格
            style_analysis = self.analyze_car_style(model_data)
            
            # 构建完整模型信息
            complete_model = {
                'uuid': model_uuid,
                'title': model_data.get('title', ''),
                'description': model_data.get('description', ''),
                'type': model_data.get('type', ''),
                'baseModel': model_data.get('baseModel', ''),
                'triggerWords': model_data.get('triggerWords', []),
                'nsfw': model_data.get('nsfw', False),
                'allowNoCredit': model_data.get('allowNoCredit', False),
                'allowCommercialUse': model_data.get('allowCommercialUse', False),
                'allowDerivatives': model_data.get('allowDerivatives', False),
                'allowDifferentLicense': model_data.get('allowDifferentLicense', False),
                
                # 统计数据
                'stats': {
                    'downloadCount': model_data.get('downloadCount', 0),
                    'favoriteCount': model_data.get('favoriteCount', 0),
                    'likeCount': model_data.get('likeCount', 0),
                    'commentCount': model_data.get('commentCount', 0),
                    'generateCount': model_data.get('generateCount', 0),
                    'viewCount': model_data.get('viewCount', 0)
                },
                
                # 作者信息
                'author': {
                    'uuid': author_data.get('uuid', ''),
                    'username': author_data.get('username', ''),
                    'nickname': author_data.get('nickname', ''),
                    'avatar': author_data.get('avatar', ''),
                    'followerCount': author_data.get('followerCount', 0),
                    'modelCount': author_data.get('modelCount', 0)
                },
                
                # 版本信息
                'versions': versions,
                
                # 标签和关键词
                'tags': tags_keywords['tags'],
                'keywords': tags_keywords['keywords'],
                
                # 汽车风格分析
                'car_analysis': style_analysis,
                
                # 评论摘要
                'comments_summary': {
                    'total_comments': len(comments),
                    'recent_comments': comments[:5]  # 最近5条评论
                },
                
                # 返图摘要
                'returns_summary': {
                    'total_returns': len(returns),
                    'recent_returns': returns[:10]  # 最近10个返图
                },
                
                # 图片信息
                'images': [],
                
                # 采集时间
                'collected_at': datetime.now(timezone.utc).isoformat(),
                'collection_timestamp': self.get_timestamp()
            }
            
            # 处理图片
            images_to_download = []
            
            # 主预览图
            if model_data.get('images'):
                for i, img in enumerate(model_data['images'][:5]):  # 最多5张主图
                    img_url = img.get('url', '')
                    if img_url:
                        filename = f"{model_uuid}_main_{i+1}.webp"
                        images_to_download.append((img_url, filename))
                        complete_model['images'].append({
                            'type': 'main',
                            'url': img_url,
                            'filename': filename,
                            'width': img.get('width', 0),
                            'height': img.get('height', 0)
                        })
            
            # 版本图片
            for version in versions:
                version_images = version.get('images', [])
                for i, img in enumerate(version_images[:3]):  # 每个版本最多3张图
                    img_url = img.get('url', '')
                    if img_url:
                        filename = f"{model_uuid}_version_{version.get('uuid', '')}_{i+1}.webp"
                        images_to_download.append((img_url, filename))
                        complete_model['images'].append({
                            'type': 'version',
                            'version_uuid': version.get('uuid', ''),
                            'url': img_url,
                            'filename': filename,
                            'width': img.get('width', 0),
                            'height': img.get('height', 0)
                        })
            
            # 返图示例
            for i, return_item in enumerate(returns[:5]):  # 最多5个返图示例
                img_url = return_item.get('url', '')
                if img_url:
                    filename = f"{model_uuid}_return_{i+1}.webp"
                    images_to_download.append((img_url, filename))
                    complete_model['images'].append({
                        'type': 'return',
                        'url': img_url,
                        'filename': filename,
                        'prompt': return_item.get('prompt', ''),
                        'user': return_item.get('user', {})
                    })
            
            # 批量下载图片
            downloaded_count = 0
            with ThreadPoolExecutor(max_workers=5) as executor:
                download_futures = {
                    executor.submit(self.download_image, url, filename): (url, filename) 
                    for url, filename in images_to_download
                }
                
                for future in as_completed(download_futures):
                    url, filename = download_futures[future]
                    try:
                        if future.result():
                            downloaded_count += 1
                    except Exception as e:
                        logger.error(f"下载图片异常 {filename}: {e}")
            
            complete_model['download_stats'] = {
                'total_images': len(images_to_download),
                'downloaded_images': downloaded_count
            }
            
            logger.info(f"模型处理完成: {complete_model['title']} (图片: {downloaded_count}/{len(images_to_download)})")
            
            self.collected_models.add(model_uuid)
            return complete_model
            
        except Exception as e:
            logger.error(f"处理模型异常 {model_uuid}: {e}")
            return None
    
    def collect_all_car_models(self) -> List[Dict[str, Any]]:
        """采集所有汽车交通模型"""
        logger.info("开始采集汽车交通板块所有模型...")
        
        page = 1
        total_collected = 0
        
        while True:
            # 获取模型列表
            models_response = self.get_car_models_list(page=page)
            
            if not models_response or models_response.get('code') != 0:
                logger.error(f"获取第 {page} 页模型列表失败")
                break
            
            data = models_response.get('data', {})
            models_list = data.get('list', [])
            
            if not models_list:
                logger.info(f"第 {page} 页无模型，采集完成")
                break
            
            logger.info(f"第 {page} 页获取到 {len(models_list)} 个模型")
            
            # 并行处理模型
            with ThreadPoolExecutor(max_workers=3) as executor:
                future_to_model = {
                    executor.submit(self.process_single_model, model): model 
                    for model in models_list
                }
                
                for future in as_completed(future_to_model):
                    model_basic = future_to_model[future]
                    try:
                        result = future.result()
                        if result:
                            self.models_data.append(result)
                            total_collected += 1
                            
                            # 每处理10个模型保存一次
                            if total_collected % 10 == 0:
                                self.save_progress()
                                
                    except Exception as e:
                        logger.error(f"处理模型异常: {e}")
            
            # 检查是否还有更多页面
            total_count = data.get('totalCount', 0)
            current_count = page * 24
            
            if current_count >= total_count:
                logger.info(f"已采集完所有模型，总计: {total_collected}")
                break
            
            page += 1
            time.sleep(1)  # 避免请求过快
        
        logger.info(f"汽车交通模型采集完成，共采集 {total_collected} 个模型")
        return self.models_data
    
    def save_progress(self):
        """保存采集进度"""
        progress_file = os.path.join(self.output_dir, 'collection_progress.json')
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump({
                'collected_count': len(self.models_data),
                'collected_models': list(self.collected_models),
                'last_update': datetime.now(timezone.utc).isoformat()
            }, f, ensure_ascii=False, indent=2)
    
    def save_final_results(self):
        """保存最终结果"""
        # 保存完整数据
        output_file = os.path.join(self.output_dir, 'complete_car_models_data.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.models_data, f, ensure_ascii=False, indent=2)
        
        # 保存采集统计
        stats = self.generate_collection_stats()
        stats_file = os.path.join(self.output_dir, 'collection_statistics.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        logger.info(f"结果已保存到 {self.output_dir}/")
    
    def generate_collection_stats(self) -> Dict[str, Any]:
        """生成采集统计"""
        if not self.models_data:
            return {}
        
        stats = {
            'collection_summary': {
                'total_models': len(self.models_data),
                'collection_time': datetime.now(timezone.utc).isoformat(),
                'total_images': sum(len(model.get('images', [])) for model in self.models_data),
                'total_downloads': sum(model.get('download_stats', {}).get('downloaded_images', 0) for model in self.models_data)
            },
            'model_types': {},
            'base_models': {},
            'authors': {},
            'vehicle_types': {},
            'design_styles': {},
            'render_styles': {},
            'use_cases': {},
            'top_models': []
        }
        
        # 统计模型类型
        for model in self.models_data:
            model_type = model.get('type', 'Unknown')
            stats['model_types'][model_type] = stats['model_types'].get(model_type, 0) + 1
        
        # 统计基础模型
        for model in self.models_data:
            base_model = model.get('baseModel', 'Unknown')
            stats['base_models'][base_model] = stats['base_models'].get(base_model, 0) + 1
        
        # 统计作者
        for model in self.models_data:
            author = model.get('author', {}).get('username', 'Unknown')
            if author not in stats['authors']:
                stats['authors'][author] = {
                    'model_count': 0,
                    'total_likes': 0,
                    'total_downloads': 0
                }
            stats['authors'][author]['model_count'] += 1
            stats['authors'][author]['total_likes'] += model.get('stats', {}).get('likeCount', 0)
            stats['authors'][author]['total_downloads'] += model.get('stats', {}).get('downloadCount', 0)
        
        # 统计汽车分析数据
        for model in self.models_data:
            car_analysis = model.get('car_analysis', {})
            
            for vehicle_type in car_analysis.get('vehicle_types', []):
                stats['vehicle_types'][vehicle_type] = stats['vehicle_types'].get(vehicle_type, 0) + 1
            
            for design_style in car_analysis.get('design_styles', []):
                stats['design_styles'][design_style] = stats['design_styles'].get(design_style, 0) + 1
            
            for render_style in car_analysis.get('render_styles', []):
                stats['render_styles'][render_style] = stats['render_styles'].get(render_style, 0) + 1
            
            for use_case in car_analysis.get('use_cases', []):
                stats['use_cases'][use_case] = stats['use_cases'].get(use_case, 0) + 1
        
        # 获取热门模型（按点赞数排序）
        sorted_models = sorted(
            self.models_data, 
            key=lambda x: x.get('stats', {}).get('likeCount', 0), 
            reverse=True
        )
        
        stats['top_models'] = [
            {
                'title': model.get('title', ''),
                'uuid': model.get('uuid', ''),
                'author': model.get('author', {}).get('username', ''),
                'likes': model.get('stats', {}).get('likeCount', 0),
                'downloads': model.get('stats', {}).get('downloadCount', 0),
                'generates': model.get('stats', {}).get('generateCount', 0)
            }
            for model in sorted_models[:20]
        ]
        
        return stats

class CompleteCarModelScraper(LiblibCarModelsScraper):
    def load_config(self) -> Dict[str, Any]:
        """Return a minimal configuration dict expected by tests.
        This keeps backward compatibility with older test imports.
        """
        return {
            'api_base': self.api_base,
            'output_dir': self.output_dir,
            'images_dir': self.images_dir,
            'default_page_size': 24,
            'default_concurrency': 3,
        }

def main():
    """主函数"""
    scraper = LiblibCarModelsScraper()
    
    try:
        # 采集所有汽车交通模型
        models = scraper.collect_all_car_models()
        
        # 保存结果
        scraper.save_final_results()
        
        print(f"\n✅ 采集完成！")
        print(f"📊 总计采集 {len(models)} 个汽车交通模型")
        print(f"📁 结果保存在 {scraper.output_dir}/ 目录中")
        print(f"🖼️ 图片保存在 {scraper.images_dir}/ 目录中")
        
    except KeyboardInterrupt:
        print("\n❌ 用户中断采集")
        scraper.save_progress()
        print(f"📁 已保存当前进度到 {scraper.output_dir}/")
    except Exception as e:
        logger.error(f"采集过程中发生错误: {e}")
        scraper.save_progress()

if __name__ == "__main__":
    main()
