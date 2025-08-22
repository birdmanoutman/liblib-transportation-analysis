#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T6 媒体下载器演示脚本
展示基本用法、配置和集成方式
"""

import os
import sys
import time
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# 加载环境变量
load_dotenv()

def demo_basic_usage():
    """演示基本用法"""
    print("🚀 T6 媒体下载器基本用法演示")
    print("=" * 50)
    
    try:
        from t6_media_downloader import MediaDownloader, MediaDownloaderConfig
        
        # 创建配置
        config = MediaDownloaderConfig()
        print(f"✅ 配置加载成功")
        print(f"   - 工作线程数: {config.max_workers}")
        print(f"   - 请求速率: {config.requests_per_second} RPS")
        print(f"   - 目标宽度: {config.target_width}")
        print(f"   - 目标格式: {config.target_format}")
        
        # 创建下载器
        downloader = MediaDownloader(config)
        print(f"✅ 下载器创建成功")
        
        # 检查数据库连接
        connection = downloader.get_database_connection()
        if connection:
            print(f"✅ 数据库连接成功")
            connection.close()
        else:
            print(f"❌ 数据库连接失败")
            return False
        
        # 检查S3连接
        if downloader.s3_manager.s3_client:
            print(f"✅ S3连接成功")
        else:
            print(f"❌ S3连接失败")
            return False
        
        print(f"✅ 基本功能检查完成")
        return True
        
    except Exception as e:
        print(f"❌ 基本用法演示失败: {e}")
        return False

def demo_config_management():
    """演示配置管理"""
    print("\n🔧 T6 媒体下载器配置管理演示")
    print("=" * 50)
    
    try:
        from t6_media_config import load_media_config, validate_config, print_config_summary
        
        # 演示不同环境配置
        for env in ['dev', 'test', 'prod']:
            print(f"\n--- {env.upper()} 环境配置 ---")
            config = load_media_config(env)
            print_config_summary(config)
            
            # 验证配置
            validation = validate_config(config)
            if validation['valid']:
                print("✅ 配置验证通过")
            else:
                print("❌ 配置验证失败")
                for error in validation['errors']:
                    print(f"   - {error}")
        
        print(f"✅ 配置管理演示完成")
        return True
        
    except Exception as e:
        print(f"❌ 配置管理演示失败: {e}")
        return False

def demo_oss_processing():
    """演示OSS图片处理"""
    print("\n🖼️  T6 媒体下载器OSS处理演示")
    print("=" * 50)
    
    try:
        from t6_media_downloader import MediaDownloader, MediaDownloaderConfig
        
        config = MediaDownloaderConfig()
        downloader = MediaDownloader(config)
        
        # 测试URL处理
        test_urls = [
            "https://liblibai-online.liblib.cloud/image1.jpg",
            "https://example.com/image2.png?existing=param",
            "https://test.com/image3.gif"
        ]
        
        print("OSS处理URL示例:")
        for url in test_urls:
            processed_url = downloader.process_image_url(url)
            print(f"原始: {url}")
            print(f"处理后: {processed_url}")
            print()
        
        print(f"✅ OSS处理演示完成")
        return True
        
    except Exception as e:
        print(f"❌ OSS处理演示失败: {e}")
        return False

def demo_database_integration():
    """演示数据库集成"""
    print("\n🗄️  T6 媒体下载器数据库集成演示")
    print("=" * 50)
    
    try:
        from t6_media_downloader import MediaDownloader, MediaDownloaderConfig
        
        config = MediaDownloaderConfig()
        downloader = MediaDownloader(config)
        
        # 查询待下载图片
        images = downloader.get_pending_images(limit=5)
        
        if images:
            print(f"✅ 找到 {len(images)} 张待下载图片")
            for i, img in enumerate(images[:3]):  # 只显示前3张
                print(f"   {i+1}. 作品: {img['work_title']}")
                print(f"      图片索引: {img['image_index']}")
                print(f"      状态: {img['status']}")
                print(f"      源URL: {img['src_url'][:50]}...")
                print()
        else:
            print("ℹ️  没有找到待下载的图片")
            print("   这可能是因为:")
            print("   - 数据库中没有work_images表")
            print("   - 表中没有PENDING或FAILED状态的图片")
            print("   - 需要先运行T5详情采集器")
        
        print(f"✅ 数据库集成演示完成")
        return True
        
    except Exception as e:
        print(f"❌ 数据库集成演示失败: {e}")
        return False

def demo_s3_integration():
    """演示S3集成"""
    print("\n🔗 T6 媒体下载器S3集成演示")
    print("=" * 50)
    
    try:
        from t6_media_downloader import MediaDownloader, MediaDownloaderConfig
        
        config = MediaDownloaderConfig()
        downloader = MediaDownloader(config)
        
        # 测试S3功能
        s3_manager = downloader.s3_manager
        
        if s3_manager.s3_client:
            print(f"✅ S3客户端已连接")
            print(f"   - 端点: {config.s3_endpoint}")
            print(f"   - 存储桶: {config.s3_bucket}")
            print(f"   - 区域: {config.s3_region}")
            
            # 测试存储桶访问
            try:
                s3_manager.s3_client.head_bucket(Bucket=config.s3_bucket)
                print(f"✅ 存储桶访问正常")
                
                # 演示S3键生成
                test_s3_key = downloader.generate_s3_key("test-work", 1, "https://example.com/image.jpg")
                print(f"✅ S3键生成示例: {test_s3_key}")
                
            except Exception as e:
                print(f"⚠️  存储桶访问测试失败: {e}")
        else:
            print(f"❌ S3客户端未连接")
            return False
        
        print(f"✅ S3集成演示完成")
        return True
        
    except Exception as e:
        print(f"❌ S3集成演示失败: {e}")
        return False

def demo_performance_features():
    """演示性能特性"""
    print("\n⚡ T6 媒体下载器性能特性演示")
    print("=" * 50)
    
    try:
        from t6_media_downloader import MediaDownloader, MediaDownloaderConfig
        
        config = MediaDownloaderConfig()
        downloader = MediaDownloader(config)
        
        print("性能特性:")
        print(f"   - 并发下载: {config.max_workers} 个工作线程")
        print(f"   - 限速控制: {config.requests_per_second} RPS")
        print(f"   - 重试机制: 最多 {config.max_retries} 次重试")
        print(f"   - 超时设置: {config.timeout} 秒")
        print(f"   - 文件验证: 大小={config.verify_size}, 哈希={config.verify_hash}")
        
        # 演示限速器
        print(f"\n限速器测试:")
        start_time = time.time()
        for i in range(5):
            downloader.rate_limiter.wait_if_needed()
            elapsed = time.time() - start_time
            print(f"   请求 {i+1}: {elapsed:.2f}s")
        
        print(f"✅ 性能特性演示完成")
        return True
        
    except Exception as e:
        print(f"❌ 性能特性演示失败: {e}")
        return False

def demo_integration_with_t5():
    """演示与T5的集成"""
    print("\n🔄 T6 媒体下载器与T5集成演示")
    print("=" * 50)
    
    try:
        # 检查T5模块是否存在
        try:
            from scripts.scraping.enhanced_detail_collector import EnhancedDetailCollector
            print("✅ T5详情采集器模块可用")
            
            # 演示集成方式
            print("\n集成方式:")
            print("1. T5执行详情采集:")
            print("   detail_collector = EnhancedDetailCollector()")
            print("   detail_collector.collect_details_batch(slugs)")
            print()
            print("2. T6并行下载媒体:")
            print("   from t6_media_downloader import MediaDownloader")
            print("   media_downloader = MediaDownloader()")
            print("   media_downloader.download_batch()")
            print()
            print("3. 或者等待T5完成后执行:")
            print("   # T5完成后")
            print("   media_downloader.download_batch()")
            
        except ImportError:
            print("⚠️  T5详情采集器模块不可用")
            print("   请确保已安装T5相关依赖")
        
        print(f"✅ 集成演示完成")
        return True
        
    except Exception as e:
        print(f"❌ 集成演示失败: {e}")
        return False

def run_all_demos():
    """运行所有演示"""
    print("🎬 开始运行T6媒体下载器演示套件")
    print("=" * 60)
    
    demos = [
        ("基本用法", demo_basic_usage),
        ("配置管理", demo_config_management),
        ("OSS处理", demo_oss_processing),
        ("数据库集成", demo_database_integration),
        ("S3集成", demo_s3_integration),
        ("性能特性", demo_performance_features),
        ("T5集成", demo_integration_with_t5)
    ]
    
    results = []
    
    for demo_name, demo_func in demos:
        try:
            print(f"\n{'='*20} {demo_name} {'='*20}")
            result = demo_func()
            results.append((demo_name, result))
            
            if result:
                print(f"✅ {demo_name} 演示成功")
            else:
                print(f"❌ {demo_name} 演示失败")
                
        except Exception as e:
            print(f"❌ {demo_name} 演示异常: {e}")
            results.append((demo_name, False))
        
        print("-" * 60)
    
    # 输出演示结果摘要
    print("\n" + "=" * 60)
    print("📊 演示结果摘要")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for demo_name, result in results:
        status = "✅ 成功" if result else "❌ 失败"
        print(f"{demo_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {total} 项演示")
    print(f"成功: {passed} 项")
    print(f"失败: {total - passed} 项")
    print(f"成功率: {(passed / total) * 100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有演示成功！T6媒体下载器功能完整")
        print("\n💡 下一步:")
        print("   1. 运行测试脚本: python test_t6_media_downloader.py")
        print("   2. 执行实际下载: python t6_media_downloader.py")
        print("   3. 查看详细文档: README_T6_MediaDownloader.md")
    else:
        print(f"\n⚠️  有 {total - passed} 项演示失败，请检查配置和依赖")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_demos()
    sys.exit(0 if success else 1)
