#!/usr/bin/env python3
"""
基于现有LiblibAI汽车模型数据的深度分析
为设计师提供趋势洞察和设计建议
"""

import json
import os
from typing import Dict, List, Any, Tuple
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime
import jieba
import re
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class ExistingDataAnalyzer:
    def __init__(self, data_file: str = 'liblib_car_models_analysis.json'):
        self.data_file = data_file
        self.models_data = []
        self.summary_data = {}
        self.output_dir = 'existing_data_analysis'
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 加载数据
        self.load_data()
        
    def load_data(self):
        """加载现有模型数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.summary_data = data.get('summary', {})
                self.models_data = data.get('models', [])
            
            print(f"✅ 成功加载 {len(self.models_data)} 个汽车模型数据")
            print(f"📊 数据概览:")
            print(f"   总浏览量: {self.summary_data.get('total_views', 0):,}")
            print(f"   总点赞数: {self.summary_data.get('total_likes', 0):,}")
            print(f"   总下载数: {self.summary_data.get('total_downloads', 0):,}")
            
        except FileNotFoundError:
            print(f"❌ 数据文件不存在: {self.data_file}")
            return
        except json.JSONDecodeError:
            print(f"❌ 数据文件格式错误: {self.data_file}")
            return
    
    def analyze_model_types_and_performance(self) -> Dict[str, Any]:
        """分析模型类型和性能表现"""
        print("🎯 分析模型类型和性能表现...")
        
        # 模型类型统计
        model_types = Counter()
        base_models = Counter()
        type_performance = defaultdict(lambda: {
            'views': [], 'likes': [], 'downloads': [], 'models': []
        })
        
        for model in self.models_data:
            model_type = model.get('type', 'Unknown')
            base_model = model.get('baseModel', 'Unknown')
            
            model_types[model_type] += 1
            base_models[base_model] += 1
            
            # 转换字符串数值
            views = self.parse_number(model.get('views', '0'))
            likes = self.parse_number(model.get('likes', '0'))
            downloads = self.parse_number(model.get('downloads', '0'))
            
            type_performance[model_type]['views'].append(views)
            type_performance[model_type]['likes'].append(likes)
            type_performance[model_type]['downloads'].append(downloads)
            type_performance[model_type]['models'].append(model)
        
        # 计算性能指标
        performance_analysis = {}
        for model_type, data in type_performance.items():
            if data['views']:
                performance_analysis[model_type] = {
                    'count': len(data['views']),
                    'avg_views': np.mean(data['views']),
                    'avg_likes': np.mean(data['likes']),
                    'avg_downloads': np.mean(data['downloads']),
                    'engagement_rate': np.mean(data['likes']) / max(np.mean(data['views']), 1) * 100,
                    'download_rate': np.mean(data['downloads']) / max(np.mean(data['views']), 1) * 100,
                    'top_model': max(data['models'], key=lambda x: self.parse_number(x.get('views', '0')))
                }
        
        # 创建可视化
        self.plot_model_performance(performance_analysis)
        
        return {
            'model_types': dict(model_types),
            'base_models': dict(base_models),
            'performance_analysis': performance_analysis
        }
    
    def analyze_content_and_keywords(self) -> Dict[str, Any]:
        """分析内容关键词和设计趋势"""
        print("🔍 分析内容关键词和设计趋势...")
        
        all_keywords = []
        title_keywords = []
        car_style_keywords = {
            '设计风格': [],
            '车辆类型': [],
            '渲染风格': [],
            '技术特征': []
        }
        
        # 关键词分类词典
        style_categories = {
            '设计风格': ['科幻', '现代', '复古', '豪华', '运动', '极简', '工业', '未来', '经典', '概念'],
            '车辆类型': ['跑车', '轿车', 'SUV', '卡车', '巴士', '摩托', '赛车', '皮卡', '概念车', 'F1'],
            '渲染风格': ['写实', '插画', '3D', '渲染', '手绘', '照片', '建模', '质感', '光影'],
            '技术特征': ['AI', '生成', '模型', 'LoRA', 'Checkpoint', '训练', '算法', '参数']
        }
        
        keyword_performance = defaultdict(lambda: {
            'count': 0, 'total_views': 0, 'total_likes': 0, 'models': []
        })
        
        for model in self.models_data:
            title = model.get('title', '')
            description = model.get('description', '')
            text = f"{title} {description}".lower()
            
            views = self.parse_number(model.get('views', '0'))
            likes = self.parse_number(model.get('likes', '0'))
            
            # 提取中文关键词
            chinese_words = re.findall(r'[\u4e00-\u9fff]+', title)
            title_keywords.extend(chinese_words)
            all_keywords.extend(chinese_words)
            
            # 提取英文关键词
            english_words = re.findall(r'[A-Za-z]+', title)
            title_keywords.extend(english_words)
            all_keywords.extend(english_words)
            
            # 分类关键词
            for category, keywords in style_categories.items():
                found_keywords = []
                for keyword in keywords:
                    if keyword.lower() in text or keyword in title:
                        found_keywords.append(keyword)
                        car_style_keywords[category].append(keyword)
                        
                        # 统计关键词性能
                        keyword_performance[keyword]['count'] += 1
                        keyword_performance[keyword]['total_views'] += views
                        keyword_performance[keyword]['total_likes'] += likes
                        keyword_performance[keyword]['models'].append(model)
        
        # 分析关键词趋势
        keyword_trends = {}
        for keyword, data in keyword_performance.items():
            if data['count'] >= 2:  # 至少出现2次
                keyword_trends[keyword] = {
                    'count': data['count'],
                    'avg_views': data['total_views'] / data['count'],
                    'avg_likes': data['total_likes'] / data['count'],
                    'engagement_score': (data['total_likes'] * 1.0 + data['total_views'] * 0.1) / data['count']
                }
        
        # 生成词云数据
        title_word_counts = Counter(title_keywords)
        # 将列表转换为Counter对象以供后续使用
        style_counters_for_viz = {}
        for k, v in car_style_keywords.items():
            style_counters_for_viz[k] = Counter(v) if v else Counter()
        self.generate_keyword_analysis(title_word_counts, style_counters_for_viz)
        
        # 确保将列表转换为Counter对象
        style_counters = {}
        for k, v in car_style_keywords.items():
            style_counters[k] = Counter(v) if v else Counter()
        
        return {
            'keyword_frequencies': dict(Counter(all_keywords).most_common(20)),
            'style_categories': style_counters,
            'keyword_trends': keyword_trends,
            'content_insights': self.generate_content_insights(style_counters, keyword_trends)
        }
    
    def analyze_author_strategies(self) -> Dict[str, Any]:
        """分析作者策略和成功模式"""
        print("👥 分析作者策略和成功模式...")
        
        author_stats = defaultdict(lambda: {
            'models': [], 'total_views': 0, 'total_likes': 0, 'total_downloads': 0,
            'specialties': [], 'avg_performance': {}
        })
        
        for model in self.models_data:
            author = model.get('author', 'Unknown')
            views = self.parse_number(model.get('views', '0'))
            likes = self.parse_number(model.get('likes', '0'))
            downloads = self.parse_number(model.get('downloads', '0'))
            
            author_stats[author]['models'].append(model)
            author_stats[author]['total_views'] += views
            author_stats[author]['total_likes'] += likes
            author_stats[author]['total_downloads'] += downloads
            
            # 分析专长
            title = model.get('title', '').lower()
            if any(word in title for word in ['概念', 'concept']):
                author_stats[author]['specialties'].append('概念设计')
            if any(word in title for word in ['渲染', 'render']):
                author_stats[author]['specialties'].append('渲染技术')
            if any(word in title for word in ['质感', '材质']):
                author_stats[author]['specialties'].append('材质表现')
        
        # 计算作者成功指标
        author_rankings = []
        for author, data in author_stats.items():
            model_count = len(data['models'])
            if model_count >= 1:  # 至少有1个模型
                engagement_score = (
                    data['total_likes'] * 2.0 + 
                    data['total_downloads'] * 3.0 + 
                    data['total_views'] * 0.1
                ) / model_count
                
                author_rankings.append({
                    'author': author,
                    'model_count': model_count,
                    'avg_views': data['total_views'] / model_count,
                    'avg_likes': data['total_likes'] / model_count,
                    'avg_downloads': data['total_downloads'] / model_count,
                    'engagement_score': engagement_score,
                    'main_specialties': list(set(data['specialties']))[:3],
                    'best_model': max(data['models'], key=lambda x: self.parse_number(x.get('views', '0')))
                })
        
        author_rankings.sort(key=lambda x: x['engagement_score'], reverse=True)
        
        return {
            'total_authors': len(author_stats),
            'top_authors': author_rankings[:10],
            'author_insights': self.generate_author_insights(author_rankings)
        }
    
    def analyze_market_trends(self) -> Dict[str, Any]:
        """分析市场趋势和机会"""
        print("📈 分析市场趋势和机会...")
        
        # 按性能排序模型
        sorted_models = sorted(
            self.models_data,
            key=lambda x: (
                self.parse_number(x.get('likes', '0')) * 2 + 
                self.parse_number(x.get('downloads', '0')) * 3 +
                self.parse_number(x.get('views', '0')) * 0.1
            ),
            reverse=True
        )
        
        # 分析热门模型特征
        top_models = sorted_models[:6]  # 前6个模型
        trending_features = {
            'model_types': Counter(),
            'design_themes': Counter(),
            'naming_patterns': []
        }
        
        for model in top_models:
            model_type = model.get('type', '')
            title = model.get('title', '')
            
            trending_features['model_types'][model_type] += 1
            trending_features['naming_patterns'].append(title)
            
            # 提取设计主题
            if any(word in title.lower() for word in ['科幻', 'sci-fi', '未来']):
                trending_features['design_themes']['科幻风格'] += 1
            if any(word in title.lower() for word in ['概念', 'concept']):
                trending_features['design_themes']['概念设计'] += 1
            if any(word in title.lower() for word in ['质感', '材质', '渲染']):
                trending_features['design_themes']['质感表现'] += 1
            if any(word in title.lower() for word in ['豪华', 'luxury']):
                trending_features['design_themes']['豪华风格'] += 1
        
        # 识别市场机会
        market_opportunities = self.identify_opportunities(sorted_models)
        
        # 生成趋势预测
        trend_predictions = self.predict_trends(trending_features, sorted_models)
        
        return {
            'top_performing_models': [
                {
                    'title': model.get('title', ''),
                    'author': model.get('author', ''),
                    'type': model.get('type', ''),
                    'views': model.get('views', ''),
                    'likes': model.get('likes', ''),
                    'downloads': model.get('downloads', '')
                }
                for model in top_models
            ],
            'trending_features': {
                'model_types': dict(trending_features['model_types']),
                'design_themes': dict(trending_features['design_themes']),
                'naming_patterns': trending_features['naming_patterns']
            },
            'market_opportunities': market_opportunities,
            'trend_predictions': trend_predictions
        }
    
    def parse_number(self, value: str) -> int:
        """解析数字字符串"""
        if isinstance(value, (int, float)):
            return int(value)
        
        if isinstance(value, str):
            # 移除逗号和空格
            clean_value = value.replace(',', '').replace(' ', '')
            try:
                return int(clean_value)
            except ValueError:
                return 0
        
        return 0
    
    def generate_content_insights(self, style_categories: Dict, keyword_trends: Dict) -> List[str]:
        """生成内容洞察"""
        insights = []
        
        # 分析设计风格趋势
        design_styles = style_categories.get('设计风格', Counter())
        if design_styles:
            top_style = design_styles.most_common(1)[0]
            insights.append(f"🎨 {top_style[0]} 是当前最受欢迎的设计风格，出现 {top_style[1]} 次")
        
        # 分析车辆类型趋势
        vehicle_types = style_categories.get('车辆类型', Counter())
        if vehicle_types:
            top_vehicle = vehicle_types.most_common(1)[0]
            insights.append(f"🚗 {top_vehicle[0]} 是最热门的车辆类型，有 {top_vehicle[1]} 个相关模型")
        
        # 分析高价值关键词
        if keyword_trends:
            high_value_keywords = [
                (k, v['engagement_score']) 
                for k, v in keyword_trends.items() 
                if v['engagement_score'] > 1000
            ]
            if high_value_keywords:
                best_keyword = max(high_value_keywords, key=lambda x: x[1])
                insights.append(f"⭐ '{best_keyword[0]}' 是最有价值的关键词，参与度得分: {best_keyword[1]:.0f}")
        
        return insights
    
    def generate_author_insights(self, author_rankings: List) -> List[str]:
        """生成作者洞察"""
        insights = []
        
        if author_rankings:
            top_author = author_rankings[0]
            insights.append(f"👑 {top_author['author']} 是表现最佳的作者，平均参与度得分: {top_author['engagement_score']:.0f}")
            
            # 分析多产作者
            productive_authors = [a for a in author_rankings if a['model_count'] >= 2]
            if productive_authors:
                insights.append(f"🏭 {len(productive_authors)} 位作者发布了多个模型，显示持续创作能力")
            
            # 分析专业化程度
            specialized_authors = [a for a in author_rankings if len(a['main_specialties']) >= 2]
            if specialized_authors:
                insights.append(f"🎯 {len(specialized_authors)} 位作者展现出明确的专业化方向")
        
        return insights
    
    def identify_opportunities(self, sorted_models: List) -> List[Dict[str, str]]:
        """识别市场机会"""
        opportunities = []
        
        # 分析模型类型分布
        model_types = Counter(model.get('type', '') for model in self.models_data)
        underrepresented_types = [t for t, count in model_types.items() if count <= 2 and t]
        
        if underrepresented_types:
            opportunities.append({
                'type': '模型类型机会',
                'description': f"关注 {', '.join(underrepresented_types[:3])} 等类型",
                'reason': '这些模型类型竞争较少，有发展空间'
            })
        
        # 分析成功模式
        top_models = sorted_models[:5]
        common_features = []
        
        for model in top_models:
            title = model.get('title', '').lower()
            if 'f.1' in title or 'f1' in title:
                common_features.append('F.1系列')
            if any(word in title for word in ['质感', '渲染', '光影']):
                common_features.append('质感表现')
            if any(word in title for word in ['概念', 'concept']):
                common_features.append('概念设计')
        
        feature_counts = Counter(common_features)
        if feature_counts:
            top_feature = feature_counts.most_common(1)[0]
            opportunities.append({
                'type': '成功模式',
                'description': f"重点发展 {top_feature[0]} 相关内容",
                'reason': f'在前5名模型中出现 {top_feature[1]} 次，证明受欢迎度高'
            })
        
        return opportunities
    
    def predict_trends(self, trending_features: Dict, sorted_models: List) -> List[Dict[str, str]]:
        """预测趋势"""
        predictions = []
        
        # 基于热门模型类型预测
        top_model_types = trending_features.get('model_types', Counter())
        if top_model_types:
            dominant_type = top_model_types.most_common(1)[0]
            predictions.append({
                'trend': '模型技术发展',
                'prediction': f"{dominant_type[0]} 将继续主导市场",
                'confidence': '高',
                'basis': f'在顶级模型中占比 {dominant_type[1]/6*100:.1f}%'
            })
        
        # 基于设计主题预测
        design_themes = trending_features.get('design_themes', Counter())
        if design_themes:
            emerging_theme = design_themes.most_common(1)[0]
            predictions.append({
                'trend': '设计风格趋势',
                'prediction': f"{emerging_theme[0]} 将成为主流设计方向",
                'confidence': '中等',
                'basis': f'在热门模型中频繁出现'
            })
        
        # 基于性能数据预测
        avg_engagement = np.mean([
            self.parse_number(model.get('likes', '0')) + self.parse_number(model.get('downloads', '0'))
            for model in sorted_models[:10]
        ])
        
        predictions.append({
            'trend': '用户参与度',
            'prediction': '高质量模型的用户参与度将持续提升',
            'confidence': '高',
            'basis': f'顶级模型平均参与度达到 {avg_engagement:.0f}'
        })
        
        return predictions
    
    def plot_model_performance(self, performance_analysis: Dict):
        """绘制模型性能分析图"""
        if not performance_analysis:
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('LiblibAI 汽车模型性能分析', fontsize=16, fontweight='bold')
        
        types = list(performance_analysis.keys())
        
        # 1. 平均浏览量
        avg_views = [performance_analysis[t]['avg_views'] for t in types]
        ax1.bar(types, avg_views, color=sns.color_palette("viridis", len(types)))
        ax1.set_title('各类型模型平均浏览量')
        ax1.set_ylabel('平均浏览量')
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. 平均点赞数
        avg_likes = [performance_analysis[t]['avg_likes'] for t in types]
        ax2.bar(types, avg_likes, color=sns.color_palette("plasma", len(types)))
        ax2.set_title('各类型模型平均点赞数')
        ax2.set_ylabel('平均点赞数')
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. 参与度对比
        engagement_rates = [performance_analysis[t]['engagement_rate'] for t in types]
        download_rates = [performance_analysis[t]['download_rate'] for t in types]
        
        x = np.arange(len(types))
        width = 0.35
        
        ax3.bar(x - width/2, engagement_rates, width, label='点赞率(%)', color='skyblue')
        ax3.bar(x + width/2, download_rates, width, label='下载率(%)', color='orange')
        ax3.set_title('用户参与度对比')
        ax3.set_ylabel('比率 (%)')
        ax3.set_xticks(x)
        ax3.set_xticklabels(types, rotation=45)
        ax3.legend()
        
        # 4. 模型数量分布
        model_counts = [performance_analysis[t]['count'] for t in types]
        ax4.pie(model_counts, labels=types, autopct='%1.1f%%', startangle=90)
        ax4.set_title('模型类型分布')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'model_performance_analysis.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 性能分析图表已保存: {self.output_dir}/model_performance_analysis.png")
    
    def generate_keyword_analysis(self, word_counts: Counter, style_categories: Dict):
        """生成关键词分析图表"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('汽车模型关键词和风格分析', fontsize=16, fontweight='bold')
        
        # 1. 热门关键词
        top_words = word_counts.most_common(10)
        if top_words:
            words, counts = zip(*top_words)
            ax1.barh(words, counts, color=sns.color_palette("Set2", len(words)))
            ax1.set_title('热门关键词 Top 10')
            ax1.set_xlabel('出现频次')
        
        # 2. 设计风格分布
        design_styles = style_categories.get('设计风格', Counter())
        if design_styles:
            styles, style_counts = zip(*design_styles.most_common())
            ax2.pie(style_counts, labels=styles, autopct='%1.1f%%', startangle=90)
            ax2.set_title('设计风格分布')
        
        # 3. 车辆类型分布
        vehicle_types = style_categories.get('车辆类型', Counter())
        if vehicle_types:
            vehicles, vehicle_counts = zip(*vehicle_types.most_common())
            ax3.bar(vehicles, vehicle_counts, color=sns.color_palette("husl", len(vehicles)))
            ax3.set_title('车辆类型分布')
            ax3.set_ylabel('出现频次')
            ax3.tick_params(axis='x', rotation=45)
        
        # 4. 技术特征
        tech_features = style_categories.get('技术特征', Counter())
        if tech_features:
            features, feature_counts = zip(*tech_features.most_common())
            ax4.barh(features, feature_counts, color=sns.color_palette("coolwarm", len(features)))
            ax4.set_title('技术特征分布')
            ax4.set_xlabel('出现频次')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'keyword_style_analysis.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"🔍 关键词分析图表已保存: {self.output_dir}/keyword_style_analysis.png")
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """生成综合分析报告"""
        print("\n" + "="*60)
        print("📊 生成LiblibAI汽车模型深度分析报告")
        print("="*60)
        
        # 执行所有分析
        model_analysis = self.analyze_model_types_and_performance()
        content_analysis = self.analyze_content_and_keywords()
        author_analysis = self.analyze_author_strategies()
        market_analysis = self.analyze_market_trends()
        
        # 生成综合报告
        comprehensive_report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'data_source': self.data_file,
                'total_models': len(self.models_data),
                'analysis_scope': 'LiblibAI 汽车交通板块现有模型'
            },
            
            'executive_summary': {
                'total_models': len(self.models_data),
                'total_views': self.summary_data.get('total_views', 0),
                'total_likes': self.summary_data.get('total_likes', 0),
                'total_downloads': self.summary_data.get('total_downloads', 0),
                'avg_performance': {
                    'views': self.summary_data.get('avg_views', 0),
                    'likes': self.summary_data.get('avg_likes', 0),
                    'downloads': self.summary_data.get('avg_downloads', 0)
                },
                'top_model_types': list(model_analysis['model_types'].keys())[:3],
                'leading_authors': [author['author'] for author in author_analysis['top_authors'][:5]]
            },
            
            'detailed_analysis': {
                'model_performance': model_analysis,
                'content_keywords': content_analysis,
                'author_strategies': author_analysis,
                'market_trends': market_analysis
            },
            
            'design_recommendations': self.generate_design_recommendations(
                model_analysis, content_analysis, market_analysis
            ),
            
            'strategic_insights': self.generate_strategic_insights(
                model_analysis, author_analysis, market_analysis, content_analysis
            )
        }
        
        return comprehensive_report
    
    def generate_design_recommendations(self, model_analysis, content_analysis, market_analysis) -> List[Dict]:
        """生成设计建议"""
        recommendations = []
        
        # 基于表现最佳的模型类型
        performance = model_analysis.get('performance_analysis', {})
        if performance:
            best_type = max(performance.items(), key=lambda x: x[1]['engagement_rate'])[0]
            recommendations.append({
                'category': '模型类型选择',
                'title': f'重点发展 {best_type} 类型模型',
                'description': f'该类型具有最高的用户参与度 ({performance[best_type]["engagement_rate"]:.2f}%)',
                'priority': '高',
                'expected_impact': '提升用户互动和下载率'
            })
        
        # 基于热门关键词
        keyword_trends = content_analysis.get('keyword_trends', {})
        if keyword_trends:
            top_keyword = max(keyword_trends.items(), key=lambda x: x[1]['engagement_score'])[0]
            recommendations.append({
                'category': '内容优化',
                'title': f'在作品中突出 "{top_keyword}" 元素',
                'description': f'该关键词具有最高的参与度得分 ({keyword_trends[top_keyword]["engagement_score"]:.0f})',
                'priority': '中',
                'expected_impact': '提高作品曝光度和用户发现率'
            })
        
        # 基于市场机会
        opportunities = market_analysis.get('market_opportunities', [])
        for opp in opportunities[:2]:
            recommendations.append({
                'category': '市场机会',
                'title': opp.get('description', ''),
                'description': opp.get('reason', ''),
                'priority': '中',
                'expected_impact': '开拓新的市场空间'
            })
        
        return recommendations
    
    def generate_strategic_insights(self, model_analysis, author_analysis, market_analysis, content_analysis=None) -> List[Dict]:
        """生成战略洞察"""
        insights = []
        
        # 市场集中度分析
        top_authors = author_analysis.get('top_authors', [])
        if len(top_authors) >= 3:
            top_3_share = sum(author['model_count'] for author in top_authors[:3])
            total_models = len(self.models_data)
            concentration = (top_3_share / total_models) * 100
            
            insights.append({
                'type': '市场结构',
                'title': f'市场集中度: {concentration:.1f}%',
                'description': f'前3名作者贡献了 {concentration:.1f}% 的模型',
                'implication': '市场仍有较大空间给新进入者' if concentration < 50 else '市场相对集中，需要差异化策略'
            })
        
        # 技术趋势分析
        model_types = model_analysis.get('model_types', {})
        if 'LORAF.1' in model_types:
            lora_share = (model_types['LORAF.1'] / sum(model_types.values())) * 100
            insights.append({
                'type': '技术趋势',
                'title': f'LoRA F.1 技术占主导地位 ({lora_share:.1f}%)',
                'description': 'LoRA F.1 是当前最受欢迎的模型技术',
                'implication': '建议深入学习和优化 LoRA F.1 技术栈'
            })
        
        # 内容策略分析
        if content_analysis:
            content_insights = content_analysis.get('content_insights', [])
            if content_insights:
                insights.append({
                    'type': '内容策略',
                    'title': '设计风格多元化机会',
                    'description': '; '.join(content_insights[:2]),
                    'implication': '在热门风格基础上探索创新表达方式'
                })
        
        return insights
    
    def save_report(self, report: Dict[str, Any]):
        """保存分析报告"""
        # 保存JSON报告
        json_file = os.path.join(self.output_dir, 'comprehensive_analysis_report.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 生成Markdown报告
        self.generate_markdown_report(report)
        
        print(f"✅ 完整分析报告已保存到 {self.output_dir}/")
    
    def generate_markdown_report(self, report: Dict[str, Any]):
        """生成Markdown报告"""
        md_content = f"""# LiblibAI 汽车设计模型深度分析报告

## 📊 执行摘要

**报告生成时间**: {report['report_metadata']['generated_at']}  
**数据来源**: {report['report_metadata']['data_source']}  
**分析模型数量**: {report['report_metadata']['total_models']}

### 🎯 核心数据

- **总浏览量**: {report['executive_summary']['total_views']:,}
- **总点赞数**: {report['executive_summary']['total_likes']:,}  
- **总下载数**: {report['executive_summary']['total_downloads']:,}
- **平均性能**: 浏览 {report['executive_summary']['avg_performance']['views']:.0f} | 点赞 {report['executive_summary']['avg_performance']['likes']:.0f} | 下载 {report['executive_summary']['avg_performance']['downloads']:.0f}

### 🏆 市场领导者

**顶级模型类型**: {', '.join(report['executive_summary']['top_model_types'])}  
**leading作者**: {', '.join(report['executive_summary']['leading_authors'])}

## 📈 详细分析

### 模型类型性能分析

{self._format_model_performance(report['detailed_analysis']['model_performance'])}

### 内容关键词趋势

{self._format_content_analysis(report['detailed_analysis']['content_keywords'])}

### 作者策略分析

{self._format_author_analysis(report['detailed_analysis']['author_strategies'])}

### 市场趋势预测

{self._format_market_trends(report['detailed_analysis']['market_trends'])}

## 💡 设计建议

{self._format_design_recommendations(report['design_recommendations'])}

## 🎯 战略洞察

{self._format_strategic_insights(report['strategic_insights'])}

## 📁 分析图表

- `model_performance_analysis.png`: 模型性能对比分析
- `keyword_style_analysis.png`: 关键词和风格分布
- `comprehensive_analysis_report.json`: 完整数据报告

---
*本报告基于LiblibAI平台现有汽车交通模型数据生成*
"""
        
        md_file = os.path.join(self.output_dir, 'analysis_report.md')
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
    
    def _format_model_performance(self, performance_data: Dict) -> str:
        """格式化模型性能数据"""
        lines = []
        model_types = performance_data.get('model_types', {})
        performance_analysis = performance_data.get('performance_analysis', {})
        
        lines.append("#### 模型类型分布")
        for model_type, count in model_types.items():
            if model_type in performance_analysis:
                perf = performance_analysis[model_type]
                lines.append(f"- **{model_type}**: {count} 个模型，平均浏览量 {perf['avg_views']:.0f}，参与度 {perf['engagement_rate']:.2f}%")
        
        return '\n'.join(lines)
    
    def _format_content_analysis(self, content_data: Dict) -> str:
        """格式化内容分析数据"""
        lines = []
        
        lines.append("#### 热门关键词")
        keyword_freq = content_data.get('keyword_frequencies', {})
        for keyword, freq in list(keyword_freq.items())[:5]:
            lines.append(f"- **{keyword}**: {freq} 次")
        
        lines.append("\n#### 设计风格趋势")
        style_categories = content_data.get('style_categories', {})
        for category, styles in style_categories.items():
            if styles:
                top_style = styles.most_common(1)[0]
                lines.append(f"- **{category}**: {top_style[0]} 最受欢迎 ({top_style[1]} 次)")
        
        return '\n'.join(lines)
    
    def _format_author_analysis(self, author_data: Dict) -> str:
        """格式化作者分析数据"""
        lines = []
        top_authors = author_data.get('top_authors', [])
        
        lines.append("#### 顶级作者排行")
        for i, author in enumerate(top_authors[:5], 1):
            lines.append(f"{i}. **{author['author']}**: {author['model_count']} 个模型，参与度得分 {author['engagement_score']:.0f}")
        
        return '\n'.join(lines)
    
    def _format_market_trends(self, market_data: Dict) -> str:
        """格式化市场趋势数据"""
        lines = []
        
        lines.append("#### 表现最佳模型")
        top_models = market_data.get('top_performing_models', [])
        for i, model in enumerate(top_models[:3], 1):
            lines.append(f"{i}. **{model['title']}** by {model['author']} - 浏览量: {model['views']}")
        
        lines.append("\n#### 趋势预测")
        predictions = market_data.get('trend_predictions', [])
        for pred in predictions[:3]:
            lines.append(f"- **{pred['trend']}**: {pred['prediction']} (置信度: {pred['confidence']})")
        
        return '\n'.join(lines)
    
    def _format_design_recommendations(self, recommendations: List) -> str:
        """格式化设计建议"""
        lines = []
        for i, rec in enumerate(recommendations, 1):
            lines.append(f"### {i}. {rec['title']}")
            lines.append(f"**类别**: {rec['category']}")
            lines.append(f"**描述**: {rec['description']}")
            lines.append(f"**优先级**: {rec['priority']}")
            lines.append(f"**预期影响**: {rec['expected_impact']}")
            lines.append("")
        return '\n'.join(lines)
    
    def _format_strategic_insights(self, insights: List) -> str:
        """格式化战略洞察"""
        lines = []
        for insight in insights:
            lines.append(f"### {insight['title']}")
            lines.append(f"**类型**: {insight['type']}")
            lines.append(f"**描述**: {insight['description']}")
            lines.append(f"**启示**: {insight['implication']}")
            lines.append("")
        return '\n'.join(lines)

def main():
    """主函数"""
    analyzer = ExistingDataAnalyzer()
    
    if not analyzer.models_data:
        print("❌ 没有可分析的数据")
        return
    
    try:
        # 生成综合分析报告
        report = analyzer.generate_comprehensive_report()
        
        # 保存报告
        analyzer.save_report(report)
        
        print(f"\n✅ 分析完成！")
        print(f"📊 分析了 {len(analyzer.models_data)} 个汽车模型")
        print(f"💡 生成了 {len(report['design_recommendations'])} 条设计建议")
        print(f"🎯 提供了 {len(report['strategic_insights'])} 条战略洞察")
        print(f"📁 报告保存在 {analyzer.output_dir}/ 目录中")
        
        # 打印关键发现
        print(f"\n🔥 关键发现:")
        print(f"   最受欢迎模型类型: {list(report['detailed_analysis']['model_performance']['model_types'].keys())[0]}")
        print(f"   顶级作者: {report['executive_summary']['leading_authors'][0]}")
        print(f"   平均用户参与度: {report['executive_summary']['avg_performance']['likes']:.0f} 点赞")
        
    except Exception as e:
        print(f"❌ 分析过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
