# T11 单元测试执行说明

## 📋 概述

本文档描述了如何执行工单T11的单元测试，该测试覆盖了解析/重试/限速/断点核心逻辑，目标测试覆盖率≥70%。

## 🎯 测试目标

- **解析逻辑测试**：数据解析、字段验证、格式转换
- **重试逻辑测试**：重试策略、延迟计算、异常处理
- **限速逻辑测试**：令牌桶算法、并发控制、突发流量处理
- **断点续采逻辑测试**：状态管理、任务恢复、数据完整性
- **集成测试**：各模块间的协作和配置集成
- **边界条件测试**：极端情况和异常数据处理
- **性能测试**：解析性能和系统响应时间

## 🚀 快速开始

### 1. 安装测试依赖

```bash
# 安装测试依赖包
pip install -r requirements-test.txt

# 或者使用conda
conda install --file requirements-test.txt
```

### 2. 运行测试

#### 方式1：使用测试脚本（推荐）

```bash
# 运行完整测试套件
python run_t11_tests.py

# 运行特定测试类别
python run_t11_tests.py --run-categories
```

#### 方式2：使用pytest直接运行

```bash
# 运行所有T11测试
pytest tests/unit/test_t11_core_logic.py -v

# 运行特定测试类
pytest tests/unit/test_t11_core_logic.py::TestDataParsingLogic -v

# 运行特定测试方法
pytest tests/unit/test_t11_core_logic.py::TestDataParsingLogic::test_parse_number_with_suffixes -v
```

#### 方式3：使用coverage运行

```bash
# 运行测试并生成覆盖率报告
coverage run --source=scripts -m pytest tests/unit/test_t11_core_logic.py -v

# 查看覆盖率报告
coverage report --show-missing

# 生成HTML覆盖率报告
coverage html --directory=htmlcov
```

## 📊 测试覆盖率

### 覆盖率要求
- **总体覆盖率**：≥70%
- **核心逻辑覆盖率**：≥80%
- **关键路径覆盖率**：≥90%

### 覆盖率报告
测试完成后，会在以下位置生成覆盖率报告：

1. **控制台报告**：显示总体覆盖率和缺失行
2. **HTML报告**：`htmlcov/` 目录下的详细可视化报告
3. **XML报告**：可用于CI/CD集成

## 🧪 测试分类

### 1. 解析逻辑测试 (TestDataParsingLogic)
- 数字后缀解析（k, w等）
- 列表响应数据解析
- 作品数据验证
- 作者数据验证

### 2. 重试逻辑测试 (TestRetryLogic)
- 重试延迟计算
- 异常重试判断
- 重试执行流程
- 最大重试次数处理

### 3. 限速逻辑测试 (TestRateLimitLogic)
- 限速器初始化
- 令牌桶算法
- 并发限制
- 突发流量处理

### 4. 断点续采逻辑测试 (TestResumeLogic)
- 断点续采点创建
- 断点续采点更新
- 断点续采点检索
- 失败任务管理
- 断点续采验证

### 5. 集成测试 (TestIntegrationLogic)
- 中间件集成
- 状态管理和重试集成
- 配置集成

### 6. 边界条件测试 (TestEdgeCases)
- 空数据处理
- 极端限速条件
- 熔断器极端条件
- 大数据处理

### 7. 性能测试 (TestPerformanceLogic)
- 解析性能
- 限速器性能
- 状态管理器性能

## 🔧 测试配置

### 环境变量
测试使用以下环境变量：

```bash
export TESTING=true
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=test_cardesignspace
export DB_USER=test_user
export DB_PASSWORD=test_password
```

### 配置文件
- `tests/conftest.py`：pytest配置和路径设置
- `tests/pytest.ini`：pytest运行配置
- `requirements-test.txt`：测试依赖包

## 📝 测试标记

### 标记说明
- `@pytest.mark.unit`：单元测试
- `@pytest.mark.integration`：集成测试
- `@pytest.mark.slow`：慢速测试
- `@pytest.mark.parsing`：解析相关测试
- `@pytest.mark.retry`：重试相关测试
- `@pytest.mark.rate_limit`：限速相关测试
- `@pytest.mark.resume`：断点续采相关测试

### 标记使用示例

```bash
# 只运行单元测试
pytest -m unit

# 排除慢速测试
pytest -m "not slow"

# 运行特定类型测试
pytest -m "parsing or retry"
```

## 🐛 故障排除

### 常见问题

#### 1. 导入错误
```
ImportError: No module named 'rate_limit_middleware'
```
**解决方案**：确保项目路径正确设置，检查`tests/conftest.py`中的路径配置。

#### 2. 测试超时
```
pytest-timeout: 300.0s timeout
```
**解决方案**：检查测试是否有无限循环或阻塞操作，适当调整超时时间。

#### 3. 覆盖率不足
```
Coverage failure: total of 65.2% is less than fail-under=70.0%
```
**解决方案**：检查测试是否覆盖了所有关键代码路径，添加缺失的测试用例。

#### 4. 异步测试失败
```
RuntimeError: Event loop is closed
```
**解决方案**：确保异步测试正确使用`@pytest.mark.asyncio`装饰器。

### 调试技巧

1. **详细输出**：使用`-v`或`-vv`参数获取详细测试信息
2. **失败时停止**：使用`-x`参数在第一个失败时停止
3. **显示局部变量**：使用`--tb=long`显示详细的错误回溯
4. **并行执行**：使用`-n auto`启用并行测试执行

## 📈 持续集成

### CI/CD配置
测试可以集成到CI/CD流程中：

```yaml
# GitHub Actions示例
- name: Run T11 Tests
  run: |
    pip install -r requirements-test.txt
    python run_t11_tests.py
    coverage report --fail-under=70
```

### 质量门禁
- 测试通过率：100%
- 代码覆盖率：≥70%
- 测试执行时间：<5分钟

## 📚 相关文档

- [T11工单说明](../tickets_transportation_scraper.md)
- [项目结构说明](../PROJECT_STRUCTURE.md)
- [测试最佳实践](../TESTING_BEST_PRACTICES.md)

## 🤝 贡献指南

### 添加新测试
1. 在相应的测试类中添加新的测试方法
2. 确保测试方法名以`test_`开头
3. 添加适当的测试标记
4. 更新覆盖率要求

### 测试命名规范
- 测试类：`Test{功能模块名}`
- 测试方法：`test_{测试场景}_{期望结果}`
- 测试文件：`test_{模块名}.py`

### 代码审查
- 确保测试覆盖了所有关键逻辑
- 验证测试的独立性和可重复性
- 检查测试的可读性和维护性

---

**注意**：执行测试前请确保所有依赖已正确安装，测试环境已正确配置。
