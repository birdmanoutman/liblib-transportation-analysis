#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T4 列表采集器运行脚本
支持命令行参数和环境配置
"""

import os
import sys
import argparse
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.scraping.t4_list_collector import T4ListCollector
from scripts.scraping.t4_config import get_config, validate_config, print_config

def setup_logging(config):
    """设置日志"""
    # 创建日志目录
    log_dir = Path(config['log_file']).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 配置日志
    logging.basicConfig(
        level=getattr(logging, config['log_level']),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config['log_file'], encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='T4 列表采集器 - Liblib 汽车交通数据采集系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 开发环境测试（少量数据）
  python run_t4_collector.py --env development
  
  # 生产环境采集1000个作品
  python run_t4_collector.py --env production --target 1000
  
  # 从指定页开始采集
  python run_t4_collector.py --start-page 10 --max-pages 20
  
  # 显示配置信息
  python run_t4_collector.py --show-config
        """
    )
    
    # 环境配置
    parser.add_argument(
        '--env', 
        choices=['development', 'testing', 'production'],
        default='development',
        help='运行环境 (默认: development)'
    )
    
    # 采集参数
    parser.add_argument(
        '--target', 
        type=int,
        help='目标采集数量'
    )
    
    parser.add_argument(
        '--start-page', 
        type=int,
        help='起始页'
    )
    
    parser.add_argument(
        '--max-pages', 
        type=int,
        help='最大页数限制'
    )
    
    parser.add_argument(
        '--page-size', 
        type=int,
        help='每页大小'
    )
    
    # 速率限制
    parser.add_argument(
        '--rps', 
        type=int,
        help='最大请求频率（RPS）'
    )
    
    parser.add_argument(
        '--concurrent', 
        type=int,
        help='最大并发数'
    )
    
    # 其他选项
    parser.add_argument(
        '--show-config', 
        action='store_true',
        help='显示当前配置信息'
    )
    
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='试运行模式（不实际采集）'
    )
    
    parser.add_argument(
        '--resume', 
        action='store_true',
        help='启用断点续采'
    )
    
    return parser.parse_args()

def update_config_with_args(config, args):
    """根据命令行参数更新配置"""
    if args.target:
        config['target_count'] = args.target
    
    if args.start_page:
        config['start_page'] = args.start_page
    
    if args.max_pages:
        config['max_pages'] = args.max_pages
    
    if args.page_size:
        config['page_size'] = args.page_size
    
    if args.rps:
        config['max_requests_per_second'] = args.rps
    
    if args.concurrent:
        config['max_concurrent'] = args.concurrent
    
    if args.resume:
        config['enable_resume'] = True
    
    return config

async def run_collector(config):
    """运行采集器"""
    print(f"开始T4列表采集任务...")
    print(f"环境: {os.getenv('ENV', 'development')}")
    print(f"目标数量: {config['target_count']}")
    print(f"起始页: {config['start_page']}")
    print(f"最大页数: {config['max_pages'] or '无限制'}")
    print(f"每页大小: {config['page_size']}")
    print(f"速率限制: {config['max_requests_per_second']} RPS")
    print(f"并发数: {config['max_concurrent']}")
    print("=" * 50)
    
    try:
        # 创建采集器
        collector = T4ListCollector(config)
        
        # 运行采集任务
        start_time = datetime.now()
        result = await collector.run_collection(
            start_page=config['start_page'],
            max_pages=config['max_pages'],
            target_count=config['target_count']
        )
        end_time = datetime.now()
        
        # 输出结果
        print("\n采集任务完成！")
        print("=" * 50)
        print(f"状态: {result['status']}")
        print(f"总作品数: {result['total_works']}")
        print(f"处理页数: {result['pages_processed']}")
        print(f"起始页: {result['start_page']}")
        print(f"结束页: {result['end_page']}")
        print(f"已采集slug: {result['collected_slugs']}")
        print(f"运行时间: {end_time - start_time}")
        
        return result
        
    except KeyboardInterrupt:
        print("\n用户中断采集任务")
        return {'status': 'interrupted'}
    except Exception as e:
        print(f"\n采集任务异常: {e}")
        logging.error(f"采集任务异常: {e}", exc_info=True)
        return {'status': 'error', 'error': str(e)}

def main():
    """主函数"""
    try:
        # 解析命令行参数
        args = parse_arguments()
        
        # 设置环境变量
        os.environ['ENV'] = args.env
        
        # 加载配置
        config = get_config(args.env)
        
        # 根据命令行参数更新配置
        config = update_config_with_args(config, args)
        
        # 显示配置信息
        if args.show_config:
            print_config(config)
            return
        
        # 验证配置
        if not validate_config(config):
            print("配置验证失败！")
            return 1
        
        # 设置日志
        setup_logging(config)
        
        # 试运行模式
        if args.dry_run:
            print("试运行模式 - 显示配置信息:")
            print_config(config)
            print("\n配置验证通过，可以开始采集！")
            return 0
        
        # 运行采集器
        result = asyncio.run(run_collector(config))
        
        if result['status'] == 'success':
            return 0
        else:
            return 1
            
    except Exception as e:
        print(f"运行异常: {e}")
        logging.error(f"运行异常: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
