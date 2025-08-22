#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T11 单元测试运行脚本
执行解析/重试/限速/断点核心逻辑测试
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_tests_with_coverage():
    """运行测试并生成覆盖率报告"""
    print("🚀 开始执行T11单元测试...")
    print("=" * 60)
    
    # 检查是否安装了coverage
    try:
        import coverage
        print("✅ coverage模块已安装")
    except ImportError:
        print("❌ coverage模块未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "coverage"], check=True)
        print("✅ coverage模块安装完成")
    
    # 运行测试
    print("\n📋 执行测试...")
    test_result = subprocess.run([
        sys.executable, "-m", "coverage", "run", 
        "--source=scripts", 
        "-m", "pytest", 
        "tests/unit/test_t11_core_logic.py", 
        "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    # 输出测试结果
    print(test_result.stdout)
    if test_result.stderr:
        print("测试错误输出:")
        print(test_result.stderr)
    
    # 生成覆盖率报告
    print("\n📊 生成覆盖率报告...")
    coverage_result = subprocess.run([
        sys.executable, "-m", "coverage", "report", 
        "--show-missing", "--fail-under=70"
    ], capture_output=True, text=True)
    
    print(coverage_result.stdout)
    
    # 生成HTML覆盖率报告
    print("\n🌐 生成HTML覆盖率报告...")
    subprocess.run([
        sys.executable, "-m", "coverage", "html", 
        "--directory=htmlcov"
    ], check=True)
    
    print("✅ HTML覆盖率报告已生成到 htmlcov/ 目录")
    
    return test_result.returncode == 0

def run_specific_test_categories():
    """运行特定测试类别"""
    print("\n🎯 运行特定测试类别...")
    
    test_categories = [
        "TestDataParsingLogic",
        "TestRetryLogic", 
        "TestRateLimitLogic",
        "TestResumeLogic",
        "TestIntegrationLogic",
        "TestEdgeCases",
        "TestPerformanceLogic"
    ]
    
    for category in test_categories:
        print(f"\n--- 运行 {category} ---")
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            f"tests/unit/test_t11_core_logic.py::{category}",
            "-v", "--tb=short"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print(f"错误: {result.stderr}")

def main():
    """主函数"""
    print("🔧 T11 单元测试执行器")
    print("=" * 60)
    print("测试目标：解析/重试/限速/断点核心逻辑")
    print("覆盖率要求：≥70%")
    print("=" * 60)
    
    # 检查测试文件是否存在
    test_file = Path("tests/unit/test_t11_core_logic.py")
    if not test_file.exists():
        print(f"❌ 测试文件不存在: {test_file}")
        return False
    
    print(f"✅ 测试文件已找到: {test_file}")
    
    # 运行完整测试套件
    success = run_tests_with_coverage()
    
    if success:
        print("\n🎉 T11测试执行成功！")
        
        # 可选：运行特定测试类别
        if "--run-categories" in sys.argv:
            run_specific_test_categories()
    else:
        print("\n❌ T11测试执行失败！")
        print("请检查测试输出和错误信息")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试执行异常: {e}")
        sys.exit(1)
