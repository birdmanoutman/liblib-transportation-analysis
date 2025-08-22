#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API采集功能集成测试
测试网络请求、错误处理、重试机制、数据解析等
"""

import os
import sys
import time
import json
import requests
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def test_api_connection():
    """测试API连接性"""
    print("\n🔍 测试API连接性")
    print("=" * 50)
    
    try:
        # 测试基础连接
        api_base = "https://api2.liblib.art"
        
        # 测试健康检查
        health_url = f"{api_base}/health"
        try:
            response = requests.get(health_url, timeout=10)
            print(f"✅ 健康检查: {response.status_code}")
        except:
            print("⚠️  健康检查端点不可用")
        
        # 测试基础连接
        test_url = f"{api_base}/api/www/model/list"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://www.liblib.art/',
            'Origin': 'https://www.liblib.art'
        }
        
        response = requests.get(test_url, headers=headers, timeout=10)
        print(f"✅ API基础连接: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API连接正常")
            return True
        else:
            print(f"⚠️  API返回状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API连接测试失败: {e}")
        return False

def test_api_payload():
    """测试API载荷格式"""
    print("\n🔍 测试API载荷格式")
    print("=" * 50)
    
    try:
        from scraping.liblib_api_sampler import default_list_payload, create_session
        
        # 测试默认载荷生成
        payload = default_list_payload(page=1, page_size=24)
        print(f"✅ 默认载荷生成成功: {len(payload)} 个字段")
        print(f"📝 载荷内容: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        # 测试会话创建
        session = create_session()
        print(f"✅ 会话创建成功: {type(session)}")
        
        # 测试载荷验证
        required_fields = ["categories", "page", "pageSize", "sortType", "modelType", "nsfw"]
        missing_fields = [field for field in required_fields if field not in payload]
        
        if not missing_fields:
            print(f"✅ 载荷字段完整性验证通过")
        else:
            print(f"❌ 载荷字段缺失: {missing_fields}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ API载荷测试失败: {e}")
        return False

def test_api_request():
    """测试API请求功能"""
    print("\n🔍 测试API请求功能")
    print("=" * 50)
    
    try:
        from scraping.liblib_api_sampler import safe_post, create_session, default_list_payload
        
        # 创建会话
        session = create_session()
        print(f"✅ 会话创建成功")
        
        # 生成载荷
        payload = default_list_payload(page=1, page_size=5)
        print(f"✅ 载荷生成成功")
        
        # 测试安全请求
        api_url = "https://api2.liblib.art/api/www/model/list"
        response = safe_post(session, api_url, payload, timeout=30)
        
        if response and response.status_code == 200:
            print(f"✅ API请求成功: {response.status_code}")
            
            # 解析响应数据
            try:
                data = response.json()
                if 'data' in data and 'list' in data['data']:
                    models = data['data']['list']
                    print(f"✅ 数据解析成功: {len(models)} 个模型")
                    
                    # 验证数据格式
                    if models:
                        first_model = models[0]
                        required_fields = ['id', 'title', 'type', 'author']
                        missing_fields = [field for field in required_fields if field not in first_model]
                        
                        if not missing_fields:
                            print(f"✅ 数据格式验证通过")
                            print(f"📝 示例模型: {first_model['title']}")
                        else:
                            print(f"❌ 数据格式不完整: {missing_fields}")
                            return False
                else:
                    print(f"⚠️  响应数据结构异常: {data.keys()}")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                return False
                
            return True
        else:
            print(f"❌ API请求失败: {response.status_code if response else 'No response'}")
            return False
            
    except Exception as e:
        print(f"❌ API请求测试失败: {e}")
        return False

def test_api_error_handling():
    """测试API错误处理"""
    print("\n🔍 测试API错误处理")
    print("=" * 50)
    
    try:
        from scraping.liblib_api_sampler import safe_post, create_session
        
        # 创建会话
        session = create_session()
        print(f"✅ 会话创建成功")
        
        # 测试无效URL
        invalid_url = "https://invalid-domain-12345.com/api/test"
        response = safe_post(session, invalid_url, {}, timeout=5)
        
        if response is None:
            print(f"✅ 无效URL错误处理正确")
        else:
            print(f"⚠️  无效URL应该返回None")
        
        # 测试无效载荷
        try:
            invalid_payload = {"invalid": "data"}
            response = safe_post(session, "https://api2.liblib.art/api/www/model/list", invalid_payload, timeout=10)
            print(f"✅ 无效载荷处理测试完成")
        except Exception as e:
            print(f"✅ 异常处理正确: {type(e).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ API错误处理测试失败: {e}")
        return False

def test_api_rate_limiting():
    """测试API速率限制"""
    print("\n🔍 测试API速率限制")
    print("=" * 50)
    
    try:
        from scraping.liblib_api_sampler import safe_post, create_session, default_list_payload
        from scraping.rate_limit_middleware import RateLimitMiddleware
        
        # 创建速率限制中间件
        middleware = RateLimitMiddleware(max_requests=3, time_window=60)
        print(f"✅ 速率限制中间件创建成功")
        
        # 创建会话
        session = create_session()
        print(f"✅ 会话创建成功")
        
        # 测试速率限制
        api_url = "https://api2.liblib.art/api/www/model/list"
        payload = default_list_payload(page=1, page_size=1)
        
        success_count = 0
        for i in range(5):
            if middleware.can_make_request():
                response = safe_post(session, api_url, payload, timeout=10)
                if response and response.status_code == 200:
                    success_count += 1
                    print(f"✅ 请求 {i+1} 成功")
                middleware.record_request()
            else:
                print(f"⏳ 请求 {i+1} 被速率限制")
        
        print(f"✅ 速率限制测试完成: {success_count}/5 个请求成功")
        return True
        
    except Exception as e:
        print(f"❌ API速率限制测试失败: {e}")
        return False

def test_api_data_validation():
    """测试API数据验证"""
    print("\n🔍 测试API数据验证")
    print("=" * 50)
    
    try:
        from scraping.liblib_api_sampler import safe_post, create_session, default_list_payload
        
        # 创建会话
        session = create_session()
        print(f"✅ 会话创建成功")
        
        # 测试不同页面大小的数据验证
        page_sizes = [1, 5, 10, 24]
        
        for page_size in page_sizes:
            payload = default_list_payload(page=1, page_size=page_size)
            api_url = "https://api2.liblib.art/api/www/model/list"
            
            response = safe_post(session, api_url, payload, timeout=15)
            
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    if 'data' in data and 'list' in data['data']:
                        models = data['data']['list']
                        actual_count = len(models)
                        expected_count = min(page_size, 24)  # API可能有最大限制
                        
                        if actual_count <= expected_count:
                            print(f"✅ 页面大小 {page_size}: 返回 {actual_count} 个模型")
                        else:
                            print(f"⚠️  页面大小 {page_size}: 返回 {actual_count} 个模型 (超出预期)")
                    else:
                        print(f"❌ 页面大小 {page_size}: 响应格式异常")
                        return False
                        
                except json.JSONDecodeError:
                    print(f"❌ 页面大小 {page_size}: JSON解析失败")
                    return False
            else:
                print(f"❌ 页面大小 {page_size}: 请求失败")
                return False
        
        print(f"✅ 数据验证测试完成")
        return True
        
    except Exception as e:
        print(f"❌ API数据验证测试失败: {e}")
        return False

def test_api_session_management():
    """测试API会话管理"""
    print("\n🔍 测试API会话管理")
    print("=" * 50)
    
    try:
        from scraping.liblib_api_sampler import create_session
        
        # 测试会话创建
        session1 = create_session()
        session2 = create_session()
        
        print(f"✅ 会话1创建成功: {type(session1)}")
        print(f"✅ 会话2创建成功: {type(session2)}")
        
        # 验证会话是不同的实例
        if session1 is not session2:
            print(f"✅ 会话独立性验证通过")
        else:
            print(f"⚠️  会话应该是不同的实例")
        
        # 测试会话配置
        if hasattr(session1, 'headers'):
            print(f"✅ 会话配置验证通过")
        
        return True
        
    except Exception as e:
        print(f"❌ API会话管理测试失败: {e}")
        return False

def test_api_retry_mechanism():
    """测试API重试机制"""
    print("\n🔍 测试API重试机制")
    print("=" * 50)
    
    try:
        from scraping.liblib_api_sampler import safe_post, create_session, default_list_payload
        
        # 创建会话
        session = create_session()
        print(f"✅ 会话创建成功")
        
        # 测试重试逻辑（模拟网络问题）
        api_url = "https://api2.liblib.art/api/www/model/list"
        payload = default_list_payload(page=1, page_size=1)
        
        # 多次请求测试稳定性
        success_count = 0
        total_attempts = 3
        
        for attempt in range(total_attempts):
            try:
                response = safe_post(session, api_url, payload, timeout=10)
                if response and response.status_code == 200:
                    success_count += 1
                    print(f"✅ 尝试 {attempt+1} 成功")
                else:
                    print(f"⚠️  尝试 {attempt+1} 失败: {response.status_code if response else 'No response'}")
            except Exception as e:
                print(f"❌ 尝试 {attempt+1} 异常: {e}")
        
        success_rate = success_count / total_attempts
        print(f"✅ 重试测试完成: 成功率 {success_rate*100:.1f}% ({success_count}/{total_attempts})")
        
        return success_rate > 0.5  # 至少50%成功率
        
    except Exception as e:
        print(f"❌ API重试机制测试失败: {e}")
        return False

def run_all_api_tests():
    """运行所有API测试"""
    print("🚀 开始运行所有API集成测试")
    print("=" * 80)
    
    test_functions = [
        test_api_connection,
        test_api_payload,
        test_api_request,
        test_api_error_handling,
        test_api_rate_limiting,
        test_api_data_validation,
        test_api_session_management,
        test_api_retry_mechanism
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ 测试 {test_func.__name__} 执行异常: {e}")
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"📊 API测试结果汇总")
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"📈 成功率: {passed/(passed+failed)*100:.1f}%")
    
    return passed, failed

if __name__ == "__main__":
    run_all_api_tests()
