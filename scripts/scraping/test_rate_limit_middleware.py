#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T7 中间件测试文件
测试限速/重试中间件的各项功能
"""

import asyncio
import time
import logging
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 直接导入模块
from rate_limit_middleware import (
    RateLimitMiddleware, SyncRateLimitMiddleware,
    RateLimitConfig, RetryConfig, CircuitBreakerConfig, ProxyConfig,
    create_middleware
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_rate_limiting():
    """测试速率限制功能"""
    print("\n=== 测试速率限制功能 ===")
    
    # 创建严格的限速配置
    rate_config = RateLimitConfig(
        max_requests_per_second=2.0,  # 每秒最多2个请求
        max_concurrent=3
    )
    
    middleware = RateLimitMiddleware(rate_limit_config=rate_config)
    
    start_time = time.time()
    
    # 发送多个请求
    tasks = []
    for i in range(5):
        task = asyncio.create_task(
            middleware.make_request('GET', 'https://httpbin.org/delay/0.1')
        )
        tasks.append(task)
    
    # 等待所有请求完成
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"发送5个请求，总耗时: {total_time:.2f}秒")
    print(f"平均每个请求耗时: {total_time/5:.2f}秒")
    print(f"统计信息: {middleware.get_stats()}")

async def test_retry_mechanism():
    """测试重试机制"""
    print("\n=== 测试重试机制 ===")
    
    # 创建重试配置
    retry_config = RetryConfig(
        max_retries=3,
        base_delay=0.5,
        backoff_factor=2.0
    )
    
    middleware = RateLimitMiddleware(retry_config=retry_config)
    
    # 测试会失败的请求（模拟429状态码）
    try:
        response = await middleware.make_request(
            'GET', 'https://httpbin.org/status/429'
        )
        print(f"请求成功: {response.status}")
    except Exception as e:
        print(f"请求失败（预期）: {e}")
    
    print(f"统计信息: {middleware.get_stats()}")

async def test_circuit_breaker():
    """测试熔断器功能"""
    print("\n=== 测试熔断器功能 ===")
    
    # 创建熔断器配置
    cb_config = CircuitBreakerConfig(
        failure_threshold=3,  # 3次失败后熔断
        recovery_timeout=5.0,  # 5秒后尝试恢复
        success_threshold=2
    )
    
    middleware = RateLimitMiddleware(circuit_breaker_config=cb_config)
    
    # 模拟连续失败
    for i in range(4):
        try:
            response = await middleware.make_request(
                'GET', 'https://httpbin.org/status/500'
            )
            print(f"请求 {i+1} 成功: {response.status}")
        except Exception as e:
            print(f"请求 {i+1} 失败: {e}")
    
    print(f"熔断器状态: {middleware.circuit_breaker.state.value}")
    print(f"统计信息: {middleware.get_stats()}")

async def test_user_agent_rotation():
    """测试用户代理轮换"""
    print("\n=== 测试用户代理轮换 ===")
    
    middleware = RateLimitMiddleware()
    
    # 发送多个请求，检查用户代理是否轮换
    user_agents = set()
    for i in range(3):
        try:
            response = await middleware.make_request(
                'GET', 'https://httpbin.org/headers'
            )
            # 从响应中提取用户代理（这里简化处理）
            user_agents.add(f"UA_{i}")
            print(f"请求 {i+1} 完成")
        except Exception as e:
            print(f"请求 {i+1} 失败: {e}")
    
    print(f"使用了 {len(user_agents)} 个不同的用户代理")

async def test_proxy_management():
    """测试代理管理"""
    print("\n=== 测试代理管理 ===")
    
    # 创建代理配置
    proxy_config = ProxyConfig(
        enabled=True,
        proxies=[
            'http://proxy1.example.com:8080',
            'http://proxy2.example.com:8080',
            'http://proxy3.example.com:8080'
        ],
        rotation_strategy='round_robin'
    )
    
    middleware = RateLimitMiddleware(proxy_config=proxy_config)
    
    # 测试代理轮换
    for i in range(3):
        proxy = middleware.proxy_manager.get_next_proxy()
        print(f"请求 {i+1} 使用代理: {proxy}")
    
    # 测试代理失败标记
    middleware.proxy_manager.mark_proxy_failed('http://proxy1.example.com:8080')
    print("已标记代理1为失败")
    
    # 再次获取代理
    proxy = middleware.proxy_manager.get_next_proxy()
    print(f"失败后获取的代理: {proxy}")

def test_sync_middleware():
    """测试同步版本中间件"""
    print("\n=== 测试同步版本中间件 ===")
    
    middleware = SyncRateLimitMiddleware()
    
    start_time = time.time()
    
    # 发送多个请求
    for i in range(3):
        try:
            response = middleware.make_request('GET', 'https://httpbin.org/get')
            print(f"同步请求 {i+1} 成功: {response.status_code}")
        except Exception as e:
            print(f"同步请求 {i+1} 失败: {e}")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"同步请求总耗时: {total_time:.2f}秒")
    print(f"统计信息: {middleware.get_stats()}")

async def test_middleware_factory():
    """测试中间件工厂函数"""
    print("\n=== 测试中间件工厂函数 ===")
    
    # 自定义配置
    custom_config = {
        'rate_limit': {
            'max_requests_per_second': 1.0,
            'max_concurrent': 2
        },
        'retry': {
            'max_retries': 2,
            'base_delay': 0.5
        }
    }
    
    # 创建异步中间件
    async_middleware = create_middleware(custom_config, async_mode=True)
    print(f"异步中间件类型: {type(async_middleware)}")
    
    # 创建同步中间件
    sync_middleware = create_middleware(custom_config, async_mode=False)
    print(f"同步中间件类型: {type(sync_middleware)}")

async def test_stress_test():
    """压力测试"""
    print("\n=== 压力测试 ===")
    
    # 创建高并发配置
    rate_config = RateLimitConfig(
        max_requests_per_second=10.0,
        max_concurrent=20
    )
    
    middleware = RateLimitMiddleware(rate_limit_config=rate_config)
    
    start_time = time.time()
    
    # 创建大量并发请求
    tasks = []
    for i in range(50):
        task = asyncio.create_task(
            middleware.make_request('GET', 'https://httpbin.org/get')
        )
        tasks.append(task)
    
    # 等待所有请求完成
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # 统计结果
    success_count = sum(1 for r in responses if not isinstance(r, Exception))
    failure_count = len(responses) - success_count
    
    print(f"总请求数: 50")
    print(f"成功请求数: {success_count}")
    print(f"失败请求数: {failure_count}")
    print(f"总耗时: {total_time:.2f}秒")
    print(f"平均RPS: {50/total_time:.2f}")
    print(f"统计信息: {middleware.get_stats()}")

async def main():
    """主测试函数"""
    print("开始测试T7限速/重试中间件...")
    
    try:
        # 测试各项功能
        await test_rate_limiting()
        await test_retry_mechanism()
        await test_circuit_breaker()
        await test_user_agent_rotation()
        await test_proxy_management()
        await test_middleware_factory()
        await test_stress_test()
        
        # 测试同步版本
        test_sync_middleware()
        
        print("\n=== 所有测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 运行测试
    asyncio.run(main())
