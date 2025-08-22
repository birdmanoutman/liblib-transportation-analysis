# 测试目录 Makefile
# 提供便捷的测试运行命令

.PHONY: help test test-all test-unit test-integration test-performance test-api test-scraping test-database test-analysis clean report

# 默认目标
help:
	@echo "🚀 Liblib Transportation Analysis 测试工具"
	@echo "=========================================="
	@echo ""
	@echo "可用命令:"
	@echo "  test          - 运行所有测试"
	@echo "  test-all      - 运行所有测试（详细模式）"
	@echo "  test-unit     - 运行单元测试"
	@echo "  test-integration - 运行集成测试"
	@echo "  test-performance - 运行性能测试"
	@echo "  test-api      - 运行API测试"
	@echo "  test-scraping - 运行采集测试"
	@echo "  test-database - 运行数据库测试"
	@echo "  test-analysis - 运行分析测试"
	@echo "  pytest        - 使用pytest运行测试"
	@echo "  pytest-unit   - 使用pytest运行单元测试"
	@echo "  pytest-integration - 使用pytest运行集成测试"
	@echo "  report        - 生成测试报告"
	@echo "  clean         - 清理测试输出"
	@echo "  help          - 显示此帮助信息"
	@echo ""

# 运行所有测试
test:
	@echo "🧪 运行所有测试..."
	python run_tests.py

# 运行所有测试（详细模式）
test-all:
	@echo "🧪 运行所有测试（详细模式）..."
	python run_tests.py --report

# 运行单元测试
test-unit:
	@echo "🧪 运行单元测试..."
	python run_tests.py --type unit

# 运行集成测试
test-integration:
	@echo "🔗 运行集成测试..."
	python run_tests.py --type integration

# 运行性能测试
test-performance:
	@echo "⚡ 运行性能测试..."
	python run_tests.py --test tests/integration/test_performance.py

# 运行API测试
test-api:
	@echo "🌐 运行API测试..."
	python run_tests.py --test tests/integration/test_api_collection.py

# 运行采集测试
test-scraping:
	@echo "📡 运行采集测试..."
	python run_tests.py --test tests/integration/test_data_collection.py

# 运行数据库测试
test-database:
	@echo "🗄️  运行数据库测试..."
	pytest tests/ -m database -v

# 运行分析测试
test-analysis:
	@echo "📊 运行分析测试..."
	pytest tests/ -m analysis -v

# 使用pytest运行所有测试
pytest:
	@echo "🐍 使用pytest运行所有测试..."
	pytest tests/ -v

# 使用pytest运行单元测试
pytest-unit:
	@echo "🐍 使用pytest运行单元测试..."
	pytest tests/unit/ -v

# 使用pytest运行集成测试
pytest-integration:
	@echo "🐍 使用pytest运行集成测试..."
	pytest tests/integration/ -v

# 运行特定测试文件
test-file:
	@if [ -z "$(FILE)" ]; then \
		echo "❌ 请指定测试文件: make test-file FILE=path/to/test.py"; \
		exit 1; \
	fi
	@echo "🎯 运行特定测试文件: $(FILE)"
	python run_tests.py --test $(FILE)

# 运行标记的测试
test-marked:
	@if [ -z "$(MARK)" ]; then \
		echo "❌ 请指定测试标记: make test-marked MARK=unit"; \
		exit 1; \
	fi
	@echo "🏷️  运行标记为 $(MARK) 的测试..."
	pytest tests/ -m $(MARK) -v

# 生成测试报告
report:
	@echo "📋 生成测试报告..."
	python run_tests.py --report

# 运行覆盖率测试
coverage:
	@echo "📊 运行覆盖率测试..."
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# 运行慢速测试
test-slow:
	@echo "🐌 运行慢速测试..."
	pytest tests/ --run-slow -v

# 运行性能测试（pytest）
test-perf-pytest:
	@echo "⚡ 使用pytest运行性能测试..."
	pytest tests/ --run-performance -v

# 运行集成测试（pytest）
test-int-pytest:
	@echo "🔗 使用pytest运行集成测试..."
	pytest tests/ --run-integration -v

# 清理测试输出
clean:
	@echo "🧹 清理测试输出..."
	rm -rf ../test_output/*
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ 清理完成"

# 检查测试环境
check-env:
	@echo "🔍 检查测试环境..."
	@python -c "import pytest; print('✅ pytest 已安装')" || echo "❌ pytest 未安装"
	@python -c "import requests; print('✅ requests 已安装')" || echo "❌ requests 未安装"
	@python -c "import psutil; print('✅ psutil 已安装')" || echo "❌ psutil 未安装"
	@echo "📋 环境检查完成"

# 安装测试依赖
install-deps:
	@echo "📦 安装测试依赖..."
	pip install pytest pytest-cov requests psutil

# 快速测试（只运行关键测试）
test-quick:
	@echo "⚡ 快速测试（只运行关键测试）..."
	python run_tests.py --type unit
	@echo "✅ 快速测试完成"

# 完整测试套件
test-suite:
	@echo "🎯 运行完整测试套件..."
	@echo "1️⃣ 运行单元测试..."
	make test-unit
	@echo "2️⃣ 运行集成测试..."
	make test-integration
	@echo "3️⃣ 生成测试报告..."
	make report
	@echo "✅ 完整测试套件完成"

# 调试模式运行
test-debug:
	@echo "🐛 调试模式运行测试..."
	pytest tests/ -v -s --pdb

# 并行运行测试
test-parallel:
	@echo "🔄 并行运行测试..."
	pytest tests/ -n auto -v

# 显示测试统计
test-stats:
	@echo "📊 显示测试统计..."
	pytest tests/ --collect-only -q

# 验证测试结构
validate:
	@echo "🔍 验证测试结构..."
	@echo "检查必要的测试文件..."
	@test -f run_tests.py && echo "✅ run_tests.py 存在" || echo "❌ run_tests.py 缺失"
	@test -f conftest.py && echo "✅ conftest.py 存在" || echo "❌ conftest.py 缺失"
	@test -d unit && echo "✅ unit/ 目录存在" || echo "❌ unit/ 目录缺失"
	@test -d integration && echo "✅ integration/ 目录存在" || echo "❌ integration/ 目录缺失"
	@test -d fixtures && echo "✅ fixtures/ 目录存在" || echo "❌ fixtures/ 目录缺失"
	@echo "📋 结构验证完成"

# 默认目标
.DEFAULT_GOAL := help
