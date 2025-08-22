# T8 断点续采与失败补偿模块 - 使用说明

## 概述

T8断点续采与失败补偿模块是Liblib汽车交通数据采集系统的重要组成部分，实现了工单T8的所有要求：

- ✅ **持久化页码/slug状态**：自动保存和恢复采集进度
- ✅ **失败队列定时重试**：智能重试机制，支持指数退避
- ✅ **运行恢复验证**：完整性检查，确保数据不丢失、不重复

## 功能特性

### 🔄 断点续采
- **状态持久化**：自动保存当前页码、游标、处理数量等状态
- **智能恢复**：中断后可从上次停止的地方继续采集
- **多任务支持**：支持列表采集、详情采集、图片下载等多种任务类型
- **元数据管理**：记录任务标签、排序方式、批次信息等元数据

### 🔁 失败重试
- **自动重试**：失败任务自动进入重试队列
- **指数退避**：重试间隔逐渐增加，避免对服务器造成压力
- **可配置策略**：支持自定义最大重试次数、重试延迟等参数
- **并发处理**：多线程并发处理重试任务，提高效率

### ✅ 完整性验证
- **数据完整性检查**：验证采集数据的完整性和一致性
- **重复检测**：自动检测重复数据，避免重复入库
- **缺失检测**：识别缺失的数据项，支持补采
- **状态验证**：验证断点续采点和失败任务的有效性

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   StateManager  │    │  RetryManager   │    │ ResumeValidator │
│                 │    │                 │    │                 │
│ • 状态持久化    │    │ • 失败重试      │    │ • 完整性验证    │
│ • 断点续采点    │    │ • 定时检查      │    │ • 数据校验      │
│ • 失败任务队列  │    │ • 并发处理      │    │ • 问题报告      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ T8ResumeAndRetry│
                    │                 │
                    │ • 统一接口      │
                    │ • 服务管理      │
                    │ • 配置管理      │
                    └─────────────────┘
```

## 安装要求

### 系统要求
- Python 3.8+
- 支持异步编程
- 文件系统写入权限

### 依赖安装
```bash
# 安装Python依赖
pip install -r requirements.txt

# 或安装特定依赖
pip install aiohttp asyncio
```

## 配置说明

### 环境变量
在`.env`文件中配置以下变量：

```bash
# T8模块环境
T8_ENV=production                    # 运行环境：development/testing/production
T8_MAX_WORKERS=10                    # 最大重试工作线程数
T8_RETRY_CHECK_INTERVAL=15           # 重试检查间隔（秒）
T8_ENABLE_AUTO_RETRY=true            # 启用自动重试
T8_ENABLE_INTEGRITY_CHECK=true       # 启用完整性检查
```

### 配置文件
T8模块使用`t8_config.py`进行配置管理，支持多环境配置：

#### 开发环境 (development)
```python
{
    'max_workers': 3,                # 较少的工作线程
    'retry_check_interval': 60,      # 较长的检查间隔
    'enable_metrics': False,         # 禁用指标收集
    'log_level': 'DEBUG'             # 详细日志
}
```

#### 测试环境 (testing)
```python
{
    'max_workers': 2,                # 最少的工作线程
    'retry_check_interval': 120,     # 最长的检查间隔
    'enable_metrics': True,          # 启用指标收集
    'log_level': 'INFO'              # 标准日志
}
```

#### 生产环境 (production)
```python
{
    'max_workers': 10,               # 较多的工作线程
    'retry_check_interval': 15,      # 较短的检查间隔
    'enable_metrics': True,          # 启用指标收集
    'log_level': 'WARNING'           # 精简日志
}
```

## 使用方法

### 1. 快速开始

```python
from scripts.scraping.t8_resume_and_retry import T8ResumeAndRetry
from scripts.scraping.t8_config import get_config

# 获取配置
config = get_config('development')

# 创建T8实例
t8 = T8ResumeAndRetry(config)

# 启动服务
t8.start_service()

# 创建断点续采点
point_id = t8.create_resume_point(
    task_type="LIST_COLLECTION",
    current_page=5,
    total_processed=120,
    metadata={"tag": "汽车交通"}
)

# 添加失败任务
task_id = t8.add_failed_task(
    task_type="DETAIL_COLLECTION",
    target="car-model-001",
    error_message="API请求超时"
)

# 停止服务
t8.stop_service()
```

### 2. 命令行运行

#### 演示模式
```bash
# 开发环境演示
python src/scraping/run_t8_resume_retry.py --env development --mode demo

# 生产环境演示
python src/scraping/run_t8_resume_retry.py --env production --mode demo
```

#### 集成测试
```bash
# 运行集成测试
python src/scraping/run_t8_resume_retry.py --env testing --mode test

# 指定日志级别
python src/scraping/run_t8_resume_retry.py --env testing --mode test --log-level DEBUG
```

#### 配置查看
```bash
# 查看配置
python src/scraping/run_t8_resume_retry.py --mode config

# 查看特定环境配置
python src/scraping/run_t8_resume_retry.py --env production --mode config
```

### 3. 与T4/T5集成

#### 在T4列表采集器中使用
```python
from src.scraping.t8_resume_and_retry import T8ResumeAndRetry

class T4ListCollector:
    def __init__(self, config):
        # 初始化T8模块
        self.t8 = T8ResumeAndRetry(config.get('t8_config', {}))
        self.t8.start_service()
    
    async def run_collection(self, start_page=1, max_pages=None):
        try:
            # 检查是否有断点续采点
            resume_point = self.t8.get_resume_point("LIST_COLLECTION")
            if resume_point:
                start_page = resume_point.current_page
                print(f"从断点续采点恢复：第{start_page}页")
            
            # 执行采集逻辑
            for page in range(start_page, max_pages + 1):
                try:
                    # 采集逻辑...
                    
                    # 创建断点续采点
                    self.t8.create_resume_point(
                        task_type="LIST_COLLECTION",
                        current_page=page,
                        total_processed=self.works_fetched
                    )
                    
                except Exception as e:
                    # 添加失败任务
                    self.t8.add_failed_task(
                        task_type="LIST_COLLECTION",
                        target=f"page_{page}",
                        error_message=str(e)
                    )
                    
        finally:
            self.t8.stop_service()
```

#### 在T5详情采集器中使用
```python
class T5DetailCollector:
    def __init__(self, config):
        # 初始化T8模块
        self.t8 = T8ResumeAndRetry(config.get('t8_config', {}))
        self.t8.start_service()
    
    async def collect_details(self, slug_list):
        try:
            # 检查是否有断点续采点
            resume_point = self.t8.get_resume_point("DETAIL_COLLECTION")
            if resume_point and resume_point.last_slug:
                # 从上次停止的slug继续
                start_index = slug_list.index(resume_point.last_slug) + 1
                slug_list = slug_list[start_index:]
                print(f"从断点续采点恢复：{resume_point.last_slug}")
            
            for slug in slug_list:
                try:
                    # 详情采集逻辑...
                    
                    # 更新断点续采点
                    self.t8.create_resume_point(
                        task_type="DETAIL_COLLECTION",
                        current_page=1,
                        last_slug=slug,
                        total_processed=self.details_fetched
                    )
                    
                except Exception as e:
                    # 添加失败任务
                    self.t8.add_failed_task(
                        task_type="DETAIL_COLLECTION",
                        target=slug,
                        error_message=str(e)
                    )
                    
        finally:
            self.t8.stop_service()
```

## 数据格式

### 断点续采点 (ResumePoint)
```json
{
    "task_type": "LIST_COLLECTION",
    "current_page": 5,
    "last_cursor": "cursor_123",
    "last_slug": "car-model-001",
    "total_processed": 120,
    "last_update": "2024-01-15T10:30:00",
    "metadata": {
        "tag": "汽车交通",
        "sort": "latest",
        "batch": "batch_1"
    }
}
```

### 失败任务 (FailedTask)
```json
{
    "task_id": "DETAIL_COLLECTION_a1b2c3d4",
    "task_type": "DETAIL_COLLECTION",
    "target": "car-model-001",
    "error_message": "API请求超时",
    "retry_count": 2,
    "max_retries": 3,
    "next_retry_time": "2024-01-15T11:00:00",
    "created_at": "2024-01-15T10:30:00",
    "metadata": {}
}
```

### 采集状态 (CollectionState)
```json
{
    "run_id": "run_20240115_001",
    "task_type": "LIST_COLLECTION",
    "status": "RUNNING",
    "start_time": "2024-01-15T10:00:00",
    "last_update": "2024-01-15T10:30:00",
    "total_items": 1000,
    "processed_items": 120,
    "failed_items": 5,
    "resume_points": [...],
    "failed_tasks": [...]
}
```

## 监控与告警

### 指标收集
T8模块提供以下关键指标：

- **断点续采点数量**：当前活跃的断点续采点数量
- **失败任务数量**：等待重试的失败任务数量
- **重试成功率**：重试任务的成功率
- **数据完整性分数**：数据完整性的评估分数

### 告警阈值
```python
alert_thresholds = {
    'failed_task_ratio': 0.1,        # 失败任务比例超过10%
    'retry_success_rate': 0.8,       # 重试成功率低于80%
    'data_integrity_score': 0.95     # 数据完整性分数低于95%
}
```

### 日志示例
```
2024-01-15 10:30:00 - T8ResumeAndRetry - INFO - 创建断点续采点：LIST_COLLECTION_1705305000
2024-01-15 10:30:01 - T8ResumeAndRetry - INFO - 添加失败任务：DETAIL_COLLECTION_a1b2c3d4
2024-01-15 10:30:02 - T8ResumeAndRetry - INFO - 任务重试：DETAIL_COLLECTION_a1b2c3d4 (第1次)
2024-01-15 10:30:03 - T8ResumeAndRetry - INFO - 任务成功，从失败队列移除：DETAIL_COLLECTION_a1b2c3d4
```

## 故障排除

### 常见问题

#### 1. 断点续采点丢失
**症状**：重启后无法找到之前的断点续采点
**原因**：状态文件损坏或权限问题
**解决方案**：
```bash
# 检查状态文件
ls -la data/state/

# 检查文件权限
chmod 644 data/state/*.json

# 备份并重新创建状态文件
cp -r data/state data/state_backup
rm data/state/*.json
```

#### 2. 重试服务无法启动
**症状**：重试服务启动失败
**原因**：线程资源不足或配置错误
**解决方案**：
```bash
# 检查系统资源
ulimit -u

# 减少工作线程数
export T8_MAX_WORKERS=2

# 检查日志
tail -f logs/t8_resume_retry.log
```

#### 3. 完整性验证失败
**症状**：数据完整性检查失败
**原因**：数据库连接问题或数据不一致
**解决方案**：
```bash
# 检查数据库连接
python -c "from scripts.database.database_manager import DatabaseManager; print('DB OK')"

# 手动验证数据
python src/scraping/run_t8_resume_retry.py --mode test --log-level DEBUG
```

### 调试模式
```bash
# 启用调试日志
export T8_LOG_LEVEL=DEBUG

# 运行调试模式
python src/scraping/run_t8_resume_retry.py --env development --mode demo --log-level DEBUG
```

## 性能优化

### 1. 并发调优
```python
# 根据服务器性能调整并发数
config = {
    'max_workers': 10,               # 生产环境建议10-20
    'retry_check_interval': 15,      # 高负载时增加间隔
    'enable_metrics': True           # 启用监控
}
```

### 2. 存储优化
```python
# 定期清理过期数据
config = {
    'resume_point_ttl': 86400 * 7,   # 7天后清理断点续采点
    'failed_task_ttl': 86400 * 30,   # 30天后清理失败任务
    'max_resume_points': 100,        # 限制断点续采点数量
    'max_failed_tasks': 1000         # 限制失败任务数量
}
```

### 3. 内存优化
```python
# 批量处理状态更新
config = {
    'batch_update_size': 100,        # 批量更新大小
    'update_interval': 60,           # 更新间隔（秒）
    'enable_compression': True       # 启用状态压缩
}
```

## 扩展开发

### 自定义重试处理器
```python
def custom_retry_handler(target: str, metadata: dict) -> bool:
    """自定义重试处理器"""
    try:
        # 实现自定义重试逻辑
        result = process_target(target, metadata)
        return result is not None
    except Exception as e:
        logger.error(f"自定义重试失败：{target} - {e}")
        return False

# 注册自定义处理器
t8.retry_manager.register_retry_handler("CUSTOM_TASK", custom_retry_handler)
```

### 自定义完整性验证
```python
class CustomValidator(ResumeValidator):
    """自定义完整性验证器"""
    
    async def custom_validation(self, state: CollectionState) -> dict:
        """自定义验证逻辑"""
        # 实现自定义验证
        pass

# 使用自定义验证器
t8.validator = CustomValidator(t8.state_manager, t8.db_manager)
```

## 版本历史

### v1.0.0 (2024-01-15)
- ✅ 实现断点续采功能
- ✅ 实现失败重试机制
- ✅ 实现完整性验证
- ✅ 支持多环境配置
- ✅ 提供完整的测试套件
- ✅ 支持与T4/T5集成

## 贡献指南

如需修改或扩展T8模块：

1. **遵循代码规范**：使用Python类型注解，添加详细注释
2. **添加测试用例**：新功能必须包含对应的测试
3. **更新文档**：修改功能后及时更新相关文档
4. **性能测试**：确保修改不会显著影响性能

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 项目Issues：在GitHub上提交Issue
- 邮件联系：项目维护者邮箱
- 文档反馈：提交文档改进建议

---

**注意**：T8模块是T4和T5的重要补充，确保在中断后能够安全恢复，避免数据丢失和重复采集。建议在生产环境中充分测试后再部署使用。
