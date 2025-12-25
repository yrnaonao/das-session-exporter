"""PolarDB处理器
处理PolarDB实例的会话信息获取逻辑
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any

from alibabacloud_das20200116 import models as das20200116_models

from models.instance import InstanceList, InstanceNodeId
from services.base_handler import BaseHandler
from services.aliyun_client_manager import AliyunClientManager


logger = logging.getLogger(__name__)


class PolarDBHandler(BaseHandler):
    """
    PolarDB处理器
    继承BaseHandler，只需实现PolarDB特有逻辑
    """
    
    def __init__(self, db_session, client_manager: AliyunClientManager, rate_limit: float = 5.0):
        super().__init__(db_session, client_manager, rate_limit)
    
    async def _get_node_session_data(
        self, 
        client, 
        instance: InstanceList, 
        node_id: str, 
        node_type_label: str
    ) -> List[Dict[str, Any]]:
        """
        获取单个节点的会话数据
        """
        session_data_list = []
        
        # 第一次调用：获取会话信息
        request = das20200116_models.GetMySQLAllSessionAsyncRequest(
            instance_id=instance.ins_id,
            node_id=node_id
        )
        
        session_data = await self._execute_api_call(client, request)
        if not session_data:
            logger.warning(f"无法获取PolarDB节点 {node_id} 的会话数据")
            return session_data_list
        
        result_id = session_data.data.result_id
        if not result_id:
            logger.error(f"PolarDB节点 {node_id} 未返回结果ID")
            return session_data_list
        
        # 轮询获取结果
        result_data = await self._poll_async_result(
            client, instance.ins_id, result_id, node_id=node_id
        )
        if not result_data:
            logger.warning(f"无法获取PolarDB节点 {node_id} 的轮询结果")
            return session_data_list
        
        # 检查结果状态
        if hasattr(result_data.data, 'state') and result_data.data.state.lower() == 'fail':
            logger.error(f"PolarDB节点 {node_id} 获取会话数据失败")
            return session_data_list
        
        session_data_result = result_data.data.session_data
        if not session_data_result:
            logger.warning(f"PolarDB节点 {node_id} 未返回会话数据")
            return session_data_list
        
        # 解析用户会话统计信息
        user_stats = self._parse_user_session_stats(session_data_result)
        
        for stat in user_stats:
            session_data_list.append(
                self._build_session_data_item(instance, stat, node_id, node_type_label)
            )
        
        return session_data_list
    
    async def get_session_data_for_instance(self, instance: InstanceList) -> List[Dict[str, Any]]:
        """
        获取PolarDB实例的会话数据（并行获取所有节点）
        """
        logger.debug(f"处理PolarDB实例: {instance.ins_id}")
        
        # 获取对应账号的客户端
        client = self.client_manager.get_client_for_account(instance.aliyun_uid)
        if not client:
            logger.error(f"无法获取账号 {instance.aliyun_uid} 的DAS客户端")
            return []
        
        # 获取所有节点
        nodes = self.db_session.query(InstanceNodeId).filter(
            InstanceNodeId.ins_id == instance.ins_id
        ).all()
        
        if not nodes:
            logger.warning(f"PolarDB实例 {instance.ins_id} 没有配置节点")
            return []
        
        # 并行获取所有节点的会话数据
        tasks = []
        for node in nodes:
            node_type_label = "read" if node.node_type == 1 else "write"
            tasks.append(
                self._get_node_session_data(client, instance, node.node_id, node_type_label)
            )
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 合并结果
        session_data_list = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"获取节点会话数据异常: {result}")
                continue
            session_data_list.extend(result)
        
        return session_data_list