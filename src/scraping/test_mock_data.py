#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T5 详情采集器模拟测试环境
使用模拟数据测试核心功能，不依赖外部API
"""

import os
import sys
import json
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mock_test.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MockDetailCollector:
    """模拟详情采集器，用于测试核心逻辑"""
    
    def __init__(self):
        # 模拟数据
        self.mock_work_data = {
            "slug": "test-work-001",
            "title": "测试汽车模型",
            "publishedAt": int(time.time() * 1000),
            "tags": ["汽车", "交通", "3D模型"],
            "prompt": "一辆未来感十足的跑车",
            "negativePrompt": "模糊的，低质量的",
            "sampler": "Euler a",
            "steps": 20,
            "cfgScale": 7.0,
            "width": 512,
            "height": 512,
            "seed": "12345",
            "likeCount": 100,
            "favoriteCount": 50,
            "commentCount": 25,
            "sourceUrl": "https://example.com/work/001",
            "authorSlug": "test-author-001"
        }
        
        self.mock_author_data = {
            "id": "author-001",
            "name": "测试作者",
            "avatar": "https://example.com/avatar.jpg",
            "profileUrl": "https://example.com/profile",
            "createdAt": int(time.time() * 1000)
        }
        
        self.mock_comments = [
            {
                "content": "这个模型很棒！",
                "commenterName": "用户A",
                "commenterAvatar": "https://example.com/user1.jpg",
                "commentedAt": int(time.time() * 1000)
            },
            {
                "content": "质量很高，细节丰富",
                "commenterName": "用户B",
                "commenterAvatar": "https://example.com/user2.jpg",
                "commentedAt": int(time.time() * 1000)
            }
        ]
        
        # 统计信息
        self.stats = {
            'total_processed': 0,
            'success_count': 0,
            'failed_count': 0,
            'authors_created': 0,
            'works_created': 0,
            'comments_created': 0,
            'start_time': datetime.now()
        }
    
    def get_mock_work_detail(self, slug: str) -> Optional[Dict[str, Any]]:
        """获取模拟作品详情"""
        logger.info(f"获取模拟作品详情: {slug}")
        
        # 模拟API延迟
        time.sleep(0.1)
        
        # 返回模拟数据
        return self.mock_work_data.copy()
    
    def get_mock_author_detail(self, author_slug: str) -> Optional[Dict[str, Any]]:
        """获取模拟作者详情"""
        logger.info(f"获取模拟作者详情: {author_slug}")
        
        # 模拟API延迟
        time.sleep(0.1)
        
        # 返回模拟数据
        return self.mock_author_data.copy()
    
    def get_mock_comments(self, work_id: str, slug: str) -> List[Dict[str, Any]]:
        """获取模拟评论"""
        logger.info(f"获取模拟评论: {slug}")
        
        # 模拟API延迟
        time.sleep(0.1)
        
        # 返回模拟数据
        return self.mock_comments.copy()
    
    def validate_and_default_work_data(self, work_data: Dict[str, Any]) -> Dict[str, Any]:
        """字段校验与缺省策略 - 作品数据"""
        validated = {}
        
        # 必填字段校验
        required_fields = ['slug', 'title']
        for field in required_fields:
            if not work_data.get(field):
                logger.warning(f"作品缺少必填字段: {field}")
                return {}
        
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
            logger.warning("作者缺少必填字段: name")
            return {}
        
        # 基础字段
        validated['external_author_id'] = author_data.get('id', '') or ''
        validated['name'] = author_data.get('name', '')
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
            logger.warning(f"无法解析时间戳: {timestamp}")
        
        return None
    
    def process_single_work(self, slug: str) -> bool:
        """处理单个作品的详情采集（模拟）"""
        try:
            logger.info(f"开始处理作品: {slug}")
            
            # 1. 获取作品详情
            work_detail = self.get_mock_work_detail(slug)
            if not work_detail:
                logger.error(f"无法获取作品详情: {slug}")
                return False
            
            # 2. 字段校验与缺省
            validated_work = self.validate_and_default_work_data(work_detail)
            if not validated_work:
                logger.error(f"作品数据验证失败: {slug}")
                return False
            
            # 3. 获取作者信息
            author_slug = work_detail.get('authorSlug', '')
            author_id = None
            
            if author_slug:
                author_detail = self.get_mock_author_detail(author_slug)
                if author_detail:
                    validated_author = self.validate_and_default_author_data(author_detail)
                    if validated_author:
                        logger.info(f"作者信息验证成功: {validated_author['name']}")
                        author_id = "mock_author_id"
            
            # 4. 模拟创建作品记录
            work_id = "mock_work_id"
            logger.info(f"模拟创建作品记录成功: {validated_work['title']} (ID: {work_id})")
            
            # 5. 获取并处理评论
            if work_detail.get('commentCount', 0) > 0:
                comments = self.get_mock_comments(work_id, slug)
                if comments:
                    logger.info(f"模拟处理评论成功: {len(comments)} 条")
            
            logger.info(f"作品处理完成: {slug}")
            return True
            
        except Exception as e:
            logger.error(f"处理作品异常 {slug}: {e}")
            return False
    
    def collect_details_batch(self, slugs: List[str]) -> Dict[str, Any]:
        """批量采集详情（模拟）"""
        logger.info(f"开始批量采集详情，共 {len(slugs)} 个作品")
        
        self.stats['total_processed'] = len(slugs)
        self.stats['start_time'] = datetime.now()
        
        # 模拟并发处理
        for slug in slugs:
            try:
                success = self.process_single_work(slug)
                if success:
                    self.stats['success_count'] += 1
                    self.stats['works_created'] += 1
                    self.stats['authors_created'] += 1
                    self.stats['comments_created'] += 2  # 模拟评论数
                else:
                    self.stats['failed_count'] += 1
            except Exception as e:
                logger.error(f"处理作品异常 {slug}: {e}")
                self.stats['failed_count'] += 1
        
        # 计算成功率
        success_rate = (self.stats['success_count'] / self.stats['total_processed']) * 100 if self.stats['total_processed'] > 0 else 0
        
        logger.info(f"批量采集完成，成功率: {success_rate:.2f}%")
        logger.info(f"成功: {self.stats['success_count']}, 失败: {self.stats['failed_count']}")
        
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
            'duration': (datetime.now() - self.stats['start_time']).total_seconds()
        }
    
    def test_field_validation(self):
        """测试字段验证功能"""
        print("\n🧪 测试字段验证功能...")
        
        # 测试正常数据
        print("1. 测试正常数据验证:")
        normal_work = self.mock_work_data.copy()
        validated = self.validate_and_default_work_data(normal_work)
        if validated:
            print(f"   ✅ 正常数据验证通过，字段数: {len(validated)}")
            print(f"   示例字段: slug={validated['slug']}, title={validated['title']}")
        else:
            print("   ❌ 正常数据验证失败")
        
        # 测试缺失必填字段
        print("\n2. 测试缺失必填字段:")
        invalid_work = self.mock_work_data.copy()
        del invalid_work['slug']
        validated = self.validate_and_default_work_data(invalid_work)
        if not validated:
            print("   ✅ 缺失必填字段检测正确")
        else:
            print("   ❌ 缺失必填字段检测失败")
        
        # 测试可选字段缺省
        print("\n3. 测试可选字段缺省:")
        incomplete_work = {
            'slug': 'test-002',
            'title': '测试标题'
        }
        validated = self.validate_and_default_work_data(incomplete_work)
        if validated:
            print(f"   ✅ 可选字段缺省正确，prompt='{validated['prompt']}', steps={validated['steps']}")
        else:
            print("   ❌ 可选字段缺省失败")
    
    def test_data_parsing(self):
        """测试数据解析功能"""
        print("\n🔍 测试数据解析功能...")
        
        # 测试时间戳解析
        print("1. 测试时间戳解析:")
        timestamp = int(time.time() * 1000)
        parsed_time = self.parse_datetime(timestamp)
        if parsed_time:
            print(f"   ✅ 时间戳解析成功: {parsed_time}")
        else:
            print("   ❌ 时间戳解析失败")
        
        # 测试标签JSON转换
        print("\n2. 测试标签JSON转换:")
        tags = ["汽车", "交通", "3D模型"]
        tags_json = json.dumps(tags, ensure_ascii=False)
        print(f"   ✅ 标签JSON转换: {tags_json}")
        
        # 测试数据类型转换
        print("\n3. 测试数据类型转换:")
        test_data = {
            'steps': '20',
            'cfgScale': '7.0',
            'width': '512',
            'height': '512'
        }
        print(f"   ✅ 原始数据: {test_data}")
        print(f"   ✅ 转换后: steps={int(test_data['steps'])}, cfg_scale={float(test_data['cfgScale'])}")

def main():
    """主测试函数"""
    print("🚀 T5 详情采集器模拟测试开始")
    print("=" * 50)
    
    try:
        # 创建模拟采集器
        collector = MockDetailCollector()
        
        # 测试字段验证
        collector.test_field_validation()
        
        # 测试数据解析
        collector.test_data_parsing()
        
        # 测试批量采集
        print("\n📊 测试批量采集功能...")
        test_slugs = [f"test-slug-{i:03d}" for i in range(1, 6)]
        stats = collector.collect_details_batch(test_slugs)
        
        # 输出统计信息
        print("\n✅ 模拟测试完成！")
        print(f"📊 采集统计:")
        print(f"   总处理数: {stats['total_processed']}")
        print(f"   成功数: {stats['success_count']}")
        print(f"   失败数: {stats['failed_count']}")
        print(f"   成功率: {stats.get('success_rate', 0):.2f}%")
        print(f"   模拟创建作者: {stats['authors_created']}")
        print(f"   模拟创建作品: {stats['works_created']}")
        print(f"   模拟创建评论: {stats['comments_created']}")
        
        # 保存测试结果
        with open('mock_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        print(f"\n📁 测试结果已保存到: mock_test_results.json")
        
    except KeyboardInterrupt:
        print("\n❌ 用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        logger.error(f"测试异常: {e}")

if __name__ == "__main__":
    main()
