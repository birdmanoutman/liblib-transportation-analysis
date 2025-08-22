# 根目录结构说明

## 📁 目录组织

```
liblib-transportation-analysis/
├── 📁 src/                    # 源代码目录
│   ├── analysis/             # 数据分析模块
│   ├── scraping/             # 数据采集模块
│   ├── download/             # 数据下载模块
│   ├── database/             # 数据库管理模块
│   ├── monitoring/           # 监控模块
│   └── liblib_car_analyzer.py # 主分析器
├── 📁 docs/                  # 文档目录
│   ├── guides/               # 使用指南
│   ├── reference/            # 参考文档
│   ├── changelog/            # 变更日志
│   └── ARCHITECTURE.md       # 架构文档
├── 📁 tests/                 # 测试目录
│   ├── unit/                 # 单元测试
│   ├── integration/          # 集成测试
│   └── fixtures/             # 测试数据
├── 📁 data/                  # 数据目录
│   ├── raw/                  # 原始数据
│   ├── processed/            # 处理后数据
│   └── images/               # 图片文件
├── 📁 config/                # 配置文件目录
│   ├── .env.example          # 环境变量示例
│   ├── .env                  # 环境变量（本地）
│   ├── pytest.ini           # 测试配置
│   ├── .pre-commit-config.yaml # 代码质量配置
│   └── pyproject.toml        # 项目配置
├── 📁 src/                    # 核心代码目录
│   ├── check_database_status.py # 数据库状态检查
│   └── run_complete_analysis.py # 完整分析运行脚本
├── 📁 build/                 # 构建输出目录
│   ├── htmlcov/              # 测试覆盖率报告
│   └── .coverage             # 覆盖率数据
├── 📁 output/                # 运行输出目录
│   ├── test_output/          # 测试输出
│   └── liblib_analysis_output/ # 分析输出
├── 📁 temp/                  # 临时文件目录
│   ├── .pytest_cache/        # 测试缓存
│   └── debug_response.json   # 调试响应文件
├── 📁 payloads/              # API请求载荷文件
├── 📁 logs/                  # 日志文件目录
│   ├── *.log                 # 各种日志文件
│   └── database_migration.log # 数据库迁移日志
├── 📁 archive/               # 归档文件
├── 📁 car_models_complete/   # 完整汽车模型数据
├── 📁 .github/               # GitHub配置
├── 📁 .cursor/               # Cursor编辑器配置
├── 📁 .git/                  # Git版本控制
├── 📁 .venv/                 # Python虚拟环境
├── 📄 README.md              # 项目说明
├── 📄 CONTRIBUTING.md        # 贡献指南
├── 📄 ROOT_STRUCTURE.md      # 本文件 - 目录结构说明
├── 📄 Makefile               # 构建脚本
├── 📄 requirements.txt       # 生产依赖
├── 📄 requirements-dev.txt   # 开发依赖
├── 📄 requirements-test.txt  # 测试依赖
├── 📄 requirements-minimal.txt # 最小依赖
├── 📄 .gitignore             # Git忽略文件
├── 📄 .cursorignore          # Cursor忽略文件
└── 📄 playwright_vs_selenium_comparison.md # 技术对比文档
```

## 🔧 配置文件说明

### config/ 目录
- **.env.example**: 环境变量模板，包含所有需要的环境变量
- **.env**: 本地环境变量（不提交到版本控制）
- **pytest.ini**: 测试框架配置
- **.pre-commit-config.yaml**: 代码质量检查配置
- **pyproject.toml**: 项目元数据和工具配置

### src/ 目录
- **check_database_status.py**: 数据库连接和状态检查脚本
- **run_complete_analysis.py**: 完整分析流程运行脚本

## 📊 输出目录说明

### build/ 目录
- 包含构建过程中生成的临时文件和报告
- 测试覆盖率报告等

### output/ 目录
- 包含程序运行时的输出结果
- 测试结果、分析报告等

### temp/ 目录
- 临时文件和缓存
- 可以定期清理

## 🚀 使用建议

1. **开发时**: 主要工作在 `src/` 目录
2. **测试时**: 使用 `tests/` 目录和 `make test` 命令
3. **配置时**: 修改 `config/` 目录下的配置文件
4. **运行时**: 使用 `src/` 目录下的脚本
5. **查看结果**: 检查 `output/` 目录下的输出文件

## 🧹 维护建议

- 定期清理 `temp/` 和 `build/` 目录
- 将重要的输出文件从 `output/` 移动到 `data/` 目录
- 使用 `make clean` 清理临时文件

## ✨ 整理完成

根目录已经整理完成，现在的结构更加清晰：

- **配置文件** 集中在 `config/` 目录
- **脚本文件** 集中在 `src/` 目录  
- **构建输出** 集中在 `build/` 目录
- **运行输出** 集中在 `output/` 目录
- **临时文件** 集中在 `temp/` 目录
- **日志文件** 集中在 `logs/` 目录

根目录现在只保留了最重要的项目文件，其他文件都按功能分类到相应的目录中。
