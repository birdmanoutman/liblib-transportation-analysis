#!/usr/bin/env python3
"""
汽车交通设计趋势完整分析流程
集成数据采集、图片下载和趋势分析的主控制脚本
"""

import os
import sys
import subprocess
import time
from datetime import datetime
import json

def print_banner():
    """打印程序横幅"""
    print("=" * 60)
    print("🚗 LiblibAI 汽车交通设计趋势完整分析系统")
    print("=" * 60)
    print("📊 为设计师提供专业的趋势洞察和市场分析")
    print("🎯 涵盖数据采集、图片下载、趋势分析全流程")
    print("=" * 60)
    print()

def check_dependencies():
    """检查依赖项"""
    print("🔍 检查系统依赖...")
    
    required_packages = [
        'requests', 'matplotlib', 'seaborn', 'pandas',
        'jieba', 'wordcloud', 'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} (缺失)")
    
    if missing_packages:
        print(f"\n⚠️ 缺少以下依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ 所有依赖项检查通过")
    return True

def run_data_collection():
    """运行数据采集"""
    print("\n" + "="*50)
    print("📥 第一阶段: 数据采集")
    print("="*50)
    
    start_time = time.time()
    
    try:
        print("🚀 启动汽车交通模型采集器...")
        result = subprocess.run([
            sys.executable, 'complete_car_scraper.py'
        ], capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 数据采集完成")
            print(result.stdout)
        else:
            print("❌ 数据采集失败")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 采集过程异常: {e}")
        return False
    
    elapsed_time = time.time() - start_time
    print(f"⏱️ 采集耗时: {elapsed_time:.2f} 秒")
    
    return True

def run_trend_analysis():
    """运行趋势分析"""
    print("\n" + "="*50)
    print("📊 第二阶段: 趋势分析")
    print("="*50)
    
    start_time = time.time()
    
    # 检查数据文件是否存在
    data_file = 'car_models_complete/complete_car_models_data.json'
    if not os.path.exists(data_file):
        print(f"❌ 数据文件不存在: {data_file}")
        print("请先完成数据采集阶段")
        return False
    
    try:
        print("🎯 启动趋势分析器...")
        result = subprocess.run([
            sys.executable, 'car_design_trend_analyzer.py'
        ], capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 趋势分析完成")
            print(result.stdout)
        else:
            print("❌ 趋势分析失败")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 分析过程异常: {e}")
        return False
    
    elapsed_time = time.time() - start_time
    print(f"⏱️ 分析耗时: {elapsed_time:.2f} 秒")
    
    return True

def generate_summary_report():
    """生成汇总报告"""
    print("\n" + "="*50)
    print("📋 第三阶段: 汇总报告")
    print("="*50)
    
    try:
        # 读取采集统计
        collection_stats_file = 'car_models_complete/collection_statistics.json'
        if os.path.exists(collection_stats_file):
            with open(collection_stats_file, 'r', encoding='utf-8') as f:
                collection_stats = json.load(f)
        else:
            collection_stats = {}
        
        # 读取趋势报告
        trend_report_file = 'trend_analysis_output/car_design_trend_report.json'
        if os.path.exists(trend_report_file):
            with open(trend_report_file, 'r', encoding='utf-8') as f:
                trend_report = json.load(f)
        else:
            trend_report = {}
        
        # 生成汇总
        summary = {
            'analysis_completed_at': datetime.now().isoformat(),
            'collection_summary': collection_stats.get('collection_summary', {}),
            'trend_insights': trend_report.get('executive_summary', {}),
            'output_files': {
                'data_directory': 'car_models_complete/',
                'images_directory': 'car_models_complete/images/',
                'analysis_directory': 'trend_analysis_output/',
                'main_data_file': 'car_models_complete/complete_car_models_data.json',
                'trend_report': 'trend_analysis_output/trend_report.md',
                'charts': [
                    'trend_analysis_output/vehicle_type_trends.png',
                    'trend_analysis_output/design_style_trends.png',
                    'trend_analysis_output/keyword_wordcloud.png'
                ]
            },
            'recommendations': trend_report.get('design_recommendations', []),
            'market_opportunities': trend_report.get('market_opportunities', [])
        }
        
        # 保存汇总报告
        summary_file = 'complete_analysis_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print("✅ 汇总报告生成完成")
        return summary
        
    except Exception as e:
        print(f"❌ 汇总报告生成失败: {e}")
        return None

def print_final_results(summary):
    """打印最终结果"""
    print("\n" + "="*60)
    print("🎉 分析完成！结果汇总")
    print("="*60)
    
    if not summary:
        print("❌ 无法生成结果汇总")
        return
    
    collection_summary = summary.get('collection_summary', {})
    trend_insights = summary.get('trend_insights', {})
    
    print("📊 数据采集结果:")
    print(f"   总计模型: {collection_summary.get('total_models', 'N/A')}")
    print(f"   图片数量: {collection_summary.get('total_images', 'N/A')}")
    print(f"   成功下载: {collection_summary.get('total_downloads', 'N/A')}")
    
    print("\n🎯 趋势洞察:")
    trending_vehicles = trend_insights.get('trending_vehicles', [])
    if trending_vehicles:
        print(f"   热门车型: {', '.join(trending_vehicles[:3])}")
    
    popular_styles = trend_insights.get('popular_styles', [])
    if popular_styles:
        print(f"   流行风格: {', '.join(popular_styles[:3])}")
    
    top_creators = trend_insights.get('top_creators', [])
    if top_creators:
        print(f"   顶级设计师: {', '.join(top_creators[:3])}")
    
    print("\n📁 输出文件:")
    output_files = summary.get('output_files', {})
    print(f"   数据目录: {output_files.get('data_directory', 'N/A')}")
    print(f"   图片目录: {output_files.get('images_directory', 'N/A')}")
    print(f"   分析目录: {output_files.get('analysis_directory', 'N/A')}")
    print(f"   趋势报告: {output_files.get('trend_report', 'N/A')}")
    
    print("\n💡 设计建议:")
    recommendations = summary.get('recommendations', [])
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"   {i}. {rec.get('recommendation', '')}")
    
    print("\n🚀 市场机会:")
    opportunities = summary.get('market_opportunities', [])
    for i, opp in enumerate(opportunities[:3], 1):
        print(f"   {i}. {opp.get('opportunity', '')}")
    
    print("\n" + "="*60)
    print("✨ 分析流程全部完成，数据和报告已保存")
    print("📖 查看 trend_analysis_output/trend_report.md 获取详细报告")
    print("="*60)

def main():
    """主函数"""
    print_banner()
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    start_time = time.time()
    
    try:
        # 第一阶段：数据采集
        if not run_data_collection():
            print("❌ 数据采集失败，终止流程")
            sys.exit(1)
        
        # 第二阶段：趋势分析
        if not run_trend_analysis():
            print("❌ 趋势分析失败，终止流程")
            sys.exit(1)
        
        # 第三阶段：汇总报告
        summary = generate_summary_report()
        
        # 打印最终结果
        print_final_results(summary)
        
        total_time = time.time() - start_time
        print(f"\n⏱️ 总耗时: {total_time:.2f} 秒")
        
    except KeyboardInterrupt:
        print("\n❌ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 流程执行异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
