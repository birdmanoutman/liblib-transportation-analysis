### PRD · Liblib 汽车交通数据采集与展示（接口优先 + 日更）

#### 背景与目标
- 内外统一：为内部分析与对外展示提供一致的数据底座与口径。
- 范围聚焦：仅“汽车交通”板块，包含作品灵感页下的汽车交通作品与其引用的模型（模型广场上下文）。
- 运行保障：支持日更、断点续采、限速合规、可观测与错误补偿。

#### 范围（In / Out）
- In：
  - 列表：作品灵感页“汽车交通”筛选下的作品列表（分页、排序）。
  - 详情：作品详情页字段（标题、日期、正/负向提示词、采样器、步数、CFG、尺寸、seed、引用模型/LoRA）。
  - 作者：作者昵称、头像、主页。
  - 互动（可选）：评论列表。
  - 媒体：图组图片下载至 S3；保留原始 URL 与关键元数据（尺寸、格式、哈希）。
- Out（首期不做）：登录/付费专属数据、非汽车类标签、用户私域。

#### 主要用户与用例
- 分析：题材/风格趋势、提示词/模型分布、图片特征抽样。
- 展示：面向外部的作品库与图像浏览，中文展示与图表适配。

#### 数据来源与接口（样例，按抓包验证）
- 列表：POST `https://api2.liblib.art/api/www/img/group/search`（检索/筛选/分页）。
- 详情：
  - POST `https://api2.liblib.art/api/www/img/group/get/{slug}`
  - POST `https://api2.liblib.art/api/www/img/author/{slug}`
  - 评论（可选）：POST `https://api2.liblib.art/api/www/community/commentList`
  - PNG 元信息：POST `https://bridge.liblib.art/gateway/sd-api/common/getPnginfo`
- 媒体：`https://liblibai-online.liblib.cloud/...`（支持 `x-oss-process` 转码/缩放）。

#### 非功能需求
- 性能：接口 RPS ≤ 4；列表并发 ≤ 5；详情并发 ≤ 5；媒体下载并发 ≤ 8。
- 稳定：超时/失败指数退避重试；断点续采；失败队列自动补偿。
- 可观测：结构化日志、成功/失败/重试计数、阶段性统计与告警预留。
- 可扩展：标签/排序/页范围/并发参数化；后续可扩展到其他分类，无需改代码。

#### 技术选型
- 语言：Python（与现有工程一致）。
- 采集：接口直采优先（httpx/requests + 限速/重试）；Playwright 仅兜底交互参数追踪。
- 校验：pydantic 定义响应模型与落库 DTO。
- 存储：
  - 结构化数据 → 远程 MySQL（来自 `.env`：`DB_HOST/PORT/NAME/USER/PASSWORD`）。
  - 媒体 → 远程 S3/MinIO（来自 `.env`：`STORAGE_DRIVER=s3` 与 S3_*）。
  - 本地仅做缓存与运行日志。

#### 数据建模（MySQL 草案）
```sql
-- 作者
CREATE TABLE IF NOT EXISTS authors (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  external_author_id VARCHAR(64) NULL,
  name VARCHAR(255) NOT NULL,
  avatar_url TEXT NULL,
  profile_url TEXT NULL,
  created_at TIMESTAMP NULL,
  updated_at TIMESTAMP NULL,
  UNIQUE KEY uk_auth_name (name)
);

-- 作品
CREATE TABLE IF NOT EXISTS works (
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
  like_count INT NULL,
  favorite_count INT NULL,
  comment_count INT NULL,
  source_url TEXT NULL,
  author_id BIGINT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_work_slug (slug),
  INDEX idx_work_pub (published_at),
  CONSTRAINT fk_work_author FOREIGN KEY (author_id) REFERENCES authors(id)
);

-- 作品与模型引用（Checkpoint/LoRA/其他）
CREATE TABLE IF NOT EXISTS work_models (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  work_id BIGINT NOT NULL,
  model_type ENUM('CHECKPOINT','LORA','OTHER') NOT NULL,
  model_name VARCHAR(512) NOT NULL,
  model_url TEXT NULL,
  is_vip TINYINT(1) DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_wm_work (work_id),
  INDEX idx_wm_name (model_name(191)),
  CONSTRAINT fk_wm_work FOREIGN KEY (work_id) REFERENCES works(id)
);

-- 作品图片（图组）
CREATE TABLE IF NOT EXISTS work_images (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  work_id BIGINT NOT NULL,
  image_index INT NOT NULL,
  src_url TEXT NOT NULL,
  s3_key VARCHAR(1024) NULL,
  width INT NULL,
  height INT NULL,
  format VARCHAR(32) NULL,
  content_hash VARCHAR(64) NULL,
  size_bytes BIGINT NULL,
  downloaded_at DATETIME NULL,
  status ENUM('PENDING','OK','FAILED') DEFAULT 'PENDING',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_wi_work (work_id),
  UNIQUE KEY uk_work_img (work_id, image_index),
  CONSTRAINT fk_wi_work FOREIGN KEY (work_id) REFERENCES works(id)
);

-- 评论（可选）
CREATE TABLE IF NOT EXISTS comments (
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

-- 采集运行记录
CREATE TABLE IF NOT EXISTS fetch_runs (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  started_at DATETIME NOT NULL,
  ended_at DATETIME NULL,
  status ENUM('RUNNING','SUCCESS','FAILED') NOT NULL,
  pages_fetched INT DEFAULT 0,
  works_fetched INT DEFAULT 0,
  details_fetched INT DEFAULT 0,
  images_downloaded INT DEFAULT 0,
  error_summary TEXT NULL
);
```

#### S3 存储规划
- Bucket：来自 `.env` 的 `S3_BUCKET`（示例：`img-station`）。
- Key 模板：`liblib/transportation/{yyyy}/{mm}/{dd}/{slug}/{index}_{hash}.{ext}`。
- 对象元数据：`original_url`, `work_slug`, `image_index`, `width`, `height`。

#### 运行与调度
- POC：采集 1,000 作品（最新优先），详情与媒体齐全；通过率≥98%（详情），≥99%（媒体）。
- 日更：每日 03:00 运行增量；按时间倒序扫描，命中已采过 slug 即止（可配置窗口）。
- 断点：持久化页码与已采 slug；失败队列定时重试，超出阈值告警。

#### 合规与风险
- 自律限速，避免影响站点；不采集登录/付费专属；仅用于合法目的。
- 风险：接口字段变更、限频、链接失效；预案：契约校验、降并发、重试与字段回退。

#### 可视化与中文支持
- 图表：matplotlib/seaborn 全局中文字体（SimHei/Noto CJK），UTF-8 输出；图例/轴标签/标题中文友好。
- 与 `save_and_analyze_collected_data.py`：统一表字段与路径；输出分析视图（如作品分布、模型引用 TopN、提示词词云）。

#### 验收标准
- POC 完成：≥1,000 作品入库与媒体入 S3；覆盖率达标；可视化中文正常渲染。
- 稳态运行 7 天：日更无致命失败；失败补偿有效；分析脚本一键跑通。


