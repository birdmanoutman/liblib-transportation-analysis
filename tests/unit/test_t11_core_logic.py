#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T11 单元测试 - 解析/重试/限速/断点核心逻辑测试
测试覆盖率目标：≥70%
"""

import os
import sys
import json
import tempfile
import shutil
import asyncio
import unittest
import time
import random
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts"))
sys.path.insert(0, str(project_root / "scripts" / "scraping"))

try:
    # 导入核心模块
    from rate_limit_middleware import (
        RateLimitMiddleware, SyncRateLimitMiddleware, RateLimiter, 
        RetryHandler, CircuitBreaker, UserAgentRotator, ProxyManager,
        RateLimitConfig, RetryConfig, CircuitBreakerConfig, ProxyConfig
    )
    from t8_resume_and_retry import (
        StateManager, RetryManager, ResumeValidator, T8ResumeAndRetry,
        ResumePoint, FailedTask, CollectionState, TaskStatus, TaskType
    )
    from enhanced_detail_collector import EnhancedDetailCollector
    from t4_list_collector import T4ListCollector, ListItem
    from detail_collector import DetailCollector
    from liblib_car_analyzer import LiblibCarModelsAnalyzer
except ImportError as e:
    print(f"导入失败：{e}")
    print("当前Python路径：")
    for path in sys.path:
        print(f"  {path}")
    sys.exit(1)

# ============================================================================
# 1. 解析逻辑测试
# ============================================================================

class TestDataParsingLogic(unittest.TestCase):
    """数据解析逻辑测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.test_data = {
            'works': [
                {
                    'slug': 'test-slug-1',
                    'title': 'Test Work 1',
                    'author': {'name': 'Test Author'},
                    'publishedAt': '2024-01-01T00:00:00Z',
                    'tags': ['汽车', '交通'],
                    'likeCount': '1.2k',
                    'favoriteCount': '500',
                    'commentCount': '100',
                    'sourceUrl': 'https://example.com/1'
                },
                {
                    'slug': 'test-slug-2',
                    'title': 'Test Work 2',
                    'author': {'name': 'Test Author 2'},
                    'publishedAt': '2024-01-02T00:00:00Z',
                    'tags': ['设计', '创意'],
                    'likeCount': '800',
                    'favoriteCount': '200',
                    'commentCount': '50',
                    'sourceUrl': 'https://example.com/2'
                }
            ]
        }
    
    def test_parse_number_with_suffixes(self):
        """测试带后缀的数字解析"""
        analyzer = LiblibCarModelsAnalyzer()
        
        # 测试k后缀
        self.assertEqual(analyzer._parse_number('1.2k'), 1200)
        self.assertEqual(analyzer._parse_number('5k'), 5000)
        
        # 测试w后缀
        self.assertEqual(analyzer._parse_number('1.5w'), 15000)
        self.assertEqual(analyzer._parse_number('10w'), 100000)
        
        # 测试纯数字
        self.assertEqual(analyzer._parse_number('123'), 123)
        self.assertEqual(analyzer._parse_number('0'), 0)
        
        # 测试无效值
        self.assertEqual(analyzer._parse_number(''), 0)
        self.assertEqual(analyzer._parse_number(None), 0)
        self.assertEqual(analyzer._parse_number('invalid'), 0)
    
    def test_parse_list_response(self):
        """测试列表响应解析"""
        collector = T4ListCollector()
        
        # 模拟响应数据
        response = {
            'data': {
                'list': self.test_data['works']
            }
        }
        
        items = collector.parse_list_response(response)
        
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].slug, 'test-slug-1')
        self.assertEqual(items[0].title, 'Test Work 1')
        self.assertEqual(items[0].author_name, 'Test Author')
        self.assertEqual(items[0].like_count, 0)  # 因为解析失败，使用默认值
    
    def test_validate_work_data(self):
        """测试作品数据验证"""
        collector = DetailCollector()
        
        # 测试有效数据
        valid_data = {
            'slug': 'test-slug',
            'title': 'Test Title',
            'publishedAt': '2024-01-01T00:00:00Z',
            'tags': ['汽车', '交通'],
            'prompt': 'Test prompt',
            'negativePrompt': 'Test negative',
            'sampler': 'Euler',
            'steps': 20,
            'cfgScale': 7.5,
            'width': 512,
            'height': 512,
            'seed': '12345',
            'likeCount': 100,
            'favoriteCount': 50,
            'commentCount': 10,
            'sourceUrl': 'https://example.com'
        }
        
        validated = collector.validate_and_default_work_data(valid_data)
        
        self.assertEqual(validated['slug'], 'test-slug')
        self.assertEqual(validated['title'], 'Test Title')
        self.assertEqual(validated['steps'], 20)
        self.assertEqual(validated['cfg_scale'], 7.5)
        self.assertEqual(validated['like_count'], 100)
    
    def test_validate_author_data(self):
        """测试作者数据验证"""
        collector = DetailCollector()
        
        # 测试有效数据
        valid_data = {
            'id': 123,
            'name': 'Test Author',
            'username': 'testuser',
            'avatar': 'https://example.com/avatar.jpg',
            'bio': 'Test bio',
            'followersCount': '1.5k',
            'followingCount': '500',
            'worksCount': '100'
        }
        
        validated = collector.validate_and_default_author_data(valid_data)
        
        self.assertEqual(validated['author_id'], 123)
        self.assertEqual(validated['author_name'], 'Test Author')
        self.assertEqual(validated['author_username'], 'testuser')
        self.assertEqual(validated['author_avatar'], 'https://example.com/avatar.jpg')

# ============================================================================
# 2. 重试逻辑测试
# ============================================================================

class TestRetryLogic(unittest.TestCase):
    """重试逻辑测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.retry_config = RetryConfig(
            max_retries=3,
            base_delay=1.0,
            max_delay=60.0,
            backoff_factor=2.0,
            jitter=True,
            retry_on_status_codes=[429, 500, 502, 503, 504],
            expected_exception=(Exception,)
        )
        self.retry_handler = RetryHandler(self.retry_config)
    
    def test_retry_delay_calculation(self):
        """测试重试延迟计算"""
        # 第一次重试
        delay1 = self.retry_handler._calculate_delay(1)
        self.assertEqual(delay1, 1.0)
        
        # 第二次重试
        delay2 = self.retry_handler._calculate_delay(2)
        self.assertEqual(delay2, 2.0)
        
        # 第三次重试
        delay3 = self.retry_handler._calculate_delay(3)
        self.assertEqual(delay3, 4.0)
        
        # 第四次重试（超过最大延迟）
        delay4 = self.retry_handler._calculate_delay(4)
        self.assertEqual(delay4, 60.0)  # 最大延迟
    
    def test_should_retry_exception(self):
        """测试异常重试判断"""
        # 测试应该重试的异常
        mock_exception = Mock()
        mock_exception.response = Mock()
        mock_exception.response.status_code = 429
        
        self.assertTrue(self.retry_handler._should_retry(mock_exception))
        
        # 测试不应该重试的异常
        mock_exception.response.status_code = 200
        self.assertFalse(self.retry_handler._should_retry(mock_exception))
    
    @patch('asyncio.sleep')
    def test_execute_with_retry_success(self, mock_sleep):
        """测试重试执行成功"""
        mock_func = MagicMock()
        mock_func.__call__ = MagicMock(return_value="success")
        
        # 创建异步函数
        async def async_func():
            return await mock_func()
        
        # 运行异步测试
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                self.retry_handler.execute_with_retry(async_func, "arg1", "arg2")
            )
            self.assertEqual(result, "success")
            mock_sleep.assert_not_called()
        finally:
            loop.close()
    
    @patch('asyncio.sleep')
    def test_execute_with_retry_failure_then_success(self, mock_sleep):
        """测试重试执行失败后成功"""
        call_count = 0
        
        async def mock_func():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("error")
            return "success"
        
        # 运行异步测试
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                self.retry_handler.execute_with_retry(mock_func, "arg1")
            )
            self.assertEqual(result, "success")
            self.assertEqual(call_count, 2)
            mock_sleep.assert_called_once()
        finally:
            loop.close()
    
    @patch('asyncio.sleep')
    def test_execute_with_retry_max_failures(self, mock_sleep):
        """测试重试执行达到最大失败次数"""
        async def mock_func():
            raise Exception("error")
        
        # 运行异步测试
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            with self.assertRaises(Exception):
                loop.run_until_complete(
                    self.retry_handler.execute_with_retry(mock_func, "arg1")
                )
            self.assertEqual(mock_sleep.call_count, 3)
        finally:
            loop.close()

# ============================================================================
# 3. 限速逻辑测试
# ============================================================================

class TestRateLimitLogic(unittest.TestCase):
    """限速逻辑测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.rate_limit_config = RateLimitConfig(
            max_requests_per_second=4.0,
            max_concurrent=5,
            burst_size=10,
            time_window=1.0
        )
        self.rate_limiter = RateLimiter(self.rate_limit_config)
    
    def test_rate_limiter_initialization(self):
        """测试限速器初始化"""
        self.assertEqual(self.rate_limiter.max_requests_per_second, 4.0)
        self.assertEqual(self.rate_limiter.max_concurrent, 5)
        self.assertEqual(self.rate_limiter.burst_size, 10)
        self.assertEqual(self.rate_limiter.time_window, 1.0)
    
    def test_token_bucket_algorithm(self):
        """测试令牌桶算法"""
        # 初始状态应该有满桶令牌
        self.assertEqual(self.rate_limiter.tokens, 10)
        
        # 消耗一个令牌
        self.rate_limiter.acquire()
        self.assertEqual(self.rate_limiter.tokens, 9)
        
        # 消耗所有令牌
        for _ in range(9):
            self.rate_limiter.acquire()
        
        self.assertEqual(self.rate_limiter.tokens, 0)
        
        # 令牌不足时应该等待
        start_time = time.time()
        self.rate_limiter.acquire()
        elapsed_time = time.time() - start_time
        
        # 应该等待至少令牌恢复时间
        self.assertGreaterEqual(elapsed_time, 0.1)  # 允许一些误差
    
    def test_concurrent_limit(self):
        """测试并发限制"""
        # 模拟多个并发请求
        async def test_concurrent():
            await self.rate_limiter.acquire()
            await asyncio.sleep(0.1)
            self.rate_limiter.release()
        
        # 创建多个并发任务
        tasks = [test_concurrent() for _ in range(10)]
        
        # 应该能够并发执行，但受限于令牌桶
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(asyncio.gather(*tasks))
        finally:
            loop.close()
    
    def test_burst_handling(self):
        """测试突发流量处理"""
        # 突发请求应该能够处理
        for _ in range(10):
            self.rate_limiter.acquire()
        
        # 令牌应该耗尽
        self.assertEqual(self.rate_limiter.tokens, 0)
        
        # 后续请求应该被限速
        start_time = time.time()
        self.rate_limiter.acquire()
        elapsed_time = time.time() - start_time
        
        self.assertGreaterEqual(elapsed_time, 0.1)

# ============================================================================
# 4. 断点续采逻辑测试
# ============================================================================

class TestResumeLogic(unittest.TestCase):
    """断点续采逻辑测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_dir = os.path.join(self.temp_dir, "state")
        os.makedirs(self.state_dir, exist_ok=True)
        
        self.state_manager = StateManager(self.state_dir)
        self.retry_manager = RetryManager()
        self.resume_validator = ResumeValidator()
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_resume_point_creation(self):
        """测试断点续采点创建"""
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
    
    def test_resume_point_update(self):
        """测试断点续采点更新"""
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
    
    def test_resume_point_retrieval(self):
        """测试断点续采点检索"""
        # 创建多个断点续采点
        self.state_manager.create_resume_point(
            task_type="LIST_COLLECTION",
            current_page=1,
            total_processed=24
        )
        
        self.state_manager.create_resume_point(
            task_type="DETAIL_COLLECTION",
            current_page=1,
            total_processed=10
        )
        
        # 按类型检索
        list_points = self.state_manager.get_resume_points_by_type("LIST_COLLECTION")
        self.assertEqual(len(list_points), 1)
        self.assertEqual(list_points[0].task_type, "LIST_COLLECTION")
        
        detail_points = self.state_manager.get_resume_points_by_type("DETAIL_COLLECTION")
        self.assertEqual(len(detail_points), 1)
        self.assertEqual(detail_points[0].task_type, "DETAIL_COLLECTION")
    
    def test_failed_task_management(self):
        """测试失败任务管理"""
        # 创建失败任务
        failed_task = FailedTask(
            task_id="task_123",
            task_type="LIST_COLLECTION",
            error_message="Network error",
            retry_count=0,
            created_at=datetime.now()
        )
        
        self.retry_manager.add_failed_task(failed_task)
        
        # 获取失败任务
        failed_tasks = self.retry_manager.get_failed_tasks()
        self.assertEqual(len(failed_tasks), 1)
        self.assertEqual(failed_tasks[0].task_id, "task_123")
        
        # 更新重试次数
        self.retry_manager.increment_retry_count("task_123")
        updated_task = self.retry_manager.get_failed_task("task_123")
        self.assertEqual(updated_task.retry_count, 1)
    
    def test_resume_validation(self):
        """测试断点续采验证"""
        # 创建断点续采点
        point_id = self.state_manager.create_resume_point(
            task_type="LIST_COLLECTION",
            current_page=5,
            total_processed=120
        )
        
        point = self.state_manager.resume_points[point_id]
        
        # 验证断点续采点
        is_valid = self.resume_validator.validate_resume_point(point)
        self.assertTrue(is_valid)
        
        # 测试过期的断点续采点
        old_point = ResumePoint(
            id="old_point",
            task_type="LIST_COLLECTION",
            current_page=1,
            total_processed=24,
            created_at=datetime.now() - timedelta(days=10),
            updated_at=datetime.now() - timedelta(days=10),
            metadata={}
        )
        
        is_valid = self.resume_validator.validate_resume_point(old_point)
        self.assertFalse(is_valid)

# ============================================================================
# 5. 集成测试
# ============================================================================

class TestIntegrationLogic(unittest.TestCase):
    """集成逻辑测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.middleware = RateLimitMiddleware()
        self.temp_dir = tempfile.mkdtemp()
        self.state_dir = os.path.join(self.temp_dir, "state")
        os.makedirs(self.state_dir, exist_ok=True)
        
        self.state_manager = StateManager(self.state_dir)
        self.retry_manager = RetryManager()
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('aiohttp.ClientSession.request')
    def test_middleware_integration(self, mock_request):
        """测试中间件集成"""
        # 模拟成功的HTTP响应
        mock_response = Mock()
        mock_response.status = 200
        mock_request.return_value.__aenter__.return_value = mock_response
        
        # 测试中间件请求
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(
                self.middleware.make_request('GET', 'https://example.com')
            )
            self.assertEqual(response.status, 200)
            self.assertEqual(self.middleware.stats['total_requests'], 1)
            self.assertEqual(self.middleware.stats['successful_requests'], 1)
        finally:
            loop.close()
    
    def test_state_and_retry_integration(self):
        """测试状态管理和重试集成"""
        # 创建断点续采点
        point_id = self.state_manager.create_resume_point(
            task_type="LIST_COLLECTION",
            current_page=5,
            total_processed=120
        )
        
        # 创建失败任务
        failed_task = FailedTask(
            task_id="task_123",
            task_type="LIST_COLLECTION",
            error_message="Network error",
            retry_count=0,
            created_at=datetime.now()
        )
        
        self.retry_manager.add_failed_task(failed_task)
        
        # 验证集成
        self.assertIn(point_id, self.state_manager.resume_points)
        self.assertEqual(len(self.retry_manager.get_failed_tasks()), 1)
    
    def test_config_integration(self):
        """测试配置集成"""
        # 测试限速配置
        rate_config = RateLimitConfig()
        self.assertEqual(rate_config.max_requests_per_second, 4.0)
        self.assertEqual(rate_config.max_concurrent, 5)
        
        # 测试重试配置
        retry_config = RetryConfig()
        self.assertEqual(retry_config.max_retries, 3)
        self.assertEqual(retry_config.base_delay, 1.0)
        
        # 测试熔断器配置
        circuit_config = CircuitBreakerConfig()
        self.assertEqual(circuit_config.failure_threshold, 5)
        self.assertEqual(circuit_config.recovery_timeout, 60.0)

# ============================================================================
# 6. 边界条件测试
# ============================================================================

class TestEdgeCases(unittest.TestCase):
    """边界条件测试类"""
    
    def test_empty_data_parsing(self):
        """测试空数据解析"""
        collector = T4ListCollector()
        
        # 测试空响应
        empty_response = {'data': {'list': []}}
        items = collector.parse_list_response(empty_response)
        self.assertEqual(len(items), 0)
        
        # 测试无效响应
        invalid_response = {}
        items = collector.parse_list_response(invalid_response)
        self.assertEqual(len(items), 0)
    
    def test_extreme_rate_limits(self):
        """测试极端限速条件"""
        # 极低限速
        low_rate_config = RateLimitConfig(
            max_requests_per_second=0.1,  # 10秒一个请求
            max_concurrent=1,
            burst_size=1,
            time_window=1.0
        )
        
        rate_limiter = RateLimiter(low_rate_config)
        
        # 第一个请求应该立即通过
        start_time = time.time()
        rate_limiter.acquire()
        first_request_time = time.time() - start_time
        self.assertLess(first_request_time, 0.1)
        
        # 第二个请求应该被限速
        start_time = time.time()
        rate_limiter.acquire()
        second_request_time = time.time() - start_time
        self.assertGreaterEqual(second_request_time, 9.0)  # 至少等待9秒
    
    def test_circuit_breaker_extremes(self):
        """测试熔断器极端条件"""
        # 高失败阈值
        high_threshold_config = CircuitBreakerConfig(
            failure_threshold=100,
            recovery_timeout=1.0,
            success_threshold=1
        )
        
        circuit_breaker = CircuitBreaker(high_threshold_config)
        
        # 应该能够承受更多失败
        for _ in range(99):
            circuit_breaker.record_failure()
        
        self.assertTrue(circuit_breaker.is_closed())
        
        # 第100次失败应该触发熔断
        circuit_breaker.record_failure()
        self.assertTrue(circuit_breaker.is_open())
    
    def test_large_data_handling(self):
        """测试大数据处理"""
        # 创建大量测试数据
        large_data = {
            'works': [
                {
                    'slug': f'test-slug-{i}',
                    'title': f'Test Work {i}',
                    'author': {'name': f'Test Author {i}'},
                    'publishedAt': '2024-01-01T00:00:00Z',
                    'tags': ['汽车', '交通'],
                    'likeCount': str(i * 100),
                    'favoriteCount': str(i * 50),
                    'commentCount': str(i * 10),
                    'sourceUrl': f'https://example.com/{i}'
                }
                for i in range(1000)
            ]
        }
        
        collector = T4ListCollector()
        response = {'data': {'list': large_data['works']}}
        
        # 应该能够处理大量数据
        start_time = time.time()
        items = collector.parse_list_response(response)
        parse_time = time.time() - start_time
        
        self.assertEqual(len(items), 1000)
        self.assertLess(parse_time, 5.0)  # 解析时间应该在5秒内

# ============================================================================
# 7. 性能测试
# ============================================================================

class TestPerformanceLogic(unittest.TestCase):
    """性能逻辑测试类"""
    
    def test_parsing_performance(self):
        """测试解析性能"""
        collector = DetailCollector()
        
        # 创建测试数据
        test_data = {
            'slug': 'test-slug',
            'title': 'Test Title',
            'publishedAt': '2024-01-01T00:00:00Z',
            'tags': ['汽车', '交通'] * 100,  # 大量标签
            'prompt': 'A' * 1000,  # 长提示词
            'negativePrompt': 'B' * 1000,  # 长负面提示词
            'sampler': 'Euler',
            'steps': 20,
            'cfgScale': 7.5,
            'width': 512,
            'height': 512,
            'seed': '12345',
            'likeCount': 100,
            'favoriteCount': 50,
            'commentCount': 10,
            'sourceUrl': 'https://example.com'
        }
        
        # 性能测试
        start_time = time.time()
        for _ in range(100):
            collector.validate_and_default_work_data(test_data)
        total_time = time.time() - start_time
        
        # 100次验证应该在1秒内完成
        self.assertLess(total_time, 1.0)
        self.assertLess(total_time / 100, 0.01)  # 每次验证应该在10ms内
    
    def test_rate_limiter_performance(self):
        """测试限速器性能"""
        rate_limiter = RateLimiter(RateLimitConfig())
        
        # 测试令牌消耗性能
        start_time = time.time()
        for _ in range(1000):
            rate_limiter.acquire()
        total_time = time.time() - start_time
        
        # 1000次令牌消耗应该在1秒内完成
        self.assertLess(total_time, 1.0)
    
    def test_state_manager_performance(self):
        """测试状态管理器性能"""
        temp_dir = tempfile.mkdtemp()
        state_dir = os.path.join(temp_dir, "state")
        os.makedirs(state_dir, exist_ok=True)
        
        state_manager = StateManager(state_dir)
        
        # 测试大量断点续采点创建
        start_time = time.time()
        for i in range(1000):
            state_manager.create_resume_point(
                task_type="LIST_COLLECTION",
                current_page=i,
                total_processed=i * 24
            )
        total_time = time.time() - start_time
        
        # 1000个断点续采点创建应该在1秒内完成
        self.assertLess(total_time, 1.0)
        
        # 清理
        shutil.rmtree(temp_dir, ignore_errors=True)

# ============================================================================
# 主测试运行
# ============================================================================

def run_tests():
    """运行所有测试"""
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestDataParsingLogic,
        TestRetryLogic,
        TestRateLimitLogic,
        TestResumeLogic,
        TestIntegrationLogic,
        TestEdgeCases,
        TestPerformanceLogic
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出测试结果统计
    print(f"\n{'='*60}")
    print(f"测试结果统计")
    print(f"{'='*60}")
    print(f"运行测试: {result.testsRun}")
    print(f"失败测试: {len(result.failures)}")
    print(f"错误测试: {len(result.errors)}")
    print(f"跳过测试: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print(f"\n失败测试详情:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print(f"\n错误测试详情:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    # 计算成功率
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\n测试成功率: {success_rate:.1f}%")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    # 运行测试
    success = run_tests()
    
    # 退出码
    sys.exit(0 if success else 1)
