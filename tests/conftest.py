#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pytest配置文件
设置测试环境和路径
"""

import os
import sys
import pytest
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# 设置环境变量
os.environ.setdefault('TESTING', 'true')
os.environ.setdefault('DB_HOST', 'localhost')
os.environ.setdefault('DB_PORT', '3306')
os.environ.setdefault('DB_NAME', 'test_cardesignspace')
os.environ.setdefault('DB_USER', 'test_user')
os.environ.setdefault('DB_PASSWORD', 'test_password')

# 测试配置
def pytest_configure(config):
    """pytest配置钩子"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "api: marks tests as API tests"
    )
    config.addinivalue_line(
        "markers", "scraping: marks tests as scraping tests"
    )
    config.addinivalue_line(
        "markers", "database: marks tests as database tests"
    )
    config.addinivalue_line(
        "markers", "analysis: marks tests as analysis tests"
    )

def pytest_collection_modifyitems(config, items):
    """修改测试项集合，自动添加标记"""
    for item in items:
        # 根据文件路径自动添加标记
        file_path = str(item.fspath)
        
        if "unit" in file_path:
            item.add_marker("unit")
        elif "integration" in file_path:
            item.add_marker("integration")
        
        # 根据文件名添加特定标记
        if "test_performance" in file_path:
            item.add_marker("performance")
        elif "test_api" in file_path:
            item.add_marker("api")
        elif "test_data_collection" in file_path:
            item.add_marker("scraping")
        elif "test_database" in file_path or "database" in file_path:
            item.add_marker("database")
        elif "test_analysis" in file_path or "analysis" in file_path:
            item.add_marker("analysis")
        
        # 根据测试函数名添加标记
        if "performance" in item.name:
            item.add_marker("performance")
        elif "api" in item.name:
            item.add_marker("api")
        elif "scraping" in item.name or "collector" in item.name:
            item.add_marker("scraping")
        elif "database" in item.name or "db" in item.name:
            item.add_marker("database")
        elif "analysis" in item.name:
            item.add_marker("analysis")

# 测试夹具
@pytest.fixture(scope="session")
def project_root_path():
    """返回项目根目录路径"""
    return project_root

@pytest.fixture(scope="session")
def src_path():
    """返回src目录路径"""
    return project_root / "src"

@pytest.fixture(scope="session")
def test_data_path():
    """返回测试数据目录路径"""
    return project_root / "tests" / "fixtures"

@pytest.fixture(scope="session")
def output_path():
    """返回输出目录路径"""
    output_dir = project_root / "test_output"
    output_dir.mkdir(exist_ok=True)
    return output_dir

@pytest.fixture(scope="function")
def temp_file():
    """创建临时文件夹具"""
    import tempfile
    
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()
    
    yield temp_file.name
    
    # 清理临时文件
    try:
        os.unlink(temp_file.name)
    except OSError:
        pass

@pytest.fixture(scope="function")
def temp_dir():
    """创建临时目录夹具"""
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    
    yield temp_dir
    
    # 清理临时目录
    try:
        shutil.rmtree(temp_dir)
    except OSError:
        pass

@pytest.fixture(scope="session")
def test_config():
    """返回测试配置"""
    return {
        "api_base": "https://api2.liblib.art",
        "max_workers": 2,
        "timeout": 10,
        "retry_attempts": 2,
        "retry_delay": 0.1,
        "rate_limit": {
            "max_requests": 10,
            "time_window": 60
        },
        "database": {
            "host": "localhost",
            "port": 3306,
            "name": "test_cardesignspace",
            "user": "test_user",
            "password": "test_password"
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(levelname)s - %(message)s"
        }
    }

@pytest.fixture(scope="session")
def sample_car_models():
    """返回示例汽车模型数据"""
    from tests.fixtures.test_data import SAMPLE_CAR_MODELS
    return SAMPLE_CAR_MODELS

@pytest.fixture(scope="session")
def sample_api_response():
    """返回示例API响应数据"""
    from tests.fixtures.test_data import SAMPLE_API_RESPONSE
    return SAMPLE_API_RESPONSE

@pytest.fixture(scope="session")
def mock_session():
    """返回模拟会话对象"""
    from tests.fixtures.test_data import create_mock_session
    return create_mock_session()

@pytest.fixture(scope="session")
def mock_response():
    """返回模拟响应对象"""
    from tests.fixtures.test_data import create_mock_response
    return create_mock_response

# 环境检查
def pytest_sessionstart(session):
    """测试会话开始时的检查"""
    print(f"🔍 测试环境检查:")
    print(f"   项目根目录: {project_root}")
    print(f"   Python版本: {sys.version}")
    print(f"   工作目录: {os.getcwd()}")
    
    # 检查必要的目录
    required_dirs = ["src", "tests", "config"]
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"   ✅ {dir_name}: {dir_path}")
        else:
            print(f"   ❌ {dir_name}: 不存在")
    
    # 检查环境变量
    env_vars = ["TESTING", "DB_HOST", "DB_NAME"]
    for var in env_vars:
        value = os.environ.get(var, "未设置")
        print(f"   📋 {var}: {value}")

def pytest_sessionfinish(session, exitstatus):
    """测试会话结束时的清理"""
    print(f"\n🧹 测试会话清理:")
    print(f"   退出状态: {exitstatus}")
    print(f"   测试收集: {len(session.items)} 个测试项")
    
    # 清理测试输出目录中的临时文件
    test_output_dir = project_root / "test_output"
    if test_output_dir.exists():
        temp_files = list(test_output_dir.glob("temp_*"))
        for temp_file in temp_files:
            try:
                temp_file.unlink()
                print(f"   🗑️  清理临时文件: {temp_file.name}")
            except OSError:
                pass

# 自定义pytest选项
def pytest_addoption(parser):
    """添加自定义pytest选项"""
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="运行标记为slow的测试"
    )
    
    parser.addoption(
        "--run-performance",
        action="store_true",
        default=False,
        help="运行性能测试"
    )
    
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="运行集成测试"
    )

def pytest_runtest_setup(item):
    """测试运行前的设置"""
    # 检查是否应该跳过慢速测试
    if not item.config.getoption("--run-slow") and "slow" in item.keywords:
        pytest.skip("需要 --run-slow 选项来运行慢速测试")
    
    # 检查是否应该跳过性能测试
    if not item.config.getoption("--run-performance") and "performance" in item.keywords:
        pytest.skip("需要 --run-performance 选项来运行性能测试")
    
    # 检查是否应该跳过集成测试
    if not item.config.getoption("--run-integration") and "integration" in item.keywords:
        pytest.skip("需要 --run-integration 选项来运行集成测试")
