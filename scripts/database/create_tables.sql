-- Liblib 汽车交通数据采集与展示系统数据库表结构
-- 数据库：cardesignspace
-- 创建时间：2024年

-- 作者表
CREATE TABLE IF NOT EXISTS liblib_authors (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  external_author_id VARCHAR(64) NULL COMMENT '外部作者ID',
  name VARCHAR(255) NOT NULL COMMENT '作者昵称',
  avatar_url TEXT NULL COMMENT '头像URL',
  profile_url TEXT NULL COMMENT '主页URL',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  UNIQUE KEY uk_auth_name (name),
  INDEX idx_auth_external (external_author_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Liblib作者信息表';

-- 作品表
CREATE TABLE IF NOT EXISTS liblib_works (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  slug VARCHAR(64) NOT NULL COMMENT '作品唯一标识',
  title VARCHAR(512) NULL COMMENT '作品标题',
  published_at DATETIME NULL COMMENT '发布时间',
  tags_json JSON NULL COMMENT '标签JSON数组',
  prompt LONGTEXT NULL COMMENT '正向提示词',
  negative_prompt LONGTEXT NULL COMMENT '负向提示词',
  sampler VARCHAR(128) NULL COMMENT '采样器',
  steps INT NULL COMMENT '步数',
  cfg_scale DECIMAL(6,2) NULL COMMENT 'CFG比例',
  width INT NULL COMMENT '图片宽度',
  height INT NULL COMMENT '图片高度',
  seed VARCHAR(64) NULL COMMENT '随机种子',
  like_count INT DEFAULT 0 COMMENT '点赞数',
  favorite_count INT DEFAULT 0 COMMENT '收藏数',
  comment_count INT DEFAULT 0 COMMENT '评论数',
  source_url TEXT NULL COMMENT '源URL',
  author_id BIGINT NULL COMMENT '作者ID',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  UNIQUE KEY uk_work_slug (slug),
  INDEX idx_work_pub (published_at),
  INDEX idx_work_author (author_id),
  INDEX idx_work_created (created_at),
  CONSTRAINT fk_work_author FOREIGN KEY (author_id) REFERENCES liblib_authors(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Liblib作品信息表';

-- 作品与模型引用表（Checkpoint/LoRA/其他）
CREATE TABLE IF NOT EXISTS liblib_work_models (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  work_id BIGINT NOT NULL COMMENT '作品ID',
  model_type ENUM('CHECKPOINT','LORA','OTHER') NOT NULL COMMENT '模型类型',
  model_name VARCHAR(512) NOT NULL COMMENT '模型名称',
  model_url TEXT NULL COMMENT '模型URL',
  is_vip TINYINT(1) DEFAULT 0 COMMENT '是否VIP模型',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  INDEX idx_wm_work (work_id),
  INDEX idx_wm_name (model_name(191)),
  INDEX idx_wm_type (model_type),
  CONSTRAINT fk_wm_work FOREIGN KEY (work_id) REFERENCES liblib_works(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Liblib作品模型引用表';

-- 作品图片表（图组）
CREATE TABLE IF NOT EXISTS liblib_work_images (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  work_id BIGINT NOT NULL COMMENT '作品ID',
  image_index INT NOT NULL COMMENT '图片索引',
  src_url TEXT NOT NULL COMMENT '原始图片URL',
  s3_key VARCHAR(1024) NULL COMMENT 'S3存储键',
  width INT NULL COMMENT '图片宽度',
  height INT NULL COMMENT '图片高度',
  format VARCHAR(32) NULL COMMENT '图片格式',
  content_hash VARCHAR(64) NULL COMMENT '内容哈希',
  size_bytes BIGINT NULL COMMENT '文件大小（字节）',
  downloaded_at DATETIME NULL COMMENT '下载时间',
  status ENUM('PENDING','OK','FAILED') DEFAULT 'PENDING' COMMENT '下载状态',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  INDEX idx_wi_work (work_id),
  INDEX idx_wi_status (status),
  INDEX idx_wi_hash (content_hash),
  UNIQUE KEY uk_work_img (work_id, image_index),
  CONSTRAINT fk_wi_work FOREIGN KEY (work_id) REFERENCES liblib_works(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Liblib作品图片表';

-- 评论表（可选）
CREATE TABLE IF NOT EXISTS liblib_comments (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  work_id BIGINT NOT NULL COMMENT '作品ID',
  commenter_name VARCHAR(255) NULL COMMENT '评论者昵称',
  commenter_avatar_url TEXT NULL COMMENT '评论者头像URL',
  content TEXT NULL COMMENT '评论内容',
  commented_at DATETIME NULL COMMENT '评论时间',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  INDEX idx_c_work (work_id),
  INDEX idx_c_time (commented_at),
  CONSTRAINT fk_c_work FOREIGN KEY (work_id) REFERENCES liblib_works(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Liblib评论表';

-- 采集运行记录表
CREATE TABLE IF NOT EXISTS liblib_fetch_runs (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  started_at DATETIME NOT NULL COMMENT '开始时间',
  ended_at DATETIME NULL COMMENT '结束时间',
  status ENUM('RUNNING','SUCCESS','FAILED') NOT NULL COMMENT '运行状态',
  pages_fetched INT DEFAULT 0 COMMENT '已采集页数',
  works_fetched INT DEFAULT 0 COMMENT '已采集作品数',
  details_fetched INT DEFAULT 0 COMMENT '已采集详情数',
  images_downloaded INT DEFAULT 0 COMMENT '已下载图片数',
  error_summary TEXT NULL COMMENT '错误摘要',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  INDEX idx_fr_status (status),
  INDEX idx_fr_started (started_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Liblib采集运行记录表';

-- 采集任务队列表
CREATE TABLE IF NOT EXISTS liblib_fetch_queue (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  work_slug VARCHAR(64) NOT NULL COMMENT '作品slug',
  priority INT DEFAULT 0 COMMENT '优先级',
  status ENUM('PENDING','PROCESSING','SUCCESS','FAILED') DEFAULT 'PENDING' COMMENT '状态',
  retry_count INT DEFAULT 0 COMMENT '重试次数',
  error_message TEXT NULL COMMENT '错误信息',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX idx_fq_status (status),
  INDEX idx_fq_priority (priority),
  INDEX idx_fq_slug (work_slug),
  UNIQUE KEY uk_fq_slug (work_slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Liblib采集任务队列表';
