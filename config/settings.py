from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    应用配置
    """
    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://root:123456@localhost:3306/das_session_exporter"
    
    # DAS API配置
    ALIBABA_CLOUD_REGION_ID: str = "cn-shanghai"
    DAS_API_RATE_LIMIT: int = 10  # 每秒API调用次数限制
    
    # 缓存配置
    SESSION_COUNT_CACHE_TTL: int = 300  # 会话数指标缓存时间（秒）
    MAX_USER_CONNECTIONS_CACHE_TTL: int = 3600  # 最大连接数指标缓存时间（秒）
    
    # 指标更新间隔
    METRICS_UPDATE_INTERVAL: int = 60  # 指标更新间隔（秒）
    
    # DAS API Endpoint配置
    DAS_API_ENDPOINT: str = "das.{region_id}.aliyuncs.com"  # DAS API端点模板
    
    class Config:
        env_file = ".env"  # 从.env文件加载配置


settings = Settings()