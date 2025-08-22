#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据夹具
提供各种测试场景的模拟数据
"""

import json
import tempfile
from pathlib import Path

# 模拟汽车模型数据
SAMPLE_CAR_MODELS = [
    {
        "id": "test_001",
        "title": "Tesla Model S 2024",
        "type": "car",
        "author": "Tesla Design Team",
        "category": "Electric Vehicle",
        "description": "Luxury electric sedan with advanced autopilot",
        "tags": ["electric", "luxury", "autopilot", "sedan"],
        "rating": 4.8,
        "downloads": 1250,
        "likes": 890,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-20T14:45:00Z"
    },
    {
        "id": "test_002",
        "title": "BMW iX Concept",
        "type": "car",
        "author": "BMW Group",
        "category": "Concept Car",
        "description": "Futuristic electric SUV concept",
        "tags": ["concept", "electric", "suv", "futuristic"],
        "rating": 4.6,
        "downloads": 890,
        "likes": 567,
        "created_at": "2024-01-10T09:15:00Z",
        "updated_at": "2024-01-18T16:20:00Z"
    },
    {
        "id": "test_003",
        "title": "Mercedes EQS",
        "type": "car",
        "author": "Mercedes-Benz",
        "category": "Luxury Electric",
        "description": "Premium electric luxury sedan",
        "tags": ["luxury", "electric", "sedan", "premium"],
        "rating": 4.7,
        "downloads": 1100,
        "likes": 720,
        "created_at": "2024-01-12T11:45:00Z",
        "updated_at": "2024-01-19T13:30:00Z"
    }
]

# 模拟API响应数据
SAMPLE_API_RESPONSE = {
    "code": 200,
    "message": "success",
    "data": {
        "list": SAMPLE_CAR_MODELS,
        "total": len(SAMPLE_CAR_MODELS),
        "page": 1,
        "pageSize": 24,
        "hasMore": False
    }
}

# 模拟配置数据
SAMPLE_CONFIG = {
    "api_base": "https://api2.liblib.art",
    "max_workers": 4,
    "timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 1,
    "rate_limit": {
        "max_requests": 100,
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

# 模拟错误响应
SAMPLE_ERROR_RESPONSE = {
    "code": 500,
    "message": "Internal server error",
    "error": "Database connection failed"
}

# 模拟速率限制响应
SAMPLE_RATE_LIMIT_RESPONSE = {
    "code": 429,
    "message": "Too many requests",
    "retry_after": 60
}

def create_temp_json_file(data, suffix=".json"):
    """创建临时JSON文件"""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False, encoding='utf-8')
    json.dump(data, temp_file, ensure_ascii=False, indent=2)
    temp_file.close()
    return temp_file.name

def create_temp_csv_file(data, suffix=".csv"):
    """创建临时CSV文件"""
    import csv
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False, encoding='utf-8', newline='')
    
    if data and isinstance(data, list):
        writer = csv.DictWriter(temp_file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    temp_file.close()
    return temp_file.name

def create_test_database_config():
    """创建测试数据库配置"""
    return {
        "host": "localhost",
        "port": 3306,
        "database": "test_cardesignspace",
        "user": "test_user",
        "password": "test_password",
        "charset": "utf8mb4"
    }

def create_test_api_config():
    """创建测试API配置"""
    return {
        "base_url": "https://api2.liblib.art",
        "endpoints": {
            "model_list": "/api/www/model/list",
            "model_detail": "/api/www/model/detail",
            "search": "/api/www/model/search"
        },
        "headers": {
            "User-Agent": "TestBot/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        "timeout": 30,
        "max_retries": 3
    }

def create_test_scraping_config():
    """创建测试采集配置"""
    return {
        "keywords": ["car", "vehicle", "automobile", "transportation"],
        "categories": ["car", "truck", "motorcycle", "concept"],
        "max_pages": 10,
        "page_size": 24,
        "delay_between_requests": 1.0,
        "concurrent_workers": 2
    }

def create_test_analysis_config():
    """创建测试分析配置"""
    return {
        "output_dir": "test_output",
        "report_formats": ["json", "csv", "html"],
        "analysis_types": ["trend", "category", "author", "rating"],
        "chart_types": ["bar", "line", "pie", "scatter"],
        "min_data_points": 10
    }

def cleanup_temp_files(file_paths):
    """清理临时文件"""
    import os
    
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Warning: Failed to cleanup {file_path}: {e}")

def get_sample_model_by_id(model_id):
    """根据ID获取示例模型"""
    for model in SAMPLE_CAR_MODELS:
        if model["id"] == model_id:
            return model
    return None

def get_sample_models_by_category(category):
    """根据分类获取示例模型"""
    return [model for model in SAMPLE_CAR_MODELS if model["category"] == category]

def get_sample_models_by_author(author):
    """根据作者获取示例模型"""
    return [model for model in SAMPLE_CAR_MODELS if model["author"] == author]

def create_mock_response(status_code=200, data=None, headers=None):
    """创建模拟响应对象"""
    class MockResponse:
        def __init__(self, status_code, data, headers):
            self.status_code = status_code
            self._data = data
            self.headers = headers or {}
        
        def json(self):
            return self._data
        
        def text(self):
            return json.dumps(self._data) if self._data else ""
    
    return MockResponse(status_code, data, headers)

def create_mock_session():
    """创建模拟会话对象"""
    class MockSession:
        def __init__(self):
            self.headers = {
                'User-Agent': 'TestBot/1.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        
        def post(self, url, json=None, timeout=None):
            # 模拟POST请求
            if "model/list" in url:
                return create_mock_response(200, SAMPLE_API_RESPONSE)
            elif "model/detail" in url:
                return create_mock_response(200, {"code": 200, "data": SAMPLE_CAR_MODELS[0]})
            else:
                return create_mock_response(404, {"code": 404, "message": "Not found"})
        
        def get(self, url, timeout=None):
            # 模拟GET请求
            return create_mock_response(200, {"code": 200, "message": "OK"})
    
    return MockSession()

# 测试数据生成器
class TestDataGenerator:
    """测试数据生成器"""
    
    @staticmethod
    def generate_car_models(count=10):
        """生成指定数量的汽车模型数据"""
        models = []
        brands = ["Tesla", "BMW", "Mercedes", "Audi", "Porsche", "Ferrari", "Lamborghini"]
        categories = ["Electric", "Hybrid", "Gasoline", "Concept", "Sports", "Luxury"]
        
        for i in range(count):
            model = {
                "id": f"generated_{i+1:03d}",
                "title": f"{brands[i % len(brands)]} Model {i+1}",
                "type": "car",
                "author": f"Designer {i+1}",
                "category": categories[i % len(categories)],
                "description": f"Generated test model {i+1}",
                "tags": ["test", "generated", f"model_{i+1}"],
                "rating": round(3.0 + (i % 20) / 10, 1),
                "downloads": (i + 1) * 100,
                "likes": (i + 1) * 50,
                "created_at": f"2024-01-{(i % 30) + 1:02d}T10:00:00Z",
                "updated_at": f"2024-01-{(i % 30) + 1:02d}T15:00:00Z"
            }
            models.append(model)
        
        return models
    
    @staticmethod
    def generate_api_responses(count=5):
        """生成指定数量的API响应数据"""
        responses = []
        
        for i in range(count):
            models = TestDataGenerator.generate_car_models(24)
            response = {
                "code": 200,
                "message": "success",
                "data": {
                    "list": models,
                    "total": len(models),
                    "page": i + 1,
                    "pageSize": 24,
                    "hasMore": i < count - 1
                }
            }
            responses.append(response)
        
        return responses
    
    @staticmethod
    def generate_error_scenarios():
        """生成错误场景数据"""
        return [
            {"code": 400, "message": "Bad Request", "error": "Invalid parameters"},
            {"code": 401, "message": "Unauthorized", "error": "Authentication required"},
            {"code": 403, "message": "Forbidden", "error": "Access denied"},
            {"code": 404, "message": "Not Found", "error": "Resource not found"},
            {"code": 429, "message": "Too Many Requests", "error": "Rate limit exceeded"},
            {"code": 500, "message": "Internal Server Error", "error": "Server error"},
            {"code": 502, "message": "Bad Gateway", "error": "Gateway error"},
            {"code": 503, "message": "Service Unavailable", "error": "Service unavailable"}
        ]

if __name__ == "__main__":
    # 测试数据生成器示例
    print("🚀 测试数据生成器示例")
    print("=" * 50)
    
    # 生成测试数据
    models = TestDataGenerator.generate_car_models(5)
    print(f"✅ 生成了 {len(models)} 个汽车模型")
    
    # 生成API响应
    responses = TestDataGenerator.generate_api_responses(3)
    print(f"✅ 生成了 {len(responses)} 个API响应")
    
    # 生成错误场景
    errors = TestDataGenerator.generate_error_scenarios()
    print(f"✅ 生成了 {len(errors)} 个错误场景")
    
    print("\n📊 测试数据准备完成！")
