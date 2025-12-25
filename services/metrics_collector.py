"""Prometheus指标收集器"""
import asyncio
import logging
import time
from typing import Dict, List, Tuple, Optional
from prometheus_client import Gauge
from sqlalchemy.orm import Session

from models.instance import InstanceList, InstanceUsers
from services.das_client import DASClient
from config.settings import settings


logger = logging.getLogger(__name__)

# 全局指标实例，避免重复注册
_db_user_session_count: Optional[Gauge] = None
_db_max_user_connections: Optional[Gauge] = None
_metrics_collector_instance: Optional['MetricsCollector'] = None


def get_or_create_gauge() -> Tuple[Gauge, Gauge]:
    """获取或创建Gauge指标实例"""
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


def get_metrics_collector(db: Session) -> 'MetricsCollector':
    """获取单例MetricsCollector实例"""
    global _metrics_collector_instance
    if _metrics_collector_instance is None:
        _metrics_collector_instance = MetricsCollector(db)
    else:
        # 更新数据库会话
        _metrics_collector_instance.db = db
        _metrics_collector_instance.das_client = DASClient(db_session=db)
    return _metrics_collector_instance


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, db: Session):
        self.db = db
        self.das_client = DASClient(db_session=db)
        self.db_user_session_count, self.db_max_user_connections = get_or_create_gauge()
        
        # 缓存
        self.session_count_cache: Dict[Tuple, float] = {}
        self.session_count_cache_time: float = 0
        self.max_connections_cache: Dict[Tuple, int] = {}
        self.max_connections_cache_time: float = 0
        
        # 并发配置
        self.max_concurrent_instances = getattr(settings, 'MAX_CONCURRENT_INSTANCES', 5)
        
    def _is_cache_valid(self, cache_time: float, ttl: int) -> bool:
        """检查缓存是否有效"""
        return time.time() - cache_time < ttl
    
    async def _collect_instance_session(self, instance: InstanceList) -> List[Dict]:
        """收集单个实例的会话数据"""
        try:
            return await self.das_client.get_session_data_for_instance(instance)
        except Exception as e:
            logger.error(f"收集实例 {instance.ins_id} 会话数据失败: {e}")
            return []
    
    async def collect_session_count_metrics(self):
        """收集会话数指标（并行采集）"""
        current_time = time.time()
        
        # 检查缓存是否有效
        if self._is_cache_valid(self.session_count_cache_time, settings.SESSION_COUNT_CACHE_TTL):
            logger.debug("使用会话数指标缓存")
            for labels, value in self.session_count_cache.items():
                self.db_user_session_count.labels(**dict(labels)).set(value)
            return
        
        logger.info("开始收集会话数指标")
        
        # 清空当前指标
        self.db_user_session_count.clear()
        
        # 查询所有启用的实例
        instances = self.db.query(InstanceList).filter(InstanceList.ins_status == 1).all()
        
        if not instances:
            logger.info("没有启用的实例")
            return
        
        # 使用信号量限制并发数
        semaphore = asyncio.Semaphore(self.max_concurrent_instances)
        
        async def collect_with_semaphore(instance: InstanceList):
            async with semaphore:
                return await self._collect_instance_session(instance)
        
        # 并行收集所有实例
        tasks = [collect_with_semaphore(instance) for instance in instances]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        new_cache: Dict[Tuple, float] = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"收集实例会话异常: {result}")
                continue
            
            for session_data_item in result:
                labels = session_data_item['labels']
                value = session_data_item['session_count']
                self.db_user_session_count.labels(**labels).set(value)
                new_cache[tuple(sorted(labels.items()))] = value
        
        self.session_count_cache = new_cache
        self.session_count_cache_time = current_time
        
        logger.info(f"会话数指标收集完成，共 {len(new_cache)} 条记录")
    
    async def collect_max_connections_metrics(self):
        """收集最大连接数指标"""
        current_time = time.time()
        
        if self._is_cache_valid(self.max_connections_cache_time, settings.MAX_USER_CONNECTIONS_CACHE_TTL):
            logger.debug("使用最大连接数指标缓存")
            for labels, value in self.max_connections_cache.items():
                self.db_max_user_connections.labels(**dict(labels)).set(value)
            return
        
        logger.info("开始收集最大连接数指标")
        
        self.db_max_user_connections.clear()
        users = self.db.query(InstanceUsers).all()
        
        new_cache: Dict[Tuple, int] = {}
        for user in users:
            labels = {'ins_id': user.ins_id, 'username': user.username}
            value = user.max_user_connections
            self.db_max_user_connections.labels(**labels).set(value)
            new_cache[tuple(sorted(labels.items()))] = value
        
        self.max_connections_cache = new_cache
        self.max_connections_cache_time = current_time
        
        logger.info(f"最大连接数指标收集完成，共 {len(new_cache)} 条记录")
    
    async def collect_all_metrics(self):
        """收集所有指标"""
        logger.info("开始收集所有指标")
        start_time = time.time()
        
        try:
            # 并行收集两类指标
            await asyncio.gather(
                self.collect_session_count_metrics(),
                self.collect_max_connections_metrics()
            )
            
            elapsed = time.time() - start_time
            logger.info(f"所有指标收集完成，耗时 {elapsed:.2f} 秒")
        except Exception as e:
            logger.error(f"收集指标时发生错误: {e}")
            raise
    
    async def manual_refresh(self):
        """手动触发指标刷新"""
        logger.info("手动触发指标刷新")
        self.session_count_cache_time = 0
        self.max_connections_cache_time = 0
        await self.collect_all_metrics()