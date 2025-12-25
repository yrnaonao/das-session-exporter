from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = Field(default="sqlite:///./das_session_exporter.db", env="DATABASE_URL")
    
    # 阿里云配置
    ALIBABA_CLOUD_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="ALIBABA_CLOUD_ACCESS_KEY_ID")
    ALIBABA_CLOUD_ACCESS_KEY_SECRET: Optional[str] = Field(default=None, env="ALIBABA_CLOUD_ACCESS_KEY_SECRET")
    ALIBABA_CLOUD_REGION_ID: str = Field(default="cn-shanghai", env="ALIBABA_CLOUD_REGION_ID")
    
    # 应用配置
    APP_HOST: str = Field(default="0.0.0.0", env="APP_HOST")
    APP_PORT: int = Field(default=8000, env="APP_PORT")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # 指标缓存配置
    SESSION_COUNT_CACHE_TTL: int = Field(default=60, env="SESSION_COUNT_CACHE_TTL")  # 会话数指标缓存时间（秒）
    MAX_USER_CONNECTIONS_CACHE_TTL: int = Field(default=300, env="MAX_USER_CONNECTIONS_CACHE_TTL")  # 最大连接数指标缓存时间（秒）
    
    # DAS API限流配置
    DAS_API_RATE_LIMIT: int = Field(default=50, env="DAS_API_RATE_LIMIT")  # 每秒API调用次数限制（低于60次/秒以避免触发流控）
    
    # 更新间隔配置
    METRICS_UPDATE_INTERVAL: int = Field(default=60, env="METRICS_UPDATE_INTERVAL")  # 指标更新间隔（秒）
    
    # 加密配置
    ENCRYPTION_PASSWORD: str = Field(default="default_password_for_encryption", env="ENCRYPTION_PASSWORD")
    
    class Config:
        env_file = ".env"  # 从 .env 文件加载配置
        case_sensitive = False


from typing import Optional
settings = Settings()