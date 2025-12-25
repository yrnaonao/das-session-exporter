"""DAS客户端统一入口"""
import logging
from typing import Dict, List, Any

from services.aliyun_client_manager import AliyunClientManager
from services.polardb_handler import PolarDBHandler
from services.rds_handler import RDSHandler
from config.settings import settings
from models.instance import InstanceList


logger = logging.getLogger(__name__)


class DASClient:
    """
    阿里云DAS API客户端 - 统一入口
    """
    
    def __init__(self, db_session):
        self.db_session = db_session
        self.client_manager = AliyunClientManager(db_session)
        # 使用配置的限流参数
        rate_limit = getattr(settings, 'DAS_API_RATE_LIMIT', 5.0)
        self.polardb_handler = PolarDBHandler(db_session, self.client_manager, rate_limit)
        self.rds_handler = RDSHandler(db_session, self.client_manager, rate_limit)
        
    async def get_session_data_for_instance(self, instance: InstanceList) -> List[Dict[str, Any]]:
        """
        根据实例类型获取会话数据
        """
        if instance.ins_type.lower() == 'polardb':
            return await self.polardb_handler.get_session_data_for_instance(instance)
        else:  # RDS
            return await self.rds_handler.get_session_data_for_instance(instance)
