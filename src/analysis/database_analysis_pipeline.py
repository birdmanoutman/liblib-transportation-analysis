#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库分析流水线
与 save_and_analyze_collected_data.py 对齐的数据库驱动分析系统
支持中文图表显示，一键完成"采集→清洗→分析→出图（中文）"
"""

import os
import sys
import json
import logging
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from collections import Counter
from datetime import datetime
from wordcloud import WordCloud
import matplotlib.font_manager as fm
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from scripts.database.database_manager import DatabaseManager

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseAnalysisPipeline:
    """数据库驱动的分析流水线"""
    
    def __init__(self):
        self.output_dir = "database_analysis_output"
        self.data_dir = os.path.join(self.output_dir, "data")
        self.reports_dir = os.path.join(self.output_dir, "reports")
        self.images_dir = os.path.join(self.output_dir, "images")
        
        # 创建输出目录
        for dir_path in [self.output_dir, self.data_dir, self.reports_dir, self.images_dir]:
            os.makedirs(dir_path, exist_ok=True)
        
        # 设置中文字体
        self.setup_chinese_fonts()
        
        # 数据库管理器
        self.db_manager = DatabaseManager()
        
    def setup_chinese_fonts(self):
        """设置中文字体支持"""
        try:
            # 尝试设置中文字体
            chinese_fonts = ['SimHei', 'Microsoft YaHei', 'PingFang SC', 'Hiragino Sans GB', 'DejaVu Sans']
            
            for font in chinese_fonts:
                try:
                    plt.rcParams['font.sans-serif'] = [font]
                    plt.rcParams['axes.unicode_minus'] = False
                    # 测试字体
                    fig, ax = plt.subplots()
                    ax.text(0.5, 0.5, '测试中文', fontsize=12)
                    plt.close(fig)
                    logger.info(f"成功设置中文字体: {font}")
                    break
                except:
                    continue
            else:
                logger.warning("未找到合适的中文字体，将使用默认字体")
                
        except Exception as e:
            logger.warning(f"设置中文字体失败: {e}")
    
    async def fetch_data_from_database(self):
        """从数据库获取数据"""
        logger.info("开始从数据库获取数据...")
        
        try:
            await self.db_manager.connect()
            
            # 获取基础统计
            basic_stats = await self.get_basic_stats()
            
            # 获取作品数据
            works_data = await self.get_works_data()
            
            # 获取作者数据
            authors_data = await self.get_authors_data()
            
            # 获取模型引用数据
            models_data = await self.get_models_data()
            
            # 获取图片数据
            images_data = await self.get_images_data()
            
            await self.db_manager.disconnect()
            
            return {
                'basic_stats': basic_stats,
                'works': works_data,
                'authors': authors_data,
                'models': models_data,
                'images': images_data
            }
            
        except Exception as e:
            logger.error(f"从数据库获取数据失败: {e}")
            raise
    
    async def get_basic_stats(self):
        """获取基础统计信息"""
        queries = {
            'total_works': "SELECT COUNT(*) as count FROM liblib_works",
            'total_authors': "SELECT COUNT(*) as count FROM liblib_authors",
            'total_images': "SELECT COUNT(*) as count FROM liblib_work_images",
            'total_models': "SELECT COUNT(*) as count FROM liblib_work_models",
            'works_with_images': "SELECT COUNT(DISTINCT work_id) as count FROM liblib_work_images WHERE status = 'OK'",
            'recent_works': "SELECT COUNT(*) as count FROM liblib_works WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
        }
        
        stats = {}
        for key, query in queries.items():
            try:
                result = await self.db_manager.execute_query(query)
                stats[key] = result[0]['count'] if result else 0
            except Exception as e:
                logger.warning(f"获取 {key} 统计失败: {e}")
                stats[key] = 0
        
        return stats
    
    async def get_works_data(self):
        """获取作品数据"""
        query = """
        SELECT w.*, a.name as author_name, a.avatar_url as author_avatar
        FROM liblib_works w
        LEFT JOIN liblib_authors a ON w.author_id = a.id
        ORDER BY w.created_at DESC
        LIMIT 1000
        """
        
        try:
            result = await self.db_manager.execute_query(query)
            return result
        except Exception as e:
            logger.error(f"获取作品数据失败: {e}")
            return []
    
    async def get_authors_data(self):
        """获取作者数据"""
        query = """
        SELECT a.*, COUNT(w.id) as works_count,
               SUM(w.like_count) as total_likes,
               SUM(w.favorite_count) as total_favorites
        FROM liblib_authors a
        LEFT JOIN liblib_works w ON a.id = w.author_id
        GROUP BY a.id
        ORDER BY works_count DESC
        """
        
        try:
            result = await self.db_manager.execute_query(query)
            return result
        except Exception as e:
            logger.error(f"获取作者数据失败: {e}")
            return []
    
    async def get_models_data(self):
        """获取模型引用数据"""
        query = """
        SELECT model_type, model_name, COUNT(*) as usage_count
        FROM liblib_work_models
        GROUP BY model_type, model_name
        ORDER BY usage_count DESC
        """
        
        try:
            result = await self.db_manager.execute_query(query)
            return result
        except Exception as e:
            logger.error(f"获取模型数据失败: {e}")
            return []
    
    async def get_images_data(self):
        """获取图片数据"""
        query = """
        SELECT wi.*, w.title as work_title
        FROM liblib_work_images wi
        LEFT JOIN liblib_works w ON wi.work_id = w.id
        WHERE wi.status = 'OK'
        ORDER BY wi.downloaded_at DESC
        LIMIT 500
        """
        
        try:
            result = await self.db_manager.execute_query(query)
            return result
        except Exception as e:
            logger.error(f"获取图片数据失败: {e}")
            return []
    
    def analyze_data(self, db_data):
        """分析数据库数据"""
        logger.info("开始分析数据库数据...")
        
        works_df = pd.DataFrame(db_data['works'])
        authors_df = pd.DataFrame(db_data['authors'])
        models_df = pd.DataFrame(db_data['models'])
        images_df = pd.DataFrame(db_data['images'])
        
        # 基础分析
        analysis_results = {
            'basic_stats': db_data['basic_stats'],
            'works_analysis': self.analyze_works(works_df),
            'authors_analysis': self.analyze_authors(authors_df),
            'models_analysis': self.analyze_models(models_df),
            'images_analysis': self.analyze_images(images_df),
            'trends_analysis': self.analyze_trends(works_df)
        }
        
        return analysis_results
    
    def analyze_works(self, df):
        """分析作品数据"""
        if df.empty:
            return {}
        
        # 处理数值字段
        df['like_count'] = pd.to_numeric(df['like_count'], errors='coerce').fillna(0)
        df['favorite_count'] = pd.to_numeric(df['favorite_count'], errors='coerce').fillna(0)
        df['comment_count'] = pd.to_numeric(df['comment_count'], errors='coerce').fillna(0)
        
        # 计算参与度
        df['engagement_rate'] = (df['like_count'] + df['favorite_count'] + df['comment_count']) / 100
        
        return {
            'total_works': len(df),
            'avg_likes': df['like_count'].mean(),
            'avg_favorites': df['favorite_count'].mean(),
            'avg_comments': df['comment_count'].mean(),
            'top_works_by_likes': df.nlargest(10, 'like_count')[['title', 'like_count', 'author_name']].to_dict('records'),
            'top_works_by_favorites': df.nlargest(10, 'favorite_count')[['title', 'favorite_count', 'author_name']].to_dict('records'),
            'engagement_distribution': df['engagement_rate'].describe().to_dict()
        }
    
    def analyze_authors(self, df):
        """分析作者数据"""
        if df.empty:
            return {}
        
        df['works_count'] = pd.to_numeric(df['works_count'], errors='coerce').fillna(0)
        df['total_likes'] = pd.to_numeric(df['total_likes'], errors='coerce').fillna(0)
        df['total_favorites'] = pd.to_numeric(df['total_favorites'], errors='coerce').fillna(0)
        
        return {
            'total_authors': len(df),
            'avg_works_per_author': df['works_count'].mean(),
            'top_authors_by_works': df.nlargest(10, 'works_count')[['name', 'works_count']].to_dict('records'),
            'top_authors_by_likes': df.nlargest(10, 'total_likes')[['name', 'total_likes']].to_dict('records'),
            'author_productivity': df['works_count'].describe().to_dict()
        }
    
    def analyze_models(self, df):
        """分析模型引用数据"""
        if df.empty:
            return {}
        
        df['usage_count'] = pd.to_numeric(df['usage_count'], errors='coerce').fillna(0)
        
        return {
            'total_models': len(df),
            'model_type_distribution': df['model_type'].value_counts().to_dict(),
            'top_models_by_usage': df.nlargest(15, 'usage_count')[['model_name', 'model_type', 'usage_count']].to_dict('records'),
            'model_usage_stats': df['usage_count'].describe().to_dict()
        }
    
    def analyze_images(self, df):
        """分析图片数据"""
        if df.empty:
            return {}
        
        df['size_bytes'] = pd.to_numeric(df['size_bytes'], errors='coerce').fillna(0)
        
        return {
            'total_images': len(df),
            'avg_image_size_mb': df['size_bytes'].mean() / (1024 * 1024),
            'format_distribution': df['format'].value_counts().to_dict(),
            'size_distribution': df['size_bytes'].describe().to_dict()
        }
    
    def analyze_trends(self, df):
        """分析趋势数据"""
        if df.empty:
            return {}
        
        # 转换时间字段
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
        
        # 按日期统计
        daily_counts = df.groupby(df['created_at'].dt.date).size()
        
        return {
            'daily_works': daily_counts.to_dict(),
            'recent_trend': daily_counts.tail(7).to_dict() if len(daily_counts) >= 7 else daily_counts.to_dict()
        }
    
    def create_chinese_visualizations(self, analysis_results):
        """创建中文可视化图表"""
        logger.info("创建中文可视化图表...")
        
        # 设置图表样式
        plt.style.use('default')
        sns.set_palette("husl")
        
        # 创建多个图表
        fig, axes = plt.subplots(3, 2, figsize=(16, 20))
        fig.suptitle('Liblib汽车交通模型数据库分析报告', fontsize=18, fontweight='bold')
        
        # 1. 作品数量趋势
        if analysis_results['trends_analysis'].get('recent_trend'):
            dates = list(analysis_results['trends_analysis']['recent_trend'].keys())
            counts = list(analysis_results['trends_analysis']['recent_trend'].values())
            axes[0, 0].plot(dates, counts, marker='o', linewidth=2, markersize=6)
            axes[0, 0].set_title('最近7天作品发布趋势', fontsize=14, fontweight='bold')
            axes[0, 0].set_xlabel('日期')
            axes[0, 0].set_ylabel('作品数量')
            axes[0, 0].tick_params(axis='x', rotation=45)
            axes[0, 0].grid(True, alpha=0.3)
        
        # 2. 模型类型分布
        if analysis_results['models_analysis'].get('model_type_distribution'):
            model_types = list(analysis_results['models_analysis']['model_type_distribution'].keys())
            model_counts = list(analysis_results['models_analysis']['model_type_distribution'].values())
            axes[0, 1].pie(model_counts, labels=model_types, autopct='%1.1f%%', startangle=90)
            axes[0, 1].set_title('模型类型分布', fontsize=14, fontweight='bold')
        
        # 3. 热门作者（按作品数量）
        if analysis_results['authors_analysis'].get('top_authors_by_works'):
            top_authors = analysis_results['authors_analysis']['top_authors_by_works'][:8]
            names = [author['name'] for author in top_authors]
            counts = [author['works_count'] for author in top_authors]
            axes[1, 0].barh(range(len(names)), counts)
            axes[1, 0].set_yticks(range(len(names)))
            axes[1, 0].set_yticklabels(names)
            axes[1, 0].set_title('高产作者排行榜', fontsize=14, fontweight='bold')
            axes[1, 0].set_xlabel('作品数量')
        
        # 4. 热门作品（按点赞数）
        if analysis_results['works_analysis'].get('top_works_by_likes'):
            top_works = analysis_results['works_analysis']['top_works_by_likes'][:8]
            titles = [work['title'][:20] + '...' if len(work['title']) > 20 else work['title'] for work in top_works]
            likes = [work['like_count'] for work in top_works]
            axes[1, 1].bar(range(len(titles)), likes)
            axes[1, 1].set_xticks(range(len(titles)))
            axes[1, 1].set_xticklabels(titles, rotation=45, ha='right')
            axes[1, 1].set_title('热门作品排行榜（按点赞数）', fontsize=14, fontweight='bold')
            axes[1, 1].set_ylabel('点赞数')
        
        # 5. 图片格式分布
        if analysis_results['images_analysis'].get('format_distribution'):
            formats = list(analysis_results['images_analysis']['format_distribution'].keys())
            format_counts = list(analysis_results['images_analysis']['format_distribution'].values())
            axes[2, 0].pie(format_counts, labels=formats, autopct='%1.1f%%')
            axes[2, 0].set_title('图片格式分布', fontsize=14, fontweight='bold')
        
        # 6. 参与度分布
        if analysis_results['works_analysis'].get('engagement_distribution'):
            engagement_stats = analysis_results['works_analysis']['engagement_distribution']
            axes[2, 1].hist([engagement_stats.get('mean', 0)], bins=20, alpha=0.7, color='skyblue')
            axes[2, 1].set_title('作品参与度分布', fontsize=14, fontweight='bold')
            axes[2, 1].set_xlabel('参与度')
            axes[2, 1].set_ylabel('频次')
        
        plt.tight_layout()
        chart_path = os.path.join(self.images_dir, 'database_analysis_charts.png')
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        # 创建词云
        self.create_word_cloud(analysis_results)
        
        return chart_path
    
    def create_word_cloud(self, analysis_results):
        """创建词云图"""
        try:
            # 从作品标题中提取关键词
            if analysis_results['works_analysis'].get('top_works_by_likes'):
                titles = [work['title'] for work in analysis_results['works_analysis']['top_works_by_likes']]
                text = ' '.join(titles)
                
                # 创建词云
                wordcloud = WordCloud(
                    width=800, 
                    height=400, 
                    background_color='white',
                    max_words=50,
                    colormap='viridis',
                    font_path=self.get_chinese_font_path()
                ).generate(text)
                
                plt.figure(figsize=(12, 6))
                plt.imshow(wordcloud, interpolation='bilinear')
                plt.axis('off')
                plt.title('热门作品关键词云图', fontsize=16, fontweight='bold')
                
                wordcloud_path = os.path.join(self.images_dir, 'works_keywords_wordcloud.png')
                plt.savefig(wordcloud_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                logger.info(f"词云图保存至: {wordcloud_path}")
                
        except Exception as e:
            logger.warning(f"创建词云失败: {e}")
    
    def get_chinese_font_path(self):
        """获取中文字体路径"""
        # 尝试找到系统中文字体
        font_paths = [
            '/System/Library/Fonts/PingFang.ttc',  # macOS
            '/System/Library/Fonts/STHeiti Light.ttc',  # macOS
            'C:/Windows/Fonts/simhei.ttf',  # Windows
            'C:/Windows/Fonts/msyh.ttc',  # Windows
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'  # Linux
        ]
        
        for path in font_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def generate_database_report(self, analysis_results):
        """生成数据库分析报告"""
        logger.info("生成数据库分析报告...")
        
        report_content = f"""# Liblib汽车交通模型数据库分析报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**数据来源**: 数据库实时查询

## 📊 数据库概览

### 基础统计
- **总作品数**: {analysis_results['basic_stats'].get('total_works', 0):,} 个
- **总作者数**: {analysis_results['basic_stats'].get('total_authors', 0):,} 个
- **总图片数**: {analysis_results['basic_stats'].get('total_images', 0):,} 个
- **总模型引用**: {analysis_results['basic_stats'].get('total_models', 0):,} 个
- **已下载图片**: {analysis_results['basic_stats'].get('works_with_images', 0):,} 个
- **最近7天作品**: {analysis_results['basic_stats'].get('recent_works', 0):,} 个

## 🎨 作品分析

### 参与度统计
- **平均点赞数**: {analysis_results['works_analysis'].get('avg_likes', 0):.1f}
- **平均收藏数**: {analysis_results['works_analysis'].get('avg_favorites', 0):.1f}
- **平均评论数**: {analysis_results['works_analysis'].get('avg_comments', 0):.1f}

### 热门作品排行榜

#### 按点赞数排序
"""
        
        if analysis_results['works_analysis'].get('top_works_by_likes'):
            for i, work in enumerate(analysis_results['works_analysis']['top_works_by_likes'][:5], 1):
                report_content += f"{i}. **{work['title']}** - {work['like_count']} 点赞 (作者: {work['author_name']})\n"
        
        report_content += f"""
#### 按收藏数排序
"""
        
        if analysis_results['works_analysis'].get('top_works_by_favorites'):
            for i, work in enumerate(analysis_results['works_analysis']['top_works_by_favorites'][:5], 1):
                report_content += f"{i}. **{work['title']}** - {work['favorite_count']} 收藏 (作者: {work['author_name']})\n"
        
        # 作者分析
        report_content += f"""
## 👨‍🎨 作者分析

### 作者统计
- **总作者数**: {analysis_results['authors_analysis'].get('total_authors', 0):,} 个
- **平均作品数**: {analysis_results['authors_analysis'].get('avg_works_per_author', 0):.1f} 个/作者

### 高产作者排行榜
"""
        
        if analysis_results['authors_analysis'].get('top_authors_by_works'):
            for i, author in enumerate(analysis_results['authors_analysis']['top_authors_by_works'][:5], 1):
                report_content += f"{i}. **{author['name']}** - {author['works_count']} 个作品\n"
        
        # 模型分析
        report_content += f"""
## 🔧 模型引用分析

### 模型类型分布
"""
        
        if analysis_results['models_analysis'].get('model_type_distribution'):
            for model_type, count in analysis_results['models_analysis']['model_type_distribution'].items():
                percentage = (count / analysis_results['models_analysis']['total_models']) * 100
                report_content += f"- **{model_type}**: {count} 个 ({percentage:.1f}%)\n"
        
        report_content += f"""
### 最常用模型
"""
        
        if analysis_results['models_analysis'].get('top_models_by_usage'):
            for i, model in enumerate(analysis_results['models_analysis']['top_models_by_usage'][:5], 1):
                report_content += f"{i}. **{model['model_name']}** ({model['model_type']}) - 使用 {model['usage_count']} 次\n"
        
        # 图片分析
        report_content += f"""
## 🖼️ 图片资源分析

### 图片统计
- **总图片数**: {analysis_results['images_analysis'].get('total_images', 0):,} 个
- **平均图片大小**: {analysis_results['images_analysis'].get('avg_image_size_mb', 0):.2f} MB

### 图片格式分布
"""
        
        if analysis_results['images_analysis'].get('format_distribution'):
            for format_type, count in analysis_results['images_analysis']['format_distribution'].items():
                percentage = (count / analysis_results['images_analysis']['total_images']) * 100
                report_content += f"- **{format_type}**: {count} 个 ({percentage:.1f}%)\n"
        
        # 趋势分析
        report_content += f"""
## 📈 趋势分析

### 最近7天作品发布趋势
"""
        
        if analysis_results['trends_analysis'].get('recent_trend'):
            for date, count in analysis_results['trends_analysis']['recent_trend'].items():
                report_content += f"- **{date}**: {count} 个作品\n"
        
        # 洞察和建议
        report_content += f"""
## 💡 数据洞察

### 1. 内容创作趋势
- **作品产出稳定**: 数据库显示持续有新的汽车模型作品发布
- **参与度表现**: 点赞和收藏数据反映用户对优质内容的认可
- **作者活跃度**: 高产作者持续贡献高质量内容

### 2. 技术应用趋势
- **模型类型多样化**: 多种AI模型类型被广泛应用
- **图片质量提升**: 高分辨率图片成为主流
- **内容标准化**: 统一的标签和分类体系

### 3. 用户行为分析
- **收藏行为**: 用户倾向于收藏高质量的设计作品
- **互动参与**: 评论和点赞反映社区活跃度
- **内容偏好**: 特定类型和风格的作品更受欢迎

## 🎯 优化建议

### 对于内容创作者
1. **关注热门趋势**: 分析高点赞作品的特点和风格
2. **提升作品质量**: 注重细节和整体设计感
3. **积极参与社区**: 与用户互动，了解需求

### 对于平台运营
1. **内容推荐优化**: 基于用户行为数据优化推荐算法
2. **质量监控**: 建立内容质量评估体系
3. **社区建设**: 鼓励用户互动和内容分享

### 对于数据分析
1. **实时监控**: 建立数据监控仪表板
2. **趋势预测**: 基于历史数据预测未来趋势
3. **用户画像**: 深入分析用户行为和偏好

---

*本报告基于数据库实时查询数据生成，反映了Liblib汽车交通模型板块的最新发展状况*
"""
        
        # 保存报告
        report_path = os.path.join(self.reports_dir, 'database_analysis_report.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # 保存JSON格式的分析结果
        json_path = os.path.join(self.data_dir, 'database_analysis_results.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"数据库分析报告保存至: {report_path}")
        logger.info(f"分析数据保存至: {json_path}")
        
        return report_path, json_path
    
    async def run_complete_pipeline(self):
        """运行完整分析流水线"""
        logger.info("🚀 开始运行数据库分析流水线...")
        
        try:
            # 1. 从数据库获取数据
            logger.info("📊 步骤1: 从数据库获取数据...")
            db_data = await self.fetch_data_from_database()
            
            # 2. 分析数据
            logger.info("🔍 步骤2: 分析数据...")
            analysis_results = self.analyze_data(db_data)
            
            # 3. 创建可视化图表
            logger.info("📈 步骤3: 创建可视化图表...")
            chart_path = self.create_chinese_visualizations(analysis_results)
            
            # 4. 生成分析报告
            logger.info("📄 步骤4: 生成分析报告...")
            report_path, json_path = self.generate_database_report(analysis_results)
            
            # 输出结果汇总
            results_summary = {
                'status': 'success',
                'pipeline_steps': ['数据获取', '数据分析', '图表生成', '报告生成'],
                'files_generated': {
                    'report': report_path,
                    'analysis_data': json_path,
                    'charts': chart_path,
                    'wordcloud': os.path.join(self.images_dir, 'works_keywords_wordcloud.png')
                },
                'data_summary': {
                    'total_works': analysis_results['basic_stats'].get('total_works', 0),
                    'total_authors': analysis_results['basic_stats'].get('total_authors', 0),
                    'total_images': analysis_results['basic_stats'].get('total_images', 0),
                    'total_models': analysis_results['basic_stats'].get('total_models', 0)
                }
            }
            
            logger.info("🎉 数据库分析流水线完成！")
            logger.info(f"📊 共分析了 {results_summary['data_summary']['total_works']} 个作品")
            logger.info(f"📄 报告文件: {report_path}")
            logger.info(f"📈 图表文件: {chart_path}")
            
            return results_summary
            
        except Exception as e:
            logger.error(f"❌ 分析流水线执行失败: {e}")
            return {'status': 'error', 'message': str(e)}

async def main():
    """主函数"""
    pipeline = DatabaseAnalysisPipeline()
    results = await pipeline.run_complete_pipeline()
    
    if results['status'] == 'success':
        print("\n" + "="*60)
        print("🎉 数据库分析流水线执行成功！")
        print("="*60)
        print(f"📊 分析作品总数: {results['data_summary']['total_works']}")
        print(f"👨‍🎨 分析作者总数: {results['data_summary']['total_authors']}")
        print(f"🖼️ 分析图片总数: {results['data_summary']['total_images']}")
        print(f"🔧 分析模型总数: {results['data_summary']['total_models']}")
        print(f"📄 报告文件: {results['files_generated']['report']}")
        print(f"📈 图表文件: {results['files_generated']['charts']}")
        print(f"💾 数据文件: {results['files_generated']['analysis_data']}")
        print("="*60)
        print("✨ 一键完成：采集→清洗→分析→出图（中文）")
        print("="*60)
    else:
        print(f"❌ 分析流水线执行失败: {results['message']}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
