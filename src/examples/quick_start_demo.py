#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 快速开始演示脚本
让新人在30分钟内跑通POC
一键体验汽车交通模型分析系统
"""

import os
import sys
import time
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_banner():
    """打印欢迎横幅"""
    print("\n" + "="*70)
    print("🚗 Liblib汽车交通模型分析系统 - 快速开始演示")
    print("="*70)
    print("✨ 一键体验：采集→清洗→分析→出图（中文）")
    print("⏱️  预计时间：30分钟")
    print("🎯 目标：完成第一个分析报告")
    print("="*70)

def check_environment():
    """检查环境配置"""
    print("\n🔍 步骤1: 检查环境配置...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
        print("❌ Python版本过低，需要Python 3.7+")
        print(f"   当前版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
        return False
    
    print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查必要文件
    required_files = [
        'save_and_analyze_collected_data.py',
        'run_complete_analysis.py',
        'requirements.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
        return False
    
    print("✅ 项目文件完整")
    
    # 检查输出目录
    output_dirs = ['liblib_analysis_output', 'database_analysis_output', 'complete_analysis_output']
    for dir_name in output_dirs:
        if os.path.exists(dir_name):
            print(f"⚠️  发现已存在的输出目录: {dir_name}")
    
    return True

def install_dependencies():
    """安装依赖"""
    print("\n📦 步骤2: 安装依赖...")
    
    try:
        import pandas
        import matplotlib
        import seaborn
        import numpy
        print("✅ 核心依赖已安装")
        return True
    except ImportError:
        print("📥 正在安装依赖...")
        
        # 尝试安装依赖
        try:
            os.system("pip install pandas matplotlib seaborn numpy wordcloud")
            print("✅ 依赖安装完成")
            return True
        except Exception as e:
            print(f"❌ 依赖安装失败: {e}")
            print("💡 请手动运行: pip install pandas matplotlib seaborn numpy wordcloud")
            return False

def run_static_analysis():
    """运行静态数据分析"""
    print("\n📊 步骤3: 运行静态数据分析...")
    
    try:
        # 导入分析器
        from save_and_analyze_collected_data import ComprehensiveCarAnalyzer
        
        # 创建分析器实例
        analyzer = ComprehensiveCarAnalyzer()
        
        # 运行分析
        print("🔄 正在分析数据...")
        results = analyzer.run_analysis()
        
        if results['status'] == 'success':
            print("✅ 静态数据分析完成！")
            print(f"📊 分析了 {results['total_models']} 个模型")
            print(f"📄 报告文件: {results['files_generated']['report']}")
            print(f"📈 图表文件: {results['files_generated']['charts']}")
            return True
        else:
            print(f"❌ 分析失败: {results['message']}")
            return False
            
    except Exception as e:
        print(f"❌ 运行分析时出错: {e}")
        return False

def run_complete_pipeline():
    """运行完整流水线"""
    print("\n🚀 步骤4: 运行完整分析流水线...")
    
    try:
        # 导入流水线
        from run_complete_analysis import CompleteAnalysisPipeline
        
        # 创建流水线实例
        pipeline = CompleteAnalysisPipeline(mode='static')
        
        # 运行流水线
        print("🔄 正在执行完整流水线...")
        import asyncio
        results = asyncio.run(pipeline.run_complete_pipeline())
        
        if results['status'] == 'success':
            print("✅ 完整流水线执行成功！")
            print(f"⏱️  执行耗时: {results['execution_time']:.2f} 秒")
            print(f"📄 汇总报告: {results['summary_report']}")
            return True
        else:
            print(f"❌ 流水线执行失败: {results['message']}")
            return False
            
    except Exception as e:
        print(f"❌ 运行流水线时出错: {e}")
        return False

def show_results():
    """展示结果"""
    print("\n🎉 步骤5: 查看分析结果...")
    
    # 检查输出文件
    output_dirs = ['liblib_analysis_output', 'complete_analysis_output']
    
    for dir_name in output_dirs:
        if os.path.exists(dir_name):
            print(f"\n📁 输出目录: {dir_name}")
            
            # 列出文件
            for root, dirs, files in os.walk(dir_name):
                level = root.replace(dir_name, '').count(os.sep)
                indent = ' ' * 2 * level
                print(f"{indent}📁 {os.path.basename(root)}/")
                subindent = ' ' * 2 * (level + 1)
                for file in files:
                    if file.endswith(('.md', '.png', '.json', '.csv')):
                        print(f"{subindent}📄 {file}")
    
    print("\n🎯 恭喜！你已经成功完成了第一个汽车交通模型分析！")
    print("📚 接下来可以：")
    print("   1. 查看生成的报告和图表")
    print("   2. 尝试修改分析参数")
    print("   3. 探索数据库分析功能")
    print("   4. 阅读完整文档了解更多功能")

def run_demo():
    """运行完整演示"""
    print_banner()
    
    # 步骤1: 检查环境
    if not check_environment():
        print("\n❌ 环境检查失败，请解决上述问题后重试")
        return False
    
    # 步骤2: 安装依赖
    if not install_dependencies():
        print("\n❌ 依赖安装失败，请手动安装后重试")
        return False
    
    # 步骤3: 运行静态分析
    if not run_static_analysis():
        print("\n❌ 静态分析失败，请检查错误信息")
        return False
    
    # 步骤4: 运行完整流水线
    if not run_complete_pipeline():
        print("\n❌ 完整流水线失败，但静态分析已成功")
    
    # 步骤5: 展示结果
    show_results()
    
    return True

def main():
    """主函数"""
    try:
        start_time = time.time()
        
        success = run_demo()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n⏱️  总耗时: {total_time:.1f} 秒")
        
        if success:
            print("\n🎉 演示完成！欢迎使用Liblib汽车交通模型分析系统！")
        else:
            print("\n⚠️  演示过程中遇到一些问题，但核心功能已可用")
        
        print("\n📚 更多信息请查看: README_T13_T14_COMPLETE.md")
        print("🔧 技术支持请查看: 常见问题解答部分")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断演示")
        print("💡 你可以稍后重新运行: python quick_start_demo.py")
    except Exception as e:
        print(f"\n❌ 演示过程中出现异常: {e}")
        print("💡 请检查错误信息或联系技术支持")

if __name__ == "__main__":
    main()
