#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行器主文件
统一运行所有测试套件
"""

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def run_unit_tests():
    """运行单元测试"""
    print("🧪 开始运行单元测试")
    print("=" * 50)
    
    try:
        # 导入并运行单元测试
        from tests.unit.test_simple_analysis import run_all_tests as run_simple_analysis
        from tests.unit.test_t11_core_logic import run_all_tests as run_t11_core_logic
        from tests.unit.test_t8_resume_retry import run_all_tests as run_t8_resume_retry
        from tests.unit.test_liblib_analyzer import run_all_tests as run_liblib_analyzer
        
        test_functions = [
            ("简单分析测试", run_simple_analysis),
            ("T11核心逻辑测试", run_t11_core_logic),
            ("T8恢复重试测试", run_t8_resume_retry),
            ("Liblib分析器测试", run_liblib_analyzer)
        ]
        
        total_passed = 0
        total_failed = 0
        
        for test_name, test_func in test_functions:
            print(f"\n🔄 运行 {test_name}...")
            try:
                passed, failed = test_func()
                total_passed += passed
                total_failed += failed
                print(f"✅ {test_name} 完成: 通过 {passed}, 失败 {failed}")
            except Exception as e:
                print(f"❌ {test_name} 执行异常: {e}")
                total_failed += 1
        
        print(f"\n📊 单元测试汇总: 通过 {total_passed}, 失败 {total_failed}")
        return total_passed, total_failed
        
    except Exception as e:
        print(f"❌ 单元测试运行失败: {e}")
        return 0, 1

def run_integration_tests():
    """运行集成测试"""
    print("\n🔗 开始运行集成测试")
    print("=" * 50)
    
    try:
        # 导入并运行集成测试
        from tests.integration.test_data_collection import run_all_tests as run_data_collection
        from tests.integration.test_api_collection import run_all_api_tests as run_api_tests
        from tests.integration.test_performance import run_performance_benchmark as run_performance
        
        test_functions = [
            ("数据采集集成测试", run_data_collection),
            ("API采集集成测试", run_api_tests),
            ("性能基准测试", run_performance)
        ]
        
        total_passed = 0
        total_failed = 0
        
        for test_name, test_func in test_functions:
            print(f"\n🔄 运行 {test_name}...")
            try:
                passed, failed = test_func()
                total_passed += passed
                total_failed += failed
                print(f"✅ {test_name} 完成: 通过 {passed}, 失败 {failed}")
            except Exception as e:
                print(f"❌ {test_name} 执行异常: {e}")
                total_failed += 1
        
        print(f"\n📊 集成测试汇总: 通过 {total_passed}, 失败 {total_failed}")
        return total_passed, total_failed
        
    except Exception as e:
        print(f"❌ 集成测试运行失败: {e}")
        return 0, 1

def run_specific_test(test_path):
    """运行特定测试文件"""
    print(f"🎯 运行特定测试: {test_path}")
    print("=" * 50)
    
    try:
        # 动态导入测试模块
        test_module = __import__(test_path.replace('/', '.').replace('.py', ''))
        
        # 查找测试运行函数
        test_functions = []
        for attr_name in dir(test_module):
            if attr_name.startswith('run_all') or attr_name.startswith('test_'):
                attr = getattr(test_module, attr_name)
                if callable(attr):
                    test_functions.append((attr_name, attr))
        
        if not test_functions:
            print(f"⚠️  在 {test_path} 中未找到测试函数")
            return 0, 1
        
        total_passed = 0
        total_failed = 0
        
        for test_name, test_func in test_functions:
            print(f"\n🔄 运行 {test_name}...")
            try:
                if test_name.startswith('run_all'):
                    # 主测试函数
                    result = test_func()
                    if isinstance(result, tuple) and len(result) == 2:
                        passed, failed = result
                    else:
                        passed, failed = (1 if result else 0, 0 if result else 1)
                else:
                    # 单个测试函数
                    result = test_func()
                    passed, failed = (1 if result else 0, 0 if result else 1)
                
                total_passed += passed
                total_failed += failed
                print(f"✅ {test_name} 完成: 通过 {passed}, 失败 {failed}")
                
            except Exception as e:
                print(f"❌ {test_name} 执行异常: {e}")
                total_failed += 1
        
        print(f"\n📊 特定测试汇总: 通过 {total_passed}, 失败 {total_failed}")
        return total_passed, total_failed
        
    except Exception as e:
        print(f"❌ 特定测试运行失败: {e}")
        return 0, 1

def run_pytest_tests():
    """使用pytest运行测试"""
    print("\n🐍 使用pytest运行测试")
    print("=" * 50)
    
    try:
        import subprocess
        
        # 构建pytest命令
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--durations=10"
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        
        # 运行pytest
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 输出结果
        if result.stdout:
            print("标准输出:")
            print(result.stdout)
        
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        print(f"返回码: {result.returncode}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ pytest运行失败: {e}")
        return False

def generate_test_report(total_passed, total_failed, test_type="所有测试"):
    """生成测试报告"""
    print(f"\n📋 {test_type} 报告")
    print("=" * 50)
    
    total_tests = total_passed + total_failed
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📊 测试统计:")
    print(f"   总测试数: {total_tests}")
    print(f"   通过: {total_passed}")
    print(f"   失败: {total_failed}")
    print(f"   成功率: {success_rate:.1f}%")
    
    # 生成状态
    if success_rate >= 90:
        status = "🟢 优秀"
    elif success_rate >= 80:
        status = "🟡 良好"
    elif success_rate >= 70:
        status = "🟠 一般"
    else:
        status = "🔴 需要改进"
    
    print(f"   状态: {status}")
    
    # 保存报告到文件
    report_dir = project_root / "test_output"
    report_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_dir / f"test_report_{timestamp}.txt"
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"{test_type} 报告\n")
            f.write("=" * 50 + "\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总测试数: {total_tests}\n")
            f.write(f"通过: {total_passed}\n")
            f.write(f"失败: {total_failed}\n")
            f.write(f"成功率: {success_rate:.1f}%\n")
            f.write(f"状态: {status}\n")
        
        print(f"📄 报告已保存到: {report_file}")
        
    except Exception as e:
        print(f"⚠️  报告保存失败: {e}")
    
    return success_rate >= 70  # 70%以上认为通过

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="测试运行器")
    parser.add_argument("--type", choices=["unit", "integration", "all", "pytest"], 
                       default="all", help="测试类型")
    parser.add_argument("--test", help="运行特定测试文件")
    parser.add_argument("--report", action="store_true", help="生成详细报告")
    
    args = parser.parse_args()
    
    print("🚀 Liblib Transportation Analysis 测试运行器")
    print("=" * 60)
    print(f"项目根目录: {project_root}")
    print(f"测试类型: {args.type}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    try:
        if args.test:
            # 运行特定测试
            passed, failed = run_specific_test(args.test)
            test_type = f"特定测试 ({args.test})"
        elif args.type == "unit":
            # 运行单元测试
            passed, failed = run_unit_tests()
            test_type = "单元测试"
        elif args.type == "integration":
            # 运行集成测试
            passed, failed = run_integration_tests()
            test_type = "集成测试"
        elif args.type == "pytest":
            # 使用pytest
            success = run_pytest_tests()
            passed, failed = (1 if success else 0, 0 if success else 1)
            test_type = "Pytest测试"
        else:
            # 运行所有测试
            print("\n🔄 运行所有测试套件...")
            
            # 单元测试
            unit_passed, unit_failed = run_unit_tests()
            
            # 集成测试
            integration_passed, integration_failed = run_integration_tests()
            
            # 汇总
            passed = unit_passed + integration_passed
            failed = unit_failed + integration_failed
            test_type = "所有测试"
        
        # 生成报告
        if args.report:
            generate_test_report(passed, failed, test_type)
        else:
            # 简单汇总
            total_tests = passed + failed
            success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
            print(f"\n📊 测试完成: 通过 {passed}, 失败 {failed}, 成功率 {success_rate:.1f}%")
        
        total_time = time.time() - start_time
        print(f"\n⏱️  总耗时: {total_time:.2f} 秒")
        
        # 返回状态码
        if failed > 0:
            print("❌ 测试完成，存在失败的测试")
            sys.exit(1)
        else:
            print("✅ 所有测试通过！")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 测试运行器异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
