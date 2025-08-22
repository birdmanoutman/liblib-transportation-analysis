#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T8 断点续采与失败补偿模块 - 简化测试
"""

import os
import sys
import json
import time
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# 添加scripts目录到Python路径
current_dir = Path(__file__).parent
scripts_dir = current_dir / "scripts"
scraping_dir = scripts_dir / "scraping"

sys.path.insert(0, str(scripts_dir))
sys.path.insert(0, str(scraping_dir))

print(f"当前目录：{current_dir}")
print(f"脚本目录：{scripts_dir}")
print(f"爬虫目录：{scraping_dir}")
print(f"Python路径：{sys.path[:3]}")

try:
    from t8_resume_and_retry import T8ResumeAndRetry
    from t8_config import get_config, validate_config
    print("✅ 模块导入成功")
except ImportError as e:
    print(f"❌ 模块导入失败：{e}")
    print("尝试直接导入...")
    
    # 尝试直接导入
    try:
        import importlib.util
        
        # 加载t8_resume_and_retry模块
        spec1 = importlib.util.spec_from_file_location(
            "t8_resume_and_retry", 
            scraping_dir / "t8_resume_and_retry.py"
        )
        t8_module = importlib.util.module_from_spec(spec1)
        spec1.loader.exec_module(t8_module)
        
        # 加载t8_config模块
        spec2 = importlib.util.spec_from_file_location(
            "t8_config", 
            scraping_dir / "t8_config.py"
        )
        config_module = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(config_module)
        
        T8ResumeAndRetry = t8_module.T8ResumeAndRetry
        get_config = config_module.get_config
        validate_config = config_module.validate_config
        
        print("✅ 模块直接导入成功")
        
    except Exception as e2:
        print(f"❌ 直接导入也失败：{e2}")
        sys.exit(1)

def test_config():
    """测试配置功能"""
    print("\n=== 测试配置功能 ===")
    
    # 测试配置获取
    config = get_config('development')
    print(f"开发环境配置：max_workers={config['max_workers']}, log_level={config['log_level']}")
    
    # 测试配置验证
    if validate_config(config):
        print("✅ 配置验证通过")
    else:
        print("❌ 配置验证失败")
        return False
    
    return True

def test_basic_functionality():
    """测试基本功能"""
    print("\n=== 测试基本功能 ===")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    state_dir = os.path.join(temp_dir, "state")
    
    try:
        # 创建配置
        config = {
            'state_dir': state_dir,
            'max_workers': 2,
            'retry_check_interval': 30,
            'max_retry_delay': 3600,
            'enable_auto_retry': True,
            'enable_integrity_check': True
        }
        
        # 创建T8实例
        t8 = T8ResumeAndRetry(config)
        print("✅ T8实例创建成功")
        
        # 测试创建断点续采点
        point_id = t8.create_resume_point(
            task_type="LIST_COLLECTION",
            current_page=5,
            total_processed=120,
            metadata={"tag": "汽车交通"}
        )
        print(f"✅ 断点续采点创建成功：{point_id}")
        
        # 测试获取断点续采点
        resume_point = t8.get_resume_point("LIST_COLLECTION")
        if resume_point:
            print(f"✅ 断点续采点获取成功：第{resume_point.current_page}页，已处理{resume_point.total_processed}项")
        else:
            print("❌ 断点续采点获取失败")
            return False
        
        # 测试添加失败任务
        task_id = t8.add_failed_task(
            task_type="DETAIL_COLLECTION",
            target="car-model-001",
            error_message="API请求超时"
        )
        print(f"✅ 失败任务添加成功：{task_id}")
        
        # 测试获取可重试任务
        retryable_tasks = t8.get_retryable_tasks()
        print(f"✅ 可重试任务获取成功：{len(retryable_tasks)}个")
        
        # 测试服务生命周期
        print("测试服务生命周期...")
        t8.start_service()
        print("✅ 服务启动成功")
        
        # 等待一段时间
        time.sleep(2)
        
        t8.stop_service()
        print("✅ 服务停止成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生异常：{e}")
        return False
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_state_persistence():
    """测试状态持久化"""
    print("\n=== 测试状态持久化 ===")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    state_dir = os.path.join(temp_dir, "state")
    
    try:
        config = {'state_dir': state_dir}
        t8 = T8ResumeAndRetry(config)
        
        # 创建多个断点续采点
        for i in range(1, 4):
            t8.create_resume_point(
                task_type="LIST_COLLECTION",
                current_page=i,
                total_processed=i * 24
            )
        
        # 添加多个失败任务
        for i in range(1, 4):
            t8.add_failed_task(
                task_type="DETAIL_COLLECTION",
                target=f"car-model-{i:03d}",
                error_message=f"模拟错误 {i}"
            )
        
        # 检查状态文件是否创建
        state_files = os.listdir(state_dir)
        print(f"状态文件：{state_files}")
        
        if len(state_files) >= 3:  # resume_points.json, failed_tasks.json, collection_state.json
            print("✅ 状态持久化成功")
            return True
        else:
            print("❌ 状态持久化失败")
            return False
            
    except Exception as e:
        print(f"❌ 状态持久化测试异常：{e}")
        return False
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    """主测试函数"""
    print("T8 断点续采与失败补偿模块 - 简化测试")
    print("=" * 50)
    
    tests = [
        ("配置功能", test_config),
        ("基本功能", test_basic_functionality),
        ("状态持久化", test_state_persistence)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常：{e}")
    
    print("\n" + "=" * 50)
    print(f"测试结果：{passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return True
    else:
        print("⚠️  部分测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
