# T6 媒体下载器

## 📋 概述

T6媒体下载器是Liblib汽车交通采集系统的核心组件，负责并发下载图组到S3存储，支持OSS图片处理参数控制，具备完善的失败重试与校验机制。

## ✨ 核心功能

### 1. 并发下载
- 支持多线程并发下载，可配置工作线程数
- 智能限速控制，避免对源站造成压力
- 优雅关闭机制，支持信号中断

### 2. S3存储集成
- 支持标准S3和MinIO存储
- 自动生成规范的S3存储键
- 文件去重检查，避免重复下载

### 3. OSS图片处理
- 集成`x-oss-process`参数控制
- 支持图片尺寸调整、格式转换、质量优化
- 可配置目标宽度、格式和质量

### 4. 数据校验
- 文件大小验证
- MD5内容哈希校验
- 下载状态跟踪

### 5. 失败重试
- 指数退避重试策略
- 可配置最大重试次数
- 失败任务自动重试

## 🏗️ 架构设计

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   数据库查询     │───▶│   并发下载器     │───▶│   S3存储管理器   │
│  (待下载图片)    │    │  (ThreadPool)   │    │   (boto3)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   状态更新       │    │   限速控制器     │    │   图片处理器     │
│  (MySQL)        │    │  (RateLimiter)  │    │  (OSS参数)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 快速开始

### 1. 环境准备

确保已安装必要的依赖：

```bash
pip install boto3 mysql-connector-python python-dotenv requests
```

### 2. 环境配置

在项目根目录创建或更新`.env`文件：

```bash
# 必选：S3/MinIO配置
STORAGE_DRIVER=s3
S3_ENDPOINT=https://minio.birdmanoutman.com
S3_BUCKET=img-station
S3_REGION=us-east-1
S3_ACCESS_KEY=your_access_key
S3_SECRET_KEY=your_secret_key

# 必选：数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_NAME=cardesignspace
DB_USER=root
DB_PASSWORD=your_password

# 可选：媒体下载器配置
MEDIA_ENV=dev                    # 环境：dev/test/prod
MEDIA_MAX_WORKERS=10             # 最大工作线程数
MEDIA_RPS=5.0                    # 请求速率限制
MEDIA_MAX_RETRIES=3              # 最大重试次数
MEDIA_TIMEOUT=30                 # 请求超时时间(秒)
MEDIA_TARGET_WIDTH=1024          # 目标图片宽度
MEDIA_TARGET_FORMAT=webp         # 目标图片格式
MEDIA_QUALITY=85                 # 图片质量(1-100)
MEDIA_VERIFY_SIZE=true           # 是否验证文件大小
MEDIA_VERIFY_HASH=true           # 是否验证文件哈希
MEDIA_MIN_SIZE=1024              # 最小文件大小(字节)
```

### 3. 运行测试

在运行主程序前，建议先运行测试脚本验证环境：

```bash
cd src/download
python test_t6_media_downloader.py
```

### 4. 执行下载

```bash
# 开发环境
MEDIA_ENV=dev python t6_media_downloader.py

# 生产环境
MEDIA_ENV=prod python t6_media_downloader.py

# 自定义配置
python t6_media_downloader.py
```

## 📊 配置说明

### 环境配置

| 环境 | 工作线程 | 请求速率 | 重试次数 | 超时时间 | 日志级别 |
|------|----------|----------|----------|----------|----------|
| dev  | 5        | 2.0 RPS  | 2        | 15s      | DEBUG    |
| test | 8        | 3.0 RPS  | 3        | 20s      | INFO     |
| prod | 20       | 8.0 RPS  | 5        | 45s      | WARNING  |

### 图片处理配置

| 参数 | 说明 | 默认值 | 范围 |
|------|------|--------|------|
| `MEDIA_TARGET_WIDTH` | 目标图片宽度 | 1024 | >0 |
| `MEDIA_TARGET_FORMAT` | 目标图片格式 | webp | jpg/png/gif/webp |
| `MEDIA_QUALITY` | 图片质量 | 85 | 1-100 |

### OSS处理参数

生成的OSS处理URL格式：
```
原始URL?x-oss-process=image/resize,w_1024,m_lfit/format,webp/quality,Q_85
```

- `resize,w_1024,m_lfit`: 调整宽度为1024px，保持比例
- `format,webp`: 转换为WebP格式
- `quality,Q_85`: 设置质量为85%

## 🔧 高级用法

### 1. 编程接口

```python
from t6_media_downloader import MediaDownloader, MediaDownloaderConfig
from t6_media_config import load_media_config

# 加载配置
config = load_media_config('prod')

# 创建下载器
downloader = MediaDownloader(config)

# 执行批量下载
stats = downloader.download_batch(max_images=1000)

# 重试失败的图片
retry_stats = downloader.retry_failed_images()

# 查看统计信息
print(f"成功率: {stats['successful'] / stats['total'] * 100:.2f}%")
```

### 2. 自定义配置

```python
from t6_media_config import MediaConfig

class CustomConfig(MediaConfig):
    def __init__(self):
        super().__init__()
        self.max_workers = 15
        self.requests_per_second = 6.0
        self.target_width = 2048
        self.quality = 90

# 使用自定义配置
downloader = MediaDownloader(CustomConfig())
```

### 3. 监控集成

```python
# 启用监控
config.enable_monitoring = True
config.metrics_interval = 30

# 监控指标
- 下载成功率
- 处理速度
- 错误率
- 重试次数
```

## 📈 性能优化

### 1. 并发调优

```bash
# 根据网络带宽调整
MEDIA_MAX_WORKERS=20          # 高带宽环境
MEDIA_MAX_WORKERS=5           # 低带宽环境

# 根据源站承受能力调整
MEDIA_RPS=10.0                # 高承受能力
MEDIA_RPS=2.0                 # 低承受能力
```

### 2. 存储优化

```bash
# 根据存储性能调整
MEDIA_TARGET_WIDTH=512        # 快速存储
MEDIA_TARGET_WIDTH=2048       # 高性能存储

# 根据网络条件调整
MEDIA_QUALITY=70              # 慢速网络
MEDIA_QUALITY=95              # 快速网络
```

## 🐛 故障排除

### 常见问题

#### 1. S3连接失败

```bash
# 检查配置
echo $S3_ENDPOINT
echo $S3_BUCKET
echo $S3_ACCESS_KEY

# 测试连接
python test_t6_media_downloader.py
```

#### 2. 数据库连接失败

```bash
# 检查数据库服务
mysql -h localhost -u root -p

# 检查表结构
USE cardesignspace;
SHOW TABLES LIKE 'work_images';
DESCRIBE work_images;
```

#### 3. 下载失败率高

```bash
# 降低并发数
export MEDIA_MAX_WORKERS=5

# 降低请求速率
export MEDIA_RPS=2.0

# 增加超时时间
export MEDIA_TIMEOUT=60
```

### 日志分析

```bash
# 查看日志
tail -f t6_media_downloader.log

# 分析错误
grep "ERROR" t6_media_downloader.log | tail -20

# 统计成功率
grep "批量下载完成" t6_media_downloader.log | tail -5
```

## 📋 验收标准

根据工单T6要求，验收标准如下：

- ✅ **下载成功率 ≥99%**
- ✅ **命名与路径规范通过**
- ✅ **支持x-oss-process控制格式与尺寸**
- ✅ **失败重试与校验（大小/哈希）**
- ✅ **与T5后半段并行执行**

## 🔄 与T5集成

T6媒体下载器设计为与T5详情采集器并行执行：

```python
# T5执行过程中，T6可以并行下载媒体
from enhanced_detail_collector import EnhancedDetailCollector
from t6_media_downloader import MediaDownloader

# T5采集详情
detail_collector = EnhancedDetailCollector()
detail_collector.collect_details_batch(slugs)

# T6并行下载媒体（在另一个进程/线程中）
media_downloader = MediaDownloader()
media_downloader.download_batch()
```

## 📚 相关文档

- [工单计划](../docs/tickets_transportation_scraper.md)
- [PRD文档](../docs/PRD_transportation_scraper.md)
- [数据库设计](../database/create_tables.sql)
- [T5详情采集器](../scraping/README_T5_DetailCollector.md)

## 🤝 贡献指南

1. 遵循项目代码规范
2. 添加必要的测试用例
3. 更新相关文档
4. 提交前运行测试套件

## �� 许可证

本项目遵循项目主许可证。
