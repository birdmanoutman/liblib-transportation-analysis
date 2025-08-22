# T5 详情采集器 - 使用说明

## 📋 概述

T5 详情采集器是 Liblib 汽车交通数据采集系统的核心组件，负责实现：

- `group/get/{slug}` 接口调用 - 获取作品详情
- `author/{slug}` 接口调用 - 获取作者信息  
- 可选评论落库 - 支持评论数据采集
- 字段校验与缺省策略 - 确保数据质量
- 与 T4 流水线并行，与 T6 局部并行

## 🚀 快速开始

### 1. 环境准备

确保已安装必要的依赖：

```bash
pip install -r requirements.txt
```

### 2. 数据库配置

在 `.env` 文件中配置数据库连接信息：

```env
DB_HOST=your_db_host
DB_PORT=3306
DB_NAME=cardesignspace
DB_USER=your_username
DB_PASSWORD=your_password
```

### 3. 运行测试

首先测试API接口是否正常：

```bash
cd scripts/scraping
python test_detail_collector.py
```

### 4. 运行采集器

```bash
# 基础版本
python detail_collector.py

# 增强版本（推荐）
python enhanced_detail_collector.py
```

## 📁 文件结构

```
scripts/scraping/
├── detail_collector.py              # 基础版详情采集器
├── enhanced_detail_collector.py     # 增强版详情采集器（推荐）
├── detail_collector_config.py       # 配置文件管理
├── test_detail_collector.py         # API测试脚本
└── README_T5_DetailCollector.md    # 本文档
```

## ⚙️ 配置选项

### 基础配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `max_workers` | 最大并发工作线程数 | 5 |
| `requests_per_second` | 每秒请求数限制 | 4.0 |
| `collect_comments` | 是否采集评论 | true |
| `collect_author_info` | 是否采集作者信息 | true |
| `strict_validation` | 严格字段验证 | false |

### 高级配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `api_timeout` | API请求超时时间（秒） | 30 |
| `api_retry_count` | API重试次数 | 3 |
| `api_retry_delay` | API重试延迟（秒） | 2.0 |
| `skip_invalid_works` | 跳过无效作品 | true |
| `save_raw_data` | 保存原始API响应 | true |

## 🔧 使用方法

### 1. 基础用法

```python
from detail_collector import DetailCollector

# 创建采集器
collector = DetailCollector(max_workers=5)

# 批量采集详情
slugs = ["slug1", "slug2", "slug3"]
stats = collector.collect_details_batch(slugs)

# 获取统计信息
print(f"成功率: {stats['success_rate']:.2f}%")

# 关闭连接
collector.close()
```

### 2. 增强版用法

```python
from enhanced_detail_collector import EnhancedDetailCollector
from detail_collector_config import load_config

# 加载配置
config = load_config()

# 创建增强版采集器
collector = EnhancedDetailCollector(config)

# 批量采集详情
slugs = ["slug1", "slug2", "slug3"]
stats = collector.collect_details_batch(slugs)

# 保存统计信息
collector.save_stats_to_file('my_collection_stats.json')

# 关闭连接
collector.close()
```

### 3. 自定义配置

```python
from detail_collector_config import CollectorConfig

# 创建自定义配置
config = CollectorConfig(
    db_host='localhost',
    db_port=3306,
    db_name='cardesignspace',
    db_user='root',
    db_password='password',
    max_workers=10,
    requests_per_second=6.0,
    collect_comments=True,
    strict_validation=True
)

# 验证配置
errors = config.validate()
if errors:
    print("配置错误:", errors)
    return

# 保存配置到文件
config.save_to_file('custom_config.json')
```

## 📊 API接口说明

### 1. 作品详情接口

**接口**: `POST /api/www/img/group/get/{slug}`

**请求参数**:
```json
{
    "timestamp": 1234567890123
}
```

**响应字段**:
- `slug`: 作品唯一标识
- `title`: 作品标题
- `publishedAt`: 发布时间
- `tags`: 标签列表
- `prompt`: 正向提示词
- `negativePrompt`: 负向提示词
- `sampler`: 采样器
- `steps`: 步数
- `cfgScale`: CFG比例
- `width`: 图片宽度
- `height`: 图片高度
- `seed`: 随机种子
- `likeCount`: 点赞数
- `favoriteCount`: 收藏数
- `commentCount`: 评论数
- `authorSlug`: 作者标识

### 2. 作者信息接口

**接口**: `POST /api/www/img/author/{slug}`

**请求参数**:
```json
{
    "timestamp": 1234567890123
}
```

**响应字段**:
- `id`: 作者ID
- `name`: 作者昵称
- `avatar`: 头像URL
- `profileUrl`: 主页URL
- `workCount`: 作品数量

### 3. 评论接口

**接口**: `POST /api/www/community/commentList`

**请求参数**:
```json
{
    "workId": "work_id",
    "page": 1,
    "pageSize": 50,
    "sortType": "hot",
    "timestamp": 1234567890123
}
```

**响应字段**:
- `list`: 评论列表
  - `content`: 评论内容
  - `commenterName`: 评论者昵称
  - `commenterAvatar`: 评论者头像
  - `commentedAt`: 评论时间

## 🗄️ 数据库表结构

### 作者表 (authors)
```sql
CREATE TABLE authors (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  external_author_id VARCHAR(64) NULL,
  name VARCHAR(255) NOT NULL,
  avatar_url TEXT NULL,
  profile_url TEXT NULL,
  created_at TIMESTAMP NULL,
  updated_at TIMESTAMP NULL,
  UNIQUE KEY uk_auth_name (name)
);
```

### 作品表 (works)
```sql
CREATE TABLE works (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  slug VARCHAR(64) NOT NULL,
  title VARCHAR(512) NULL,
  published_at DATETIME NULL,
  tags_json JSON NULL,
  prompt LONGTEXT NULL,
  negative_prompt LONGTEXT NULL,
  sampler VARCHAR(128) NULL,
  steps INT NULL,
  cfg_scale DECIMAL(6,2) NULL,
  width INT NULL,
  height INT NULL,
  seed VARCHAR(64) NULL,
  like_count INT DEFAULT 0,
  favorite_count INT DEFAULT 0,
  comment_count INT DEFAULT 0,
  source_url TEXT NULL,
  author_id BIGINT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_work_slug (slug),
  CONSTRAINT fk_work_author FOREIGN KEY (author_id) REFERENCES authors(id)
);
```

### 评论表 (comments)
```sql
CREATE TABLE comments (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  work_id BIGINT NOT NULL,
  commenter_name VARCHAR(255) NULL,
  commenter_avatar_url TEXT NULL,
  content TEXT NULL,
  commented_at DATETIME NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_c_work (work_id),
  CONSTRAINT fk_c_work FOREIGN KEY (work_id) REFERENCES works(id)
);
```

## 🔍 字段校验策略

### 必填字段
- `slug`: 作品唯一标识
- `title`: 作品标题

### 可选字段缺省值
- `prompt`: 空字符串
- `negative_prompt`: 空字符串
- `sampler`: 空字符串
- `steps`: 0
- `cfg_scale`: 0.0
- `width`: 0
- `height`: 0
- `seed`: 空字符串
- `like_count`: 0
- `favorite_count`: 0
- `comment_count`: 0

### 验证模式
- **严格模式** (`strict_validation=true`): 缺少必填字段时返回错误
- **宽松模式** (`strict_validation=false`): 缺少必填字段时使用默认值

## 📈 性能优化

### 1. 并发控制
- 默认最大并发数: 5
- 可根据服务器性能调整 `max_workers` 参数

### 2. 限速控制
- 默认每秒请求数: 4
- 符合API使用规范，避免被封禁

### 3. 重试机制
- 指数退避重试策略
- 默认重试3次，可配置

### 4. 数据库优化
- 使用连接池
- 批量事务处理
- 索引优化

## 🚨 错误处理

### 1. 网络错误
- 自动重试机制
- 指数退避策略
- 详细错误日志

### 2. 数据验证错误
- 字段缺失处理
- 数据类型转换
- 验证失败记录

### 3. 数据库错误
- 事务回滚
- 连接重试
- 错误统计

## 📝 日志说明

### 日志级别
- `DEBUG`: 详细调试信息
- `INFO`: 一般信息
- `WARNING`: 警告信息
- `ERROR`: 错误信息

### 日志文件
- 默认日志文件: `detail_collector.log`
- 可配置日志格式和级别

### 统计信息
- 处理总数
- 成功/失败数量
- 成功率
- 错误详情

## 🔄 与T4、T6的集成

### T4 列表采集器集成
```python
# T4 生成 slug 列表
from list_collector import ListCollector
list_collector = ListCollector()
slugs = list_collector.collect_slugs()

# T5 处理详情
from enhanced_detail_collector import EnhancedDetailCollector
detail_collector = EnhancedDetailCollector()
stats = detail_collector.collect_details_batch(slugs)
```

### T6 媒体下载器集成
```python
# T5 完成后，T6 可以并行下载媒体
from media_downloader import MediaDownloader
media_downloader = MediaDownloader()

# 获取需要下载的作品
works = detail_collector.get_works_for_download()
media_downloader.download_batch(works)
```

## 🧪 测试验证

### 1. 单元测试
```bash
python -m pytest tests/test_detail_collector.py
```

### 2. 集成测试
```bash
python test_detail_collector.py
```

### 3. 性能测试
```bash
# 测试并发性能
python -c "
from enhanced_detail_collector import EnhancedDetailCollector
collector = EnhancedDetailCollector()
slugs = ['test1', 'test2', 'test3'] * 100
stats = collector.collect_details_batch(slugs)
print(f'处理速度: {stats[\"total_processed\"] / stats[\"duration\"]:.2f} 个/秒')
"
```

## 📊 监控指标

### 关键指标
- **成功率**: ≥98% (验收标准)
- **处理速度**: 4-6 个/秒
- **错误率**: ≤2%
- **响应时间**: ≤30秒

### 监控告警
- 成功率低于95%
- 错误率超过5%
- 响应时间超过60秒
- 数据库连接失败

## 🚀 部署建议

### 1. 生产环境
- 使用 `PROD_CONFIG` 配置
- 启用严格验证
- 设置合适的并发数
- 配置监控告警

### 2. 开发环境
- 使用 `DEV_CONFIG` 配置
- 启用调试日志
- 降低并发数
- 保存原始数据

### 3. 容器化部署
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "enhanced_detail_collector.py"]
```

## 🔧 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查 `.env` 配置
   - 验证数据库服务状态
   - 检查网络连接

2. **API请求失败**
   - 检查网络连接
   - 验证API接口状态
   - 检查限速设置

3. **字段验证失败**
   - 检查API响应格式
   - 调整验证策略
   - 查看详细错误日志

### 调试技巧

1. **启用调试日志**
   ```python
   config.log_level = 'DEBUG'
   ```

2. **保存原始数据**
   ```python
   config.save_raw_data = True
   ```

3. **降低并发数**
   ```python
   config.max_workers = 1
   ```

## 📚 参考资料

- [Liblib API 文档](https://www.liblib.art/api/docs)
- [MySQL 连接器文档](https://dev.mysql.com/doc/connector-python/en/)
- [Python 并发编程](https://docs.python.org/3/library/concurrent.futures.html)

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来改进 T5 详情采集器！

### 开发规范
- 遵循 PEP 8 代码风格
- 添加适当的注释和文档
- 编写单元测试
- 更新相关文档

---

**版本**: 1.0.0  
**最后更新**: 2024年12月  
**维护者**: Liblib 开发团队
