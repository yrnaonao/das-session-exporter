"""
阿里云客户端管理器
管理阿里云客户端的认证和缓存
"""
import logging
from typing import Dict, Optional
from alibabacloud_das20200116.client import Client as DAS20200116Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models

from config.settings import settings
from utils.encryption import decrypt_string
from models.instance import AliyunAccount


logger = logging.getLogger(__name__)


class AliyunClientManager:
    """
    阿里云客户端管理器
    """
    
    def __init__(self, db_session):
        self.db_session = db_session
        self.client_cache: Dict[str, DAS20200116Client] = {}
        
    def get_client_for_account(self, aliyun_uid: str) -> Optional[DAS20200116Client]:
        """
        获取指定阿里云账号的客户端实例
        """
        # 检查缓存中是否已有对应账号的客户端
        if aliyun_uid in self.client_cache:
            return self.client_cache[aliyun_uid]
        
        # 从数据库获取账号信息
        account = self.db_session.query(AliyunAccount).filter(
            AliyunAccount.aliyun_uid == aliyun_uid,
            AliyunAccount.status == 1
        ).first()
        
        if not account:
            logger.error(f"未找到阿里云账号信息: {aliyun_uid}")
            return None
        
        try:
            # 解密Access Key Secret
            access_key_secret = decrypt_string(account.encrypted_access_key_secret)
            
            # 创建使用指定账号认证的配置
            config = open_api_models.Config(
                access_key_id=account.access_key_id,
                access_key_secret=access_key_secret
            )
            # 使用配置化的endpoint
            config.endpoint = settings.DAS_API_ENDPOINT.format(region_id=account.region_id)
            
            client = DAS20200116Client(config)
            
            # 缓存客户端实例
            self.client_cache[aliyun_uid] = client
            
            logger.info(f"成功创建阿里云账号 {aliyun_uid} 的DAS客户端")
            return client
            
        except Exception as e:
            logger.error(f"创建阿里云账号 {aliyun_uid} 的DAS客户端失败: {str(e)}")
            return None