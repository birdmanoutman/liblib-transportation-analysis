#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T8 断点续采与失败补偿模块运行脚本
演示断点续采、失败重试、完整性验证等功能
"""

import os
import sys
import asyncio
import argparse
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.scraping.t8_resume_and_retry import T8ResumeAndRetry
from scripts.scraping.t8_config import get_config, validate_config, print_config

def setup_logging(log_level: str = 'INFO', log_file: str = 'logs/t8_resume_retry.log'):
    """设置日志"""
    # 创建日志目录
    Path("logs").mkdir(exist_ok=True)
    
    # 配置日志
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

async def demo_resume_points(t8: T8ResumeAndRetry):
    """演示断点续采点功能"""
    print("\n=== 断点续采点功能演示 ===")
    
    # 创建列表采集断点续采点
    list_point_id = t8.create_resume_point(
        task_type="LIST_COLLECTION",
        current_page=5,
        last_cursor="cursor_123",
        total_processed=120,
        metadata={"tag": "汽车交通", "sort": "latest"}
    )
    print(f"创建列表采集断点续采点：{list_point_id}")
    
    # 创建详情采集断点续采点
    detail_point_id = t8.create_resume_point(
        task_type="DETAIL_COLLECTION",
        current_page=1,
        last_slug="car-model-001",
        total_processed=50,
        metadata={"batch_size": 100}
    )
    print(f"创建详情采集断点续采点：{detail_point_id}")
    
    # 获取断点续采点
    list_point = t8.get_resume_point("LIST_COLLECTION")
    if list_point:
        print(f"列表采集断点续采点：第{list_point.current_page}页，已处理{list_point.total_processed}项")
    
    detail_point = t8.get_resume_point("DETAIL_COLLECTION")
    if detail_point:
        print(f"详情采集断点续采点：第{detail_point.current_page}页，最后slug：{detail_point.last_slug}")

async def demo_failed_tasks(t8: T8ResumeAndRetry):
    """演示失败任务功能"""
    print("\n=== 失败任务功能演示 ===")
    
    # 添加不同类型的失败任务
    list_task_id = t8.add_failed_task(
        task_type="LIST_COLLECTION",
        target="page_5",
        error_message="API请求超时",
        max_retries=3,
        retry_delay=60
    )
    print(f"添加列表采集失败任务：{list_task_id}")
    
    detail_task_id = t8.add_failed_task(
        task_type="DETAIL_COLLECTION",
        target="car-model-002",
        error_message="数据解析失败",
        max_retries=5,
        retry_delay=120
    )
    print(f"添加详情采集失败任务：{detail_task_id}")
    
    image_task_id = t8.add_failed_task(
        task_type="IMAGE_DOWNLOAD",
        target="https://example.com/image.jpg",
        error_message="网络连接失败",
        max_retries=3,
        retry_delay=180
    )
    print(f"添加图片下载失败任务：{image_task_id}")
    
    # 获取可重试任务
    retryable_tasks = t8.get_retryable_tasks()
    print(f"发现{len(retryable_tasks)}个可重试任务")
    
    for task in retryable_tasks:
        print(f"  - {task.task_type}: {task.target} (重试{task.retry_count}/{task.max_retries})")

async def demo_integrity_validation(t8: T8ResumeAndRetry):
    """演示完整性验证功能"""
    print("\n=== 完整性验证功能演示 ===")
    
    # 创建模拟的运行状态
    run_id = "demo_run_001"
    
    # 验证完整性
    try:
        validation_result = await t8.validate_integrity(run_id)
        print(f"完整性验证结果：{validation_result}")
        
        if validation_result.get('valid'):
            print("✅ 完整性验证通过")
        else:
            print("❌ 完整性验证失败")
            for error in validation_result.get('errors', []):
                print(f"  - 错误：{error}")
        
        for warning in validation_result.get('warnings', []):
            print(f"  - 警告：{warning}")
            
    except Exception as e:
        print(f"完整性验证异常：{e}")

async def demo_service_lifecycle(t8: T8ResumeAndRetry):
    """演示服务生命周期"""
    print("\n=== 服务生命周期演示 ===")
    
    # 启动服务
    print("启动T8服务...")
    t8.start_service()
    
    # 等待一段时间让重试服务运行
    print("等待重试服务运行...")
    await asyncio.sleep(5)
    
    # 停止服务
    print("停止T8服务...")
    t8.stop_service()
    
    print("服务生命周期演示完成")

async def run_demo(config: dict):
    """运行完整演示"""
    print("T8 断点续采与失败补偿模块演示")
    print("=" * 50)
    
    # 创建T8实例
    t8 = T8ResumeAndRetry(config)
    
    try:
        # 演示各个功能
        await demo_resume_points(t8)
        await demo_failed_tasks(t8)
        await demo_integrity_validation(t8)
        await demo_service_lifecycle(t8)
        
        print("\n✅ 所有演示完成")
        
    except Exception as e:
        print(f"\n❌ 演示过程中发生异常：{e}")
        raise

async def run_integration_test(config: dict):
    """运行集成测试"""
    print("T8 集成测试")
    print("=" * 50)
    
    t8 = T8ResumeAndRetry(config)
    
    try:
        # 启动服务
        t8.start_service()
        
        # 模拟真实场景
        print("模拟真实采集场景...")
        
        # 创建多个断点续采点
        for i in range(1, 6):
            t8.create_resume_point(
                task_type="LIST_COLLECTION",
                current_page=i,
                total_processed=i * 24,
                metadata={"tag": "汽车交通", "batch": f"batch_{i}"}
            )
        
        # 添加多个失败任务
        for i in range(1, 11):
            t8.add_failed_task(
                task_type="DETAIL_COLLECTION",
                target=f"car-model-{i:03d}",
                error_message=f"模拟错误 {i}",
                max_retries=3,
                retry_delay=60
            )
        
        # 等待重试服务处理
        print("等待重试服务处理失败任务...")
        await asyncio.sleep(10)
        
        # 检查状态
        resume_points = len([p for p in t8.state_manager.resume_points.values() 
                           if p.task_type == "LIST_COLLECTION"])
        failed_tasks = len(t8.state_manager.failed_tasks)
        retryable_tasks = len(t8.get_retryable_tasks())
        
        print(f"集成测试结果：")
        print(f"  - 断点续采点：{resume_points}个")
        print(f"  - 失败任务：{failed_tasks}个")
        print(f"  - 可重试任务：{retryable_tasks}个")
        
        # 停止服务
        t8.stop_service()
        
        print("✅ 集成测试完成")
        
    except Exception as e:
        print(f"❌ 集成测试异常：{e}")
        t8.stop_service()
        raise

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='T8 断点续采与失败补偿模块')
    parser.add_argument('--env', default='development', 
                       choices=['development', 'testing', 'production'],
                       help='运行环境')
    parser.add_argument('--mode', default='demo', 
                       choices=['demo', 'test', 'config'],
                       help='运行模式')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='日志级别')
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.log_level)
    
    # 获取配置
    config = get_config(args.env)
    
    if args.mode == 'config':
        # 显示配置
        print_config(config)
        if validate_config(config):
            print("✅ 配置验证通过")
        else:
            print("❌ 配置验证失败")
        return
    
    # 验证配置
    if not validate_config(config):
        print("❌ 配置验证失败，退出")
        sys.exit(1)
    
    try:
        if args.mode == 'demo':
            # 运行演示
            asyncio.run(run_demo(config))
        elif args.mode == 'test':
            # 运行集成测试
            asyncio.run(run_integration_test(config))
            
    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        print(f"运行异常：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
