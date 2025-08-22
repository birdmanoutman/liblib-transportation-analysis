#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T8 断点续采与失败补偿模块单元测试
"""

import os
import sys
import json
import tempfile
import shutil
import asyncio
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 修复导入路径
sys.path.insert(0, str(project_root / "scripts"))
sys.path.insert(0, str(project_root / "scripts" / "scraping"))

try:
    from t8_resume_and_retry import (
        StateManager, RetryManager, ResumeValidator, T8ResumeAndRetry,
        ResumePoint, FailedTask, CollectionState, TaskStatus, TaskType
    )
    from t8_config import get_config, validate_config
except ImportError as e:
    print(f"导入失败：{e}")
    print("当前Python路径：")
    for path in sys.path:
        print(f"  {path}")
    sys.exit(1)

class TestStateManager(unittest.TestCase):
    """StateManager 测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.state_dir = os.path.join(self.temp_dir, "state")
        os.makedirs(self.state_dir, exist_ok=True)
        
        # 创建StateManager实例
        self.state_manager = StateManager(self.state_dir)
    
    def tearDown(self):
        """测试后清理"""
        # 清理临时目录
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_resume_point(self):
        """测试创建断点续采点"""
        point_id = self.state_manager.create_resume_point(
            task_type="LIST_COLLECTION",
            current_page=5,
            last_cursor="cursor_123",
            total_processed=120,
            metadata={"tag": "汽车交通"}
        )
        
        self.assertIsNotNone(point_id)
        self.assertIn(point_id, self.state_manager.resume_points)
        
        point = self.state_manager.resume_points[point_id]
        self.assertEqual(point.task_type, "LIST_COLLECTION")
        self.assertEqual(point.current_page, 5)
        self.assertEqual(point.last_cursor, "cursor_123")
        self.assertEqual(point.total_processed, 120)
        self.assertEqual(point.metadata["tag"], "汽车交通")
    
    def test_update_resume_point(self):
        """测试更新断点续采点"""
        point_id = self.state_manager.create_resume_point(
            task_type="LIST_COLLECTION",
            current_page=5,
            total_processed=120
        )
        
        # 更新断点续采点
        self.state_manager.update_resume_point(
            point_id,
            current_page=6,
            total_processed=144
        )
        
        point = self.state_manager.resume_points[point_id]
        self.assertEqual(point.current_page, 6)
        self.assertEqual(point.total_processed, 144)
    
    def test_get_resume_point(self):
        """测试获取断点续采点"""
        # 创建多个断点续采点
        self.state_manager.create_resume_point(
            task_type="LIST_COLLECTION",
            current_page=5,
            total_processed=120
        )
        
        self.state_manager.create_resume_point(
            task_type="DETAIL_COLLECTION",
            current_page=1,
            total_processed=50
        )
        
        # 获取指定类型的断点续采点
        list_point = self.state_manager.get_resume_point("LIST_COLLECTION")
        self.assertIsNotNone(list_point)
        self.assertEqual(list_point.task_type, "LIST_COLLECTION")
        
        detail_point = self.state_manager.get_resume_point("DETAIL_COLLECTION")
        self.assertIsNotNone(detail_point)
        self.assertEqual(detail_point.task_type, "DETAIL_COLLECTION")
    
    def test_add_failed_task(self):
        """测试添加失败任务"""
        task_id = self.state_manager.add_failed_task(
            task_type="DETAIL_COLLECTION",
            target="car-model-001",
            error_message="API请求超时",
            max_retries=3,
            retry_delay=60
        )
        
        self.assertIsNotNone(task_id)
        self.assertIn(task_id, self.state_manager.failed_tasks)
        
        task = self.state_manager.failed_tasks[task_id]
        self.assertEqual(task.task_type, "DETAIL_COLLECTION")
        self.assertEqual(task.target, "car-model-001")
        self.assertEqual(task.error_message, "API请求超时")
        self.assertEqual(task.max_retries, 3)
        self.assertEqual(task.retry_count, 0)
    
    def test_get_retryable_tasks(self):
        """测试获取可重试任务"""
        # 添加失败任务
        task_id1 = self.state_manager.add_failed_task(
            task_type="DETAIL_COLLECTION",
            target="car-model-001",
            error_message="API请求超时",
            max_retries=3,
            retry_delay=60
        )
        
        task_id2 = self.state_manager.add_failed_task(
            task_type="IMAGE_DOWNLOAD",
            target="https://example.com/image.jpg",
            error_message="网络连接失败",
            max_retries=2,
            retry_delay=120
        )
        
        # 获取可重试任务
        retryable_tasks = self.state_manager.get_retryable_tasks()
        self.assertEqual(len(retryable_tasks), 2)
        
        # 验证任务类型
        task_types = [task.task_type for task in retryable_tasks]
        self.assertIn("DETAIL_COLLECTION", task_types)
        self.assertIn("IMAGE_DOWNLOAD", task_types)
    
    def test_mark_task_success(self):
        """测试标记任务成功"""
        task_id = self.state_manager.add_failed_task(
            task_type="DETAIL_COLLECTION",
            target="car-model-001",
            error_message="API请求超时"
        )
        
        # 标记任务成功
        self.state_manager.mark_task_success(task_id)
        
        # 验证任务已从失败队列移除
        self.assertNotIn(task_id, self.state_manager.failed_tasks)
    
    def test_mark_task_retry(self):
        """测试标记任务重试"""
        task_id = self.state_manager.add_failed_task(
            task_type="DETAIL_COLLECTION",
            target="car-model-001",
            error_message="API请求超时"
        )
        
        # 标记任务重试
        next_retry_time = datetime.now() + timedelta(minutes=5)
        self.state_manager.mark_task_retry(task_id, next_retry_time)
        
        task = self.state_manager.failed_tasks[task_id]
        self.assertEqual(task.retry_count, 1)
        self.assertEqual(task.next_retry_time, next_retry_time)
    
    def test_create_collection_state(self):
        """测试创建采集状态"""
        run_id = self.state_manager.create_collection_state(
            run_id="test_run_001",
            task_type="LIST_COLLECTION"
        )
        
        self.assertEqual(run_id, "test_run_001")
        self.assertIn(run_id, self.state_manager.collection_states)
        
        state = self.state_manager.collection_states[run_id]
        self.assertEqual(state.run_id, "test_run_001")
        self.assertEqual(state.task_type, "LIST_COLLECTION")
        self.assertEqual(state.status, "RUNNING")
    
    def test_update_collection_state(self):
        """测试更新采集状态"""
        run_id = self.state_manager.create_collection_state(
            run_id="test_run_001",
            task_type="LIST_COLLECTION"
        )
        
        # 更新状态
        self.state_manager.update_collection_state(
            run_id,
            status="SUCCESS",
            processed_items=100
        )
        
        state = self.state_manager.collection_states[run_id]
        self.assertEqual(state.status, "SUCCESS")
        self.assertEqual(state.processed_items, 100)

class TestRetryManager(unittest.TestCase):
    """RetryManager 测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.state_dir = os.path.join(self.temp_dir, "state")
        os.makedirs(self.state_dir, exist_ok=True)
        
        # 创建StateManager和RetryManager实例
        self.state_manager = StateManager(self.state_dir)
        self.retry_manager = RetryManager(self.state_manager, max_workers=2)
    
    def tearDown(self):
        """测试后清理"""
        # 停止重试服务
        self.retry_manager.stop_retry_service()
        
        # 清理临时目录
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_register_retry_handler(self):
        """测试注册重试处理器"""
        def mock_handler(target, metadata):
            return True
        
        self.retry_manager.register_retry_handler("TEST_TASK", mock_handler)
        
        self.assertIn("TEST_TASK", self.retry_manager.retry_handlers)
        self.assertEqual(self.retry_manager.retry_handlers["TEST_TASK"], mock_handler)
    
    def test_start_stop_service(self):
        """测试启动和停止服务"""
        # 启动服务
        self.retry_manager.start_retry_service()
        self.assertTrue(self.retry_manager.running)
        self.assertIsNotNone(self.retry_manager.retry_thread)
        
        # 停止服务
        self.retry_manager.stop_retry_service()
        self.assertFalse(self.retry_manager.running)

class TestResumeValidator(unittest.TestCase):
    """ResumeValidator 测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.state_dir = os.path.join(self.temp_dir, "state")
        os.makedirs(self.state_dir, exist_ok=True)
        
        # 创建StateManager和ResumeValidator实例
        self.state_manager = StateManager(self.state_dir)
        
        # Mock DatabaseManager
        self.mock_db_manager = Mock()
        self.validator = ResumeValidator(self.state_manager, self.mock_db_manager)
    
    def tearDown(self):
        """测试后清理"""
        # 清理临时目录
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validate_resume_point(self):
        """测试验证断点续采点"""
        point = ResumePoint(
            task_type="LIST_COLLECTION",
            current_page=5,
            last_cursor="cursor_123",
            last_slug=None,
            total_processed=120,
            last_update=datetime.now(),
            metadata={}
        )
        
        # 验证有效的断点续采点
        validation = asyncio.run(self.validator._validate_resume_point(point))
        self.assertTrue(validation["valid"])
        
        # 验证无效的断点续采点
        invalid_point = ResumePoint(
            task_type="LIST_COLLECTION",
            current_page=-1,  # 无效页码
            last_cursor=None,
            last_slug=None,
            total_processed=-1,  # 无效数量
            last_update=datetime.now(),
            metadata={}
        )
        
        validation = asyncio.run(self.validator._validate_resume_point(invalid_point))
        self.assertFalse(validation["valid"])
    
    def test_validate_failed_task(self):
        """测试验证失败任务"""
        task = FailedTask(
            task_id="test_task_001",
            task_type="DETAIL_COLLECTION",
            target="car-model-001",
            error_message="API请求超时",
            retry_count=2,
            max_retries=3,
            next_retry_time=datetime.now() + timedelta(minutes=5),
            created_at=datetime.now(),
            metadata={}
        )
        
        # 验证有效的失败任务
        validation = asyncio.run(self.validator._validate_failed_task(task))
        self.assertTrue(validation["valid"])
        
        # 验证无效的失败任务
        invalid_task = FailedTask(
            task_id="test_task_002",
            task_type="DETAIL_COLLECTION",
            target="car-model-002",
            error_message="",  # 空错误信息
            retry_count=5,  # 超过最大重试次数
            max_retries=3,
            next_retry_time=datetime.now() - timedelta(minutes=5),  # 过期
            created_at=datetime.now(),
            metadata={}
        )
        
        validation = asyncio.run(self.validator._validate_failed_task(invalid_task))
        self.assertFalse(validation["valid"])

class TestT8ResumeAndRetry(unittest.TestCase):
    """T8ResumeAndRetry 测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.state_dir = os.path.join(self.temp_dir, "state")
        os.makedirs(self.state_dir, exist_ok=True)
        
        # 测试配置
        self.config = {
            'state_dir': self.state_dir,
            'max_workers': 2,
            'retry_check_interval': 30,
            'max_retry_delay': 3600,
            'enable_auto_retry': True,
            'enable_integrity_check': True
        }
        
        # 创建T8实例
        self.t8 = T8ResumeAndRetry(self.config)
    
    def tearDown(self):
        """测试后清理"""
        # 停止服务
        self.t8.stop_service()
        
        # 清理临时目录
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.t8.state_manager)
        self.assertIsNotNone(self.t8.retry_manager)
        self.assertIsNotNone(self.t8.validator)
    
    def test_create_resume_point(self):
        """测试创建断点续采点"""
        point_id = self.t8.create_resume_point(
            task_type="LIST_COLLECTION",
            current_page=5,
            total_processed=120
        )
        
        self.assertIsNotNone(point_id)
        
        # 验证断点续采点已创建
        point = self.t8.get_resume_point("LIST_COLLECTION")
        self.assertIsNotNone(point)
        self.assertEqual(point.current_page, 5)
        self.assertEqual(point.total_processed, 120)
    
    def test_add_failed_task(self):
        """测试添加失败任务"""
        task_id = self.t8.add_failed_task(
            task_type="DETAIL_COLLECTION",
            target="car-model-001",
            error_message="API请求超时"
        )
        
        self.assertIsNotNone(task_id)
        
        # 验证失败任务已添加
        failed_tasks = self.t8.get_retryable_tasks()
        self.assertEqual(len(failed_tasks), 1)
        self.assertEqual(failed_tasks[0].target, "car-model-001")
    
    def test_service_lifecycle(self):
        """测试服务生命周期"""
        # 启动服务
        self.t8.start_service()
        self.assertTrue(self.t8.retry_manager.running)
        
        # 停止服务
        self.t8.stop_service()
        self.assertFalse(self.t8.retry_manager.running)

class TestT8Config(unittest.TestCase):
    """T8配置测试类"""
    
    def test_get_config(self):
        """测试获取配置"""
        config = get_config('development')
        
        # 验证基础配置
        self.assertIn('state_dir', config)
        self.assertIn('max_workers', config)
        self.assertIn('retry_check_interval', config)
        
        # 验证环境特定配置
        self.assertEqual(config['max_workers'], 3)  # development环境
        self.assertEqual(config['log_level'], 'DEBUG')
    
    def test_validate_config(self):
        """测试配置验证"""
        # 有效配置
        valid_config = {
            'state_dir': 'data/state',
            'max_workers': 5,
            'retry_check_interval': 30,
            'max_retry_delay': 3600
        }
        self.assertTrue(validate_config(valid_config))
        
        # 无效配置 - 缺少必要字段
        invalid_config = {
            'state_dir': 'data/state'
            # 缺少其他必要字段
        }
        self.assertFalse(validate_config(invalid_config))
        
        # 无效配置 - 数值超出范围
        invalid_config2 = {
            'state_dir': 'data/state',
            'max_workers': 100,  # 超出范围
            'retry_check_interval': 30,
            'max_retry_delay': 3600
        }
        self.assertFalse(validate_config(invalid_config2))

def run_tests():
    """运行所有测试"""
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestStateManager,
        TestRetryManager,
        TestResumeValidator,
        TestT8ResumeAndRetry,
        TestT8Config
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 返回测试结果
    return result.wasSuccessful()

if __name__ == "__main__":
    # 运行测试
    success = run_tests()
    
    if success:
        print("\n✅ 所有测试通过")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败")
        sys.exit(1)
