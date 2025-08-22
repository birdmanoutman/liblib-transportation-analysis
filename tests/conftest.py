#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pytest配置文件
设置测试环境和路径
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts"))
sys.path.insert(0, str(project_root / "scripts" / "scraping"))

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

def pytest_collection_modifyitems(config, items):
    """修改测试项集合"""
    for item in items:
        # 为测试文件添加标记
        if "test_t11_core_logic.py" in str(item.fspath):
            item.add_marker("unit")
        elif "test_t8_resume_retry.py" in str(item.fspath):
            item.add_marker("unit")
        elif "test_liblib_analyzer.py" in str(item.fspath):
            item.add_marker("unit")
        elif "integration" in str(item.fspath):
            item.add_marker("integration")
