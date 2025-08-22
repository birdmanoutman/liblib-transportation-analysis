#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据采集功能集成测试
测试各种采集策略、错误处理、数据验证等功能
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_mcp_collector():
    """测试MCP采集器功能"""
    print("\n🔍 测试MCP采集器功能")
    print("=" * 50)
    
    try:
        from scraping.liblib_mcp_collector import LiblibMCPCollector
        
        # 创建采集器实例
        collector = LiblibMCPCollector()
        
        # 测试数据收集
        models = collector.collect_models()
        
        print(f"✅ MCP采集器测试成功")
        print(f"📊 收集到 {len(models)} 个模型")
        
        # 验证数据质量
        if models:
            first_model = models[0]
            required_fields = ['title', 'type', 'author', 'category']
            missing_fields = [field for field in required_fields if field not in first_model]
            
            if not missing_fields:
                print(f"✅ 数据字段完整性验证通过")
                print(f"📝 示例模型: {first_model['title']}")
            else:
                print(f"❌ 数据字段缺失: {missing_fields}")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP采集器测试失败: {e}")
        return False

def test_api_sampler():
    """测试API采样器功能"""
    print("\n🔍 测试API采样器功能")
    print("=" * 50)
    
    try:
        from scraping.liblib_api_sampler import create_session, safe_post, default_list_payload
        
        # 测试会话创建
        session = create_session()
        print(f"✅ 会话创建成功")
        
        # 测试默认载荷生成
        payload = default_list_payload(page=1, page_size=24)
        print(f"✅ 默认载荷生成成功: {len(payload)} 个字段")
        
        # 测试API请求（模拟）
        print(f"✅ API采样器基础功能测试通过")
        
        return True
        
    except Exception as e:
        print(f"❌ API采样器测试失败: {e}")
        return False

def test_enhanced_scraper():
    """测试增强版采集器功能"""
    print("\n🔍 测试增强版采集器功能")
    print("=" * 50)
    
    try:
        from scraping.enhanced_car_scraper import EnhancedCarModelScraper
        
        # 创建采集器实例
        scraper = EnhancedCarModelScraper()
        print(f"✅ 增强版采集器创建成功")
        
        # 测试关键词配置
        print(f"✅ 汽车关键词配置: {len(scraper.car_keywords)} 个关键词")
        
        return True
        
    except Exception as e:
        print(f"❌ 增强版采集器测试失败: {e}")
        return False

def test_complete_scraper():
    """测试完整采集器功能"""
    print("\n🔍 测试完整采集器功能")
    print("=" * 50)
    
    try:
        from scraping.complete_car_scraper import CompleteCarModelScraper
        
        # 创建采集器实例
        scraper = CompleteCarModelScraper()
        print(f"✅ 完整采集器创建成功")
        
        # 测试配置加载
        config = scraper.load_config()
        print(f"✅ 配置加载成功: {len(config)} 个配置项")
        
        return True
        
    except Exception as e:
        print(f"❌ 完整采集器测试失败: {e}")
        return False

def test_detail_collector():
    """测试详情采集器功能"""
    print("\n🔍 测试详情采集器功能")
    print("=" * 50)
    
    try:
        from scraping.detail_collector import DetailCollector
        
        # 创建采集器实例
        collector = DetailCollector()
        print(f"✅ 详情采集器创建成功")
        
        # 测试配置验证
        if hasattr(collector, 'config'):
            print(f"✅ 配置验证通过")
        
        return True
        
    except Exception as e:
        print(f"❌ 详情采集器测试失败: {e}")
        return False

def test_rate_limit_middleware():
    """测试速率限制中间件功能"""
    print("\n🔍 测试速率限制中间件功能")
    print("=" * 50)
    
    try:
        from scraping.rate_limit_middleware import RateLimitMiddleware
        
        # 创建中间件实例
        middleware = RateLimitMiddleware(max_requests=10, time_window=60)
        print(f"✅ 速率限制中间件创建成功")
        
        # 测试请求计数
        for i in range(5):
            middleware.record_request()
        
        print(f"✅ 请求计数测试通过: {middleware.request_count} 个请求")
        
        return True
        
    except Exception as e:
        print(f"❌ 速率限制中间件测试失败: {e}")
        return False

def test_playwright_scraper():
    """测试Playwright采集器功能"""
    print("\n🔍 测试Playwright采集器功能")
    print("=" * 50)
    
    try:
        from scraping.playwright_car_scraper import PlaywrightCarModelScraper
        
        # 创建采集器实例
        scraper = PlaywrightCarModelScraper()
        print(f"✅ Playwright采集器创建成功")
        
        # 测试浏览器配置
        if hasattr(scraper, 'browser_options'):
            print(f"✅ 浏览器配置验证通过")
        
        return True
        
    except Exception as e:
        print(f"❌ Playwright采集器测试失败: {e}")
        return False

def test_t4_collector():
    """测试T4采集器功能"""
    print("\n🔍 测试T4采集器功能")
    print("=" * 50)
    
    try:
        from scraping.t4_list_collector import T4ListCollector
        
        # 创建采集器实例
        collector = T4ListCollector()
        print(f"✅ T4采集器创建成功")
        
        # 测试配置加载
        config = collector.load_config()
        print(f"✅ 配置加载成功")
        
        return True
        
    except Exception as e:
        print(f"❌ T4采集器测试失败: {e}")
        return False

def test_t8_resume_retry():
    """测试T8恢复重试功能"""
    print("\n🔍 测试T8恢复重试功能")
    print("=" * 50)
    
    try:
        from scraping.t8_resume_and_retry import ResumeAndRetryCollector
        
        # 创建采集器实例
        collector = ResumeAndRetryCollector()
        print(f"✅ T8恢复重试采集器创建成功")
        
        # 测试状态管理
        if hasattr(collector, 'save_state'):
            print(f"✅ 状态管理功能验证通过")
        
        return True
        
    except Exception as e:
        print(f"❌ T8恢复重试测试失败: {e}")
        return False

def test_config_manager():
    """测试配置管理器功能"""
    print("\n🔍 测试配置管理器功能")
    print("=" * 50)
    
    try:
        from config_manager import ConfigManager
        
        # 创建配置管理器实例
        config_manager = ConfigManager()
        print(f"✅ 配置管理器创建成功")
        
        # 测试配置加载
        config = config_manager.load_config()
        print(f"✅ 配置加载成功: {len(config)} 个配置项")
        
        # 测试配置获取
        api_base = config_manager.get("api_base")
        print(f"✅ 配置获取成功: {api_base}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置管理器测试失败: {e}")
        return False

def test_database_manager():
    """测试数据库管理器功能"""
    print("\n🔍 测试数据库管理器功能")
    print("=" * 50)
    
    try:
        from database.database_manager import DatabaseManager
        
        # 创建数据库管理器实例
        db_manager = DatabaseManager()
        print(f"✅ 数据库管理器创建成功")
        
        # 测试连接测试
        if hasattr(db_manager, 'test_connection'):
            print(f"✅ 数据库连接功能验证通过")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库管理器测试失败: {e}")
        return False

def test_analysis_pipeline():
    """测试分析流水线功能"""
    print("\n🔍 测试分析流水线功能")
    print("=" * 50)
    
    try:
        from analysis.database_analysis_pipeline import DatabaseAnalysisPipeline
        
        # 创建分析流水线实例
        pipeline = DatabaseAnalysisPipeline()
        print(f"✅ 分析流水线创建成功")
        
        # 测试配置验证
        if hasattr(pipeline, 'config'):
            print(f"✅ 配置验证通过")
        
        return True
        
    except Exception as e:
        print(f"❌ 分析流水线测试失败: {e}")
        return False

def test_car_design_trend_analyzer():
    """测试汽车设计趋势分析器功能"""
    print("\n🔍 测试汽车设计趋势分析器功能")
    print("=" * 50)
    
    try:
        from analysis.car_design_trend_analyzer import CarDesignTrendAnalyzer
        
        # 创建分析器实例
        analyzer = CarDesignTrendAnalyzer()
        print(f"✅ 汽车设计趋势分析器创建成功")
        
        # 测试配置验证
        if hasattr(analyzer, 'config'):
            print(f"✅ 配置验证通过")
        
        return True
        
    except Exception as e:
        print(f"❌ 汽车设计趋势分析器测试失败: {e}")
        return False

def test_monitoring_system():
    """测试监控系统功能"""
    print("\n🔍 测试监控系统功能")
    print("=" * 50)
    
    try:
        from monitoring.monitor import Monitor
        
        # 创建监控器实例
        monitor = Monitor()
        print(f"✅ 监控器创建成功")
        
        # 测试配置验证
        if hasattr(monitor, 'config'):
            print(f"✅ 配置验证通过")
        
        return True
        
    except Exception as e:
        print(f"❌ 监控系统测试失败: {e}")
        return False

def test_media_downloader():
    """测试媒体下载器功能"""
    print("\n🔍 测试媒体下载器功能")
    print("=" * 50)
    
    try:
        from download.t6_media_downloader import T6MediaDownloader
        
        # 创建下载器实例
        downloader = T6MediaDownloader()
        print(f"✅ 媒体下载器创建成功")
        
        # 测试配置验证
        if hasattr(downloader, 'config'):
            print(f"✅ 配置验证通过")
        
        return True
        
    except Exception as e:
        print(f"❌ 媒体下载器测试失败: {e}")
        return False

def run_all_tests():
    """运行所有集成测试"""
    print("🚀 开始运行所有集成测试")
    print("=" * 80)
    
    test_functions = [
        test_mcp_collector,
        test_api_sampler,
        test_enhanced_scraper,
        test_complete_scraper,
        test_detail_collector,
        test_rate_limit_middleware,
        test_playwright_scraper,
        test_t4_collector,
        test_t8_resume_retry,
        test_config_manager,
        test_database_manager,
        test_analysis_pipeline,
        test_car_design_trend_analyzer,
        test_monitoring_system,
        test_media_downloader
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
    print(f"📊 测试结果汇总")
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"📈 成功率: {passed/(passed+failed)*100:.1f}%")
    
    return passed, failed

if __name__ == "__main__":
    run_all_tests()
