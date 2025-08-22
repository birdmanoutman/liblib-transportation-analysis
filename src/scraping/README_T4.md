# T4 列表采集器 - 使用说明

## 概述

T4列表采集器是Liblib汽车交通数据采集系统的核心组件，负责按标签"汽车交通"调用`img/group/search` API进行分页采集，实现断点续采、速率限制和slug队列生成。

## 功能特性

- ✅ **分页采集**: 支持分页获取汽车交通标签下的作品列表
- ✅ **断点续采**: 自动保存和恢复采集状态，支持中断后继续
- ✅ **速率限制**: 内置速率限制器，确保不超过4 RPS
- ✅ **并发控制**: 最大并发数≤5，避免对服务器造成压力
- ✅ **数据去重**: 自动检测已采集的slug，避免重复入库
- ✅ **状态持久化**: 采集状态和slug队列自动保存到文件
- ✅ **错误重试**: 内置重试机制，提高采集成功率
- ✅ **配置灵活**: 支持多环境配置和命令行参数覆盖

## 系统要求

- Python 3.8+
- MySQL 5.7+ 或 MariaDB 10.2+
- 网络访问权限（访问 api2.liblib.art）

## 依赖安装

```bash
# 安装Python依赖
pip install -r requirements.txt

# 或安装特定依赖
pip install aiomysql aiohttp python-dotenv
```

## 配置说明

### 环境变量

在`.env`文件中配置以下变量：

```bash
# 数据库配置
DB_HOST=your_db_host
DB_PORT=3306
DB_NAME=cardesignspace
DB_USER=your_username
DB_PASSWORD=your_password

# S3存储配置
STORAGE_DRIVER=s3
S3_ENDPOINT=your_s3_endpoint
S3_BUCKET=your_bucket_name
S3_ACCESS_KEY=your_access_key
S3_SECRET_KEY=your_secret_key
```

### 配置文件

T4采集器使用`t4_config.py`进行配置管理，支持多环境配置：

- **development**: 开发环境，目标100个作品，限制5页
- **testing**: 测试环境，目标50个作品，限制3页  
- **production**: 生产环境，目标1000个作品，无页数限制

## 使用方法

### 1. 快速开始

```bash
# 开发环境测试
python src/scraping/run_t4_collector.py --env development

# 生产环境采集
python src/scraping/run_t4_collector.py --env production
```

### 2. 命令行参数

```bash
# 显示帮助信息
python run_t4_collector.py --help

# 自定义目标数量
python run_t4_collector.py --target 500

# 从指定页开始采集
python run_t4_collector.py --start-page 10 --max-pages 20

# 调整速率限制
python run_t4_collector.py --rps 3 --concurrent 4

# 显示当前配置
python run_t4_collector.py --show-config

# 试运行模式
python run_t4_collector.py --dry-run
```

### 3. 环境变量覆盖

```bash
# 设置环境变量覆盖配置
export T4_TARGET_COUNT=2000
export T4_MAX_PAGES=100
export T4_MAX_REQUESTS_PER_SECOND=3

# 运行采集器
python run_t4_collector.py
```

## 运行流程

1. **初始化**: 加载配置，验证环境变量，创建必要目录
2. **状态恢复**: 检查历史状态文件，恢复断点信息
3. **API调用**: 按页调用`img/group/search` API获取作品列表
4. **数据解析**: 解析响应数据，提取作品信息
5. **数据入库**: 保存作者和作品信息到数据库
6. **队列生成**: 将slug添加到采集队列（为T5详情采集器准备）
7. **状态保存**: 保存当前采集状态，支持断点续采
8. **循环继续**: 继续下一页，直到达到目标或限制

## 输出文件

### 数据文件

- `data/fetch_state.json`: 采集状态信息
- `data/slug_queue.json`: 已采集的slug队列
- `data/fetch_queue.txt`: 待处理的slug列表（T5使用）

### 日志文件

- `logs/t4_list_collector.log`: 详细运行日志

## 数据库表结构

T4采集器会向以下表插入数据：

- **authors**: 作者信息
- **works**: 作品基本信息
- **fetch_runs**: 采集运行记录

## 监控和调试

### 1. 查看运行状态

```bash
# 查看当前配置
python run_t4_collector.py --show-config

# 查看日志
tail -f logs/t4_list_collector.log
```

### 2. 运行测试

```bash
# 运行功能测试
python src/scraping/test_t4_collector.py
```

### 3. 检查数据

```sql
-- 查看采集状态
SELECT * FROM fetch_runs ORDER BY id DESC LIMIT 5;

-- 查看作品数量
SELECT COUNT(*) FROM works;

-- 查看作者数量
SELECT COUNT(*) FROM authors;
```

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查`.env`文件中的数据库配置
   - 确认数据库服务正在运行
   - 验证网络连接和防火墙设置

2. **API请求失败**
   - 检查网络连接
   - 确认API端点可访问
   - 检查速率限制设置

3. **权限错误**
   - 确认数据库用户有足够权限
   - 检查文件系统权限

### 调试模式

```bash
# 启用调试日志
export T4_LOG_LEVEL=DEBUG
python run_t4_collector.py --env development
```

## 性能优化

### 1. 并发调优

```bash
# 根据服务器性能调整并发数
python run_t4_collector.py --concurrent 8
```

### 2. 速率限制调优

```bash
# 根据API限制调整RPS
python run_t4_collector.py --rps 5
```

### 3. 批量处理

T4采集器支持批量插入，减少数据库交互次数。

## 与T5的集成

T4采集器生成的slug队列会被T5详情采集器读取：

1. T4完成列表采集后，生成`data/fetch_queue.txt`
2. T5读取队列文件，获取需要采集详情的slug列表
3. T5调用`group/get/{slug}`等API获取详细信息
4. 形成完整的采集流水线

## 扩展性

T4采集器设计为可扩展的架构：

- 支持自定义标签（修改配置文件中的`target_tag`）
- 支持不同的排序方式（`latest`, `popular`, `random`）
- 支持自定义API参数和请求头
- 支持插件式的数据处理器

## 版本历史

- **v1.0.0**: 初始版本，支持基本的列表采集功能
- 支持断点续采、速率限制、并发控制
- 集成数据库管理和状态持久化
- 提供完整的配置管理和命令行接口

## 贡献指南

如需修改或扩展T4采集器：

1. 遵循现有的代码结构和命名规范
2. 添加适当的日志和错误处理
3. 更新配置文件和文档
4. 运行测试确保功能正常

## 许可证

本项目遵循项目整体许可证。
