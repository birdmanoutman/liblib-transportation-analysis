#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T7 限速/重试中间件
提供全局 RPS 控制、指数退避、熔断机制、随机 UA 和可选代理功能
"""

import os
import sys
import time
import random
import logging
import asyncio
import aiohttp
import requests
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
from pathlib import Path
import threading
from contextlib import asynccontextmanager, contextmanager

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """熔断器状态"""
    CLOSED = "CLOSED"      # 正常状态
    OPEN = "OPEN"          # 熔断状态
    HALF_OPEN = "HALF_OPEN"  # 半开状态

@dataclass
class RetryConfig:
    """重试配置"""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    jitter: bool = True
    retry_on_status_codes: List[int] = field(default_factory=lambda: [429, 500, 502, 503, 504])

@dataclass
class RateLimitConfig:
    """限速配置"""
    max_requests_per_second: float = 4.0
    max_concurrent: int = 5
    burst_size: int = 10
    time_window: float = 1.0

@dataclass
class CircuitBreakerConfig:
    """熔断器配置"""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    expected_exception: type = Exception
    success_threshold: int = 2

@dataclass
class ProxyConfig:
    """代理配置"""
    enabled: bool = False
    proxies: List[str] = field(default_factory=list)
    rotation_strategy: str = "round_robin"  # round_robin, random, failover
    health_check_interval: float = 300.0  # 5分钟

class UserAgentRotator:
    """用户代理轮换器"""
    
    def __init__(self, custom_agents: List[str] = None):
        self.custom_agents = custom_agents or [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        self.current_index = 0
        self.lock = threading.Lock()
    
    def get_random_agent(self) -> str:
        """获取随机用户代理"""
        return random.choice(self.custom_agents)
    
    def get_next_agent(self) -> str:
        """获取下一个用户代理（轮询）"""
        with self.lock:
            agent = self.custom_agents[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.custom_agents)
            return agent

class ProxyManager:
    """代理管理器"""
    
    def __init__(self, config: ProxyConfig):
        self.config = config
        self.proxies = config.proxies.copy()
        self.current_index = 0
        self.failed_proxies = set()
        self.last_health_check = time.time()
        self.lock = threading.Lock()
    
    def get_next_proxy(self) -> Optional[str]:
        """获取下一个可用代理"""
        if not self.config.enabled or not self.proxies:
            return None
        
        with self.lock:
            # 健康检查
            if time.time() - self.last_health_check > self.config.health_check_interval:
                self._health_check()
            
            if self.config.rotation_strategy == "random":
                available_proxies = [p for p in self.proxies if p not in self.failed_proxies]
                if available_proxies:
                    return random.choice(available_proxies)
            elif self.config.rotation_strategy == "round_robin":
                for _ in range(len(self.proxies)):
                    proxy = self.proxies[self.current_index]
                    self.current_index = (self.current_index + 1) % len(self.proxies)
                    if proxy not in self.failed_proxies:
                        return proxy
            elif self.config.rotation_strategy == "failover":
                # 故障转移：优先使用未失败的代理
                available_proxies = [p for p in self.proxies if p not in self.failed_proxies]
                if available_proxies:
                    return available_proxies[0]
                # 如果所有代理都失败，重置失败状态
                self.failed_proxies.clear()
                return self.proxies[0] if self.proxies else None
        
        return None
    
    def mark_proxy_failed(self, proxy: str):
        """标记代理失败"""
        if proxy in self.proxies:
            self.failed_proxies.add(proxy)
            logger.warning(f"代理 {proxy} 标记为失败")
    
    def _health_check(self):
        """代理健康检查"""
        self.last_health_check = time.time()
        # 简单的健康检查：尝试连接
        for proxy in self.proxies[:]:
            try:
                # 这里可以添加更复杂的健康检查逻辑
                pass
            except Exception:
                self.failed_proxies.add(proxy)
                logger.warning(f"代理 {proxy} 健康检查失败")

class RateLimiter:
    """速率限制器"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.requests = []
        self.semaphore = asyncio.Semaphore(config.max_concurrent)
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """获取请求许可"""
        async with self.lock:
            now = time.time()
            # 清理过期的请求记录
            self.requests = [req_time for req_time in self.requests 
                           if now - req_time < self.config.time_window]
            
            if len(self.requests) >= self.config.max_requests_per_second:
                # 需要等待
                wait_time = self.config.time_window - (now - self.requests[0])
                if wait_time > 0:
                    logger.debug(f"速率限制：等待 {wait_time:.2f} 秒")
                    await asyncio.sleep(wait_time)
            
            self.requests.append(time.time())
        
        # 并发限制
        await self.semaphore.acquire()
    
    def release(self):
        """释放并发许可"""
        self.semaphore.release()

class CircuitBreaker:
    """熔断器"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0
        self.lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """执行函数，应用熔断逻辑"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("熔断器状态：OPEN -> HALF_OPEN")
            else:
                raise Exception("熔断器处于OPEN状态，拒绝请求")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """异步执行函数，应用熔断逻辑"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("熔断器状态：OPEN -> HALF_OPEN")
            else:
                raise Exception("熔断器处于OPEN状态，拒绝请求")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """成功回调"""
        with self.lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
                    logger.info("熔断器状态：HALF_OPEN -> CLOSED")
            else:
                self.failure_count = 0
    
    def _on_failure(self):
        """失败回调"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
                logger.warning(f"熔断器状态：CLOSED -> OPEN (失败次数: {self.failure_count})")
    
    def _should_attempt_reset(self) -> bool:
        """是否应该尝试重置"""
        if self.last_failure_time is None:
            return False
        
        return time.time() - self.last_failure_time >= self.config.recovery_timeout

class RetryHandler:
    """重试处理器"""
    
    def __init__(self, config: RetryConfig):
        self.config = config
    
    async def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """执行函数，应用重试逻辑"""
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                if attempt > 0:
                    delay = self._calculate_delay(attempt)
                    logger.info(f"重试 {attempt}/{self.config.max_retries}，等待 {delay:.2f} 秒")
                    await asyncio.sleep(delay)
                
                return await func(*args, **kwargs)
            
            except Exception as e:
                last_exception = e
                if not self._should_retry(e):
                    raise e
                
                if attempt == self.config.max_retries:
                    logger.error(f"重试 {self.config.max_retries} 次后仍然失败: {e}")
                    raise e
                
                logger.warning(f"第 {attempt + 1} 次尝试失败: {e}")
        
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """计算重试延迟"""
        delay = self.config.base_delay * (self.config.backoff_factor ** (attempt - 1))
        
        if self.config.jitter:
            # 添加随机抖动
            jitter = random.uniform(0, 0.1 * delay)
            delay += jitter
        
        return min(delay, self.config.max_delay)
    
    def _should_retry(self, exception: Exception) -> bool:
        """判断是否应该重试"""
        # 检查状态码
        if hasattr(exception, 'response') and hasattr(exception.response, 'status_code'):
            return exception.response.status_code in self.config.retry_on_status_codes
        
        # 检查异常类型
        return isinstance(exception, self.config.expected_exception)

class RateLimitMiddleware:
    """限速/重试中间件主类"""
    
    def __init__(self, 
                 rate_limit_config: RateLimitConfig = None,
                 retry_config: RetryConfig = None,
                 circuit_breaker_config: CircuitBreakerConfig = None,
                 proxy_config: ProxyConfig = None):
        
        # 使用默认配置
        self.rate_limit_config = rate_limit_config or RateLimitConfig()
        self.retry_config = retry_config or RetryConfig()
        self.circuit_breaker_config = circuit_breaker_config or CircuitBreakerConfig()
        self.proxy_config = proxy_config or ProxyConfig()
        
        # 初始化组件
        self.rate_limiter = RateLimiter(self.rate_limit_config)
        self.retry_handler = RetryHandler(self.retry_config)
        self.circuit_breaker = CircuitBreaker(self.circuit_breaker_config)
        self.ua_rotator = UserAgentRotator()
        self.proxy_manager = ProxyManager(self.proxy_config)
        
        # 统计信息
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'retried_requests': 0,
            'circuit_breaker_trips': 0,
            'rate_limit_delays': 0
        }
    
    async def make_request(self, 
                          method: str, 
                          url: str, 
                          **kwargs) -> aiohttp.ClientResponse:
        """发送HTTP请求，应用所有中间件逻辑"""
        self.stats['total_requests'] += 1
        
        # 获取用户代理
        user_agent = self.ua_rotator.get_next_agent()
        headers = kwargs.get('headers', {})
        headers['User-Agent'] = user_agent
        kwargs['headers'] = headers
        
        # 获取代理
        proxy = self.proxy_manager.get_next_proxy()
        if proxy:
            kwargs['proxy'] = proxy
        
        # 应用速率限制
        await self.rate_limiter.acquire()
        
        try:
            # 应用熔断器
            response = await self.circuit_breaker.call_async(
                self._execute_request, method, url, **kwargs
            )
            
            self.stats['successful_requests'] += 1
            return response
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            
            # 标记代理失败
            if proxy and self._is_proxy_error(e):
                self.proxy_manager.mark_proxy_failed(proxy)
            
            raise e
        
        finally:
            self.rate_limiter.release()
    
    async def _execute_request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """执行实际的HTTP请求"""
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, **kwargs) as response:
                # 检查是否需要重试
                if response.status in self.retry_config.retry_on_status_codes:
                    self.stats['retried_requests'] += 1
                    # 这里可以触发重试逻辑
                
                return response
    
    def _is_proxy_error(self, exception: Exception) -> bool:
        """判断是否为代理相关错误"""
        proxy_errors = [
            'Proxy connection failed',
            'Proxy authentication required',
            'Proxy server unreachable',
            'Connection timeout'
        ]
        
        error_str = str(exception).lower()
        return any(err.lower() in error_str for err in proxy_errors)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = self.stats.copy()
        stats['success_rate'] = (self.stats['successful_requests'] / 
                               max(self.stats['total_requests'], 1)) * 100
        stats['circuit_breaker_state'] = self.circuit_breaker.state.value
        return stats
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'retried_requests': 0,
            'circuit_breaker_trips': 0,
            'rate_limit_delays': 0
        }

# 同步版本的中间件（用于requests库）
class SyncRateLimitMiddleware:
    """同步版本限速/重试中间件"""
    
    def __init__(self, 
                 rate_limit_config: RateLimitConfig = None,
                 retry_config: RetryConfig = None,
                 circuit_breaker_config: CircuitBreakerConfig = None,
                 proxy_config: ProxyConfig = None):
        
        self.rate_limit_config = rate_limit_config or RateLimitConfig()
        self.retry_config = retry_config or RetryConfig()
        self.circuit_breaker_config = circuit_breaker_config or CircuitBreakerConfig()
        self.proxy_config = proxy_config or ProxyConfig()
        
        # 初始化组件
        self.ua_rotator = UserAgentRotator()
        self.proxy_manager = ProxyManager(self.proxy_config)
        self.circuit_breaker = CircuitBreaker(self.circuit_breaker_config)
        
        # 简单的限速器
        self.last_request_time = 0
        self.min_interval = 1.0 / self.rate_limit_config.max_requests_per_second
        
        # 统计信息
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'retried_requests': 0
        }
    
    def make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """发送HTTP请求"""
        self.stats['total_requests'] += 1
        
        # 应用速率限制
        self._apply_rate_limit()
        
        # 获取用户代理和代理
        headers = kwargs.get('headers', {})
        headers['User-Agent'] = self.ua_rotator.get_next_agent()
        kwargs['headers'] = headers
        
        proxy = self.proxy_manager.get_next_proxy()
        if proxy:
            kwargs['proxies'] = {'http': proxy, 'https': proxy}
        
        # 应用熔断器
        try:
            response = self.circuit_breaker.call(
                requests.request, method, url, **kwargs
            )
            
            self.stats['successful_requests'] += 1
            return response
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            
            if proxy and self._is_proxy_error(e):
                self.proxy_manager.mark_proxy_failed(proxy)
            
            raise e
    
    def _apply_rate_limit(self):
        """应用速率限制"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _is_proxy_error(self, exception: Exception) -> bool:
        """判断是否为代理相关错误"""
        proxy_errors = [
            'Proxy connection failed',
            'Proxy authentication required',
            'Proxy server unreachable',
            'Connection timeout'
        ]
        
        error_str = str(exception).lower()
        return any(err.lower() in error_str for err in proxy_errors)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = self.stats.copy()
        stats['success_rate'] = (self.stats['successful_requests'] / 
                               max(self.stats['total_requests'], 1)) * 100
        stats['circuit_breaker_state'] = self.circuit_breaker.state.value
        return stats

# 装饰器版本
def with_rate_limit(middleware: RateLimitMiddleware):
    """装饰器：为函数添加限速/重试功能"""
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            return await middleware.make_request(func, *args, **kwargs)
        return wrapper
    return decorator

# 配置加载函数
def load_middleware_config(config_path: str = None) -> Dict[str, Any]:
    """加载中间件配置"""
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # 默认配置
    return {
        'rate_limit': {
            'max_requests_per_second': 4.0,
            'max_concurrent': 5,
            'burst_size': 10,
            'time_window': 1.0
        },
        'retry': {
            'max_retries': 3,
            'base_delay': 1.0,
            'max_delay': 60.0,
            'backoff_factor': 2.0,
            'jitter': True,
            'retry_on_status_codes': [429, 500, 502, 503, 504]
        },
        'circuit_breaker': {
            'failure_threshold': 5,
            'recovery_timeout': 60.0,
            'success_threshold': 2
        },
        'proxy': {
            'enabled': False,
            'proxies': [],
            'rotation_strategy': 'round_robin',
            'health_check_interval': 300.0
        }
    }

# 工厂函数
def create_middleware(config: Dict[str, Any] = None, 
                     async_mode: bool = True) -> Union[RateLimitMiddleware, SyncRateLimitMiddleware]:
    """创建中间件实例"""
    if config is None:
        config = load_middleware_config()
    
    rate_limit_config = RateLimitConfig(**config.get('rate_limit', {}))
    retry_config = RetryConfig(**config.get('retry', {}))
    circuit_breaker_config = CircuitBreakerConfig(**config.get('circuit_breaker', {}))
    proxy_config = ProxyConfig(**config.get('proxy', {}))
    
    if async_mode:
        return RateLimitMiddleware(
            rate_limit_config, retry_config, circuit_breaker_config, proxy_config
        )
    else:
        return SyncRateLimitMiddleware(
            rate_limit_config, retry_config, circuit_breaker_config, proxy_config
        )

if __name__ == "__main__":
    # 测试代码
    async def test_middleware():
        """测试中间件功能"""
        # 创建中间件
        middleware = create_middleware()
        
        # 测试请求
        try:
            response = await middleware.make_request(
                'GET', 'https://httpbin.org/get'
            )
            print(f"请求成功: {response.status}")
        except Exception as e:
            print(f"请求失败: {e}")
        
        # 显示统计信息
        print("统计信息:", middleware.get_stats())
    
    # 运行测试
    asyncio.run(test_middleware())
