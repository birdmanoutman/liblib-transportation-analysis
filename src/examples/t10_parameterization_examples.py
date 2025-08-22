#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T10工单参数化配置使用示例
展示如何使用新的命令行参数和配置文件功能

功能演示：
1. 标签切换（无需改码）
2. 排序方式配置
3. 页范围和并发控制
4. 存储路径自定义
5. 配置模板创建
"""

import sys
import os
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n🚀 {description}")
    print(f"命令: {cmd}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        if result.stdout:
            print("输出:")
            print(result.stdout)
        if result.stderr:
            print("错误:")
            print(result.stderr)
        print(f"退出码: {result.returncode}")
    except Exception as e:
        print(f"执行失败: {e}")
    
    print("-" * 60)

def main():
    """主函数 - 演示各种参数化配置"""
    print("🎯 T10工单参数化配置功能演示")
    print("=" * 80)
    
    # 切换到项目根目录
    os.chdir(project_root)
    
    # 1. 显示当前配置
    print("\n📋 1. 显示当前配置")
    run_command(
        "python src/liblib_car_analyzer.py --show-config",
        "显示当前配置摘要"
    )
    
    # 2. 创建配置模板
    print("\n📝 2. 创建配置模板")
    run_command(
        "python src/liblib_car_analyzer.py --create-config",
        "创建配置模板文件"
    )
    
    # 3. 标签切换示例（无需改码）
    print("\n🏷️  3. 标签切换示例（无需改码）")
    
    # 3.1 切换到摩托车标签
    run_command(
        "python src/liblib_car_analyzer.py --tags '摩托车,电动车,自行车' --show-config",
        "切换到摩托车相关标签"
    )
    
    # 3.2 切换到飞机标签
    run_command(
        "python src/liblib_car_analyzer.py --tags '飞机,客机,战斗机,直升机' --show-config",
        "切换到飞机相关标签"
    )
    
    # 3.3 切换到船舶标签
    run_command(
        "python src/liblib_car_analyzer.py --tags '船,轮船,游艇,帆船' --show-config",
        "切换到船舶相关标签"
    )
    
    # 4. 排序方式配置
    print("\n📊 4. 排序方式配置")
    
    # 4.1 按点赞数排序
    run_command(
        "python src/liblib_car_analyzer.py --sort-by likes --sort-order desc --show-config",
        "按点赞数降序排序"
    )
    
    # 4.2 按创建时间排序
    run_command(
        "python src/liblib_car_analyzer.py --sort-by created_at --sort-order asc --show-config",
        "按创建时间升序排序"
    )
    
    # 5. 页范围和并发控制
    print("\n📄 5. 页范围和并发控制")
    
    # 5.1 限制页数和并发
    run_command(
        "python src/liblib_car_analyzer.py --max-pages 5 --max-workers 2 --concurrent-downloads 3 --show-config",
        "限制最大页数为5，工作线程为2，并发下载为3"
    )
    
    # 5.2 高并发配置
    run_command(
        "python src/liblib_car_analyzer.py --max-workers 8 --concurrent-downloads 10 --show-config",
        "高并发配置：8个工作线程，10个并发下载"
    )
    
    # 6. 存储路径自定义
    print("\n📁 6. 存储路径自定义")
    
    # 6.1 自定义输出目录
    run_command(
        "python src/liblib_car_analyzer.py --output-dir './custom_output' --images-dir 'custom_images' --show-config",
        "自定义输出目录和图片目录"
    )
    
    # 6.2 使用配置文件
    run_command(
        "python src/liblib_car_analyzer.py --config config/default.json --show-config",
        "使用默认配置文件"
    )
    
    # 7. 日志级别控制
    print("\n📝 7. 日志级别控制")
    
    # 7.1 详细日志
    run_command(
        "python src/liblib_car_analyzer.py --verbose --show-config",
        "启用详细日志输出"
    )
    
    # 7.2 警告级别日志
    run_command(
        "python src/liblib_car_analyzer.py --log-level WARNING --show-config",
        "设置日志级别为警告"
    )
    
    # 8. 组合配置示例
    print("\n🔧 8. 组合配置示例")
    
    # 8.1 摩托车高并发采集
    run_command(
        "python src/liblib_car_analyzer.py --tags '摩托车,电动车' --max-workers 6 --concurrent-downloads 8 --output-dir './motorcycle_analysis' --show-config",
        "摩托车高并发采集配置"
    )
    
    # 8.2 飞机按时间排序采集
    run_command(
        "python src/liblib_car_analyzer.py --tags '飞机,客机' --sort-by created_at --sort-order asc --max-pages 3 --show-config",
        "飞机按创建时间倒序采集，限制3页"
    )
    
    print("\n✅ T10工单参数化配置功能演示完成！")
    print("\n💡 使用提示:")
    print("1. 使用 --show-config 查看当前配置")
    print("2. 使用 --create-config 创建配置模板")
    print("3. 使用 --help 查看所有可用参数")
    print("4. 标签切换无需修改代码，直接使用 --tags 参数")
    print("5. 所有配置都可以通过命令行参数覆盖")

if __name__ == "__main__":
    main()
