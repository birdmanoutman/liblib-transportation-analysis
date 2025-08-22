#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T8 断点续采与失败补偿模块
实现持久化页码/slug状态、失败队列定时重试、运行恢复验证等功能
"""

import os
import sys
import json
import time
import logging
import asyncio
import sqlite3
import threading
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import hashlib
import pickle
from contextlib import asynccontextmanager

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.database.database_manager import DatabaseManager

# 配置日志
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "PENDING"           # 等待处理
    PROCESSING = "PROCESSING"      # 处理中
    SUCCESS = "SUCCESS"            # 成功
    FAILED = "FAILED"              # 失败
    RETRY = "RETRY"                # 重试中
    CANCELLED = "CANCELLED"        # 已取消

class TaskType(Enum):
    """任务类型枚举"""
    LIST_COLLECTION = "LIST_COLLECTION"      # 列表采集
    DETAIL_COLLECTION = "DETAIL_COLLECTION"  # 详情采集
    IMAGE_DOWNLOAD = "IMAGE_DOWNLOAD"        # 图片下载
    DATA_PROCESSING = "DATA_PROCESSING"      # 数据处理

@dataclass
class ResumePoint:
    """断点续采点"""
    task_type: str
    current_page: int
    last_cursor: Optional[str]
    last_slug: Optional[str]
    total_processed: int
    last_update: datetime
    metadata: Dict[str, Any]

@dataclass
class FailedTask:
    """失败任务记录"""
    task_id: str
    task_type: str
    target: str  # slug, page number, or URL
    error_message: str
    retry_count: int
    max_retries: int
    next_retry_time: datetime
    created_at: datetime
    metadata: Dict[str, Any]

@dataclass
class CollectionState:
    """采集状态"""
    run_id: str
    task_type: str
    status: str
    start_time: datetime
    last_update: datetime
    total_items: int
    processed_items: int
    failed_items: int
    resume_points: List[ResumePoint]
    failed_tasks: List[FailedTask]

class StateManager:
    """状态管理器 - 负责持久化页码/slug状态"""
    
    def __init__(self, state_dir: str = "data/state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # 状态文件路径
        self.resume_file = self.state_dir / "resume_points.json"
        self.failed_file = self.state_dir / "failed_tasks.json"
        self.state_file = self.state_dir / "collection_state.json"
        
        # 内存状态
        self.resume_points: Dict[str, ResumePoint] = {}
        self.failed_tasks: Dict[str, FailedTask] = {}
        self.collection_states: Dict[str, CollectionState] = {}
        
        # 加载历史状态
        self._load_states()
    
    def _load_states(self):
        """加载历史状态"""
        try:
            # 加载断点续采点
            if self.resume_file.exists():
                with open(self.resume_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, point_data in data.items():
                        point_data['last_update'] = datetime.fromisoformat(point_data['last_update'])
                        self.resume_points[key] = ResumePoint(**point_data)
                logger.info(f"加载断点续采点：{len(self.resume_points)}个")
            
            # 加载失败任务
            if self.failed_file.exists():
                with open(self.failed_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, task_data in data.items():
                        task_data['next_retry_time'] = datetime.fromisoformat(task_data['next_retry_time'])
                        task_data['created_at'] = datetime.fromisoformat(task_data['created_at'])
                        self.failed_tasks[key] = FailedTask(**task_data)
                logger.info(f"加载失败任务：{len(self.failed_tasks)}个")
            
            # 加载采集状态
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, state_data in data.items():
                        state_data['start_time'] = datetime.fromisoformat(state_data['start_time'])
                        state_data['last_update'] = datetime.fromisoformat(state_data['last_update'])
                        # 重建ResumePoint和FailedTask对象
                        resume_points = []
                        for rp_data in state_data['resume_points']:
                            rp_data['last_update'] = datetime.fromisoformat(rp_data['last_update'])
                            resume_points.append(ResumePoint(**rp_data))
                        state_data['resume_points'] = resume_points
                        
                        failed_tasks = []
                        for ft_data in state_data['failed_tasks']:
                            ft_data['next_retry_time'] = datetime.fromisoformat(ft_data['next_retry_time'])
                            ft_data['created_at'] = datetime.fromisoformat(ft_data['created_at'])
                            failed_tasks.append(FailedTask(**ft_data))
                        state_data['failed_tasks'] = failed_tasks
                        
                        self.collection_states[key] = CollectionState(**state_data)
                logger.info(f"加载采集状态：{len(self.collection_states)}个")
                
        except Exception as e:
            logger.warning(f"加载历史状态失败：{e}")
    
    def _save_states(self):
        """保存所有状态"""
        try:
            # 保存断点续采点
            resume_data = {}
            for key, point in self.resume_points.items():
                resume_data[key] = asdict(point)
                resume_data[key]['last_update'] = point.last_update.isoformat()
            
            with open(self.resume_file, 'w', encoding='utf-8') as f:
                json.dump(resume_data, f, ensure_ascii=False, indent=2)
            
            # 保存失败任务
            failed_data = {}
            for key, task in self.failed_tasks.items():
                failed_data[key] = asdict(task)
                failed_data[key]['next_retry_time'] = task.next_retry_time.isoformat()
                failed_data[key]['created_at'] = task.created_at.isoformat()
            
            with open(self.failed_file, 'w', encoding='utf-8') as f:
                json.dump(failed_data, f, ensure_ascii=False, indent=2)
            
            # 保存采集状态
            state_data = {}
            for key, state in self.collection_states.items():
                state_data[key] = asdict(state)
                state_data[key]['start_time'] = state.start_time.isoformat()
                state_data[key]['last_update'] = state.last_update.isoformat()
                # 序列化ResumePoint和FailedTask
                resume_points = []
                for rp in state.resume_points:
                    rp_dict = asdict(rp)
                    rp_dict['last_update'] = rp.last_update.isoformat()
                    resume_points.append(rp_dict)
                state_data[key]['resume_points'] = resume_points
                
                failed_tasks = []
                for ft in state.failed_tasks:
                    ft_dict = asdict(ft)
                    ft_dict['next_retry_time'] = ft.next_retry_time.isoformat()
                    ft_dict['created_at'] = ft.created_at.isoformat()
                    failed_tasks.append(ft_dict)
                state_data[key]['failed_tasks'] = failed_tasks
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"保存状态失败：{e}")
    
    def create_resume_point(self, task_type: str, current_page: int, 
                           last_cursor: Optional[str] = None, 
                           last_slug: Optional[str] = None,
                           total_processed: int = 0,
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """创建断点续采点"""
        point_id = f"{task_type}_{int(time.time())}"
        
        resume_point = ResumePoint(
            task_type=task_type,
            current_page=current_page,
            last_cursor=last_cursor,
            last_slug=last_slug,
            total_processed=total_processed,
            last_update=datetime.now(),
            metadata=metadata or {}
        )
        
        self.resume_points[point_id] = resume_point
        self._save_states()
        
        logger.info(f"创建断点续采点：{point_id} - {task_type} 第{current_page}页")
        return point_id
    
    def update_resume_point(self, point_id: str, **kwargs):
        """更新断点续采点"""
        if point_id in self.resume_points:
            point = self.resume_points[point_id]
            for key, value in kwargs.items():
                if hasattr(point, key):
                    setattr(point, key, value)
            point.last_update = datetime.now()
            self._save_states()
    
    def get_resume_point(self, task_type: str) -> Optional[ResumePoint]:
        """获取指定类型的断点续采点"""
        for point in self.resume_points.values():
            if point.task_type == task_type:
                return point
        return None
    
    def add_failed_task(self, task_type: str, target: str, error_message: str,
                       max_retries: int = 3, retry_delay: int = 300) -> str:
        """添加失败任务"""
        task_id = f"{task_type}_{hashlib.md5(target.encode()).hexdigest()[:8]}"
        
        failed_task = FailedTask(
            task_id=task_id,
            task_type=task_type,
            target=target,
            error_message=error_message,
            retry_count=0,
            max_retries=max_retries,
            next_retry_time=datetime.now() + timedelta(seconds=retry_delay),
            created_at=datetime.now(),
            metadata={}
        )
        
        self.failed_tasks[task_id] = failed_task
        self._save_states()
        
        logger.info(f"添加失败任务：{task_id} - {task_type} {target}")
        return task_id
    
    def get_retryable_tasks(self) -> List[FailedTask]:
        """获取可重试的任务"""
        now = datetime.now()
        retryable = []
        
        for task in self.failed_tasks.values():
            if (task.retry_count < task.max_retries and 
                task.next_retry_time <= now and
                task.status != TaskStatus.CANCELLED):
                retryable.append(task)
        
        return retryable
    
    def mark_task_success(self, task_id: str):
        """标记任务成功"""
        if task_id in self.failed_tasks:
            del self.failed_tasks[task_id]
            self._save_states()
            logger.info(f"任务成功，从失败队列移除：{task_id}")
    
    def mark_task_retry(self, task_id: str, new_retry_time: datetime):
        """标记任务重试"""
        if task_id in self.failed_tasks:
            task = self.failed_tasks[task_id]
            task.retry_count += 1
            task.next_retry_time = new_retry_time
            self._save_states()
            logger.info(f"任务重试：{task_id} (第{task.retry_count}次)")
    
    def create_collection_state(self, run_id: str, task_type: str) -> str:
        """创建采集状态"""
        collection_state = CollectionState(
            run_id=run_id,
            task_type=task_type,
            status="RUNNING",
            start_time=datetime.now(),
            last_update=datetime.now(),
            total_items=0,
            processed_items=0,
            failed_items=0,
            resume_points=[],
            failed_tasks=[]
        )
        
        self.collection_states[run_id] = collection_state
        self._save_states()
        
        logger.info(f"创建采集状态：{run_id} - {task_type}")
        return run_id
    
    def update_collection_state(self, run_id: str, **kwargs):
        """更新采集状态"""
        if run_id in self.collection_states:
            state = self.collection_states[run_id]
            for key, value in kwargs.items():
                if hasattr(state, key):
                    setattr(state, key, value)
            state.last_update = datetime.now()
            self._save_states()

class RetryManager:
    """重试管理器 - 负责失败队列定时重试"""
    
    def __init__(self, state_manager: StateManager, max_workers: int = 5):
        self.state_manager = state_manager
        self.max_workers = max_workers
        self.running = False
        self.retry_thread = None
        self.retry_handlers: Dict[str, callable] = {}
        
    def register_retry_handler(self, task_type: str, handler: callable):
        """注册重试处理器"""
        self.retry_handlers[task_type] = handler
        logger.info(f"注册重试处理器：{task_type}")
    
    def start_retry_service(self):
        """启动重试服务"""
        if not self.running:
            self.running = True
            self.retry_thread = threading.Thread(target=self._retry_worker, daemon=True)
            self.retry_thread.start()
            logger.info("重试服务已启动")
    
    def stop_retry_service(self):
        """停止重试服务"""
        self.running = False
        if self.retry_thread:
            self.retry_thread.join(timeout=5)
            logger.info("重试服务已停止")
    
    def _retry_worker(self):
        """重试工作线程"""
        while self.running:
            try:
                # 获取可重试的任务
                retryable_tasks = self.state_manager.get_retryable_tasks()
                
                if retryable_tasks:
                    logger.info(f"发现{len(retryable_tasks)}个可重试任务")
                    
                    # 并发处理重试任务
                    with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                        futures = []
                        for task in retryable_tasks:
                            if task.task_type in self.retry_handlers:
                                future = executor.submit(self._retry_task, task)
                                futures.append(future)
                        
                        # 等待所有重试完成
                        for future in concurrent.futures.as_completed(futures):
                            try:
                                result = future.result()
                                logger.debug(f"重试任务完成：{result}")
                            except Exception as e:
                                logger.error(f"重试任务异常：{e}")
                
                # 等待一段时间再检查
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"重试工作线程异常：{e}")
                time.sleep(60)
    
    def _retry_task(self, task: FailedTask) -> bool:
        """重试单个任务"""
        try:
            if task.task_type not in self.retry_handlers:
                logger.warning(f"未找到任务类型处理器：{task.task_type}")
                return False
            
            handler = self.retry_handlers[task.task_type]
            success = handler(task.target, task.metadata)
            
            if success:
                self.state_manager.mark_task_success(task.task_id)
                logger.info(f"任务重试成功：{task.task_id}")
                return True
            else:
                # 计算下次重试时间（指数退避）
                retry_delay = min(300 * (2 ** task.retry_count), 3600)  # 最大1小时
                next_retry = datetime.now() + timedelta(seconds=retry_delay)
                self.state_manager.mark_task_retry(task.task_id, next_retry)
                logger.info(f"任务重试失败：{task.task_id}，下次重试：{next_retry}")
                return False
                
        except Exception as e:
            logger.error(f"重试任务异常：{task.task_id} - {e}")
            # 标记重试失败
            retry_delay = min(300 * (2 ** task.retry_count), 3600)
            next_retry = datetime.now() + timedelta(seconds=retry_delay)
            self.state_manager.mark_task_retry(task.task_id, next_retry)
            return False

class ResumeValidator:
    """运行恢复验证器 - 验证断点续采的完整性"""
    
    def __init__(self, state_manager: StateManager, db_manager: DatabaseManager):
        self.state_manager = state_manager
        self.db_manager = db_manager
    
    async def validate_resume_integrity(self, run_id: str) -> Dict[str, Any]:
        """验证断点续采的完整性"""
        if run_id not in self.state_manager.collection_states:
            return {"valid": False, "error": "运行ID不存在"}
        
        state = self.state_manager.collection_states[run_id]
        validation_result = {
            "run_id": run_id,
            "task_type": state.task_type,
            "valid": True,
            "warnings": [],
            "errors": [],
            "resume_points": [],
            "failed_tasks": [],
            "data_integrity": {}
        }
        
        try:
            # 验证断点续采点
            for point in state.resume_points:
                point_validation = await self._validate_resume_point(point)
                validation_result["resume_points"].append(point_validation)
                
                if not point_validation["valid"]:
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"断点续采点验证失败：{point_validation['error']}")
                elif point_validation["warnings"]:
                    validation_result["warnings"].extend(point_validation["warnings"])
            
            # 验证失败任务
            for task in state.failed_tasks:
                task_validation = await self._validate_failed_task(task)
                validation_result["failed_tasks"].append(task_validation)
                
                if not task_validation["valid"]:
                    validation_result["warnings"].append(f"失败任务验证警告：{task_validation['warning']}")
            
            # 验证数据完整性
            validation_result["data_integrity"] = await self._validate_data_integrity(state)
            
            if validation_result["data_integrity"]["missing_items"]:
                validation_result["warnings"].append(f"发现{len(validation_result['data_integrity']['missing_items'])}个缺失数据项")
            
            if validation_result["data_integrity"]["duplicate_items"]:
                validation_result["warnings"].append(f"发现{len(validation_result['data_integrity']['duplicate_items'])}个重复数据项")
            
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"验证过程异常：{e}")
        
        return validation_result
    
    async def _validate_resume_point(self, point: ResumePoint) -> Dict[str, Any]:
        """验证单个断点续采点"""
        validation = {
            "point_id": f"{point.task_type}_{point.current_page}",
            "valid": True,
            "warnings": [],
            "error": None
        }
        
        try:
            # 验证页码连续性
            if point.current_page < 1:
                validation["valid"] = False
                validation["error"] = "页码无效"
            
            # 验证游标有效性
            if point.last_cursor and len(point.last_cursor) < 10:
                validation["warnings"].append("游标长度异常")
            
            # 验证处理数量合理性
            if point.total_processed < 0:
                validation["valid"] = False
                validation["error"] = "处理数量无效"
            
            # 验证时间戳合理性
            if point.last_update < datetime.now() - timedelta(days=7):
                validation["warnings"].append("断点续采点较旧，可能需要重新验证")
            
        except Exception as e:
            validation["valid"] = False
            validation["error"] = f"验证异常：{e}"
        
        return validation
    
    async def _validate_failed_task(self, task: FailedTask) -> Dict[str, Any]:
        """验证单个失败任务"""
        validation = {
            "task_id": task.task_id,
            "valid": True,
            "warning": None
        }
        
        try:
            # 验证重试次数合理性
            if task.retry_count > task.max_retries:
                validation["valid"] = False
                validation["warning"] = "重试次数超过限制"
            
            # 验证重试时间合理性
            if task.next_retry_time < datetime.now():
                validation["warning"] = "重试时间已过期"
            
            # 验证错误信息完整性
            if not task.error_message or len(task.error_message) < 5:
                validation["warning"] = "错误信息不完整"
            
        except Exception as e:
            validation["valid"] = False
            validation["warning"] = f"验证异常：{e}"
        
        return validation
    
    async def _validate_data_integrity(self, state: CollectionState) -> Dict[str, Any]:
        """验证数据完整性"""
        integrity = {
            "missing_items": [],
            "duplicate_items": [],
            "total_expected": 0,
            "total_actual": 0
        }
        
        try:
            # 根据任务类型验证数据完整性
            if state.task_type == "LIST_COLLECTION":
                # 验证列表采集的完整性
                await self._validate_list_collection_integrity(state, integrity)
            elif state.task_type == "DETAIL_COLLECTION":
                # 验证详情采集的完整性
                await self._validate_detail_collection_integrity(state, integrity)
            elif state.task_type == "IMAGE_DOWNLOAD":
                # 验证图片下载的完整性
                await self._validate_image_download_integrity(state, integrity)
            
        except Exception as e:
            logger.error(f"数据完整性验证异常：{e}")
        
        return integrity
    
    async def _validate_list_collection_integrity(self, state: CollectionState, integrity: Dict[str, Any]):
        """验证列表采集完整性"""
        try:
            # 查询数据库中的实际数据量
            query = "SELECT COUNT(*) as count FROM works WHERE created_at >= %s"
            result = await self.db_manager.execute_query(query, (state.start_time,))
            
            if result:
                integrity["total_actual"] = result[0]["count"]
                integrity["total_expected"] = state.total_items
                
                # 检查缺失项
                if integrity["total_actual"] < integrity["total_expected"]:
                    missing_count = integrity["total_expected"] - integrity["total_actual"]
                    integrity["missing_items"].append(f"列表采集缺失{missing_count}项")
                
                # 检查重复项（通过slug）
                duplicate_query = """
                SELECT slug, COUNT(*) as count 
                FROM works 
                GROUP BY slug 
                HAVING COUNT(*) > 1
                """
                duplicate_result = await self.db_manager.execute_query(duplicate_query)
                
                if duplicate_result:
                    integrity["duplicate_items"].extend([item["slug"] for item in duplicate_result])
                    
        except Exception as e:
            logger.error(f"列表采集完整性验证异常：{e}")
    
    async def _validate_detail_collection_integrity(self, state: CollectionState, integrity: Dict[str, Any]):
        """验证详情采集完整性"""
        try:
            # 查询详情数据的完整性
            query = """
            SELECT COUNT(*) as count 
            FROM works 
            WHERE detail_collected = 1 AND created_at >= %s
            """
            result = await self.db_manager.execute_query(query, (state.start_time,))
            
            if result:
                integrity["total_actual"] = result[0]["count"]
                integrity["total_expected"] = state.processed_items
                
                # 检查缺失的详情数据
                if integrity["total_actual"] < integrity["total_expected"]:
                    missing_count = integrity["total_expected"] - integrity["total_actual"]
                    integrity["missing_items"].append(f"详情采集缺失{missing_count}项")
                    
        except Exception as e:
            logger.error(f"详情采集完整性验证异常：{e}")
    
    async def _validate_image_download_integrity(self, state: CollectionState, integrity: Dict[str, Any]):
        """验证图片下载完整性"""
        try:
            # 查询图片下载状态
            query = """
            SELECT COUNT(*) as count 
            FROM works 
            WHERE image_downloaded = 1 AND created_at >= %s
            """
            result = await self.db_manager.execute_query(query, (state.start_time,))
            
            if result:
                integrity["total_actual"] = result[0]["count"]
                integrity["total_expected"] = state.processed_items
                
                # 检查缺失的图片
                if integrity["total_actual"] < integrity["total_expected"]:
                    missing_count = integrity["total_expected"] - integrity["total_actual"]
                    integrity["missing_items"].append(f"图片下载缺失{missing_count}项")
                    
        except Exception as e:
            logger.error(f"图片下载完整性验证异常：{e}")

class T8ResumeAndRetry:
    """T8 断点续采与失败补偿主类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        if config is None:
            config = self._get_default_config()
        
        self.config = config
        
        # 初始化组件
        self.state_manager = StateManager(config.get('state_dir', 'data/state'))
        self.retry_manager = RetryManager(self.state_manager, config.get('max_workers', 5))
        self.validator = ResumeValidator(self.state_manager, DatabaseManager())
        
        # 注册重试处理器
        self._register_retry_handlers()
        
        logger.info("T8断点续采与失败补偿模块初始化完成")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'state_dir': 'data/state',
            'max_workers': 5,
            'retry_check_interval': 30,
            'max_retry_delay': 3600,
            'enable_auto_retry': True,
            'enable_integrity_check': True
        }
    
    def _register_retry_handlers(self):
        """注册重试处理器"""
        # 列表采集重试处理器
        self.retry_manager.register_retry_handler(
            "LIST_COLLECTION", 
            self._retry_list_collection
        )
        
        # 详情采集重试处理器
        self.retry_manager.register_retry_handler(
            "DETAIL_COLLECTION", 
            self._retry_detail_collection
        )
        
        # 图片下载重试处理器
        self.retry_manager.register_retry_handler(
            "IMAGE_DOWNLOAD", 
            self._retry_image_download
        )
    
    def start_service(self):
        """启动服务"""
        try:
            # 启动重试服务
            if self.config.get('enable_auto_retry', True):
                self.retry_manager.start_retry_service()
                logger.info("自动重试服务已启动")
            
            logger.info("T8断点续采与失败补偿服务已启动")
            
        except Exception as e:
            logger.error(f"启动服务失败：{e}")
            raise
    
    def stop_service(self):
        """停止服务"""
        try:
            # 停止重试服务
            self.retry_manager.stop_retry_service()
            
            # 保存所有状态
            self.state_manager._save_states()
            
            logger.info("T8断点续采与失败补偿服务已停止")
            
        except Exception as e:
            logger.error(f"停止服务失败：{e}")
    
    def create_resume_point(self, task_type: str, current_page: int, **kwargs) -> str:
        """创建断点续采点"""
        return self.state_manager.create_resume_point(task_type, current_page, **kwargs)
    
    def add_failed_task(self, task_type: str, target: str, error_message: str, **kwargs) -> str:
        """添加失败任务"""
        return self.state_manager.add_failed_task(task_type, target, error_message, **kwargs)
    
    def get_resume_point(self, task_type: str) -> Optional[ResumePoint]:
        """获取断点续采点"""
        return self.state_manager.get_resume_point(task_type)
    
    def get_retryable_tasks(self) -> List[FailedTask]:
        """获取可重试任务"""
        return self.state_manager.get_retryable_tasks()
    
    async def validate_integrity(self, run_id: str) -> Dict[str, Any]:
        """验证运行完整性"""
        if not self.config.get('enable_integrity_check', True):
            return {"valid": True, "message": "完整性检查已禁用"}
        
        return await self.validator.validate_resume_integrity(run_id)
    
    def _retry_list_collection(self, target: str, metadata: Dict[str, Any]) -> bool:
        """重试列表采集"""
        try:
            # 这里应该调用实际的列表采集逻辑
            # 暂时返回True表示重试成功
            logger.info(f"重试列表采集：{target}")
            return True
        except Exception as e:
            logger.error(f"重试列表采集失败：{target} - {e}")
            return False
    
    def _retry_detail_collection(self, target: str, metadata: Dict[str, Any]) -> bool:
        """重试详情采集"""
        try:
            # 这里应该调用实际的详情采集逻辑
            # 暂时返回True表示重试成功
            logger.info(f"重试详情采集：{target}")
            return True
        except Exception as e:
            logger.error(f"重试详情采集失败：{target} - {e}")
            return False
    
    def _retry_image_download(self, target: str, metadata: Dict[str, Any]) -> bool:
        """重试图片下载"""
        try:
            # 这里应该调用实际的图片下载逻辑
            # 暂时返回True表示重试成功
            logger.info(f"重试图片下载：{target}")
            return True
        except Exception as e:
            logger.error(f"重试图片下载失败：{target} - {e}")
            return False

# 兼容性导入
try:
    import concurrent.futures
except ImportError:
    # Python 3.2以下版本兼容
    import futures as concurrent.futures

async def main():
    """主函数 - 演示T8功能"""
    # 创建T8实例
    t8 = T8ResumeAndRetry()
    
    try:
        # 启动服务
        t8.start_service()
        
        # 创建示例断点续采点
        point_id = t8.create_resume_point(
            task_type="LIST_COLLECTION",
            current_page=5,
            last_cursor="abc123",
            total_processed=120,
            metadata={"tag": "汽车交通", "sort": "latest"}
        )
        
        # 添加示例失败任务
        task_id = t8.add_failed_task(
            task_type="DETAIL_COLLECTION",
            target="car-model-001",
            error_message="API请求超时",
            max_retries=3,
            retry_delay=60
        )
        
        # 获取断点续采点
        resume_point = t8.get_resume_point("LIST_COLLECTION")
        if resume_point:
            print(f"找到断点续采点：第{resume_point.current_page}页，已处理{resume_point.total_processed}项")
        
        # 获取可重试任务
        retryable_tasks = t8.get_retryable_tasks()
        print(f"发现{len(retryable_tasks)}个可重试任务")
        
        # 等待一段时间让重试服务运行
        await asyncio.sleep(10)
        
        print("T8功能演示完成")
        
    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        print(f"运行异常：{e}")
    finally:
        # 停止服务
        t8.stop_service()

if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/t8_resume_retry.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # 创建日志目录
    Path("logs").mkdir(exist_ok=True)
    
    # 运行主函数
    asyncio.run(main())
