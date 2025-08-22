#!/usr/bin/env python3
"""
汽车设计趋势分析器
基于LiblibAI汽车交通模型数据为设计师提供趋势洞察
"""

import json
import os
from typing import Dict, List, Any, Tuple
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime, timedelta
import jieba
import wordcloud
from matplotlib import font_manager
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class CarDesignTrendAnalyzer:
    def __init__(self, data_file: str = 'car_models_complete/complete_car_models_data.json'):
        self.data_file = data_file
        self.models_data = []
        self.output_dir = 'trend_analysis_output'
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 加载数据
        self.load_data()
        
        # 设计趋势分析结果
        self.trend_insights = {}
    
    def load_data(self):
        """加载模型数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.models_data = json.load(f)
            print(f"✅ 成功加载 {len(self.models_data)} 个汽车模型数据")
        except FileNotFoundError:
            print(f"❌ 数据文件不存在: {self.data_file}")
            print("请先运行 complete_car_scraper.py 采集数据")
            return
        except json.JSONDecodeError:
            print(f"❌ 数据文件格式错误: {self.data_file}")
            return
    
    def analyze_vehicle_type_trends(self) -> Dict[str, Any]:
        """分析车辆类型趋势"""
        print("🚗 分析车辆类型趋势...")
        
        vehicle_counts = Counter()
        vehicle_stats = defaultdict(lambda: {
            'total_likes': 0,
            'total_downloads': 0,
            'total_generates': 0,
            'models': []
        })
        
        for model in self.models_data:
            car_analysis = model.get('car_analysis', {})
            vehicle_types = car_analysis.get('vehicle_types', [])
            stats = model.get('stats', {})
            
            if not vehicle_types:
                vehicle_types = ['未分类']
            
            for vehicle_type in vehicle_types:
                vehicle_counts[vehicle_type] += 1
                vehicle_stats[vehicle_type]['total_likes'] += stats.get('likeCount', 0)
                vehicle_stats[vehicle_type]['total_downloads'] += stats.get('downloadCount', 0)
                vehicle_stats[vehicle_type]['total_generates'] += stats.get('generateCount', 0)
                vehicle_stats[vehicle_type]['models'].append({
                    'title': model.get('title', ''),
                    'uuid': model.get('uuid', ''),
                    'likes': stats.get('likeCount', 0)
                })
        
        # 计算平均受欢迎度
        vehicle_popularity = {}
        for vehicle_type, stats in vehicle_stats.items():
            count = vehicle_counts[vehicle_type]
            vehicle_popularity[vehicle_type] = {
                'count': count,
                'avg_likes': stats['total_likes'] / count if count > 0 else 0,
                'avg_downloads': stats['total_downloads'] / count if count > 0 else 0,
                'avg_generates': stats['total_generates'] / count if count > 0 else 0,
                'total_engagement': stats['total_likes'] + stats['total_downloads'] + stats['total_generates'],
                'top_models': sorted(stats['models'], key=lambda x: x['likes'], reverse=True)[:3]
            }
        
        # 创建可视化
        self.plot_vehicle_type_trends(vehicle_counts, vehicle_popularity)
        
        return {
            'vehicle_counts': dict(vehicle_counts),
            'vehicle_popularity': vehicle_popularity,
            'trend_insights': self.generate_vehicle_insights(vehicle_counts, vehicle_popularity)
        }
    
    def analyze_design_style_trends(self) -> Dict[str, Any]:
        """分析设计风格趋势"""
        print("🎨 分析设计风格趋势...")
        
        style_counts = Counter()
        style_combinations = Counter()
        style_performance = defaultdict(lambda: {
            'total_likes': 0,
            'total_downloads': 0,
            'models': []
        })
        
        for model in self.models_data:
            car_analysis = model.get('car_analysis', {})
            design_styles = car_analysis.get('design_styles', [])
            stats = model.get('stats', {})
            
            if not design_styles:
                design_styles = ['通用设计']
            
            # 单一风格统计
            for style in design_styles:
                style_counts[style] += 1
                style_performance[style]['total_likes'] += stats.get('likeCount', 0)
                style_performance[style]['total_downloads'] += stats.get('downloadCount', 0)
                style_performance[style]['models'].append({
                    'title': model.get('title', ''),
                    'uuid': model.get('uuid', ''),
                    'likes': stats.get('likeCount', 0)
                })
            
            # 风格组合统计
            if len(design_styles) > 1:
                combo = ' + '.join(sorted(design_styles))
                style_combinations[combo] += 1
        
        # 创建可视化
        self.plot_design_style_trends(style_counts, style_combinations)
        
        return {
            'style_counts': dict(style_counts),
            'style_combinations': dict(style_combinations.most_common(10)),
            'style_performance': {
                style: {
                    'count': style_counts[style],
                    'avg_likes': data['total_likes'] / style_counts[style] if style_counts[style] > 0 else 0,
                    'avg_downloads': data['total_downloads'] / style_counts[style] if style_counts[style] > 0 else 0,
                    'top_models': sorted(data['models'], key=lambda x: x['likes'], reverse=True)[:3]
                }
                for style, data in style_performance.items()
            }
        }
    
    def analyze_render_style_trends(self) -> Dict[str, Any]:
        """分析渲染风格趋势"""
        print("🖼️ 分析渲染风格趋势...")
        
        render_counts = Counter()
        render_quality = defaultdict(lambda: {
            'total_likes': 0,
            'total_generates': 0,
            'models': []
        })
        
        for model in self.models_data:
            car_analysis = model.get('car_analysis', {})
            render_styles = car_analysis.get('render_styles', [])
            stats = model.get('stats', {})
            
            if not render_styles:
                render_styles = ['通用渲染']
            
            for render_style in render_styles:
                render_counts[render_style] += 1
                render_quality[render_style]['total_likes'] += stats.get('likeCount', 0)
                render_quality[render_style]['total_generates'] += stats.get('generateCount', 0)
                render_quality[render_style]['models'].append({
                    'title': model.get('title', ''),
                    'uuid': model.get('uuid', ''),
                    'likes': stats.get('likeCount', 0),
                    'generates': stats.get('generateCount', 0)
                })
        
        return {
            'render_counts': dict(render_counts),
            'render_quality': {
                style: {
                    'count': render_counts[style],
                    'avg_likes': data['total_likes'] / render_counts[style] if render_counts[style] > 0 else 0,
                    'avg_generates': data['total_generates'] / render_counts[style] if render_counts[style] > 0 else 0,
                    'engagement_ratio': (data['total_likes'] + data['total_generates']) / render_counts[style] if render_counts[style] > 0 else 0,
                    'top_models': sorted(data['models'], key=lambda x: x['likes'], reverse=True)[:3]
                }
                for style, data in render_quality.items()
            }
        }
    
    def analyze_author_trends(self) -> Dict[str, Any]:
        """分析作者和创作趋势"""
        print("👥 分析作者创作趋势...")
        
        author_stats = defaultdict(lambda: {
            'model_count': 0,
            'total_likes': 0,
            'total_downloads': 0,
            'total_generates': 0,
            'specialties': Counter(),
            'models': []
        })
        
        for model in self.models_data:
            author = model.get('author', {})
            username = author.get('username', '未知作者')
            stats = model.get('stats', {})
            car_analysis = model.get('car_analysis', {})
            
            author_stats[username]['model_count'] += 1
            author_stats[username]['total_likes'] += stats.get('likeCount', 0)
            author_stats[username]['total_downloads'] += stats.get('downloadCount', 0)
            author_stats[username]['total_generates'] += stats.get('generateCount', 0)
            
            # 统计专长
            for vehicle_type in car_analysis.get('vehicle_types', []):
                author_stats[username]['specialties'][vehicle_type] += 1
            
            author_stats[username]['models'].append({
                'title': model.get('title', ''),
                'uuid': model.get('uuid', ''),
                'likes': stats.get('likeCount', 0)
            })
        
        # 计算作者排名
        top_authors = []
        for username, data in author_stats.items():
            if data['model_count'] >= 2:  # 至少2个模型才考虑
                engagement_score = (
                    data['total_likes'] * 1.0 + 
                    data['total_downloads'] * 2.0 + 
                    data['total_generates'] * 0.5
                )
                top_authors.append({
                    'username': username,
                    'model_count': data['model_count'],
                    'avg_likes': data['total_likes'] / data['model_count'],
                    'engagement_score': engagement_score,
                    'main_specialty': data['specialties'].most_common(1)[0] if data['specialties'] else ('通用', 0),
                    'top_model': max(data['models'], key=lambda x: x['likes'])
                })
        
        top_authors.sort(key=lambda x: x['engagement_score'], reverse=True)
        
        return {
            'total_authors': len(author_stats),
            'active_authors': len([a for a in author_stats.values() if a['model_count'] >= 2]),
            'top_authors': top_authors[:15],
            'author_specialties': {
                username: dict(data['specialties'].most_common(3))
                for username, data in author_stats.items() 
                if data['model_count'] >= 3
            }
        }
    
    def analyze_keyword_trends(self) -> Dict[str, Any]:
        """分析关键词和标签趋势"""
        print("🔍 分析关键词趋势...")
        
        all_keywords = []
        all_tags = []
        keyword_performance = defaultdict(lambda: {
            'count': 0,
            'total_likes': 0,
            'models': []
        })
        
        for model in self.models_data:
            keywords = model.get('keywords', [])
            tags = model.get('tags', [])
            stats = model.get('stats', {})
            
            all_keywords.extend(keywords)
            all_tags.extend(tags)
            
            for keyword in keywords:
                keyword_performance[keyword]['count'] += 1
                keyword_performance[keyword]['total_likes'] += stats.get('likeCount', 0)
                keyword_performance[keyword]['models'].append({
                    'title': model.get('title', ''),
                    'likes': stats.get('likeCount', 0)
                })
        
        # 筛选高频关键词
        keyword_counts = Counter(all_keywords)
        tag_counts = Counter(all_tags)
        
        # 热门关键词（出现频率 >= 3）
        hot_keywords = {
            keyword: {
                'count': keyword_performance[keyword]['count'],
                'avg_likes': keyword_performance[keyword]['total_likes'] / keyword_performance[keyword]['count'],
                'top_model': max(keyword_performance[keyword]['models'], key=lambda x: x['likes'])
            }
            for keyword, count in keyword_counts.items() 
            if count >= 3
        }
        
        # 生成词云
        self.generate_keyword_wordcloud(keyword_counts)
        
        return {
            'top_keywords': dict(keyword_counts.most_common(30)),
            'top_tags': dict(tag_counts.most_common(20)),
            'hot_keywords': hot_keywords,
            'keyword_insights': self.generate_keyword_insights(keyword_counts, hot_keywords)
        }
    
    def analyze_temporal_trends(self) -> Dict[str, Any]:
        """分析时间趋势（基于模型受欢迎程度推断）"""
        print("📅 分析时间趋势...")
        
        # 根据点赞数和生成数推断流行度时间线
        models_by_popularity = sorted(
            self.models_data, 
            key=lambda x: x.get('stats', {}).get('likeCount', 0) + x.get('stats', {}).get('generateCount', 0),
            reverse=True
        )
        
        # 将模型分为不同时期（基于受欢迎程度）
        total_models = len(models_by_popularity)
        recent_models = models_by_popularity[:total_models//3]  # 最近流行
        stable_models = models_by_popularity[total_models//3:2*total_models//3]  # 稳定期
        emerging_models = models_by_popularity[2*total_models//3:]  # 新兴
        
        periods = {
            '热门流行期': recent_models,
            '稳定发展期': stable_models,
            '新兴探索期': emerging_models
        }
        
        period_analysis = {}
        for period_name, models in periods.items():
            if not models:
                continue
                
            vehicle_types = Counter()
            design_styles = Counter()
            render_styles = Counter()
            
            for model in models:
                car_analysis = model.get('car_analysis', {})
                vehicle_types.update(car_analysis.get('vehicle_types', []))
                design_styles.update(car_analysis.get('design_styles', []))
                render_styles.update(car_analysis.get('render_styles', []))
            
            period_analysis[period_name] = {
                'model_count': len(models),
                'top_vehicle_types': dict(vehicle_types.most_common(5)),
                'top_design_styles': dict(design_styles.most_common(5)),
                'top_render_styles': dict(render_styles.most_common(5)),
                'avg_likes': sum(m.get('stats', {}).get('likeCount', 0) for m in models) / len(models),
                'representative_models': [
                    {
                        'title': m.get('title', ''),
                        'uuid': m.get('uuid', ''),
                        'likes': m.get('stats', {}).get('likeCount', 0),
                        'author': m.get('author', {}).get('username', '')
                    }
                    for m in models[:5]
                ]
            }
        
        return period_analysis
    
    def generate_vehicle_insights(self, vehicle_counts: Counter, vehicle_popularity: Dict) -> List[str]:
        """生成车辆类型洞察"""
        insights = []
        
        # 最受欢迎的车型
        most_popular = max(vehicle_counts, key=vehicle_counts.get)
        insights.append(f"🏆 {most_popular} 是最受关注的车辆类型，共有 {vehicle_counts[most_popular]} 个相关模型")
        
        # 最高互动率车型
        if vehicle_popularity:
            best_engagement = max(
                vehicle_popularity.items(), 
                key=lambda x: x[1]['total_engagement']
            )
            insights.append(f"💖 {best_engagement[0]} 具有最高的用户互动率，平均每个模型获得 {best_engagement[1]['avg_likes']:.1f} 个点赞")
        
        # 新兴趋势
        emerging_types = [vtype for vtype, count in vehicle_counts.items() if count >= 2 and count <= 5]
        if emerging_types:
            insights.append(f"🌟 新兴车型趋势：{', '.join(emerging_types[:3])} 正在获得设计师关注")
        
        return insights
    
    def generate_keyword_insights(self, keyword_counts: Counter, hot_keywords: Dict) -> List[str]:
        """生成关键词洞察"""
        insights = []
        
        # 最热门关键词
        top_keyword = keyword_counts.most_common(1)[0] if keyword_counts else None
        if top_keyword:
            insights.append(f"🔥 '{top_keyword[0]}' 是最热门的设计关键词，出现在 {top_keyword[1]} 个模型中")
        
        # 高质量关键词
        quality_keywords = [
            (keyword, data['avg_likes']) 
            for keyword, data in hot_keywords.items() 
            if data['avg_likes'] > 50
        ]
        if quality_keywords:
            best_quality = max(quality_keywords, key=lambda x: x[1])
            insights.append(f"⭐ '{best_quality[0]}' 相关模型质量最高，平均获得 {best_quality[1]:.1f} 个点赞")
        
        # 设计方向建议
        tech_keywords = [k for k in keyword_counts.keys() if any(tech in k.lower() for tech in ['3d', 'render', 'ai', '渲染', '建模'])]
        if tech_keywords:
            insights.append(f"🔧 技术导向关键词趋势：{', '.join(tech_keywords[:3])} 表明设计师关注技术实现")
        
        return insights
    
    def plot_vehicle_type_trends(self, vehicle_counts: Counter, vehicle_popularity: Dict):
        """绘制车辆类型趋势图"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('汽车类型设计趋势分析', fontsize=16, fontweight='bold')
        
        # 1. 车型数量分布
        types = list(vehicle_counts.keys())
        counts = list(vehicle_counts.values())
        
        ax1.bar(types, counts, color=sns.color_palette("husl", len(types)))
        ax1.set_title('各车型模型数量分布')
        ax1.set_xlabel('车辆类型')
        ax1.set_ylabel('模型数量')
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. 车型平均受欢迎度
        if vehicle_popularity:
            pop_types = list(vehicle_popularity.keys())
            avg_likes = [vehicle_popularity[t]['avg_likes'] for t in pop_types]
            
            ax2.barh(pop_types, avg_likes, color=sns.color_palette("viridis", len(pop_types)))
            ax2.set_title('车型平均受欢迎度（点赞数）')
            ax2.set_xlabel('平均点赞数')
        
        # 3. 车型总互动量
        if vehicle_popularity:
            total_engagement = [vehicle_popularity[t]['total_engagement'] for t in pop_types]
            
            ax3.pie(total_engagement, labels=pop_types, autopct='%1.1f%%', startangle=90)
            ax3.set_title('车型总互动量分布')
        
        # 4. 车型质量 vs 数量散点图
        if vehicle_popularity:
            x_data = [vehicle_popularity[t]['count'] for t in pop_types]
            y_data = [vehicle_popularity[t]['avg_likes'] for t in pop_types]
            
            scatter = ax4.scatter(x_data, y_data, s=100, alpha=0.7, c=range(len(pop_types)), cmap='tab10')
            ax4.set_xlabel('模型数量')
            ax4.set_ylabel('平均点赞数')
            ax4.set_title('车型数量 vs 质量分析')
            
            # 添加标签
            for i, txt in enumerate(pop_types):
                ax4.annotate(txt, (x_data[i], y_data[i]), xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'vehicle_type_trends.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_design_style_trends(self, style_counts: Counter, style_combinations: Counter):
        """绘制设计风格趋势图"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle('设计风格趋势分析', fontsize=16, fontweight='bold')
        
        # 1. 设计风格分布
        styles = list(style_counts.keys())
        counts = list(style_counts.values())
        
        ax1.pie(counts, labels=styles, autopct='%1.1f%%', startangle=90)
        ax1.set_title('设计风格分布')
        
        # 2. 热门风格组合
        if style_combinations:
            combo_names = list(style_combinations.keys())[:8]  # 前8个组合
            combo_counts = list(style_combinations.values())[:8]
            
            ax2.barh(combo_names, combo_counts, color=sns.color_palette("Set3", len(combo_names)))
            ax2.set_title('热门风格组合')
            ax2.set_xlabel('出现次数')
            
            # 调整标签显示
            ax2.tick_params(axis='y', labelsize=8)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'design_style_trends.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_keyword_wordcloud(self, keyword_counts: Counter):
        """生成关键词词云"""
        if not keyword_counts:
            return
        
        # 过滤掉过短的词
        filtered_keywords = {k: v for k, v in keyword_counts.items() if len(k) >= 2}
        
        if not filtered_keywords:
            return
        
        try:
            # 生成词云
            wc = wordcloud.WordCloud(
                width=1200, 
                height=600,
                background_color='white',
                font_path='SimHei.ttf',  # 尝试使用中文字体
                max_words=100,
                relative_scaling=0.5,
                colormap='viridis'
            ).generate_from_frequencies(filtered_keywords)
            
            plt.figure(figsize=(12, 6))
            plt.imshow(wc, interpolation='bilinear')
            plt.axis('off')
            plt.title('汽车设计关键词云图', fontsize=16, pad=20)
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_dir, 'keyword_wordcloud.png'), dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            print(f"⚠️ 词云生成失败: {e}")
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """生成综合趋势报告"""
        print("📊 生成综合趋势报告...")
        
        # 执行所有分析
        vehicle_trends = self.analyze_vehicle_type_trends()
        design_trends = self.analyze_design_style_trends()
        render_trends = self.analyze_render_style_trends()
        author_trends = self.analyze_author_trends()
        keyword_trends = self.analyze_keyword_trends()
        temporal_trends = self.analyze_temporal_trends()
        
        # 生成综合洞察
        comprehensive_insights = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_models_analyzed': len(self.models_data),
                'analysis_scope': '汽车交通设计趋势'
            },
            
            'executive_summary': {
                'key_findings': [
                    f"共分析了 {len(self.models_data)} 个汽车交通相关AI模型",
                    f"发现 {len(vehicle_trends['vehicle_counts'])} 种主要车辆类型设计方向",
                    f"识别出 {len(design_trends['style_counts'])} 种设计风格趋势",
                    f"统计了 {author_trends['total_authors']} 位活跃设计师的创作偏好"
                ],
                'trending_vehicles': list(vehicle_trends['vehicle_counts'].keys())[:5],
                'popular_styles': list(design_trends['style_counts'].keys())[:5],
                'top_creators': [author['username'] for author in author_trends['top_authors'][:5]]
            },
            
            'detailed_analysis': {
                'vehicle_type_trends': vehicle_trends,
                'design_style_trends': design_trends,
                'render_style_trends': render_trends,
                'author_trends': author_trends,
                'keyword_trends': keyword_trends,
                'temporal_trends': temporal_trends
            },
            
            'design_recommendations': self.generate_design_recommendations(
                vehicle_trends, design_trends, render_trends, keyword_trends
            ),
            
            'market_opportunities': self.identify_market_opportunities(
                vehicle_trends, design_trends, author_trends
            )
        }
        
        return comprehensive_insights
    
    def generate_design_recommendations(self, vehicle_trends, design_trends, render_trends, keyword_trends) -> List[Dict[str, str]]:
        """生成设计建议"""
        recommendations = []
        
        # 基于车型趋势的建议
        top_vehicle = max(vehicle_trends['vehicle_counts'], key=vehicle_trends['vehicle_counts'].get)
        recommendations.append({
            'category': '车型选择',
            'recommendation': f"重点关注 {top_vehicle} 设计，这是当前最受欢迎的车型类别",
            'reason': f"该类型已有 {vehicle_trends['vehicle_counts'][top_vehicle]} 个模型，显示出强烈的市场需求"
        })
        
        # 基于设计风格的建议
        if design_trends['style_combinations']:
            top_combo = list(design_trends['style_combinations'].keys())[0]
            recommendations.append({
                'category': '风格融合',
                'recommendation': f"尝试 {top_combo} 的设计组合",
                'reason': "这种风格组合已被多位设计师验证，具有良好的用户接受度"
            })
        
        # 基于渲染风格的建议
        best_render = max(
            render_trends['render_quality'].items(),
            key=lambda x: x[1]['engagement_ratio']
        )[0]
        recommendations.append({
            'category': '渲染技术',
            'recommendation': f"采用 {best_render} 渲染风格",
            'reason': f"该风格具有最高的用户互动率，平均每个模型获得 {render_trends['render_quality'][best_render]['avg_likes']:.1f} 个点赞"
        })
        
        # 基于关键词的建议
        hot_keywords = list(keyword_trends['top_keywords'].keys())[:3]
        recommendations.append({
            'category': '关键词优化',
            'recommendation': f"在作品标题和描述中包含: {', '.join(hot_keywords)}",
            'reason': "这些是当前最热门的设计关键词，有助于提高作品曝光度"
        })
        
        return recommendations
    
    def identify_market_opportunities(self, vehicle_trends, design_trends, author_trends) -> List[Dict[str, str]]:
        """识别市场机会"""
        opportunities = []
        
        # 低竞争但有潜力的车型
        vehicle_counts = vehicle_trends['vehicle_counts']
        underrepresented_vehicles = [
            vtype for vtype, count in vehicle_counts.items() 
            if 2 <= count <= 5
        ]
        
        if underrepresented_vehicles:
            opportunities.append({
                'type': '蓝海车型',
                'opportunity': f"关注 {', '.join(underrepresented_vehicles[:3])} 等车型设计",
                'potential': "这些车型竞争较少但有增长潜力，适合开拓性设计师"
            })
        
        # 高质量作者较少涉及的领域
        author_specialties = author_trends.get('author_specialties', {})
        all_specialties = Counter()
        for specialties in author_specialties.values():
            all_specialties.update(specialties.keys())
        
        rare_specialties = [
            specialty for specialty, count in all_specialties.items() 
            if count <= 2
        ]
        
        if rare_specialties:
            opportunities.append({
                'type': '专业化机会',
                'opportunity': f"专注于 {', '.join(rare_specialties[:3])} 领域",
                'potential': "这些领域缺乏专业设计师，有机会建立专业声誉"
            })
        
        # 风格创新机会
        style_counts = design_trends['style_counts']
        innovative_styles = [
            style for style, count in style_counts.items() 
            if count >= 3 and count <= 8
        ]
        
        if innovative_styles:
            opportunities.append({
                'type': '风格创新',
                'opportunity': f"深化 {', '.join(innovative_styles[:2])} 风格",
                'potential': "这些风格有基础但未饱和，适合深入发展"
            })
        
        return opportunities
    
    def save_report(self, report: Dict[str, Any]):
        """保存分析报告"""
        # 保存JSON格式报告
        report_file = os.path.join(self.output_dir, 'car_design_trend_report.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 保存Markdown格式报告
        self.generate_markdown_report(report)
        
        print(f"✅ 趋势分析报告已保存到 {self.output_dir}/")
    
    def generate_markdown_report(self, report: Dict[str, Any]):
        """生成Markdown格式报告"""
        md_content = f"""# 汽车设计趋势洞察报告

## 📊 执行摘要

**报告生成时间**: {report['report_metadata']['generated_at']}  
**分析范围**: {report['report_metadata']['analysis_scope']}  
**模型总数**: {report['report_metadata']['total_models_analyzed']}

### 🎯 核心发现

{chr(10).join(f"- {finding}" for finding in report['executive_summary']['key_findings'])}

### 🚗 热门车型趋势
{', '.join(report['executive_summary']['trending_vehicles'])}

### 🎨 流行设计风格  
{', '.join(report['executive_summary']['popular_styles'])}

### 👑 顶级设计师
{', '.join(report['executive_summary']['top_creators'])}

## 📈 详细分析

### 车辆类型趋势
{self._format_vehicle_trends(report['detailed_analysis']['vehicle_type_trends'])}

### 设计风格分析
{self._format_design_trends(report['detailed_analysis']['design_style_trends'])}

### 作者创作趋势
{self._format_author_trends(report['detailed_analysis']['author_trends'])}

## 💡 设计建议

{self._format_recommendations(report['design_recommendations'])}

## 🚀 市场机会

{self._format_opportunities(report['market_opportunities'])}

## 📁 附件说明

- `vehicle_type_trends.png`: 车辆类型趋势可视化
- `design_style_trends.png`: 设计风格趋势图表  
- `keyword_wordcloud.png`: 关键词词云图
- `car_design_trend_report.json`: 完整数据报告

---
*本报告由LiblibAI汽车设计趋势分析器自动生成*
"""
        
        md_file = os.path.join(self.output_dir, 'trend_report.md')
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
    
    def _format_vehicle_trends(self, trends: Dict) -> str:
        """格式化车辆趋势"""
        lines = []
        for vehicle, count in list(trends['vehicle_counts'].items())[:5]:
            lines.append(f"- **{vehicle}**: {count} 个模型")
        return '\n'.join(lines)
    
    def _format_design_trends(self, trends: Dict) -> str:
        """格式化设计趋势"""
        lines = []
        for style, count in list(trends['style_counts'].items())[:5]:
            lines.append(f"- **{style}**: {count} 个模型")
        return '\n'.join(lines)
    
    def _format_author_trends(self, trends: Dict) -> str:
        """格式化作者趋势"""
        lines = []
        for author in trends['top_authors'][:5]:
            lines.append(f"- **{author['username']}**: {author['model_count']} 个模型，平均 {author['avg_likes']:.1f} 点赞")
        return '\n'.join(lines)
    
    def _format_recommendations(self, recommendations: List) -> str:
        """格式化建议"""
        lines = []
        for rec in recommendations:
            lines.append(f"### {rec['category']}")
            lines.append(f"**建议**: {rec['recommendation']}")
            lines.append(f"**理由**: {rec['reason']}")
            lines.append("")
        return '\n'.join(lines)
    
    def _format_opportunities(self, opportunities: List) -> str:
        """格式化机会"""
        lines = []
        for opp in opportunities:
            lines.append(f"### {opp['type']}")
            lines.append(f"**机会**: {opp['opportunity']}")
            lines.append(f"**潜力**: {opp['potential']}")
            lines.append("")
        return '\n'.join(lines)

def main():
    """主函数"""
    analyzer = CarDesignTrendAnalyzer()
    
    if not analyzer.models_data:
        print("❌ 没有可分析的数据，请先运行采集器")
        return
    
    try:
        # 生成综合报告
        report = analyzer.generate_comprehensive_report()
        
        # 保存报告
        analyzer.save_report(report)
        
        print(f"\n✅ 趋势分析完成！")
        print(f"📊 分析了 {len(analyzer.models_data)} 个汽车模型")
        print(f"📈 生成了 {len(report['design_recommendations'])} 条设计建议")
        print(f"🚀 识别了 {len(report['market_opportunities'])} 个市场机会")
        print(f"📁 报告保存在 {analyzer.output_dir}/ 目录中")
        
    except Exception as e:
        print(f"❌ 分析过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
