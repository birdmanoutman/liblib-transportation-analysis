# T7 限速/重试中间件

## 概述

T7中间件是一个功能完整的HTTP请求管理中间件，为Liblib汽车交通采集系统提供：

- **全局RPS控制**：精确控制请求频率，避免触发限流
- **指数退避重试**：智能重试机制，提高请求成功率
- **熔断保护**：自动熔断故障服务，防止雪崩效应
- **随机UA轮换**：动态切换用户代理，降低被识别风险
- **可选代理支持**：支持多种代理轮换策略
- **可配置化**：灵活的参数配置，适应不同场景需求

## 核心特性

### 1. 速率限制 (Rate Limiting)
- 基于令牌桶算法的精确限速
- 支持突发流量控制
- 并发请求数量限制
- 可配置的时间窗口

### 2. 重试机制 (Retry Mechanism)
- 指数退避算法
- 随机抖动避免惊群效应
- 可配置重试次数和延迟
- 智能状态码重试判断

### 3. 熔断器 (Circuit Breaker)
- 三种状态：CLOSED、OPEN、HALF_OPEN
- 可配置失败阈值和恢复超时
- 自动状态转换
- 防止故障扩散

### 4. 用户代理轮换 (User Agent Rotation)
- 内置多种现代浏览器UA
- 支持自定义UA列表
- 轮询和随机两种策略
- 线程安全的轮换机制

### 5. 代理管理 (Proxy Management)
- 支持HTTP/HTTPS/SOCKS代理
- 多种轮换策略：轮询、随机、故障转移
- 代理健康检查
- 失败代理自动标记

## 快速开始

### 安装依赖

```bash
pip install aiohttp requests
```

### 基本使用

#### 异步版本

```python
from scripts.scraping.rate_limit_middleware import RateLimitMiddleware

# 创建中间件
middleware = RateLimitMiddleware()

# 发送请求
response = await middleware.make_request('GET', 'https://api.example.com/data')
```

#### 同步版本

```python
from scripts.scraping.rate_limit_middleware import SyncRateLimitMiddleware

# 创建同步中间件
middleware = SyncRateLimitMiddleware()

# 发送请求
response = middleware.make_request('GET', 'https://api.example.com/data')
```

### 自定义配置

```python
from scripts.scraping.rate_limit_middleware import (
    RateLimitMiddleware, RateLimitConfig, RetryConfig, 
    CircuitBreakerConfig, ProxyConfig
)

# 自定义配置
rate_config = RateLimitConfig(
    max_requests_per_second=2.0,
    max_concurrent=3
)

retry_config = RetryConfig(
    max_retries=5,
    base_delay=2.0,
    backoff_factor=2.0
)

cb_config = CircuitBreakerConfig(
    failure_threshold=3,
    recovery_timeout=60.0
)

proxy_config = ProxyConfig(
    enabled=True,
    proxies=['http://proxy1:8080', 'http://proxy2:8080'],
    rotation_strategy='round_robin'
)

# 创建中间件
middleware = RateLimitMiddleware(
    rate_limit_config=rate_config,
    retry_config=retry_config,
    circuit_breaker_config=cb_config,
    proxy_config=proxy_config
)
```

## 配置参数详解

### RateLimitConfig

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `max_requests_per_second` | float | 4.0 | 每秒最大请求数 |
| `max_concurrent` | int | 5 | 最大并发请求数 |
| `burst_size` | int | 10 | 突发流量大小 |
| `time_window` | float | 1.0 | 时间窗口（秒） |

### RetryConfig

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `max_retries` | int | 3 | 最大重试次数 |
| `base_delay` | float | 1.0 | 基础延迟时间（秒） |
| `max_delay` | float | 60.0 | 最大延迟时间（秒） |
| `backoff_factor` | float | 2.0 | 退避因子 |
| `jitter` | bool | True | 是否添加随机抖动 |
| `retry_on_status_codes` | List[int] | [429,500,502,503,504] | 重试状态码列表 |

### CircuitBreakerConfig

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `failure_threshold` | int | 5 | 失败阈值 |
| `recovery_timeout` | float | 60.0 | 恢复超时（秒） |
| `success_threshold` | int | 2 | 成功阈值 |

### ProxyConfig

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | bool | False | 是否启用代理 |
| `proxies` | List[str] | [] | 代理服务器列表 |
| `rotation_strategy` | str | 'round_robin' | 轮换策略 |
| `health_check_interval` | float | 300.0 | 健康检查间隔（秒） |

## 使用场景

### 1. 与T4采集器集成

```python
from scripts.scraping.integration_example import EnhancedT4Collector

# 创建增强版T4采集器
collector = EnhancedT4Collector()

# 采集数据
data = await collector.collect_pages(start_page=1, end_page=5, tag="汽车交通")
```

### 2. 与T5采集器集成

```python
from scripts.scraping.integration_example import EnhancedT5Collector

# 创建增强版T5采集器
collector = EnhancedT5Collector()

# 获取作品详情
details = await collector.collect_work_details(['slug1', 'slug2', 'slug3'])
```

### 3. 完整流水线

```python
from scripts.scraping.integration_example import IntegratedScrapingPipeline

# 创建流水线
pipeline = IntegratedScrapingPipeline()

# 运行完整采集流程
result = await pipeline.run_pipeline(start_page=1, end_page=10, tag="汽车交通")
```

## 监控和统计

### 获取统计信息

```python
# 获取中间件统计
stats = middleware.get_stats()
print(f"总请求数: {stats['total_requests']}")
print(f"成功率: {stats['success_rate']:.1f}%")
print(f"熔断器状态: {stats['circuit_breaker_state']}")
```

### 重置统计

```python
# 重置统计信息
middleware.reset_stats()
```

## 环境变量配置

支持通过环境变量配置中间件参数：

```bash
# 速率限制
export MIDDLEWARE_RPS=2.0
export MIDDLEWARE_MAX_CONCURRENT=3

# 重试配置
export MIDDLEWARE_MAX_RETRIES=5
export MIDDLEWARE_BASE_DELAY=2.0

# 熔断器配置
export MIDDLEWARE_FAILURE_THRESHOLD=3
export MIDDLEWARE_RECOVERY_TIMEOUT=60.0

# 代理配置
export MIDDLEWARE_PROXY_ENABLED=true
export MIDDLEWARE_PROXIES="http://proxy1:8080,http://proxy2:8080"
```

## 测试

### 运行单元测试

```bash
cd src/scraping
python test_rate_limit_middleware.py
```

### 运行集成测试

```bash
cd src/scraping
python integration_example.py
```

## 性能优化建议

### 1. 限速配置
- 生产环境建议RPS不超过5.0
- 根据目标网站的实际限流策略调整
- 监控429状态码出现频率

### 2. 重试策略
- 基础延迟建议1-2秒
- 退避因子建议2.0-3.0
- 最大重试次数建议3-5次

### 3. 熔断器配置
- 失败阈值建议5-10次
- 恢复超时建议60-300秒
- 根据服务稳定性调整

### 4. 代理使用
- 代理数量建议3-5个
- 轮换策略建议使用round_robin
- 定期检查代理健康状态

## 故障排除

### 常见问题

1. **请求被限流**
   - 降低RPS配置
   - 增加重试延迟
   - 检查目标网站限流策略

2. **熔断器频繁触发**
   - 增加失败阈值
   - 延长恢复超时
   - 检查网络和服务稳定性

3. **代理连接失败**
   - 验证代理服务器状态
   - 检查代理认证信息
   - 更新代理列表

### 日志分析

中间件提供详细的日志信息，包括：
- 请求成功/失败统计
- 重试次数和延迟
- 熔断器状态变化
- 代理轮换记录

## 扩展开发

### 自定义重试策略

```python
class CustomRetryHandler(RetryHandler):
    def _should_retry(self, exception: Exception) -> bool:
        # 自定义重试判断逻辑
        if isinstance(exception, CustomException):
            return True
        return super()._should_retry(exception)
```

### 自定义限速算法

```python
class CustomRateLimiter(RateLimiter):
    async def acquire(self):
        # 自定义限速逻辑
        # 例如：基于IP的限速
        pass
```

## 版本历史

- **v1.0.0**: 初始版本，支持基本限速和重试功能
- **v1.1.0**: 添加熔断器功能
- **v1.2.0**: 支持用户代理轮换和代理管理
- **v1.3.0**: 优化性能和配置管理

## 贡献指南

欢迎提交Issue和Pull Request来改进这个中间件。

## 许可证

本项目采用MIT许可证。
