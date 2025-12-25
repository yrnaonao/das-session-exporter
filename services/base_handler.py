"""
基础处理器
提取RDS和PolarDB处理器的公共逻辑
"""
import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor

from alibabacloud_das20200116 import models as das20200116_models
from alibabacloud_tea_util import models as util_models

from models.instance import InstanceList
from services.aliyun_client_manager import AliyunClientManager


logger = logging.getLogger(__name__)

# 全局线程池，避免重复创建
_executor: Optional[ThreadPoolExecutor] = None


def get_executor(max_workers: int = 10) -> ThreadPoolExecutor:
    """获取全局线程池"""
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=max_workers)
    return _executor


class BaseHandler(ABC):
    """
    基础处理器抽象类
    提供公共的限流、轮询和解析逻辑
    """
    
    def __init__(self, db_session, client_manager: AliyunClientManager, rate_limit: float = 5.0):
        self.db_session = db_session
        self.client_manager = client_manager
        self.rate_limit = rate_limit  # 每秒API调用次数限制
        self._last_call_time = 0
        self._rate_lock = asyncio.Lock()
        
    async def _rate_limit_delay(self):
        """
        实现API调用限流（线程安全）
        """
        async with self._rate_lock:
            current_time = time.time()
            min_interval = 1.0 / self.rate_limit
            time_since_last_call = current_time - self._last_call_time
            if time_since_last_call < min_interval:
                await asyncio.sleep(min_interval - time_since_last_call)
            self._last_call_time = time.time()
    
    async def _execute_api_call(self, client, request) -> Optional[Any]:
        """
        执行API调用（使用全局线程池）
        """
        await self._rate_limit_delay()
        
        try:
            runtime = util_models.RuntimeOptions()
            loop = asyncio.get_running_loop()
            executor = get_executor()
            
            response = await loop.run_in_executor(
                executor,
                lambda: client.get_my_sqlall_session_async_with_options(request, runtime)
            )
            return response.body
        except Exception as e:
            logger.error(f"API调用失败: {str(e)}")
            return None
    
    async def _poll_async_result(
        self, 
        client, 
        ins_id: str, 
        result_id: str, 
        node_id: Optional[str] = None,
        max_attempts: int = 30,
        poll_interval: float = 1.0
    ) -> Optional[Any]:
        """
        轮询获取异步结果
        """
        attempt = 0
        
        # 构建请求
        if node_id:
            request = das20200116_models.GetMySQLAllSessionAsyncRequest(
                instance_id=ins_id,
                node_id=node_id,
                result_id=result_id
            )
        else:
            request = das20200116_models.GetMySQLAllSessionAsyncRequest(
                instance_id=ins_id,
                result_id=result_id
            )
        
        while attempt < max_attempts:
            try:
                response_data = await self._execute_api_call(client, request)
                if not response_data:
                    return None
                
                # 检查是否完成
                if response_data.data.is_finish:
                    logger.debug(f"轮询结果 {result_id} 完成")
                    return response_data
                
                # 如果失败，直接返回
                if hasattr(response_data.data, 'state') and response_data.data.state.lower() == 'fail':
                    logger.error(f"轮询结果 {result_id} 失败")
                    return response_data
                
                attempt += 1
                await asyncio.sleep(poll_interval)
                
            except Exception as e:
                logger.error(f"轮询结果 {result_id} 异常: {str(e)}")
                return None
        
        logger.warning(f"轮询结果 {result_id} 超时 (尝试 {max_attempts} 次)")
        return None
    
    def _parse_user_session_stats(self, session_data: Any) -> List[Dict[str, Any]]:
        """
        解析用户会话统计信息
        """
        user_stats = session_data.user_stats
        parsed_stats = []
        
        for user_stat in user_stats:
            user_list = user_stat.user_list
            total_count = user_stat.total_count
            
            for user in user_list:
                parsed_stats.append({
                    'db_user': user,
                    'session_count': total_count
                })
        
        return parsed_stats
    
    def _build_session_data_item(
        self,
        instance: InstanceList,
        stat: Dict[str, Any],
        node_id: str = '',
        node_type_label: str = 'write',
        session_data: Any = None
    ) -> Dict[str, Any]:
        """
        构建会话数据项
        """
        return {
            'labels': {
                'ins_id': instance.ins_id,
                'ins_name': instance.ins_name,
                'ins_type': instance.ins_type.lower(),
                'aliyun_uid': instance.aliyun_uid,
                'db_user': stat['db_user'],
                'node_id': node_id,
                'node_type': node_type_label
            },
            'session_count': stat['session_count']
        }
    
    @abstractmethod
    async def get_session_data_for_instance(self, instance: InstanceList) -> List[Dict[str, Any]]:
        """
        获取实例的会话数据（子类实现）
        """
        pass
