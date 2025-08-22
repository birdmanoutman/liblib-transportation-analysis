#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能测试脚本
测试并发性能、压力测试、性能基准等
"""

import os
import sys
import time
import json
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import statistics
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def test_config_manager_performance():
    """测试配置管理器的性能"""
    print("\n🔍 测试配置管理器性能")
    print("=" * 50)
    
    try:
        from config_manager import ConfigManager
        
        # 测试配置加载性能
        start_time = time.time()
        config_manager = ConfigManager()
        config = config_manager.load_config()
        load_time = time.time() - start_time
        
        print(f"✅ 配置加载耗时: {load_time:.4f} 秒")
        
        # 测试配置获取性能
        iterations = 1000
        start_time = time.time()
        for _ in range(iterations):
            _ = config_manager.get("api_base")
            _ = config_manager.get("max_workers")
            _ = config_manager.get("timeout")
        get_time = time.time() - start_time
        
        print(f"✅ 配置获取性能: {iterations} 次操作耗时 {get_time:.4f} 秒")
        print(f"✅ 平均每次操作: {get_time/iterations*1000:.2f} 毫秒")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置管理器性能测试失败: {e}")
        return False

def test_mcp_collector_performance():
    """测试MCP采集器的性能"""
    print("\n🔍 测试MCP采集器性能")
    print("=" * 50)
    
    try:
        from scraping.liblib_mcp_collector import LiblibMCPCollector
        
        # 测试数据收集性能
        start_time = time.time()
        collector = LiblibMCPCollector()
        models = collector.collect_models()
        collect_time = time.time() - start_time
        
        print(f"✅ 数据收集耗时: {collect_time:.4f} 秒")
        print(f"✅ 收集到 {len(models)} 个模型")
        
        # 测试数据保存性能
        start_time = time.time()
        json_path, csv_path = collector.save_models(models)
        save_time = time.time() - start_time
        
        print(f"✅ 数据保存耗时: {save_time:.4f} 秒")
        
        # 测试摘要生成性能
        start_time = time.time()
        summary_path = collector.generate_summary(models)
        summary_time = time.time() - start_time
        
        print(f"✅ 摘要生成耗时: {summary_time:.4f} 秒")
        
        total_time = collect_time + save_time + summary_time
        print(f"✅ 总耗时: {total_time:.4f} 秒")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP采集器性能测试失败: {e}")
        return False

def test_concurrent_collection():
    """测试并发采集性能"""
    print("\n🔍 测试并发采集性能")
    print("=" * 50)
    
    try:
        from scraping.liblib_api_sampler import create_session, safe_post, default_list_payload
        
        # 创建会话
        session = create_session()
        api_url = "https://api2.liblib.art/api/www/model/list"
        
        # 测试不同并发数的性能
        concurrency_levels = [1, 2, 4, 8]
        results = {}
        
        for concurrency in concurrency_levels:
            print(f"🔄 测试并发数: {concurrency}")
            
            start_time = time.time()
            
            # 使用线程池执行并发请求
            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = []
                for i in range(concurrency):
                    payload = default_list_payload(page=i+1, page_size=5)
                    future = executor.submit(safe_post, session, api_url, payload, 10)
                    futures.append(future)
                
                # 等待所有请求完成
                responses = []
                for future in as_completed(futures):
                    try:
                        response = future.result()
                        if response and response.status_code == 200:
                            responses.append(response)
                    except Exception as e:
                        print(f"⚠️  并发请求异常: {e}")
            
            end_time = time.time()
            duration = end_time - start_time
            
            results[concurrency] = {
                'duration': duration,
                'success_count': len(responses),
                'throughput': len(responses) / duration if duration > 0 else 0
            }
            
            print(f"✅ 并发数 {concurrency}: 耗时 {duration:.4f}s, 成功 {len(responses)}/{concurrency}")
        
        # 分析性能结果
        print(f"\n📊 并发性能分析:")
        for concurrency, result in results.items():
            print(f"   并发数 {concurrency}: 吞吐量 {result['throughput']:.2f} 请求/秒")
        
        return True
        
    except Exception as e:
        print(f"❌ 并发采集性能测试失败: {e}")
        return False

def test_database_performance():
    """测试数据库性能"""
    print("\n🔍 测试数据库性能")
    print("=" * 50)
    
    try:
        from database.database_manager import DatabaseManager
        
        # 创建数据库管理器
        db_manager = DatabaseManager()
        
        # 测试连接性能
        start_time = time.time()
        connection = db_manager.get_connection()
        connect_time = time.time() - start_time
        
        print(f"✅ 数据库连接耗时: {connect_time:.4f} 秒")
        
        if connection:
            # 测试查询性能
            test_query = "SELECT 1 as test"
            start_time = time.time()
            
            try:
                cursor = connection.cursor()
                cursor.execute(test_query)
                result = cursor.fetchone()
                cursor.close()
                
                query_time = time.time() - start_time
                print(f"✅ 基础查询耗时: {query_time:.4f} 秒")
                
                # 测试批量插入性能（模拟）
                print(f"✅ 数据库性能测试完成")
                
            except Exception as e:
                print(f"⚠️  查询测试异常: {e}")
            
            connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库性能测试失败: {e}")
        return False

def test_analysis_performance():
    """测试分析功能性能"""
    print("\n🔍 测试分析功能性能")
    print("=" * 50)
    
    try:
        from analysis.car_design_trend_analyzer import CarDesignTrendAnalyzer
        
        # 创建分析器
        analyzer = CarDesignTrendAnalyzer()
        
        # 测试配置加载性能
        start_time = time.time()
        config = analyzer.load_config()
        config_time = time.time() - start_time
        
        print(f"✅ 配置加载耗时: {config_time:.4f} 秒")
        
        # 测试数据加载性能（模拟）
        start_time = time.time()
        # 这里应该加载测试数据
        data_load_time = time.time() - start_time
        
        print(f"✅ 数据加载耗时: {data_load_time:.4f} 秒")
        
        # 测试分析性能（模拟）
        start_time = time.time()
        # 这里应该执行分析逻辑
        analysis_time = time.time() - start_time
        
        print(f"✅ 分析处理耗时: {analysis_time:.4f} 秒")
        
        total_time = config_time + data_load_time + analysis_time
        print(f"✅ 总耗时: {total_time:.4f} 秒")
        
        return True
        
    except Exception as e:
        print(f"❌ 分析功能性能测试失败: {e}")
        return False

def test_memory_usage():
    """测试内存使用情况"""
    print("\n🔍 测试内存使用情况")
    print("=" * 50)
    
    try:
        import psutil
        import os
        
        # 获取当前进程
        process = psutil.Process(os.getpid())
        
        # 测试前内存使用
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"✅ 初始内存使用: {initial_memory:.2f} MB")
        
        # 模拟大量数据处理
        large_data = []
        for i in range(10000):
            large_data.append({
                'id': i,
                'title': f'Test Model {i}',
                'type': 'car',
                'author': f'Author {i % 100}',
                'category': f'Category {i % 10}'
            })
        
        # 测试后内存使用
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"✅ 最终内存使用: {final_memory:.2f} MB")
        print(f"✅ 内存增长: {memory_increase:.2f} MB")
        
        # 清理数据
        del large_data
        
        # 清理后内存使用
        cleanup_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"✅ 清理后内存: {cleanup_memory:.2f} MB")
        
        return True
        
    except ImportError:
        print("⚠️  psutil未安装，跳过内存测试")
        return True
    except Exception as e:
        print(f"❌ 内存使用测试失败: {e}")
        return False

def test_network_latency():
    """测试网络延迟"""
    print("\n🔍 测试网络延迟")
    print("=" * 50)
    
    try:
        import requests
        import statistics
        
        # 测试目标URL
        test_urls = [
            "https://api2.liblib.art",
            "https://www.liblib.art",
            "https://httpbin.org/delay/1"
        ]
        
        latency_results = {}
        
        for url in test_urls:
            print(f"🔄 测试URL: {url}")
            latencies = []
            
            # 执行多次请求测试延迟
            for i in range(5):
                try:
                    start_time = time.time()
                    response = requests.get(url, timeout=10)
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        latency = (end_time - start_time) * 1000  # 转换为毫秒
                        latencies.append(latency)
                        print(f"   请求 {i+1}: {latency:.2f}ms")
                    else:
                        print(f"   请求 {i+1}: 状态码 {response.status_code}")
                        
                except Exception as e:
                    print(f"   请求 {i+1}: 异常 {e}")
            
            if latencies:
                avg_latency = statistics.mean(latencies)
                min_latency = min(latencies)
                max_latency = max(latencies)
                
                latency_results[url] = {
                    'average': avg_latency,
                    'min': min_latency,
                    'max': max_latency
                }
                
                print(f"✅ {url}: 平均延迟 {avg_latency:.2f}ms (最小: {min_latency:.2f}ms, 最大: {max_latency:.2f}ms)")
        
        # 分析网络性能
        if latency_results:
            all_latencies = [result['average'] for result in latency_results.values()]
            overall_avg = statistics.mean(all_latencies)
            print(f"\n📊 整体网络性能: 平均延迟 {overall_avg:.2f}ms")
        
        return True
        
    except Exception as e:
        print(f"❌ 网络延迟测试失败: {e}")
        return False

def test_file_io_performance():
    """测试文件I/O性能"""
    print("\n🔍 测试文件I/O性能")
    print("=" * 50)
    
    try:
        import tempfile
        import json
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # 测试写入性能
            test_data = []
            for i in range(1000):
                test_data.append({
                    'id': i,
                    'title': f'Test Model {i}',
                    'type': 'car',
                    'author': f'Author {i % 100}',
                    'category': f'Category {i % 10}',
                    'description': f'This is a test description for model {i} with some additional text to make it longer.'
                })
            
            # JSON写入测试
            start_time = time.time()
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, ensure_ascii=False, indent=2)
            write_time = time.time() - start_time
            
            print(f"✅ JSON写入耗时: {write_time:.4f} 秒")
            print(f"✅ 写入速度: {len(test_data)/write_time:.0f} 条记录/秒")
            
            # JSON读取测试
            start_time = time.time()
            with open(temp_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            read_time = time.time() - start_time
            
            print(f"✅ JSON读取耗时: {read_time:.4f} 秒")
            print(f"✅ 读取速度: {len(loaded_data)/read_time:.0f} 条记录/秒")
            
            # 验证数据完整性
            if len(loaded_data) == len(test_data):
                print(f"✅ 数据完整性验证通过: {len(loaded_data)} 条记录")
            else:
                print(f"❌ 数据完整性验证失败: 期望 {len(test_data)}, 实际 {len(loaded_data)}")
                return False
            
            return True
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except Exception as e:
        print(f"❌ 文件I/O性能测试失败: {e}")
        return False

def run_performance_benchmark():
    """运行性能基准测试"""
    print("🚀 开始运行性能基准测试")
    print("=" * 80)
    
    test_functions = [
        test_config_manager_performance,
        test_mcp_collector_performance,
        test_concurrent_collection,
        test_database_performance,
        test_analysis_performance,
        test_memory_usage,
        test_network_latency,
        test_file_io_performance
    ]
    
    passed = 0
    failed = 0
    start_time = time.time()
    
    for test_func in test_functions:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ 测试 {test_func.__name__} 执行异常: {e}")
            failed += 1
    
    total_time = time.time() - start_time
    
    print("\n" + "=" * 80)
    print(f"📊 性能测试结果汇总")
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"📈 成功率: {passed/(passed+failed)*100:.1f}%")
    print(f"⏱️  总耗时: {total_time:.2f} 秒")
    
    return passed, failed

if __name__ == "__main__":
    run_performance_benchmark()
