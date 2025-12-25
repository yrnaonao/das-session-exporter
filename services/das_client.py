import asyncio
import time
import logging
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor
import requests

# 尝试导入阿里云SDK，如果失败则使用模拟实现
try:
    from alibabacloud_das20200116.client import Client as DAS20200116Client
    from alibabacloud_credentials.client import Client as CredentialClient
    from alibabacloud_tea_openapi import models as open_api_models
    from alibabacloud_das20200116 import models as das20200116_models
    from alibabacloud_tea_util import models as util_models
    from alibabacloud_tea_util.client import Client as UtilClient
    ALIBABA_SDK_AVAILABLE = True
except ImportError:
    ALIBABA_SDK_AVAILABLE = False
    logging.warning("阿里云SDK未安装，将使用模拟模式")

from config.settings import settings
from utils.encryption import decrypt_string


logger = logging.getLogger(__name__)


class DASClient:
    """
    阿里云DAS API客户端
    """
    
    def __init__(self, db_session=None):
        # 创建客户端缓存，按阿里云账号ID缓存客户端实例
        self.client_cache = {}
        self.db_session = db_session
        self.rate_limit = settings.DAS_API_RATE_LIMIT
        self._last_call_time = 0
        self._call_count = 0
        self._call_reset_time = time.time()
        
    def _create_client(self, aliyun_uid: str = None) -> 'DAS20200116Client':
        """
        创建DAS客户端，支持多账号
        """
        if not ALIBABA_SDK_AVAILABLE:
            return None
            
        try:
            # 如果指定了阿里云账号ID，从数据库获取该账号的认证信息
            if aliyun_uid and self.db_session:
                from models.instance import AliyunAccount
                account = self.db_session.query(AliyunAccount).filter(
                    AliyunAccount.aliyun_uid == aliyun_uid,
                    AliyunAccount.status == 1
                ).first()
                
                if account:
                    # 解密Access Key Secret
                    access_key_secret = decrypt_string(account.encrypted_access_key_secret)
                    
                    # 创建使用指定账号认证的配置
                    config = open_api_models.Config(
                        access_key_id=account.access_key_id,
                        access_key_secret=access_key_secret
                    )
                    # 使用配置化的endpoint
                    config.endpoint = settings.DAS_API_ENDPOINT.format(region_id=account.region_id)
                else:
                    # 如果数据库中没有找到对应账号，使用默认认证
                    credential = CredentialClient()
                    config = open_api_models.Config(
                        credential=credential
                    )
                    # 使用配置化的endpoint
                    config.endpoint = settings.DAS_API_ENDPOINT.format(region_id=settings.ALIBABA_CLOUD_REGION_ID)
            else:
                # 使用默认凭证（从环境变量获取）
                credential = CredentialClient()
                config = open_api_models.Config(
                    credential=credential
                )
                # 使用配置化的endpoint
                config.endpoint = settings.DAS_API_ENDPOINT.format(region_id=settings.ALIBABA_CLOUD_REGION_ID)
            
            return DAS20200116Client(config)
        except Exception as e:
            logger.error(f"创建DAS客户端失败: {str(e)}")
            raise
    
    def get_client_for_account(self, aliyun_uid: str = None) -> Optional['DAS20200116Client']:
        """
        获取指定阿里云账号的客户端实例
        """
        if not ALIBABA_SDK_AVAILABLE:
            return None
            
        # 如果没有指定账号ID，使用默认客户端
        if aliyun_uid is None:
            if 'default' not in self.client_cache:
                self.client_cache['default'] = self._create_client()
            return self.client_cache['default']
        
        # 检查缓存中是否已有对应账号的客户端
        if aliyun_uid not in self.client_cache:
            self.client_cache[aliyun_uid] = self._create_client(aliyun_uid)
        
        return self.client_cache[aliyun_uid]
        
    async def _rate_limit_delay(self):
        """
        实现API调用限流
        """
        current_time = time.time()
        
        # 每秒重置计数
        if current_time - self._call_reset_time >= 1:
            self._call_reset_time = current_time
            self._call_count = 0
        
        # 如果已达到限流阈值，等待
        if self._call_count >= self.rate_limit:
            sleep_time = 1 - (current_time - self._call_reset_time)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
            self._call_count = 0
            self._call_reset_time = time.time()
        
        # 增加调用计数
        self._call_count += 1
        
        # 确保两次调用之间有足够间隔
        min_interval = 1.0 / self.rate_limit
        time_since_last_call = current_time - self._last_call_time
        if time_since_last_call < min_interval:
            await asyncio.sleep(min_interval - time_since_last_call)
        self._last_call_time = time.time()
    
    async def get_mysql_session_async(self, instance_id: str, aliyun_uid: str = None, node_id: str = None) -> Optional[Dict[str, Any]]:
        """
        异步获取MySQL会话信息
        对于RDS: 使用 instance_id
        对于PolarDB: 使用 node_id (但可能需要实例ID作为参考)
        """
        await self._rate_limit_delay()
        
        if not ALIBABA_SDK_AVAILABLE:
            # 模拟模式：返回测试数据
            logger.warning(f"阿里云SDK不可用，使用模拟数据: {instance_id}, node_id: {node_id}")
            return {
                'Code': 200,
                'Success': True,
                'Data': {
                    'ResultId': f'async_test_{instance_id}_{int(time.time())}',
                    'IsFinish': True,
                    'Timestamp': int(time.time() * 1000),
                    'Fail': False
                }
            }
        
        try:
            # 获取对应账号的客户端
            client = self.get_client_for_account(aliyun_uid)
            if not client:
                logger.error(f"无法获取账号 {aliyun_uid} 的DAS客户端")
                return None
                
            # 对于PolarDB，使用node_id作为实例ID；对于RDS，使用instance_id
            db_instance_id = node_id if node_id else instance_id
            
            request = das20200116_models.GetMySQLAllSessionAsyncRequest(
                dbInstanceId=db_instance_id  # 使用正确的参数名
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
            logger.info(f"获取实例 {db_instance_id} 会话信息成功: {response_data.get('Code', 'Unknown')}")
            
            return response_data
        except Exception as e:
            logger.error(f"获取实例 {instance_id} 会话信息失败: {str(e)}")
            return None
    
    async def poll_result(self, result_id: str, aliyun_uid: str = None) -> Optional[Dict[str, Any]]:
        """
        轮询获取DAS API异步调用结果
        """
        await self._rate_limit_delay()
        
        if not ALIBABA_SDK_AVAILABLE:
            # 模拟模式：返回测试数据
            logger.warning(f"阿里云SDK不可用，使用模拟数据: {result_id}")
            return {
                'Code': 200,
                'Success': True,
                'Data': {
                    'SessionData': {
                        'UserStats': [
                            {
                                'TotalCount': 5,
                                'ActiveCount': 0,
                                'UserList': ['test_user'],
                                'Key': 'test_user'
                            },
                            {
                                'TotalCount': 3,
                                'ActiveCount': 0,
                                'UserList': ['admin_user'],
                                'Key': 'admin_user'
                            }
                        ],
                        'TimeStamp': int(time.time() * 1000)
                    },
                    'IsFinish': True,
                    'Timestamp': int(time.time() * 1000),
                    'Fail': False
                }
            }
        
        # 获取对应账号的客户端
        client = self.get_client_for_account(aliyun_uid)
        if not client:
            logger.error(f"无法获取账号 {aliyun_uid} 的DAS客户端")
            return None
            
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
    
    async def get_mysql_session_data(self, instance_id: str, aliyun_uid: str = None, node_id: str = None) -> Optional[Dict[str, Any]]:
        """
        获取MySQL会话数据，包含异步调用和轮询结果
        """
        # 首先发起异步获取会话请求
        async_response = await self.get_mysql_session_async(instance_id, aliyun_uid, node_id)
        if not async_response:
            return None
        
        # 获取结果ID
        result_id = async_response.get('Data', {}).get('ResultId')
        if not result_id:
            logger.error(f"实例 {instance_id} 未返回结果ID")
            return None
        
        # 轮询获取结果
        result_data = await self.poll_result(result_id, aliyun_uid)
        if not result_data:
            return None
        
        # 检查结果状态
        if result_data.get('Data', {}).get('Fail', False):
            logger.error(f"实例 {instance_id} 获取会话数据失败")
            return None
        
        session_data = result_data.get('Data', {}).get('SessionData')
        if not session_data:
            logger.warning(f"实例 {instance_id} 未返回会话数据")
            return None
        
        return session_data
    
    def parse_user_session_stats(self, session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
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