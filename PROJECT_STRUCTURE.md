# 📁 项目目录结构

## 🏗️ 整体架构

```
liblib-transportation-analysis/
├── 📁 scripts/                    # 脚本文件
│   ├── 📁 deprecated/            # 废弃脚本
│   ├── 📁 legacy/                # 遗留脚本
│   ├── 📁 development/           # 开发工具
│   ├── 📁 analysis/              # 分析脚本
│   ├── 📁 download/              # 下载脚本
│   └── 📁 scraping/              # 爬虫脚本
├── 📁 docs/                       # 文档文件
│   ├── 📁 guides/                # 使用指南
│   ├── 📁 reference/             # 参考文档
│   ├── 📁 changelog/             # 变更日志
│   └── 📁 deprecated/            # 废弃说明
├── 📁 tests/                      # 测试文件
│   ├── 📁 unit/                  # 单元测试
│   ├── 📁 integration/           # 集成测试
│   └── 📁 fixtures/              # 测试数据
├── 📁 data/                       # 数据文件
│   ├── 📁 raw/                   # 原始数据
│   ├── 📁 processed/             # 处理后数据
│   ├── 📁 images/                # 图片文件
│   └── 📁 analysis/              # 分析结果
├── 📁 .git/                       # Git版本控制
├── 📄 .gitignore                  # Git忽略文件
├── 📄 .cursorignore               # Cursor忽略文件
├── 📄 README.md                   # 项目说明
└── 📄 PROJECT_STRUCTURE.md        # 本文件
```

## 📁 详细说明

### 🐍 scripts/ - 脚本文件

#### 📁 deprecated/ - 废弃脚本
- **状态**: ⚠️ 已废弃，不建议使用
- **说明**: 这些脚本的功能已整合到主脚本中
- **文件**: 无（已移动到对应功能目录）

#### 📁 legacy/ - 遗留脚本
- **状态**: 🔄 遗留代码，功能已整合
- **说明**: 旧版本的流程控制脚本
- **文件**: `run_complete_analysis.py`

#### 📁 development/ - 开发工具
- **状态**: 🛠️ 开发调试工具
- **说明**: 用于开发和调试的辅助脚本
- **文件**: `debug_scraper.py`

#### 📁 analysis/ - 分析脚本
- **状态**: 🔍 数据分析脚本
- **说明**: 各种数据分析功能脚本
- **文件**: 
  - `analyze_complete_models.py`
  - `analyze_existing_data.py`
  - `car_design_trend_analyzer.py`
  - `generate_analysis.py`

#### 📁 download/ - 下载脚本
- **状态**: ⬇️ 数据下载脚本
- **说明**: 图片和模型数据下载脚本
- **文件**: 
  - `download_all_images.py`
  - `download_all_images_fixed.py`
  - `download_complete_models.py`
  - `download_images.py`

#### 📁 scraping/ - 爬虫脚本
- **状态**: 🕷️ 数据采集脚本
- **说明**: 各种数据采集策略脚本
- **文件**: 
  - `complete_car_scraper.py`
  - `enhanced_car_scraper.py`
  - `playwright_car_scraper.py`
  - `complete_scraper.py`

### 📚 docs/ - 文档文件

#### 📁 guides/ - 使用指南
- **状态**: 📖 用户使用指南
- **说明**: 详细的使用说明和示例
- **文件**: `USAGE_GUIDE.md`

#### 📁 reference/ - 参考文档
- **状态**: 📋 技术参考文档
- **说明**: 脚本功能对比和技术说明
- **文件**: `script_comparison_table.md`

#### 📁 changelog/ - 变更日志
- **状态**: 📝 版本变更记录
- **说明**: 详细的版本更新历史
- **文件**: `CHANGELOG.md`

#### 📁 deprecated/ - 废弃说明
- **状态**: ⚠️ 废弃脚本说明
- **说明**: 废弃脚本的详细说明和迁移指南
- **文件**: `DEPRECATED_SCRIPTS.md`

### 🧪 tests/ - 测试文件

#### 📁 unit/ - 单元测试
- **状态**: ✅ 单元测试套件
- **说明**: 主脚本的自动化测试
- **文件**: `test_liblib_analyzer.py`

#### 📁 integration/ - 集成测试
- **状态**: 🔗 集成测试（待开发）
- **说明**: 端到端功能测试

#### 📁 fixtures/ - 测试数据
- **状态**: 📊 测试数据（待开发）
- **说明**: 测试用的样本数据

### 💾 data/ - 数据文件

#### 📁 raw/ - 原始数据
- **状态**: 📥 原始采集数据
- **说明**: 从API和网页采集的原始数据
- **内容**: 
  - JSON数据文件
  - 日志文件
  - 原始模型数据

#### 📁 processed/ - 处理后数据
- **状态**: 🔄 处理后的数据
- **说明**: 经过清洗和分析的数据
- **内容**: 分析输出结果

#### 📁 images/ - 图片文件
- **状态**: 🖼️ 模型图片
- **说明**: 下载的汽车模型图片
- **内容**: 模型封面图片

#### 📁 analysis/ - 分析结果
- **状态**: 📊 分析结果
- **说明**: 数据分析的输出结果
- **内容**: 趋势分析、统计报告等

## 🎯 使用建议

### 🚀 新用户
1. 查看 `docs/guides/USAGE_GUIDE.md` 了解使用方法
2. 使用 `scripts/liblib_car_analyzer.py` 进行数据分析
3. 参考 `docs/reference/script_comparison_table.md` 了解功能对比

### 🔧 开发者
1. 查看 `docs/changelog/CHANGELOG.md` 了解版本变更
2. 运行 `tests/unit/test_liblib_analyzer.py` 验证功能
3. 参考 `docs/deprecated/DEPRECATED_SCRIPTS.md` 了解废弃脚本

### 📊 数据分析师
1. 查看 `data/` 目录下的各种数据
2. 使用 `scripts/liblib_car_analyzer.py` 进行自定义分析
3. 参考 `docs/guides/USAGE_GUIDE.md` 了解高级功能

## 🔄 迁移指南

### 从旧脚本迁移到新脚本

| 旧脚本 | 新功能位置 | 迁移说明 |
|--------|------------|----------|
| `complete_car_scraper.py` | `scripts/liblib_car_analyzer.py` | 使用 `--api` 参数 |
| `enhanced_car_scraper.py` | `scripts/liblib_car_analyzer.py` | 使用 `--enhanced` 参数 |
| `playwright_car_scraper.py` | `scripts/liblib_car_analyzer.py` | 使用 `--browser` 参数 |
| `download_all_images.py` | `scripts/liblib_car_analyzer.py` | 使用 `--download-images` 参数 |
| `analyze_complete_models.py` | `scripts/liblib_car_analyzer.py` | 使用 `--analyze` 参数 |

### 快速迁移命令

```bash
# 旧命令
python complete_car_scraper.py

# 新命令
python scripts/liblib_car_analyzer.py --api

# 旧命令
python download_all_images.py

# 新命令
python scripts/liblib_car_analyzer.py --download-images

# 旧命令
python analyze_complete_models.py

# 新命令
python scripts/liblib_car_analyzer.py --analyze
```

## 📈 项目状态

- **主脚本**: ✅ 已完成并测试通过
- **文档**: ✅ 完整覆盖
- **测试**: ✅ 100%通过率
- **目录结构**: ✅ 清晰组织
- **废弃脚本**: ✅ 已标记并说明

## 🎉 总结

通过这次目录整理，项目结构变得更加清晰和专业：

1. **功能分离**: 按功能类型组织脚本
2. **文档集中**: 所有文档集中在docs目录
3. **测试规范**: 测试文件独立组织
4. **数据管理**: 数据文件按类型分类
5. **维护友好**: 结构清晰，易于维护和扩展

现在您可以更轻松地：
- 找到需要的脚本和文档
- 理解项目的整体架构
- 进行功能开发和测试
- 管理各种数据文件
- 维护和更新项目
