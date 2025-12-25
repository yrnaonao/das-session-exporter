from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    
    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://root:123456@localhost:3306/das_session_exporter"
    
    # DAS API配置
    ALIBABA_CLOUD_REGION_ID: str = "cn-shanghai"
    DAS_API_RATE_LIMIT: float = 5.0  # 每秒API调用次数限制
    DAS_API_ENDPOINT: str = "das.{region_id}.aliyuncs.com"
    
    # 缓存配置
    SESSION_COUNT_CACHE_TTL: int = 300  # 会话数指标缓存时间（秒）
    MAX_USER_CONNECTIONS_CACHE_TTL: int = 3600  # 最大连接数指标缓存时间（秒）
    
    # 指标更新间隔
    METRICS_UPDATE_INTERVAL: int = 60  # 指标更新间隔（秒）
    
    # 并发配置
    MAX_CONCURRENT_INSTANCES: int = 5  # 最大并发实例采集数
    THREAD_POOL_SIZE: int = 10  # 线程池大小
    
    # 轮询配置
    POLL_MAX_ATTEMPTS: int = 30  # 最大轮询次数
    POLL_INTERVAL: float = 1.0  # 轮询间隔（秒）
    
    class Config:
        env_file = ".env"


settings = Settings()