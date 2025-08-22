#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试版采集器
"""

import requests
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_api():
    """测试API调用"""
    api_base = "https://api2.liblib.art"
    url = f"{api_base}/api/www/model/list"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://www.liblib.art/',
        'Origin': 'https://www.liblib.art'
    }
    
    payload = {
        "categories": ["汽车交通"],
        "page": 1,
        "pageSize": 48,
        "sortType": "recommend",
        "modelType": "",
        "nsfw": False
    }
    
    try:
        logger.info("发送API请求...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        logger.info(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"响应数据类型: {type(data)}")
            logger.info(f"响应数据键: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
            
            # 保存完整响应以供检查
            with open('debug_response.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("响应已保存到 debug_response.json")
            
            if isinstance(data, dict) and 'data' in data:
                data_content = data['data']
                logger.info(f"data键内容类型: {type(data_content)}")
                logger.info(f"data键内容: {data_content}")
                
                if isinstance(data_content, dict) and 'list' in data_content:
                    models = data_content['list']
                    logger.info(f"获取到 {len(models)} 个模型")
                    
                    # 检查第一个模型的数据结构
                    if models:
                        first_model = models[0]
                        logger.info(f"第一个模型的数据结构: {first_model.keys() if isinstance(first_model, dict) else 'Not a dict'}")
                        logger.info(f"第一个模型标题: {first_model.get('title', 'No title')}")
                        logger.info(f"第一个模型描述: {first_model.get('description', 'No description')}")
                        
                        # 保存响应以供检查
                        with open('debug_response.json', 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        logger.info("响应已保存到 debug_response.json")
                        
                    return models
        else:
            logger.error(f"API请求失败: {response.text}")
            
    except Exception as e:
        logger.error(f"请求异常: {e}")
        
    return []

if __name__ == "__main__":
    models = test_api()
    if models:
        logger.info(f"成功获取 {len(models)} 个模型")
    else:
        logger.error("未获取到任何模型")
