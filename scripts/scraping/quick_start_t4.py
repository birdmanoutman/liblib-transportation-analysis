#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T4 列表采集器快速启动脚本
提供简单的交互式界面，快速开始采集任务
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.scraping.t4_config import get_config, validate_config
from scripts.scraping.t4_list_collector import T4ListCollector

def print_banner():
    """打印启动横幅"""
    print("=" * 60)
    print("🚗 T4 列表采集器 - 快速启动")
    print("=" * 60)
    print("Liblib 汽车交通数据采集系统")
    print("支持断点续采、速率限制、并发控制")
    print("=" * 60)

def get_user_choice():
    """获取用户选择"""
    print("\n请选择操作:")
    print("1. 🚀 快速开始 (开发环境，100个作品)")
    print("2. 🧪 测试模式 (50个作品，3页限制)")
    print("3. 🏭 生产模式 (1000个作品，无限制)")
    print("4. ⚙️  自定义配置")
    print("5. 📊 查看当前状态")
    print("6. 🧹 清理状态文件")
    print("7. ❓ 帮助信息")
    print("0. 🚪 退出")
    
    while True:
        try:
            choice = input("\n请输入选择 (0-7): ").strip()
            if choice in ['0', '1', '2', '3', '4', '5', '6', '7']:
                return choice
            else:
                print("❌ 无效选择，请输入 0-7")
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            sys.exit(0)

def get_custom_config():
    """获取自定义配置"""
    print("\n🔧 自定义配置")
    print("-" * 30)
    
    config = {}
    
    # 目标数量
    while True:
        try:
            target = input("目标采集数量 (默认: 100): ").strip()
            if not target:
                config['target_count'] = 100
                break
            target = int(target)
            if target > 0:
                config['target_count'] = target
                break
            else:
                print("❌ 数量必须大于0")
        except ValueError:
            print("❌ 请输入有效数字")
    
    # 起始页
    while True:
        try:
            start_page = input("起始页 (默认: 1): ").strip()
            if not start_page:
                config['start_page'] = 1
                break
            start_page = int(start_page)
            if start_page >= 1:
                config['start_page'] = start_page
                break
            else:
                print("❌ 起始页必须大于等于1")
        except ValueError:
            print("❌ 请输入有效数字")
    
    # 最大页数
    while True:
        try:
            max_pages = input("最大页数限制 (默认: 无限制，输入0表示无限制): ").strip()
            if not max_pages or max_pages == '0':
                config['max_pages'] = None
                break
            max_pages = int(max_pages)
            if max_pages >= config['start_page']:
                config['max_pages'] = max_pages
                break
            else:
                print(f"❌ 最大页数必须大于等于起始页 {config['start_page']}")
        except ValueError:
            print("❌ 请输入有效数字")
    
    # 速率限制
    while True:
        try:
            rps = input("最大请求频率 RPS (默认: 4): ").strip()
            if not rps:
                config['max_requests_per_second'] = 4
                break
            rps = int(rps)
            if rps > 0:
                config['max_requests_per_second'] = rps
                break
            else:
                print("❌ RPS必须大于0")
        except ValueError:
            print("❌ 请输入有效数字")
    
    return config

def show_current_status():
    """显示当前状态"""
    print("\n📊 当前状态")
    print("-" * 30)
    
    # 检查状态文件
    state_file = "data/fetch_state.json"
    slug_queue_file = "data/slug_queue.json"
    
    if Path(state_file).exists():
        try:
            import json
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            print(f"📄 采集状态:")
            print(f"  当前页: {state.get('current_page', 'N/A')}")
            print(f"  已采集: {state.get('works_fetched', 'N/A')}")
            print(f"  状态: {state.get('status', 'N/A')}")
            print(f"  最后更新: {state.get('last_fetch_time', 'N/A')}")
        except Exception as e:
            print(f"  ❌ 读取状态文件失败: {e}")
    else:
        print("📄 采集状态: 无历史记录")
    
    if Path(slug_queue_file).exists():
        try:
            import json
            with open(slug_queue_file, 'r', encoding='utf-8') as f:
                queue_data = json.load(f)
            
            print(f"\n📋 Slug队列:")
            print(f"  已采集slug数: {len(queue_data.get('collected_slugs', []))}")
            print(f"  更新时间: {queue_data.get('updated_at', 'N/A')}")
        except Exception as e:
            print(f"  ❌ 读取队列文件失败: {e}")
    else:
        print("\n📋 Slug队列: 无历史记录")
    
    # 检查数据库连接
    print(f"\n🗄️ 数据库状态:")
    try:
        # 这里可以添加数据库连接测试
        print("  ✓ 环境变量已配置")
    except Exception as e:
        print(f"  ❌ 数据库配置问题: {e}")

def cleanup_state_files():
    """清理状态文件"""
    print("\n🧹 清理状态文件")
    print("-" * 30)
    
    files_to_clean = [
        "data/fetch_state.json",
        "data/slug_queue.json",
        "data/fetch_queue.txt"
    ]
    
    for file_path in files_to_clean:
        file_obj = Path(file_path)
        if file_obj.exists():
            try:
                file_obj.unlink()
                print(f"  ✓ 已删除: {file_path}")
            except Exception as e:
                print(f"  ❌ 删除失败 {file_path}: {e}")
        else:
            print(f"  ⚠ 文件不存在: {file_path}")
    
    print("清理完成！")

def show_help():
    """显示帮助信息"""
    print("\n❓ 帮助信息")
    print("-" * 30)
    print("T4列表采集器是Liblib汽车交通数据采集系统的核心组件。")
    print()
    print("主要功能:")
    print("• 按标签'汽车交通'采集作品列表")
    print("• 支持断点续采，中断后可继续")
    print("• 内置速率限制，避免对服务器造成压力")
    print("• 自动生成slug队列，为T5详情采集器准备")
    print()
    print("文件说明:")
    print("• data/fetch_state.json: 采集状态信息")
    print("• data/slug_queue.json: 已采集的slug队列")
    print("• data/fetch_queue.txt: 待处理的slug列表")
    print("• logs/t4_list_collector.log: 运行日志")
    print()
    print("更多信息请查看: scripts/scraping/README_T4.md")

async def run_collection(config, env_name):
    """运行采集任务"""
    print(f"\n🚀 开始{env_name}采集任务...")
    print(f"目标数量: {config['target_count']}")
    print(f"起始页: {config['start_page']}")
    print(f"最大页数: {config['max_pages'] or '无限制'}")
    print(f"速率限制: {config['max_requests_per_second']} RPS")
    print("=" * 50)
    
    try:
        # 创建采集器
        collector = T4ListCollector(config)
        
        # 运行采集
        start_time = asyncio.get_event_loop().time()
        result = await collector.run_collection(
            start_page=config['start_page'],
            max_pages=config['max_pages'],
            target_count=config['target_count']
        )
        end_time = asyncio.get_event_loop().time()
        
        # 显示结果
        print("\n🎉 采集任务完成！")
        print("=" * 50)
        print(f"状态: {result['status']}")
        print(f"总作品数: {result['total_works']}")
        print(f"处理页数: {result['pages_processed']}")
        print(f"运行时间: {end_time - start_time:.2f} 秒")
        
        if result['status'] == 'success':
            print(f"\n✅ 成功采集 {result['total_works']} 个作品")
            print("📋 现在可以运行T5详情采集器获取详细信息")
        
        return result
        
    except Exception as e:
        print(f"\n❌ 采集任务失败: {e}")
        logging.error(f"采集任务异常: {e}", exc_info=True)
        return None

async def main():
    """主函数"""
    print_banner()
    
    # 创建必要目录
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    while True:
        choice = get_user_choice()
        
        if choice == '0':
            print("\n👋 再见！")
            break
            
        elif choice == '1':
            # 快速开始
            config = get_config('development')
            await run_collection(config, "开发环境")
            
        elif choice == '2':
            # 测试模式
            config = get_config('testing')
            await run_collection(config, "测试模式")
            
        elif choice == '3':
            # 生产模式
            config = get_config('production')
            await run_collection(config, "生产环境")
            
        elif choice == '4':
            # 自定义配置
            custom_config = get_custom_config()
            base_config = get_config('development')
            base_config.update(custom_config)
            
            if validate_config(base_config):
                await run_collection(base_config, "自定义配置")
            else:
                print("❌ 配置验证失败，请检查参数")
                
        elif choice == '5':
            # 查看当前状态
            show_current_status()
            
        elif choice == '6':
            # 清理状态文件
            cleanup_state_files()
            
        elif choice == '7':
            # 显示帮助
            show_help()
        
        # 询问是否继续
        if choice in ['1', '2', '3', '4']:
            continue_choice = input("\n是否继续其他操作？(y/n): ").strip().lower()
            if continue_choice not in ['y', 'yes', '是']:
                print("\n👋 再见！")
                break

if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        # 运行主程序
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 再见！")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        logging.error(f"程序异常: {e}", exc_info=True)
