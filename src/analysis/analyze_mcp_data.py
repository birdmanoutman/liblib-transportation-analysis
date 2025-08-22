#!/usr/bin/env python3
"""
分析MCP工具采集到的Liblib汽车交通模型数据
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
from typing import Dict, List, Any
import re

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MCPDataAnalyzer:
    """分析MCP工具采集的数据"""
    
    def __init__(self, data_dir: str = "data/raw/liblib/mcp_collection"):
        self.data_dir = Path(data_dir)
        self.data = None
        self.df = None
        
    def load_latest_data(self) -> bool:
        """加载最新的数据文件"""
        try:
            # 查找最新的JSON文件
            json_files = list(self.data_dir.glob("car_models_*.json"))
            if not json_files:
                logger.error(f"在 {self.data_dir} 中未找到数据文件")
                return False
                
            latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
            logger.info(f"加载数据文件: {latest_file}")
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
                
            # 转换为DataFrame
            self.df = pd.DataFrame(self.data)
            logger.info(f"成功加载 {len(self.df)} 条数据")
            return True
            
        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            return False
    
    def analyze_downloads(self) -> Dict[str, Any]:
        """分析下载量数据"""
        if self.df is None:
            return {}
            
        # 清理下载量数据（移除k, M等后缀）
        def clean_downloads(download_str):
            if pd.isna(download_str):
                return 0
            download_str = str(download_str)
            if 'k' in download_str.lower():
                return float(download_str.lower().replace('k', '')) * 1000
            elif 'm' in download_str.lower():
                return float(download_str.lower().replace('m', '')) * 1000000
            else:
                try:
                    return float(download_str)
                except:
                    return 0
        
        self.df['downloads_clean'] = self.df['downloads'].apply(clean_downloads)
        
        analysis = {
            'total_downloads': int(self.df['downloads_clean'].sum()),
            'avg_downloads': int(self.df['downloads_clean'].mean()),
            'max_downloads': int(self.df['downloads_clean'].max()),
            'min_downloads': int(self.df['downloads_clean'].min()),
            'download_distribution': self.df['downloads_clean'].describe().to_dict()
        }
        
        return analysis
    
    def analyze_authors(self) -> Dict[str, Any]:
        """分析作者数据"""
        if self.df is None:
            return {}
            
        author_stats = self.df.groupby('author').agg({
            'title': 'count',
            'downloads_clean': 'sum',
            'likes': lambda x: sum(int(str(i)) for i in x if str(i).isdigit()),
            'collections': lambda x: sum(int(str(i)) for i in x if str(i).isdigit())
        }).rename(columns={
            'title': 'model_count',
            'downloads_clean': 'total_downloads',
            'likes': 'total_likes',
            'collections': 'total_collections'
        })
        
        return {
            'total_authors': len(author_stats),
            'author_stats': author_stats.to_dict('index'),
            'top_authors_by_models': author_stats.nlargest(3, 'model_count').to_dict('index'),
            'top_authors_by_downloads': author_stats.nlargest(3, 'total_downloads').to_dict('index')
        }
    
    def analyze_model_types(self) -> Dict[str, Any]:
        """分析模型类型数据"""
        if self.df is None:
            return {}
            
        type_stats = self.df['type'].value_counts().to_dict()
        version_stats = self.df['version'].value_counts().to_dict()
        
        return {
            'type_distribution': type_stats,
            'version_distribution': version_stats,
            'total_types': len(type_stats),
            'total_versions': len(version_stats)
        }
    
    def generate_visualizations(self, output_dir: str = "data/processed/mcp_analysis"):
        """生成可视化图表"""
        if self.df is None:
            logger.error("没有数据可以可视化")
            return
            
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 1. 下载量分布
        plt.figure(figsize=(10, 6))
        self.df['downloads_clean'].hist(bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        plt.title('模型下载量分布')
        plt.xlabel('下载量')
        plt.ylabel('模型数量')
        plt.grid(True, alpha=0.3)
        plt.savefig(output_path / 'downloads_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. 作者模型数量
        author_counts = self.df['author'].value_counts()
        plt.figure(figsize=(12, 6))
        author_counts.plot(kind='bar', color='lightcoral')
        plt.title('各作者模型数量')
        plt.xlabel('作者')
        plt.ylabel('模型数量')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(output_path / 'author_model_counts.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. 模型类型分布
        type_counts = self.df['type'].value_counts()
        plt.figure(figsize=(8, 8))
        plt.pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%', startangle=90)
        plt.title('模型类型分布')
        plt.axis('equal')
        plt.savefig(output_path / 'model_type_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"可视化图表已保存到: {output_path}")
    
    def generate_report(self, output_dir: str = "data/processed/mcp_analysis") -> str:
        """生成分析报告"""
        if self.df is None:
            return "没有数据可以分析"
            
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 执行各项分析
        download_analysis = self.analyze_downloads()
        author_analysis = self.analyze_authors()
        type_analysis = self.analyze_model_types()
        
        # 生成报告
        report = f"""# Liblib汽车交通模型数据分析报告

## 📊 数据概览
- **采集时间**: {self.df['collected_at'].iloc[0][:19]}
- **总模型数**: {len(self.df)}
- **数据来源**: MCP浏览器观察

## 📈 下载量分析
- **总下载量**: {download_analysis.get('total_downloads', 0):,}
- **平均下载量**: {download_analysis.get('avg_downloads', 0):,}
- **最高下载量**: {download_analysis.get('max_downloads', 0):,}
- **最低下载量**: {download_analysis.get('min_downloads', 0):,}

## 👥 作者分析
- **总作者数**: {author_analysis.get('total_authors', 0)}
- **最多模型作者**: {list(author_analysis.get('top_authors_by_models', {}).keys())[:3] if author_analysis.get('top_authors_by_models') else []}

## 🏷️ 模型类型分析
- **模型类型**: {list(type_analysis.get('type_distribution', {}).keys())}
- **版本分布**: {type_analysis.get('version_distribution', {})}

## 📋 详细数据
"""
        
        # 添加模型列表
        for i, row in self.df.iterrows():
            report += f"""
### {row['title']}
- **类型**: {row['type']} {row['version']}
- **作者**: {row['author']}
- **下载量**: {row['downloads']}
- **点赞数**: {row['likes']}
- **收藏数**: {row['collections']}
- **专属**: {'是' if row['exclusive'] else '否'}
"""
        
        # 保存报告
        report_path = output_path / 'analysis_report.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
            
        logger.info(f"分析报告已保存到: {report_path}")
        return str(report_path)
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """运行完整分析"""
        logger.info("开始运行完整数据分析...")
        
        if not self.load_latest_data():
            return {}
            
        # 执行各项分析
        results = {
            'download_analysis': self.analyze_downloads(),
            'author_analysis': self.analyze_authors(),
            'type_analysis': self.analyze_model_types(),
            'total_models': len(self.df)
        }
        
        # 生成可视化
        self.generate_visualizations()
        
        # 生成报告
        report_path = self.generate_report()
        results['report_path'] = report_path
        
        logger.info("数据分析完成！")
        return results

def main():
    """主函数"""
    analyzer = MCPDataAnalyzer()
    results = analyzer.run_full_analysis()
    
    if results:
        print("\n✅ 数据分析完成！")
        print(f"📊 总模型数: {results['total_models']}")
        print(f"📈 总下载量: {results['download_analysis'].get('total_downloads', 0):,}")
        print(f"👥 总作者数: {results['author_analysis'].get('total_authors', 0)}")
        print(f"📄 报告文件: {results['report_path']}")
    else:
        print("❌ 数据分析失败")

if __name__ == "__main__":
    main()
