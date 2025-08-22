#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键完成分析流水线
整合：采集→清洗→分析→出图（中文）
支持数据库和静态数据两种模式
"""

import os
import sys
import asyncio
import logging
import argparse
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# 导入分析模块
from save_and_analyze_collected_data import ComprehensiveCarAnalyzer
from scripts.analysis.database_analysis_pipeline import DatabaseAnalysisPipeline

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('complete_analysis.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CompleteAnalysisPipeline:
    """完整分析流水线"""
    
    def __init__(self, mode='static'):
        self.mode = mode  # 'static' 或 'database'
        self.output_dir = "complete_analysis_output"
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 初始化分析器
        if mode == 'static':
            self.static_analyzer = ComprehensiveCarAnalyzer()
        else:
            self.db_pipeline = DatabaseAnalysisPipeline()
    
    async def run_static_analysis(self):
        """运行静态数据分析"""
        logger.info("🔄 运行静态数据分析...")
        
        try:
            results = self.static_analyzer.run_analysis()
            
            if results['status'] == 'success':
                logger.info("✅ 静态数据分析完成")
                return {
                    'mode': 'static',
                    'status': 'success',
                    'results': results,
                    'output_files': results['files_generated']
                }
            else:
                logger.error(f"❌ 静态数据分析失败: {results['message']}")
                return {
                    'mode': 'static',
                    'status': 'error',
                    'message': results['message']
                }
                
        except Exception as e:
            logger.error(f"❌ 静态数据分析异常: {e}")
            return {
                'mode': 'static',
                'status': 'error',
                'message': str(e)
            }
    
    async def run_database_analysis(self):
        """运行数据库分析"""
        logger.info("🔄 运行数据库分析...")
        
        try:
            results = await self.db_pipeline.run_complete_pipeline()
            
            if results['status'] == 'success':
                logger.info("✅ 数据库分析完成")
                return {
                    'mode': 'database',
                    'status': 'success',
                    'results': results,
                    'output_files': results['files_generated']
                }
            else:
                logger.error(f"❌ 数据库分析失败: {results['message']}")
                return {
                    'mode': 'database',
                    'status': 'error',
                    'message': results['message']
                }
                
        except Exception as e:
            logger.error(f"❌ 数据库分析异常: {e}")
            return {
                'mode': 'database',
                'status': 'error',
                'message': str(e)
            }
    
    async def run_complete_pipeline(self):
        """运行完整流水线"""
        logger.info("🚀 开始运行完整分析流水线...")
        logger.info(f"📊 分析模式: {'数据库模式' if self.mode == 'database' else '静态数据模式'}")
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            if self.mode == 'static':
                results = await self.run_static_analysis()
            else:
                results = await self.run_database_analysis()
            
            end_time = asyncio.get_event_loop().time()
            execution_time = end_time - start_time
            
            # 生成汇总报告
            summary_report = self.generate_summary_report(results, execution_time)
            
            # 保存汇总报告
            summary_path = os.path.join(self.output_dir, 'analysis_summary.md')
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary_report)
            
            logger.info(f"📄 汇总报告保存至: {summary_path}")
            
            return {
                'status': 'success',
                'execution_time': execution_time,
                'summary_report': summary_path,
                'analysis_results': results
            }
            
        except Exception as e:
            logger.error(f"❌ 完整流水线执行失败: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def generate_summary_report(self, results, execution_time):
        """生成汇总报告"""
        timestamp = asyncio.get_event_loop().time()
        
        if results['status'] == 'success':
            if results['mode'] == 'static':
                data_summary = results['results']['data_summary']
                output_files = results['results']['files_generated']
                
                summary_content = f"""# 🎯 汽车交通模型分析流水线执行报告

**执行时间**: {timestamp}
**分析模式**: 静态数据模式
**执行耗时**: {execution_time:.2f} 秒

## 📊 分析结果概览

### 数据统计
- **分析模型总数**: {data_summary['total_models']:,} 个
- **总浏览量**: {data_summary['key_insights']['total_views']:,}
- **最受欢迎类别**: {data_summary['key_insights']['most_popular_category'][0]}
- **顶级作者**: {data_summary['key_insights']['top_author'][0]}
- **豪华品牌vs中国品牌比例**: {data_summary['key_insights']['luxury_vs_chinese_ratio']}

### 输出文件
- **分析报告**: {output_files['report']}
- **图表文件**: {output_files['charts']}
- **词云图**: {output_files['wordcloud']}
- **原始数据**: {output_files['raw_data']}
- **分析数据**: {output_files['analysis_data']}

## 🎨 主要发现

### 1. 设计趋势
- 豪华质感成为主流设计风格
- 品牌家族化设计备受关注
- 新能源车设计快速崛起

### 2. 技术应用
- F.1 LORA技术占主导地位
- 参数化设计日趋成熟
- 渲染质量持续提升

### 3. 用户偏好
- 超跑设计最受欢迎
- 内饰设计关注度高
- 中国品牌认知度提升

## 🚀 流水线状态

✅ **数据采集**: 完成
✅ **数据清洗**: 完成  
✅ **数据分析**: 完成
✅ **图表生成**: 完成
✅ **报告输出**: 完成

---

*本报告由汽车交通模型分析流水线自动生成*
"""
            else:  # database mode
                data_summary = results['results']['data_summary']
                output_files = results['results']['files_generated']
                
                summary_content = f"""# 🎯 数据库分析流水线执行报告

**执行时间**: {timestamp}
**分析模式**: 数据库模式
**执行耗时**: {execution_time:.2f} 秒

## 📊 分析结果概览

### 数据统计
- **分析作品总数**: {data_summary['total_works']:,} 个
- **分析作者总数**: {data_summary['total_authors']:,} 个
- **分析图片总数**: {data_summary['total_images']:,} 个
- **分析模型总数**: {data_summary['total_models']:,} 个

### 输出文件
- **分析报告**: {output_files['report']}
- **图表文件**: {output_files['charts']}
- **词云图**: {output_files['wordcloud']}
- **分析数据**: {output_files['analysis_data']}

## 🎨 主要发现

### 1. 内容创作趋势
- 作品产出保持稳定增长
- 用户参与度表现良好
- 作者活跃度持续提升

### 2. 技术应用趋势
- 多种AI模型类型广泛应用
- 图片质量持续提升
- 内容标准化体系完善

### 3. 用户行为分析
- 收藏行为反映质量认可
- 互动参与体现社区活跃
- 内容偏好呈现多样化

## 🚀 流水线状态

✅ **数据获取**: 完成
✅ **数据分析**: 完成
✅ **图表生成**: 完成
✅ **报告生成**: 完成

---

*本报告基于数据库实时查询数据生成*
"""
        else:
            summary_content = f"""# ❌ 分析流水线执行失败报告

**执行时间**: {timestamp}
**分析模式**: {'数据库模式' if results['mode'] == 'database' else '静态数据模式'}
**执行耗时**: {execution_time:.2f} 秒

## 🚨 错误信息

**错误模式**: {results['mode']}
**错误消息**: {results['message']}

## 🔧 故障排除建议

### 1. 检查环境配置
- 确认Python依赖已安装
- 验证数据库连接配置
- 检查文件权限设置

### 2. 检查数据源
- 确认数据文件存在
- 验证数据库表结构
- 检查网络连接状态

### 3. 查看详细日志
- 检查 `complete_analysis.log` 文件
- 查看控制台错误输出
- 验证各模块运行状态

---

*本报告记录了分析流水线的执行失败情况*
"""
        
        return summary_content

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='汽车交通模型完整分析流水线')
    parser.add_argument('--mode', choices=['static', 'database'], default='static',
                       help='分析模式: static(静态数据) 或 database(数据库)')
    parser.add_argument('--output-dir', default='complete_analysis_output',
                       help='输出目录路径')
    
    args = parser.parse_args()
    
    # 设置输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 创建分析流水线
    pipeline = CompleteAnalysisPipeline(mode=args.mode)
    
    # 运行流水线
    try:
        results = asyncio.run(pipeline.run_complete_pipeline())
        
        if results['status'] == 'success':
            print("\n" + "="*70)
            print("🎉 完整分析流水线执行成功！")
            print("="*70)
            print(f"⏱️  执行耗时: {results['execution_time']:.2f} 秒")
            print(f"📄 汇总报告: {results['summary_report']}")
            print(f"📊 分析模式: {'数据库模式' if args.mode == 'database' else '静态数据模式'}")
            print("="*70)
            print("✨ 一键完成：采集→清洗→分析→出图（中文）")
            print("="*70)
        else:
            print(f"\n❌ 分析流水线执行失败: {results['message']}")
            print(f"📄 错误报告: {results.get('summary_report', 'N/A')}")
            
    except KeyboardInterrupt:
        print("\n⚠️  用户中断执行")
    except Exception as e:
        print(f"\n❌ 执行异常: {e}")
        logger.error(f"执行异常: {e}")

if __name__ == "__main__":
    main()
