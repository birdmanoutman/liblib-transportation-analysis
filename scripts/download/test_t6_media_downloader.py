#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T6 媒体下载器测试脚本
测试配置、S3连接、数据库连接等功能
"""

import os
import sys
import time
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# 加载环境变量
load_dotenv()

def test_config_loading():
    """测试配置加载"""
    print("🔧 测试配置加载...")
    
    try:
        from t6_media_config import load_media_config, validate_config, print_config_summary
        
        # 测试不同环境配置
        for env in ['dev', 'test', 'prod']:
            print(f"\n--- 测试 {env.upper()} 环境配置 ---")
            config = load_media_config(env)
            print_config_summary(config)
            
            # 验证配置
            validation = validate_config(config)
            if validation['valid']:
                print("✅ 配置验证通过")
            else:
                print("❌ 配置验证失败:")
                for error in validation['errors']:
                    print(f"   - {error}")
            
            if validation['warnings']:
                print("⚠️  配置警告:")
                for warning in validation['warnings']:
                    print(f"   - {warning}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置加载测试失败: {e}")
        return False

def test_s3_connection():
    """测试S3连接"""
    print("\n🔗 测试S3连接...")
    
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        # 获取S3配置
        s3_endpoint = os.getenv('S3_ENDPOINT')
        s3_bucket = os.getenv('S3_BUCKET')
        s3_access_key = os.getenv('S3_ACCESS_KEY')
        s3_secret_key = os.getenv('S3_SECRET_KEY')
        s3_region = os.getenv('S3_REGION', 'us-east-1')
        
        if not all([s3_endpoint, s3_bucket, s3_access_key, s3_secret_key]):
            print("⚠️  S3配置不完整，跳过连接测试")
            return False
        
        # 创建S3客户端
        s3_config = {
            'endpoint_url': s3_endpoint,
            'aws_access_key_id': s3_access_key,
            'aws_secret_access_key': s3_secret_key,
            'region_name': s3_region
        }
        
        s3_client = boto3.client('s3', **s3_config)
        
        # 测试连接
        print(f"正在连接 {s3_endpoint}...")
        response = s3_client.list_buckets()
        print(f"✅ 连接成功，找到 {len(response['Buckets'])} 个存储桶")
        
        # 测试目标存储桶
        print(f"正在测试存储桶 {s3_bucket}...")
        s3_client.head_bucket(Bucket=s3_bucket)
        print(f"✅ 存储桶 {s3_bucket} 访问正常")
        
        # 测试上传权限（上传一个测试文件）
        test_key = 'test/t6_media_downloader_test.txt'
        test_content = f'T6媒体下载器测试文件 - {time.strftime("%Y-%m-%d %H:%M:%S")}'
        
        print(f"正在测试上传权限...")
        s3_client.put_object(
            Bucket=s3_bucket,
            Key=test_key,
            Body=test_content.encode('utf-8'),
            ContentType='text/plain'
        )
        print(f"✅ 上传测试成功: {test_key}")
        
        # 清理测试文件
        s3_client.delete_object(Bucket=s3_bucket, Key=test_key)
        print(f"✅ 测试文件清理完成")
        
        return True
        
    except ImportError:
        print("❌ boto3 未安装，无法测试S3连接")
        return False
    except Exception as e:
        print(f"❌ S3连接测试失败: {e}")
        return False

def test_database_connection():
    """测试数据库连接"""
    print("\n🗄️  测试数据库连接...")
    
    try:
        import mysql.connector
        from mysql.connector import Error
        
        # 获取数据库配置
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = int(os.getenv('DB_PORT', '3306'))
        db_name = os.getenv('DB_NAME', 'cardesignspace')
        db_user = os.getenv('DB_USER', 'root')
        db_password = os.getenv('DB_PASSWORD', '')
        
        print(f"正在连接数据库 {db_host}:{db_port}/{db_name}...")
        
        connection = mysql.connector.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        
        if connection.is_connected():
            print("✅ 数据库连接成功")
            
            # 测试查询
            cursor = connection.cursor()
            
            # 检查必要的表是否存在
            cursor.execute("SHOW TABLES LIKE 'work_images'")
            if cursor.fetchone():
                print("✅ work_images 表存在")
                
                # 检查表结构
                cursor.execute("DESCRIBE work_images")
                columns = cursor.fetchall()
                required_columns = ['id', 'work_id', 'image_index', 'src_url', 's3_key', 'status']
                
                existing_columns = [col[0] for col in columns]
                missing_columns = [col for col in required_columns if col not in existing_columns]
                
                if not missing_columns:
                    print("✅ work_images 表结构完整")
                else:
                    print(f"⚠️  缺少必要的列: {missing_columns}")
                
                # 检查是否有待下载的图片
                cursor.execute("SELECT COUNT(*) FROM work_images WHERE status IN ('PENDING', 'FAILED')")
                pending_count = cursor.fetchone()[0]
                print(f"📊 待下载图片数量: {pending_count}")
                
            else:
                print("❌ work_images 表不存在")
            
            cursor.close()
            connection.close()
            print("✅ 数据库连接已关闭")
            
            return True
            
        else:
            print("❌ 数据库连接失败")
            return False
            
    except ImportError:
        print("❌ mysql-connector-python 未安装，无法测试数据库连接")
        return False
    except Error as e:
        print(f"❌ 数据库连接测试失败: {e}")
        return False

def test_media_downloader_import():
    """测试媒体下载器模块导入"""
    print("\n📦 测试媒体下载器模块导入...")
    
    try:
        from t6_media_downloader import MediaDownloader, MediaDownloaderConfig
        print("✅ 媒体下载器模块导入成功")
        
        # 测试配置创建
        config = MediaDownloaderConfig()
        print("✅ 配置对象创建成功")
        
        # 测试下载器创建
        downloader = MediaDownloader(config)
        print("✅ 下载器对象创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 媒体下载器模块导入失败: {e}")
        return False

def test_oss_process_url():
    """测试OSS处理URL生成"""
    print("\n🖼️  测试OSS处理URL生成...")
    
    try:
        from t6_media_downloader import MediaDownloader, MediaDownloaderConfig
        
        config = MediaDownloaderConfig()
        downloader = MediaDownloader(config)
        
        # 测试URL
        test_urls = [
            "https://liblibai-online.liblib.cloud/image1.jpg",
            "https://example.com/image2.png?existing=param",
            "https://test.com/image3.gif"
        ]
        
        for url in test_urls:
            processed_url = downloader.process_image_url(url)
            print(f"原始URL: {url}")
            print(f"处理后: {processed_url}")
            print()
        
        print("✅ OSS处理URL生成测试通过")
        return True
        
    except Exception as e:
        print(f"❌ OSS处理URL生成测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始运行T6媒体下载器测试套件")
    print("=" * 60)
    
    test_results = []
    
    # 运行各项测试
    tests = [
        ("配置加载", test_config_loading),
        ("S3连接", test_s3_connection),
        ("数据库连接", test_database_connection),
        ("模块导入", test_media_downloader_import),
        ("OSS处理URL", test_oss_process_url)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            test_results.append((test_name, False))
    
    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("📊 测试结果摘要")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {total} 项测试")
    print(f"通过: {passed} 项")
    print(f"失败: {total - passed} 项")
    print(f"成功率: {(passed / total) * 100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有测试通过！T6媒体下载器准备就绪")
        return True
    else:
        print(f"\n⚠️  有 {total - passed} 项测试失败，请检查配置和依赖")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
