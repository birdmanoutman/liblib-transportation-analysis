# 数据库脚本使用说明

本目录包含工单T3（数据模型与迁移）的相关脚本。

## 文件说明

- `create_tables.sql` - MySQL DDL脚本，包含所有必要的表结构
- `migrate_database.py` - 数据库迁移脚本，用于执行DDL和验证连接
- `test_connection.py` - 数据库连接测试脚本，验证本地/远程连接
- `requirements.txt` - Python依赖包列表

## 使用方法

### 1. 安装依赖

```bash
cd src/database
pip install -r requirements.txt
```

### 2. 测试数据库连接

```bash
python test_connection.py
```

这个脚本会：
- 测试MySQL数据库连接
- 验证环境变量配置
- 测试S3连接（如果安装了boto3）

### 3. 执行数据库迁移

```bash
python migrate_database.py
```

这个脚本会：
- 连接到数据库
- 执行DDL脚本创建所有表
- 验证表结构
- 检查索引

## 环境变量要求

确保在项目根目录的`.env`文件中配置了以下变量：

```bash
# 数据库配置
DB_HOST=your_host
DB_PORT=3306
DB_NAME=cardesignspace
DB_USER=your_username
DB_PASSWORD=your_password

# S3配置（可选）
STORAGE_DRIVER=s3
S3_ENDPOINT=your_s3_endpoint
S3_BUCKET=your_bucket
S3_REGION=your_region
S3_ACCESS_KEY=your_access_key
S3_SECRET_KEY=your_secret_key
```

## 表结构说明

### 核心表

1. **authors** - 作者信息
2. **works** - 作品信息
3. **work_models** - 作品引用的模型
4. **work_images** - 作品图片
5. **comments** - 评论（可选）
6. **fetch_runs** - 采集运行记录
7. **fetch_queue** - 采集任务队列

### 索引设计

- 主键索引：所有表都有自增主键
- 唯一索引：作品slug、作者名称等
- 外键索引：关联查询优化
- 复合索引：时间范围查询优化

## 注意事项

1. 确保MySQL服务器支持utf8mb4字符集
2. 确保数据库用户有CREATE、ALTER、INDEX权限
3. 建议在测试环境中先执行迁移脚本
4. 如果表已存在，脚本会跳过创建（使用IF NOT EXISTS）

## 故障排除

### 连接失败
- 检查网络连接
- 验证数据库服务器地址和端口
- 确认用户名和密码正确
- 检查防火墙设置

### 权限不足
- 确保数据库用户有足够权限
- 检查数据库是否允许远程连接

### 字符集问题
- 确保MySQL支持utf8mb4
- 检查collation设置
