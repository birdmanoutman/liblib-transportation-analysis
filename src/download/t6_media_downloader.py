#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T6 媒体下载器
并发下载图组到S3，支持x-oss-process控制格式与尺寸，失败重试与校验
"""

import os
import sys
import json
import time
import logging
import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
import requests
from urllib.parse import urlparse
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import signal
from queue import Queue
import mimetypes

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# 加载环境变量
load_dotenv()

class MediaDownloaderConfig:
    """T6媒体下载器配置"""
    
    def __init__(self):
        # S3/MinIO配置
        self.storage_driver = os.getenv('STORAGE_DRIVER', 's3')
        self.s3_endpoint = os.getenv('S3_ENDPOINT')
        self.s3_bucket = os.getenv('S3_BUCKET')
        self.s3_region = os.getenv('S3_REGION', 'us-east-1')
        self.s3_access_key = os.getenv('S3_ACCESS_KEY')
        self.s3_secret_key = os.getenv('S3_SECRET_KEY')
        
        # 数据库配置
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_port = int(os.getenv('DB_PORT', '3306'))
        self.db_name = os.getenv('DB_NAME', 'cardesignspace')
        self.db_user = os.getenv('DB_USER', 'root')
        self.db_password = os.getenv('DB_PASSWORD', '')
        
        # 下载配置
        self.max_workers = int(os.getenv('MEDIA_MAX_WORKERS', '10'))
        self.requests_per_second = float(os.getenv('MEDIA_RPS', '5.0'))
        self.max_retries = int(os.getenv('MEDIA_MAX_RETRIES', '3'))
        self.timeout = int(os.getenv('MEDIA_TIMEOUT', '30'))
        
        # 图片处理配置
        self.target_width = int(os.getenv('MEDIA_TARGET_WIDTH', '1024'))
        self.target_format = os.getenv('MEDIA_TARGET_FORMAT', 'webp')
        self.quality = int(os.getenv('MEDIA_QUALITY', '85'))
        
        # 验证配置
        self.verify_size = os.getenv('MEDIA_VERIFY_SIZE', 'true').lower() == 'true'
        self.verify_hash = os.getenv('MEDIA_VERIFY_HASH', 'true').lower() == 'true'
        self.min_file_size = int(os.getenv('MEDIA_MIN_SIZE', '1024'))  # 1KB

class RateLimiter:
    """请求限速器"""
    
    def __init__(self, requests_per_second: float):
        self.requests_per_second = requests_per_second
        self.delay = 1.0 / requests_per_second
        self.last_request_time = 0
        self.lock = threading.Lock()
    
    def wait_if_needed(self):
        """等待如果需要限速"""
        with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            if time_since_last < self.delay:
                sleep_time = self.delay - time_since_last
                time.sleep(sleep_time)
            
            self.last_request_time = time.time()

class S3StorageManager:
    """S3存储管理器"""
    
    def __init__(self, config: MediaDownloaderConfig):
        self.config = config
        self.s3_client = None
        self.setup_s3_client()
    
    def setup_s3_client(self):
        """设置S3客户端"""
        try:
            if self.config.storage_driver == 's3':
                s3_config = {
                    'endpoint_url': self.config.s3_endpoint,
                    'aws_access_key_id': self.config.s3_access_key,
                    'aws_secret_access_key': self.config.s3_secret_key,
                    'region_name': self.config.s3_region
                }
                
                # 如果是MinIO，需要特殊配置
                if 'minio' in self.config.s3_endpoint.lower():
                    s3_config['aws_access_key_id'] = self.config.s3_access_key
                    s3_config['aws_secret_access_key'] = self.config.s3_secret_key
                
                self.s3_client = boto3.client('s3', **s3_config)
                
                # 测试连接
                self.s3_client.head_bucket(Bucket=self.config.s3_bucket)
                logging.info(f"✅ S3连接成功: {self.config.s3_endpoint}")
                
        except Exception as e:
            logging.error(f"❌ S3连接失败: {e}")
            self.s3_client = None
    
    def upload_file(self, file_data: bytes, s3_key: str, content_type: str = None) -> bool:
        """上传文件到S3"""
        if not self.s3_client:
            return False
        
        try:
            # 自动检测内容类型
            if not content_type:
                content_type = mimetypes.guess_type(s3_key)[0] or 'application/octet-stream'
            
            # 上传文件
            self.s3_client.put_object(
                Bucket=self.config.s3_bucket,
                Key=s3_key,
                Body=file_data,
                ContentType=content_type,
                Metadata={
                    'uploaded_at': datetime.now().isoformat(),
                    'source': 't6_media_downloader'
                }
            )
            
            logging.debug(f"✅ 上传成功: {s3_key}")
            return True
            
        except Exception as e:
            logging.error(f"❌ 上传失败 {s3_key}: {e}")
            return False
    
    def file_exists(self, s3_key: str) -> bool:
        """检查文件是否已存在"""
        if not self.s3_client:
            return False
        
        try:
            self.s3_client.head_object(Bucket=self.config.s3_bucket, Key=s3_key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                logging.warning(f"检查文件存在性失败 {s3_key}: {e}")
                return False
        except Exception as e:
            logging.warning(f"检查文件存在性异常 {s3_key}: {e}")
            return False

class MediaDownloader:
    """T6媒体下载器主类"""
    
    def __init__(self, config: MediaDownloaderConfig = None):
        self.config = config or MediaDownloaderConfig()
        self.setup_logging()
        
        # 初始化组件
        self.rate_limiter = RateLimiter(self.config.requests_per_second)
        self.s3_manager = S3StorageManager(self.config)
        self.session = requests.Session()
        
        # 统计信息
        self.stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'retried': 0,
            'start_time': None,
            'end_time': None
        }
        
        # 线程安全的统计更新
        self.stats_lock = threading.Lock()
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.shutdown_requested = False
    
    def setup_logging(self):
        """设置日志"""
        log_level = getattr(self.config, 'log_level', 'INFO')
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('t6_media_downloader.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('T6MediaDownloader')
    
    def signal_handler(self, signum, frame):
        """信号处理器"""
        self.logger.info(f"收到信号 {signum}，开始优雅关闭...")
        self.shutdown_requested = True
    
    def get_database_connection(self):
        """获取数据库连接"""
        try:
            connection = mysql.connector.connect(
                host=self.config.db_host,
                port=self.config.db_port,
                database=self.config.db_name,
                user=self.config.db_user,
                password=self.config.db_password,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            return connection
        except Error as e:
            self.logger.error(f"数据库连接失败: {e}")
            return None
    
    def get_pending_images(self, limit: int = 1000) -> List[Dict]:
        """获取待下载的图片列表"""
        connection = self.get_database_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # 查询待下载的图片
            query = """
                SELECT 
                    wi.id,
                    wi.work_id,
                    wi.image_index,
                    wi.src_url,
                    wi.s3_key,
                    wi.status,
                    w.slug as work_slug,
                    w.title as work_title
                FROM work_images wi
                JOIN works w ON wi.work_id = w.id
                WHERE wi.status IN ('PENDING', 'FAILED')
                AND wi.src_url IS NOT NULL
                AND wi.src_url != ''
                ORDER BY wi.created_at ASC
                LIMIT %s
            """
            
            cursor.execute(query, (limit,))
            images = cursor.fetchall()
            
            self.logger.info(f"找到 {len(images)} 张待下载图片")
            return images
            
        except Error as e:
            self.logger.error(f"查询待下载图片失败: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def generate_s3_key(self, work_slug: str, image_index: int, original_url: str) -> str:
        """生成S3存储键"""
        # 解析原始URL获取文件扩展名
        parsed_url = urlparse(original_url)
        path = parsed_url.path
        
        # 获取文件扩展名
        if '.' in path:
            ext = path.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                ext = 'jpg'
        else:
            ext = 'jpg'
        
        # 生成S3键：works/{work_slug}/images/{image_index}.{ext}
        s3_key = f"works/{work_slug}/images/{image_index:03d}.{ext}"
        return s3_key
    
    def process_image_url(self, original_url: str) -> str:
        """处理图片URL，添加OSS处理参数"""
        if not original_url:
            return original_url
        
        # 移除现有的查询参数
        base_url = original_url.split('?')[0]
        
        # 添加OSS处理参数
        oss_params = [
            f"x-oss-process=image/resize,w_{self.config.target_width},m_lfit",
            f"format,{self.config.target_format}",
            f"quality,Q_{self.config.quality}"
        ]
        
        processed_url = f"{base_url}?{'/'.join(oss_params)}"
        return processed_url
    
    def download_and_upload_image(self, image_info: Dict) -> Dict:
        """下载并上传单个图片"""
        image_id = image_info['id']
        work_slug = image_info['work_slug']
        image_index = image_info['image_index']
        original_url = image_info['src_url']
        
        try:
            # 生成S3键
            s3_key = self.generate_s3_key(work_slug, image_index, original_url)
            
            # 检查S3是否已存在
            if self.s3_manager.file_exists(s3_key):
                self.logger.debug(f"图片已存在，跳过: {s3_key}")
                return {
                    'image_id': image_id,
                    'status': 'skipped',
                    's3_key': s3_key,
                    'message': '图片已存在'
                }
            
            # 限速等待
            self.rate_limiter.wait_if_needed()
            
            # 处理图片URL
            processed_url = self.process_image_url(original_url)
            
            # 下载图片
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = self.session.get(
                processed_url, 
                headers=headers, 
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            image_data = response.content
            
            # 验证文件大小
            if self.config.verify_size and len(image_data) < self.config.min_file_size:
                raise ValueError(f"文件大小过小: {len(image_data)} bytes")
            
            # 计算内容哈希
            content_hash = None
            if self.config.verify_hash:
                content_hash = hashlib.md5(image_data).hexdigest()
            
            # 上传到S3
            content_type = response.headers.get('content-type', 'image/jpeg')
            if not self.s3_manager.upload_file(image_data, s3_key, content_type):
                raise Exception("S3上传失败")
            
            # 更新数据库状态
            self.update_image_status(image_id, 'OK', s3_key, content_hash, len(image_data))
            
            return {
                'image_id': image_id,
                'status': 'success',
                's3_key': s3_key,
                'content_hash': content_hash,
                'size_bytes': len(image_data),
                'message': '下载并上传成功'
            }
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"处理图片失败 {image_id}: {error_msg}")
            
            # 更新数据库状态
            self.update_image_status(image_id, 'FAILED', None, None, None, error_msg)
            
            return {
                'image_id': image_id,
                'status': 'failed',
                'error': error_msg,
                'message': '处理失败'
            }
    
    def update_image_status(self, image_id: int, status: str, s3_key: str = None, 
                           content_hash: str = None, size_bytes: int = None, 
                           error_message: str = None):
        """更新图片状态"""
        connection = self.get_database_connection()
        if not connection:
            return
        
        try:
            cursor = connection.cursor()
            
            if status == 'OK':
                query = """
                    UPDATE work_images 
                    SET status = %s, s3_key = %s, content_hash = %s, 
                        size_bytes = %s, downloaded_at = NOW()
                    WHERE id = %s
                """
                cursor.execute(query, (status, s3_key, content_hash, size_bytes, image_id))
            else:
                query = """
                    UPDATE work_images 
                    SET status = %s, downloaded_at = NOW()
                    WHERE id = %s
                """
                cursor.execute(query, (status, image_id))
            
            connection.commit()
            
        except Error as e:
            self.logger.error(f"更新图片状态失败 {image_id}: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def download_batch(self, max_images: int = 1000) -> Dict:
        """批量下载图片"""
        self.logger.info("开始批量下载图片...")
        
        # 重置统计
        self.stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'retried': 0,
            'start_time': datetime.now(),
            'end_time': None
        }
        
        # 获取待下载图片
        images = self.get_pending_images(max_images)
        if not images:
            self.logger.warning("没有找到待下载的图片")
            return self.stats
        
        self.stats['total'] = len(images)
        self.logger.info(f"开始处理 {len(images)} 张图片")
        
        # 并发下载
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # 提交所有任务
            future_to_image = {
                executor.submit(self.download_and_upload_image, image): image 
                for image in images
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_image):
                if self.shutdown_requested:
                    self.logger.info("收到关闭信号，停止处理新任务...")
                    break
                
                try:
                    result = future.result()
                    self.update_stats(result['status'])
                    
                    # 记录结果
                    if result['status'] == 'success':
                        self.logger.debug(f"✅ 成功: {result['s3_key']}")
                    elif result['status'] == 'skipped':
                        self.logger.debug(f"⏭️  跳过: {result['message']}")
                    else:
                        self.logger.warning(f"❌ 失败: {result['error']}")
                        
                except Exception as e:
                    self.logger.error(f"任务执行异常: {e}")
                    self.update_stats('failed')
        
        # 完成统计
        self.stats['end_time'] = datetime.now()
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        
        # 计算成功率
        success_rate = (self.stats['successful'] / self.stats['total']) * 100 if self.stats['total'] > 0 else 0
        
        self.logger.info(f"批量下载完成!")
        self.logger.info(f"总计: {self.stats['total']} 张")
        self.logger.info(f"成功: {self.stats['successful']} 张")
        self.logger.info(f"失败: {self.stats['failed']} 张")
        self.logger.info(f"跳过: {self.stats['skipped']} 张")
        self.logger.info(f"成功率: {success_rate:.2f}%")
        self.logger.info(f"耗时: {duration:.2f} 秒")
        
        # 验收检查
        if success_rate >= 99.0:
            self.logger.info("✅ 验收标准通过：下载成功率 ≥99%")
        else:
            self.logger.warning(f"⚠️  验收标准未通过：下载成功率 {success_rate:.2f}% < 99%")
        
        return self.stats
    
    def update_stats(self, status: str):
        """更新统计信息"""
        with self.stats_lock:
            if status == 'success':
                self.stats['successful'] += 1
            elif status == 'failed':
                self.stats['failed'] += 1
            elif status == 'skipped':
                self.stats['skipped'] += 1
    
    def retry_failed_images(self, max_retries: int = None) -> Dict:
        """重试失败的图片"""
        max_retries = max_retries or self.config.max_retries
        self.logger.info(f"开始重试失败的图片，最大重试次数: {max_retries}")
        
        # 获取失败的图片
        connection = self.get_database_connection()
        if not connection:
            return {}
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT 
                    wi.id,
                    wi.work_id,
                    wi.image_index,
                    wi.src_url,
                    w.slug as work_slug,
                    w.title as work_title
                FROM work_images wi
                JOIN works w ON wi.work_id = w.id
                WHERE wi.status = 'FAILED'
                AND wi.src_url IS NOT NULL
                AND wi.src_url != ''
                ORDER BY wi.updated_at ASC
            """
            
            cursor.execute(query)
            failed_images = cursor.fetchall()
            
            if not failed_images:
                self.logger.info("没有找到失败的图片")
                return {}
            
            self.logger.info(f"找到 {len(failed_images)} 张失败的图片，开始重试...")
            
            # 重试下载
            return self.download_batch(len(failed_images))
            
        except Error as e:
            self.logger.error(f"查询失败图片失败: {e}")
            return {}
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

def main():
    """主函数"""
    # 创建配置
    config = MediaDownloaderConfig()
    
    # 创建下载器
    downloader = MediaDownloader(config)
    
    try:
        # 执行批量下载
        stats = downloader.download_batch()
        
        # 如果有失败的图片，尝试重试
        if stats['failed'] > 0:
            print(f"\n发现 {stats['failed']} 张失败的图片，开始重试...")
            retry_stats = downloader.retry_failed_images()
            
            # 合并统计
            final_success_rate = ((stats['successful'] + retry_stats.get('successful', 0)) / 
                                stats['total']) * 100 if stats['total'] > 0 else 0
            
            print(f"重试后最终成功率: {final_success_rate:.2f}%")
        
    except KeyboardInterrupt:
        print("\n用户中断，正在关闭...")
    except Exception as e:
        print(f"程序异常: {e}")
        logging.error(f"程序异常: {e}", exc_info=True)

if __name__ == "__main__":
    main()
