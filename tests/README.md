# 测试目录

本目录包含项目的所有测试代码，采用分层架构设计，确保测试的完整性和可维护性。

## 目录结构

```
tests/
├── __init__.py                 # 测试包初始化文件
├── conftest.py                 # pytest配置文件
├── run_tests.py                # 测试运行器主文件
├── unit/                       # 单元测试
│   ├── __init__.py
│   ├── test_simple_analysis.py
│   ├── test_t11_core_logic.py
│   ├── test_t8_resume_retry.py
│   └── test_liblib_analyzer.py
├── integration/                # 集成测试
│   ├── __init__.py
│   ├── test_data_collection.py
│   ├── test_api_collection.py
│   └── test_performance.py
└── fixtures/                   # 测试夹具
    ├── __init__.py
    └── test_data.py
```

## 测试分类

### 1. 单元测试 (Unit Tests)
- **位置**: `tests/unit/`
- **目的**: 测试单个函数、类或模块的独立功能
- **特点**: 快速执行，不依赖外部资源
- **标记**: `@pytest.mark.unit`

### 2. 集成测试 (Integration Tests)
- **位置**: `tests/integration/`
- **目的**: 测试多个组件之间的协作
- **特点**: 可能依赖外部资源，执行时间较长
- **标记**: `@pytest.mark.integration`

### 3. 性能测试 (Performance Tests)
- **位置**: `tests/integration/test_performance.py`
- **目的**: 测试系统性能和基准
- **特点**: 需要特殊标记运行
- **标记**: `@pytest.mark.performance`

### 4. 测试夹具 (Fixtures)
- **位置**: `tests/fixtures/`
- **目的**: 提供测试数据和通用功能
- **特点**: 可重用的测试资源

## 运行测试

### 方法1: 使用测试运行器
```bash
# 运行所有测试
python tests/run_tests.py

# 运行特定类型测试
python tests/run_tests.py --type unit
python tests/run_tests.py --type integration

# 运行特定测试文件
python tests/run_tests.py --test tests/unit/test_simple_analysis.py

# 生成详细报告
python tests/run_tests.py --report
```

### 方法2: 使用pytest
```bash
# 运行所有测试
pytest tests/

# 运行特定类型测试
pytest tests/unit/                    # 单元测试
pytest tests/integration/             # 集成测试

# 运行标记的测试
pytest -m unit                       # 单元测试
pytest -m integration                # 集成测试
pytest -m performance                # 性能测试
pytest -m api                        # API测试
pytest -m scraping                   # 采集测试

# 跳过慢速测试
pytest -m "not slow"

# 运行性能测试
pytest --run-performance

# 运行集成测试
pytest --run-integration
```

### 方法3: 直接运行测试文件
```bash
# 运行单元测试
python tests/unit/test_simple_analysis.py
python tests/unit/test_t11_core_logic.py

# 运行集成测试
python tests/integration/test_data_collection.py
python tests/integration/test_api_collection.py
python tests/integration/test_performance.py
```

## 测试标记

### 自动标记
pytest会根据文件路径和测试函数名自动添加标记：

- `unit`: 单元测试
- `integration`: 集成测试
- `performance`: 性能测试
- `api`: API相关测试
- `scraping`: 数据采集测试
- `database`: 数据库测试
- `analysis`: 分析功能测试

### 手动标记
```python
import pytest

@pytest.mark.slow
def test_slow_function():
    """标记为慢速测试"""
    pass

@pytest.mark.integration
def test_integration():
    """标记为集成测试"""
    pass
```

## 测试夹具

### 内置夹具
- `project_root_path`: 项目根目录路径
- `src_path`: src目录路径
- `test_data_path`: 测试数据目录路径
- `output_path`: 输出目录路径
- `temp_file`: 临时文件
- `temp_dir`: 临时目录
- `test_config`: 测试配置
- `sample_car_models`: 示例汽车模型数据
- `sample_api_response`: 示例API响应
- `mock_session`: 模拟会话对象
- `mock_response`: 模拟响应对象

### 使用夹具
```python
def test_with_fixtures(sample_car_models, temp_file):
    """使用夹具的测试"""
    assert len(sample_car_models) > 0
    # 使用临时文件进行测试
```

## 测试数据

### 模拟数据
- `SAMPLE_CAR_MODELS`: 示例汽车模型数据
- `SAMPLE_API_RESPONSE`: 示例API响应
- `SAMPLE_CONFIG`: 示例配置
- `SAMPLE_ERROR_RESPONSE`: 示例错误响应

### 数据生成器
```python
from tests.fixtures.test_data import TestDataGenerator

# 生成测试数据
models = TestDataGenerator.generate_car_models(10)
responses = TestDataGenerator.generate_api_responses(5)
errors = TestDataGenerator.generate_error_scenarios()
```

## 配置选项

### 环境变量
- `TESTING`: 测试模式标识
- `DB_HOST`: 测试数据库主机
- `DB_PORT`: 测试数据库端口
- `DB_NAME`: 测试数据库名称
- `DB_USER`: 测试数据库用户
- `DB_PASSWORD`: 测试数据库密码

### 自定义选项
- `--run-slow`: 运行慢速测试
- `--run-performance`: 运行性能测试
- `--run-integration`: 运行集成测试

## 测试报告

测试完成后会生成详细的测试报告，包括：

- 测试统计信息
- 通过/失败数量
- 成功率
- 执行时间
- 测试状态评估

报告保存在 `test_output/` 目录中。

## 最佳实践

### 1. 测试命名
- 测试文件以 `test_` 开头
- 测试函数以 `test_` 开头
- 使用描述性的名称

### 2. 测试组织
- 按功能模块组织测试
- 使用夹具减少重复代码
- 保持测试的独立性

### 3. 错误处理
- 测试异常情况
- 验证错误消息
- 测试边界条件

### 4. 性能考虑
- 标记慢速测试
- 使用适当的超时设置
- 避免不必要的网络请求

## 故障排除

### 常见问题

1. **导入错误**
   - 检查Python路径设置
   - 确保依赖包已安装

2. **测试失败**
   - 查看详细错误信息
   - 检查测试环境配置
   - 验证测试数据

3. **性能问题**
   - 使用 `--run-performance` 选项
   - 检查网络连接
   - 调整超时设置

### 调试技巧

1. **详细输出**
   ```bash
   pytest -v -s tests/
   ```

2. **单步调试**
   ```bash
   pytest --pdb tests/
   ```

3. **覆盖率报告**
   ```bash
   pytest --cov=src tests/
   ```

## 贡献指南

1. 为新功能编写测试
2. 保持测试覆盖率
3. 遵循测试命名规范
4. 添加适当的测试标记
5. 更新本文档

## 相关文档

- [pytest官方文档](https://docs.pytest.org/)
- [项目架构文档](../docs/ARCHITECTURE.md)
- [编码标准](../docs/CODING_STANDARDS.md)
- [使用指南](../docs/guides/USAGE_GUIDE.md)
