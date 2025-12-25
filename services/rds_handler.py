"""
RDS处理器
处理RDS实例的会话信息获取逻辑
"""
import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor

from alibabacloud_das20200116 import models as das20200116_models
from alibabacloud_tea_util import models as util_models

from models.instance import InstanceList
from services.aliyun_client_manager import AliyunClientManager


logger = logging.getLogger(__name__)


class RDSHandler:
    """
    RDS处理器
    """
    
    def __init__(self, db_session, client_manager: AliyunClientManager):
        self.db_session = db_session
        self.client_manager = client_manager
        self.rate_limit = 1  # 每秒API调用次数限制
        self._last_call_time = 0
        
    async def _rate_limit_delay(self):
        """
        实现API调用限流
        """
        current_time = time.time()
        
        # 确保两次调用之间有足够间隔
        min_interval = 1.0 / self.rate_limit
        time_since_last_call = current_time - self._last_call_time
        if time_since_last_call < min_interval:
            await asyncio.sleep(min_interval - time_since_last_call)
        self._last_call_time = time.time()
    
    async def get_session_data_for_instance(self, instance: InstanceList) -> List[Dict[str, Any]]:
        """
        获取RDS实例的会话数据
        """
        session_data_list = []
        
        logger.info(f"处理RDS实例: {instance.ins_id}")
        
        node_type_label = "read" if instance.ins_is_readonly == 1 else "write"
        
        # 获取对应账号的客户端
        client = self.client_manager.get_client_for_account(instance.aliyun_uid)
        if not client:
            logger.error(f"无法获取账号 {instance.aliyun_uid} 的DAS客户端")
            return session_data_list
        
        # 第一次调用：获取会话信息，传入ins_id参数
        session_data = await self._get_mysql_session_async(client, instance.ins_id)
        if not session_data:
            logger.warning(f"无法获取RDS实例 {instance.ins_id} 的会话数据")
            return session_data_list
        
        # 从返回中获取result_id
        result_id = session_data.get('Data', {}).get('ResultId')
        if not result_id:
            logger.error(f"RDS实例 {instance.ins_id} 未返回结果ID")
            return session_data_list
        
        # 第二次调用：轮询获取结果，传入ins_id/result_id
        result_data = await self._get_async_result(client, result_id)
        if not result_data:
            logger.warning(f"无法获取RDS实例 {instance.ins_id} 的轮询结果")
            return session_data_list
        
        # 检查结果状态
        if result_data.get('Data', {}).get('Fail', False):
            logger.error(f"RDS实例 {instance.ins_id} 获取会话数据失败")
            return session_data_list
        
        session_data_result = result_data.get('Data', {}).get('SessionData')
        if not session_data_result:
            logger.warning(f"RDS实例 {instance.ins_id} 未返回会话数据")
            return session_data_list
        
        # 解析用户会话统计信息
        user_stats = self._parse_user_session_stats(session_data_result)
        
        for stat in user_stats:
            session_data_list.append({
                'labels': {
                    'ins_id': instance.ins_id,
                    'ins_name': instance.ins_name,
                    'ins_type': instance.ins_type.lower(),
                    'aliyun_uid': instance.aliyun_uid,
                    'db_user': stat['db_user'],
                    'node_id': '',
                    'node_type': node_type_label
                },
                'session_count': stat['session_count'],
                'session_data': session_data_result
            })
        
        return session_data_list
    
    async def _get_mysql_session_async(self, client, ins_id: str) -> Optional[Dict[str, Any]]:
        """
        异步获取MySQL会话信息 - 第一次调用
        传入ins_id参数
        """
        await self._rate_limit_delay()
        
        try:
            request = das20200116_models.GetMySQLAllSessionAsyncRequest(
                instance_id=ins_id  # 对于RDS，使用实例ID
            )
            
            runtime = util_models.RuntimeOptions()
            
            # 在异步环境中调用同步方法
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                response = await loop.run_in_executor(
                    executor,
                    lambda: client.get_my_sqlall_session_async_with_options(request, runtime)
                )
            
            response_data = response.body.to_map()
            logger.info(f"获取RDS实例 {ins_id} 会话信息成功: {response_data.get('Code', 'Unknown')}")
            
            return response_data
            
        except Exception as e:
            logger.error(f"获取RDS实例 {ins_id} 会话信息失败: {str(e)}")
            return None
    
    async def _get_async_result(self, client, result_id: str) -> Optional[Dict[str, Any]]:
        """
        获取异步结果 - 第二次调用
        传入result_id进行查询
        """
        await self._rate_limit_delay()
        
        max_attempts = 30  # 最多轮询30次
        attempt = 0
        
        while attempt < max_attempts:
            try:
                request = das20200116_models.GetAsyncResultRequest(
                    resultId=result_id  # 使用正确的参数名
                )
                runtime = util_models.RuntimeOptions()
                
                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor() as executor:
                    response = await loop.run_in_executor(
                        executor,
                        lambda: client.get_async_result_with_options(request, runtime)
                    )
                
                response_data = response.body.to_map()
                
                # 检查是否完成
                if response_data.get('Data', {}).get('IsFinish', False):
                    logger.info(f"轮询结果 {result_id} 完成")
                    return response_data
                
                # 如果失败，直接返回
                if response_data.get('Data', {}).get('Fail', False):
                    logger.error(f"轮询结果 {result_id} 失败")
                    return response_data
                
                attempt += 1
                await asyncio.sleep(2)  # 等待2秒后继续轮询
                
            except Exception as e:
                logger.error(f"轮询结果 {result_id} 失败: {str(e)}")
                return None
        
        logger.warning(f"轮询结果 {result_id} 超时")
        return None
    
    def _parse_user_session_stats(self, session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        解析用户会话统计信息
        """
        user_stats = session_data.get('UserStats', [])
        parsed_stats = []
        
        for user_stat in user_stats:
            user_list = user_stat.get('UserList', [])
            total_count = user_stat.get('TotalCount', 0)
            key = user_stat.get('Key', '')
            
            # 为每个用户创建统计记录
            for user in user_list:
                parsed_stats.append({
                    'db_user': user,
                    'session_count': total_count
                })
        
        return parsed_stats