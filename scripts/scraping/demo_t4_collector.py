#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T4 列表采集器演示脚本
展示基本功能和使用方法
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.scraping.t4_config import get_config, print_config
from scripts.scraping.t4_list_collector import T4ListCollector

def setup_demo_environment():
    """设置演示环境"""
    print("🚀 设置T4列表采集器演示环境...")
    
    # 创建必要的目录
    directories = ['data', 'logs', 'data/raw', 'data/processed']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ 创建目录: {directory}")
    
    # 设置环境变量为开发模式
    os.environ['ENV'] = 'development'
    
    print("演示环境设置完成！\n")

async def demo_config_management():
    """演示配置管理功能"""
    print("📋 演示配置管理功能...")
    
    # 显示不同环境的配置
    for env in ['development', 'testing', 'production']:
        print(f"\n{env.upper()} 环境配置:")
        config = get_config(env)
        print(f"  目标数量: {config['target_count']}")
        print(f"  最大页数: {config['max_pages'] or '无限制'}")
        print(f"  速率限制: {config['max_requests_per_second']} RPS")
        print(f"  并发数: {config['max_concurrent']}")
    
    print("\n配置管理演示完成！\n")

async def demo_collector_initialization():
    """演示采集器初始化"""
    print("🔧 演示采集器初始化...")
    
    try:
        # 创建采集器实例
        collector = T4ListCollector()
        print("  ✓ 采集器创建成功")
        
        # 显示配置信息
        print(f"  ✓ API基础URL: {collector.api_base}")
        print(f"  ✓ 目标标签: {collector.config['target_tag']}")
        print(f"  ✓ 排序方式: {collector.config['sort_type']}")
        print(f"  ✓ 速率限制: {collector.config['max_requests_per_second']} RPS")
        
        return collector
        
    except Exception as e:
        print(f"  ✗ 采集器初始化失败: {e}")
        return None

async def demo_small_collection(collector, target_count=10):
    """演示小规模采集"""
    print(f"📥 演示小规模采集 (目标: {target_count}个作品)...")
    
    try:
        # 运行采集任务
        start_time = datetime.now()
        result = await collector.run_collection(
            start_page=1,
            max_pages=2,  # 限制页数
            target_count=target_count
        )
        end_time = datetime.now()
        
        # 显示结果
        print("\n采集结果:")
        print("=" * 40)
        print(f"状态: {result['status']}")
        print(f"总作品数: {result['total_works']}")
        print(f"处理页数: {result['pages_processed']}")
        print(f"运行时间: {end_time - start_time}")
        
        return result
        
    except Exception as e:
        print(f"  ✗ 采集演示失败: {e}")
        return None

async def demo_state_persistence():
    """演示状态持久化"""
    print("💾 演示状态持久化...")
    
    # 检查状态文件
    state_file = "data/fetch_state.json"
    slug_queue_file = "data/slug_queue.json"
    
    if Path(state_file).exists():
        print(f"  ✓ 状态文件存在: {state_file}")
        # 读取并显示状态
        import json
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
            print(f"    当前页: {state.get('current_page', 'N/A')}")
            print(f"    已采集: {state.get('works_fetched', 'N/A')}")
            print(f"    状态: {state.get('status', 'N/A')}")
    else:
        print(f"  ⚠ 状态文件不存在: {state_file}")
    
    if Path(slug_queue_file).exists():
        print(f"  ✓ Slug队列文件存在: {slug_queue_file}")
        # 读取并显示队列信息
        import json
        with open(slug_queue_file, 'r', encoding='utf-8') as f:
            queue_data = json.load(f)
            print(f"    已采集slug数: {len(queue_data.get('collected_slugs', []))}")
            print(f"    更新时间: {queue_data.get('updated_at', 'N/A')}")
    else:
        print(f"  ⚠ Slug队列文件不存在: {slug_queue_file}")
    
    print("状态持久化演示完成！\n")

async def demo_error_handling():
    """演示错误处理"""
    print("⚠️ 演示错误处理...")
    
    try:
        # 尝试创建无效配置的采集器
        invalid_config = {
            'target_count': -1,  # 无效值
            'max_requests_per_second': 0,  # 无效值
            'max_concurrent': 0  # 无效值
        }
        
        # 这应该会抛出异常
        collector = T4ListCollector(invalid_config)
        
    except ValueError as e:
        print(f"  ✓ 配置验证生效: {e}")
    except Exception as e:
        print(f"  ✓ 错误处理生效: {e}")
    
    print("错误处理演示完成！\n")

async def demo_resume_functionality():
    """演示断点续采功能"""
    print("🔄 演示断点续采功能...")
    
    # 检查是否有历史状态
    state_file = "data/fetch_state.json"
    if Path(state_file).exists():
        print("  ✓ 发现历史状态文件，可以启用断点续采")
        
        # 读取状态
        import json
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        if state.get('status') == 'PAUSED':
            print("  ✓ 检测到暂停状态，可以从断点继续")
            print(f"    断点页: {state.get('current_page', 'N/A')}")
            print(f"    已采集: {state.get('works_fetched', 'N/A')}")
        elif state.get('status') == 'SUCCESS':
            print("  ✓ 检测到完成状态，可以开始新的采集任务")
        else:
            print(f"  ✓ 当前状态: {state.get('status', 'N/A')}")
    else:
        print("  ⚠ 无历史状态，将从头开始采集")
    
    print("断点续采演示完成！\n")

def show_next_steps():
    """显示后续步骤"""
    print("🎯 后续步骤建议:")
    print("=" * 50)
    print("1. 运行完整测试:")
    print("   python scripts/scraping/test_t4_collector.py")
    print()
    print("2. 开发环境小规模采集:")
    print("   python scripts/scraping/run_t4_collector.py --env development")
    print()
    print("3. 生产环境采集:")
    print("   python scripts/scraping/run_t4_collector.py --env production")
    print()
    print("4. 查看详细文档:")
    print("   cat scripts/scraping/README_T4.md")
    print()
    print("5. 准备T5详情采集器:")
    print("   T4完成后，T5将读取slug队列进行详情采集")
    print()

async def main():
    """主演示函数"""
    print("🎬 T4 列表采集器功能演示")
    print("=" * 50)
    print("本演示将展示T4采集器的核心功能和使用方法")
    print()
    
    try:
        # 设置演示环境
        setup_demo_environment()
        
        # 演示配置管理
        await demo_config_management()
        
        # 演示采集器初始化
        collector = await demo_collector_initialization()
        if not collector:
            print("❌ 采集器初始化失败，演示终止")
            return
        
        # 演示小规模采集
        result = await demo_small_collection(collector, target_count=5)
        if not result:
            print("❌ 采集演示失败，演示终止")
            return
        
        # 演示状态持久化
        await demo_state_persistence()
        
        # 演示错误处理
        await demo_error_handling()
        
        # 演示断点续采
        await demo_resume_functionality()
        
        # 显示后续步骤
        show_next_steps()
        
        print("🎉 T4列表采集器演示完成！")
        print("现在您可以开始使用T4采集器进行实际的数据采集工作。")
        
    except KeyboardInterrupt:
        print("\n⏹️ 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出现异常: {e}")
        logging.error(f"演示异常: {e}", exc_info=True)

if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 运行演示
    asyncio.run(main())
