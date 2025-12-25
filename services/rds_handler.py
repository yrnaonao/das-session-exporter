"""RDS处理器
处理RDS实例的会话信息获取逻辑
"""
import logging
from typing import Dict, List, Any

from alibabacloud_das20200116 import models as das20200116_models

from models.instance import InstanceList
from services.base_handler import BaseHandler
from services.aliyun_client_manager import AliyunClientManager


logger = logging.getLogger(__name__)


class RDSHandler(BaseHandler):
    """
    RDS处理器
    继承BaseHandler，只需实现RDS特有逻辑
    """
    
    def __init__(self, db_session, client_manager: AliyunClientManager, rate_limit: float = 5.0):
        super().__init__(db_session, client_manager, rate_limit)
    
    async def get_session_data_for_instance(self, instance: InstanceList) -> List[Dict[str, Any]]:
        """
        获取RDS实例的会话数据
        """
        logger.debug(f"处理RDS实例: {instance.ins_id}")
        
        node_type_label = "read" if instance.ins_is_readonly == 1 else "write"
        
        # 获取对应账号的客户端
        client = self.client_manager.get_client_for_account(instance.aliyun_uid)
        if not client:
            logger.error(f"无法获取账号 {instance.aliyun_uid} 的DAS客户端")
            return []
        
        # 第一次调用：获取会话信息
        request = das20200116_models.GetMySQLAllSessionAsyncRequest(
            instance_id=instance.ins_id
        )
        
        session_data = await self._execute_api_call(client, request)
        if not session_data:
            logger.warning(f"无法获取RDS实例 {instance.ins_id} 的会话数据")
            return []
        
        result_id = session_data.data.result_id
        if not result_id:
            logger.error(f"RDS实例 {instance.ins_id} 未返回结果ID")
            return []
        
        # 轮询获取结果
        result_data = await self._poll_async_result(client, instance.ins_id, result_id)
        if not result_data:
            logger.warning(f"无法获取RDS实例 {instance.ins_id} 的轮询结果")
            return []
        
        # 检查结果状态
        if hasattr(result_data.data, 'state') and result_data.data.state.lower() == 'fail':
            logger.error(f"RDS实例 {instance.ins_id} 获取会话数据失败")
            return []
        
        session_data_result = result_data.data.session_data
        if not session_data_result:
            logger.warning(f"RDS实例 {instance.ins_id} 未返回会话数据")
            return []
        
        # 解析用户会话统计信息
        user_stats = self._parse_user_session_stats(session_data_result)
        
        session_data_list = []
        for stat in user_stats:
            session_data_list.append(
                self._build_session_data_item(instance, stat, '', node_type_label)
            )
        
        return session_data_list