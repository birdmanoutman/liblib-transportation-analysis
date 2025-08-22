#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T5 详情采集器测试脚本
测试 group/get/{slug}、author/{slug} 接口
验证字段校验与缺省策略
"""

import os
import sys
import json
import time
import requests
from typing import Dict, Any, Optional

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def test_api_endpoints():
    """测试API端点"""
    print("🔍 测试API端点...")
    
    # API配置
    api_base = 'https://api2.liblib.art'
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://www.liblib.art/',
        'Origin': 'https://www.liblib.art'
    })
    
    def get_timestamp():
        return int(time.time() * 1000)
    
    # 测试1: 搜索汽车交通模型列表（使用正确的API接口）
    print("\n📋 测试1: 搜索汽车交通模型列表")
    search_url = f"{api_base}/api/www/model/list"
    search_payload = {
        "categories": ["汽车交通"],  # 使用正确的参数格式
        "page": 1,
        "pageSize": 10,
        "sortType": "recommend",
        "modelType": "",
        "nsfw": False
    }
    
    try:
        response = session.post(search_url, json=search_payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0:
                models = data.get('data', {}).get('list', [])
                print(f"✅ 搜索成功，获取到 {len(models)} 个模型")
                
                # 保存搜索结果用于后续测试
                with open('test_search_results.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                # 提取前3个模型ID用于详情测试
                test_model_ids = []
                for model in models[:3]:
                    model_id = model.get('uuid')
                    if model_id:
                        test_model_ids.append(model_id)
                        print(f"   - {model.get('title', 'Unknown')} (ID: {model_id})")
                
                return test_model_ids
            else:
                print(f"❌ 搜索失败: {data.get('message', 'Unknown error')}")
                print(f"响应数据: {data}")
        else:
            print(f"❌ 搜索请求失败: HTTP {response.status_code}")
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 搜索异常: {e}")
    
    return []
    
def test_model_detail_api(model_id: str):
    """测试模型详情API"""
    print(f"\n🖼️ 测试模型详情API: {model_id}")
    
    api_base = 'https://api2.liblib.art'
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://www.liblib.art/',
        'Origin': 'https://www.liblib.art'
    })
    
    def get_timestamp():
        return int(time.time() * 1000)
    
    # 测试模型详情接口
    detail_url = f"{api_base}/api/www/model/getByUuid/{model_id}"
    detail_params = {
        "timestamp": get_timestamp()
    }
    
    try:
        response = session.post(detail_url, params=detail_params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0:
                model_data = data.get('data', {})
                print(f"✅ 模型详情获取成功")
                print(f"   标题: {model_data.get('title', 'Unknown')}")
                print(f"   类型: {model_data.get('type', 'Unknown')}")
                print(f"   基础模型: {model_data.get('baseModel', 'Unknown')}")
                print(f"   标签数量: {len(model_data.get('tagList', []))}")
                print(f"   下载数: {model_data.get('downloadCount', 0)}")
                
                # 保存详情数据
                with open(f'test_model_detail_{model_id}.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                return model_data
            else:
                print(f"❌ 模型详情获取失败: {data.get('message', 'Unknown error')}")
                print(f"响应数据: {data}")
        else:
            print(f"❌ 模型详情请求失败: HTTP {response.status_code}")
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 模型详情异常: {e}")
    
    return None

def test_author_api(model_id: str):
    """测试作者API"""
    print(f"\n👤 测试作者API: {model_id}")
    
    api_base = 'https://api2.liblib.art'
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://www.liblib.art/',
        'Origin': 'https://www.liblib.art'
    })
    
    def get_timestamp():
        return int(time.time() * 1000)
    
    # 测试作者接口
    author_url = f"{api_base}/api/www/model/author/{model_id}"
    author_params = {
        "timestamp": get_timestamp()
    }
    
    try:
        response = session.post(author_url, params=author_params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0:
                author_data = data.get('data', {})
                print(f"✅ 作者信息获取成功")
                print(f"   昵称: {author_data.get('nickname', 'Unknown')}")
                print(f"   用户名: {author_data.get('username', 'Unknown')}")
                print(f"   头像: {author_data.get('avatar', 'No avatar')}")
                print(f"   模型数: {author_data.get('modelCount', 0)}")
                
                # 保存作者数据
                with open(f'test_author_{model_id}.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                return author_data
            else:
                print(f"❌ 作者信息获取失败: {data.get('message', 'Unknown error')}")
                print(f"响应数据: {data}")
        else:
            print(f"❌ 作者信息请求失败: HTTP {response.status_code}")
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 作者信息异常: {e}")
    
    return None

def test_comments_api(model_id: str):
    """测试评论API"""
    print(f"\n💬 测试评论API: {model_id}")
    
    api_base = 'https://api2.liblib.art'
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://www.liblib.art/',
        'Origin': 'https://www.liblib.art'
    })
    
    def get_timestamp():
        return int(time.time() * 1000)
    
    # 测试评论接口
    comments_url = f"{api_base}/api/www/community/commentList"
    comments_payload = {
        "modelId": model_id,
        "page": 1,
        "pageSize": 10,
        "sortType": "hot",
        "timestamp": get_timestamp()
    }
    
    try:
        response = session.post(comments_url, json=comments_payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0:
                comments = data.get('data', {}).get('list', [])
                print(f"✅ 评论获取成功，共 {len(comments)} 条评论")
                
                # 显示前3条评论
                for i, comment in enumerate(comments[:3]):
                    print(f"   评论{i+1}: {comment.get('content', '')[:50]}...")
                
                # 保存评论数据
                with open(f'test_comments_{model_id}.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                return comments
            else:
                print(f"❌ 评论获取失败: {data.get('message', 'Unknown error')}")
                print(f"响应数据: {data}")
        else:
            print(f"❌ 评论请求失败: HTTP {response.status_code}")
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 评论异常: {e}")
    
    return None

def analyze_api_structure():
    """分析API响应结构"""
    print("\n🔍 分析API响应结构...")
    
    # 检查保存的测试文件
    test_files = [
        'test_search_results.json',
        'test_model_detail_*.json',
        'test_author_*.json',
        'test_comments_*.json'
    ]
    
    import glob
    for pattern in test_files:
        files = glob.glob(pattern)
        for file_path in files:
            if os.path.exists(file_path):
                print(f"\n📄 分析文件: {file_path}")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 分析数据结构
                    if 'data' in data:
                        if 'list' in data['data']:
                            print("   📋 列表结构 (list)")
                            if data['data']['list']:
                                first_item = data['data']['list'][0]
                                print(f"   示例字段: {list(first_item.keys())}")
                        else:
                            print("   📄 详情结构 (single item)")
                            print(f"   字段: {list(data['data'].keys())}")
                except Exception as e:
                    print(f"   ❌ 文件读取失败: {e}")

def main():
    """主测试函数"""
    print("🚀 T5 详情采集器测试开始")
    print("=" * 50)
    
    try:
        # 1. 测试搜索接口，获取测试用的模型ID
        test_model_ids = test_api_endpoints()
        
        if not test_model_ids:
            print("❌ 无法获取测试用的模型ID，测试终止")
            return
        
        # 2. 测试模型详情API
        for model_id in test_model_ids[:2]:  # 只测试前2个
            model_data = test_model_detail_api(model_id)
            
            if model_data:
                # 3. 测试作者API
                test_author_api(model_id)
                
                # 4. 测试评论API
                test_comments_api(model_id)
        
        # 5. 分析API结构
        analyze_api_structure()
        
        print("\n" + "=" * 50)
        print("✅ T5 详情采集器测试完成")
        print("📁 测试数据已保存到当前目录")
        
    except KeyboardInterrupt:
        print("\n❌ 用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")

if __name__ == "__main__":
    main()
