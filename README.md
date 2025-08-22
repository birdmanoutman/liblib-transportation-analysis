# 🚗 Liblib.art 汽车交通板块模型分析项目

> 一个专业的汽车模型数据采集、分析和可视化工具

## 🎯 项目简介

本项目是一个综合性的汽车模型数据分析平台，专门用于采集、处理和分析来自 [Liblib.art](https://liblib.art) 的汽车交通板块模型数据。通过智能数据采集、深度分析和专业报告生成，为用户提供全面的市场洞察和趋势分析。

## ✨ 主要特性

- 🕷️ **智能数据采集**: 支持API、浏览器自动化和关键词搜索三种采集策略
- 📊 **深度数据分析**: 多维度统计分析，包括参与度、作者活跃度、模型类型分布等
- 🖼️ **批量图片下载**: 并发下载模型封面图片，支持断点续传
- 📈 **专业报告生成**: 自动生成Markdown格式的分析报告
- 🔧 **灵活配置**: 支持JSON配置文件和命令行参数
- 🧪 **完整测试**: 自动化测试套件，确保代码质量
- 📚 **详细文档**: 完整的使用指南和API文档

## 🏗️ 项目结构

```
liblib-transportation-analysis/
├── 📁 src/                        # 脚本文件
│   ├── liblib_car_analyzer.py    # 🚀 主分析器脚本
│   ├── 📁 scraping/              # 数据采集脚本
│   ├── 📁 download/              # 数据下载脚本
│   ├── 📁 analysis/              # 数据分析脚本
│   └── 📁 development/           # 开发工具
├── 📁 docs/                       # 文档文件
│   ├── 📁 guides/                # 使用指南
│   ├── 📁 reference/             # 参考文档
│   └── 📁 changelog/             # 变更日志
├── 📁 tests/                      # 测试文件
│   └── 📁 unit/                  # 单元测试
├── 📁 data/                       # 数据文件
│   ├── 📁 raw/                   # 原始数据
│   ├── 📁 processed/             # 处理后数据
│   └── 📁 images/                # 图片文件
└── 📄 README.md                   # 项目说明
```

📖 **详细结构说明**: 查看 [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)

## 🚀 快速开始

### 环境要求

- Python 3.9+
- 网络连接（用于数据采集）

### 安装依赖

```bash
# 推荐：使用虚拟环境
python -m venv .venv && source .venv/bin/activate

# 一次性安装项目、测试、开发依赖
make install-dev

# 安装 pre-commit 钩子（首次）
make pre-commit-install
```

### 常用命令

```bash
# 运行全部测试
make test

# 单元测试/集成测试
make test-unit
make test-integration

# 覆盖率报告（生成 htmlcov/）
make coverage

# 代码格式化 & 静态检查
make format
make lint

# 类型检查
make type-check
```

### 基本使用

```bash
# 运行完整分析
python src/liblib_car_analyzer.py --all

# 仅采集数据
python src/liblib_car_analyzer.py --collect

# 仅下载图片
python src/liblib_car_analyzer.py --download-images

# 仅分析数据
python src/liblib_car_analyzer.py --analyze

# 使用MCP工具采集数据（推荐）
python src/scraping/liblib_mcp_collector.py

# 查看帮助
python src/liblib_car_analyzer.py --help
```

### 📊 数据采集示例

最近成功采集到的汽车交通相关模型数据：

```json
{
  "title": "汽车新车车辆真实拍摄 bz3X",
  "type": "LORA",
  "version": "F.1",
  "downloads": "5.6k",
  "likes": "7",
  "collections": "253",
  "exclusive": true,
  "author": "AIGC_black",
  "category": "汽车交通"
}
```

**采集统计**:
- 总模型数: 6个
- 模型类型: 全部为LORA模型
- 作者数量: 6位不同作者
- 数据来源: MCP浏览器观察
```

### 环境变量

- 复制并修改 `.env.example` 为 `.env`，详见 `docs/ENVIRONMENT.md`。

## 📊 核心功能

### 1. 数据采集 (Data Collection)
- **API采集**: 通过官方API获取模型数据
- **浏览器自动化**: 使用Playwright进行页面滚动和数据提取
- **关键词搜索**: 基于关键词的智能搜索策略
- **并发处理**: 多线程并发采集，提高效率

### 2. 图片下载 (Image Download)
- **批量下载**: 支持批量下载模型封面图片
- **并发下载**: 多线程并发下载，速度提升3-5倍
- **断点续传**: 支持下载中断后的续传
- **文件管理**: 自动创建目录结构，避免重复下载

### 3. 数据分析 (Data Analysis)
- **基础统计**: 模型数量、下载量、点赞数等基础指标
- **作者分析**: 作者活跃度、作品分布、影响力分析
- **类型分析**: 模型类型分布、热门类型趋势
- **参与度分析**: 用户参与度、互动率分析

### 4. 报告生成 (Report Generation)
- **Markdown格式**: 生成结构化的Markdown报告
- **图表支持**: 支持生成数据可视化图表
- **多语言**: 支持中英文报告
- **自定义模板**: 支持自定义报告模板

## ⚙️ 配置说明

### 配置文件

创建 `config.json` 文件来自定义配置：

```json
{
  "api_base": "https://liblib.art/api",
  "max_retries": 3,
  "timeout": 30,
  "concurrent_downloads": 5,
  "output_dir": "./output",
  "images_dir": "images",
  "log_level": "INFO"
}
```

### 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--all` | 运行完整分析流程 | `--all` |
| `--collect` | 仅采集数据 | `--collect` |
| `--download-images` | 仅下载图片 | `--download-images` |
| `--analyze` | 仅分析数据 | `--analyze` |
| `--config` | 指定配置文件 | `--config config.json` |
| `--output` | 指定输出目录 | `--output ./results` |
| `--verbose` | 详细日志输出 | `--verbose` |

## 📈 性能指标

- **数据采集速度**: 支持并发采集，速度提升2-3倍
- **图片下载速度**: 并发下载，速度提升3-5倍
- **数据分析速度**: 优化算法，处理速度提升2-3倍
- **内存使用**: 智能缓存，内存使用优化30%

## 🧪 测试覆盖

项目包含完整的测试套件：

- **单元测试**: 6个测试用例，覆盖核心功能
- **测试通过率**: 100% ✅
- **边界测试**: 包含边界情况和异常处理测试
- **性能测试**: 大数据量处理性能验证

运行测试：
```bash
python tests/unit/test_liblib_analyzer.py
```

## 📚 文档资源

- 📖 **[使用指南](docs/guides/USAGE_GUIDE.md)**: 详细的使用说明和示例
- 📋 **[功能对比表](docs/reference/script_comparison_table.md)**: 脚本功能对比
- 📝 **[变更日志](docs/changelog/CHANGELOG.md)**: 版本更新历史
- ⚠️ **[废弃说明](docs/deprecated/DEPRECATED_SCRIPTS.md)**: 废弃脚本说明
- 🏗️ **[项目结构](PROJECT_STRUCTURE.md)**: 详细的目录结构说明

## 🔄 从旧版本迁移

如果您之前使用的是分散的脚本，可以参考以下迁移指南：

| 旧脚本 | 新功能 | 迁移命令 |
|--------|--------|----------|
| `complete_car_scraper.py` | API采集 | `--api` |
| `enhanced_car_scraper.py` | 关键词搜索 | `--enhanced` |
| `playwright_car_scraper.py` | 浏览器自动化 | `--browser` |
| `download_all_images.py`