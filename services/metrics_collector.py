import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple
from prometheus_client import Gauge, REGISTRY
from sqlalchemy.orm import Session
from sqlalchemy import text

from models.instance import InstanceList, InstanceUsers
from services.das_client import DASClient
from config.settings import settings


logger = logging.getLogger(__name__)

# 全局指标实例，避免重复注册
_db_user_session_count = None
_db_max_user_connections = None

def get_or_create_gauge():
    """
    获取或创建Gauge指标实例，避免重复注册
    """
    global _db_user_session_count, _db_max_user_connections
    
    if _db_user_session_count is None:
        _db_user_session_count = Gauge(
            'db_user_session_count',
            '数据库用户会话数',
            ['ins_id', 'ins_name', 'ins_type', 'aliyun_uid', 'db_user', 'node_id', 'node_type']
        )
    
    if _db_max_user_connections is None:
        _db_max_user_connections = Gauge(
            'db_max_user_connections',
            '用户最大连接数',
            ['ins_id', 'username']
        )
    
    return _db_user_session_count, _db_max_user_connections


class MetricsCollector:
    """
    指标收集器
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.das_client = DASClient(db_session=db)  # 传递数据库会话给DAS客户端
        
        # 获取或创建指标实例
        self.db_user_session_count, self.db_max_user_connections = get_or_create_gauge()
        
        # 缓存相关
        self.session_count_cache = {}
        self.session_count_cache_time = 0
        self.max_connections_cache = {}
        self.max_connections_cache_time = 0
        
    def _is_cache_valid(self, cache_time: int, ttl: int) -> bool:
        """
        检查缓存是否有效
        """
        return time.time() - cache_time < ttl
    
    async def collect_session_count_metrics(self):
        """
        收集会话数指标
        """
        current_time = time.time()
        
        # 检查缓存是否有效
        if self._is_cache_valid(self.session_count_cache_time, settings.SESSION_COUNT_CACHE_TTL):
            logger.info("使用会话数指标缓存")
            # 从缓存恢复指标
            for labels, value in self.session_count_cache.items():
                self.db_user_session_count.labels(**labels).set(value)
            return
        
        logger.info("开始收集会话数指标")
        
        # 清空当前指标
        self.db_user_session_count.clear()
        
        # 查询所有启用的实例
        instances = self.db.query(InstanceList).filter(InstanceList.ins_status == 1).all()
        
        # 存储新的指标数据
        new_cache = {}
        
        for instance in instances:
            logger.info(f"处理实例: {instance.ins_id}, 类型: {instance.ins_type}, 阿里云账号: {instance.aliyun_uid}")
            
            # 使用DAS客户端获取会话数据
            session_data_list = await self.das_client.get_session_data_for_instance(instance)
            
            for session_data_item in session_data_list:
                labels = session_data_item['labels']
                value = session_data_item['session_count']
                
                self.db_user_session_count.labels(**labels).set(value)
                new_cache[tuple(sorted(labels.items()))] = value
        
        # 更新缓存
        self.session_count_cache = new_cache
        self.session_count_cache_time = current_time
        
        logger.info("会话数指标收集完成")
    
    async def collect_max_connections_metrics(self):
        """
        收集最大连接数指标
        """
        current_time = time.time()
        
        # 检查缓存是否有效
        if self._is_cache_valid(self.max_connections_cache_time, settings.MAX_USER_CONNECTIONS_CACHE_TTL):
            logger.info("使用最大连接数指标缓存")
            # 从缓存恢复指标
            for labels, value in self.max_connections_cache.items():
                self.db_max_user_connections.labels(**labels).set(value)
            return
        
        logger.info("开始收集最大连接数指标")
        
        # 清空当前指标
        self.db_max_user_connections.clear()
        
        # 查询所有用户最大连接数
        users = self.db.query(InstanceUsers).all()
        
        # 存储新的指标数据
        new_cache = {}
        
        for user in users:
            labels = {
                'ins_id': user.ins_id,
                'username': user.username
            }
            value = user.max_user_connections
            
            self.db_max_user_connections.labels(**labels).set(value)
            new_cache[tuple(sorted(labels.items()))] = value
        
        # 更新缓存
        self.max_connections_cache = new_cache
        self.max_connections_cache_time = current_time
        
        logger.info("最大连接数指标收集完成")
    
    async def collect_all_metrics(self):
        """
        收集所有指标
        """
        logger.info("开始收集所有指标")
        
        try:
            await self.collect_session_count_metrics()
            await self.collect_max_connections_metrics()
            logger.info("所有指标收集完成")
        except Exception as e:
            logger.error(f"收集指标时发生错误: {str(e)}")
            raise
    
    async def manual_refresh(self):
        """
        手动触发指标刷新
        """
        logger.info("手动触发指标刷新")
        self.session_count_cache_time = 0  # 清除会话数缓存
        self.max_connections_cache_time = 0  # 清除最大连接数缓存
        await self.collect_all_metrics()