import logging
import time
import asyncio
from typing import Optional
from fastapi import FastAPI
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from contextlib import asynccontextmanager
from threading import Lock

from models.database import SessionLocal, engine
from models.instance import Base
from services.metrics_collector import MetricsCollector
from config.settings import settings


logger = logging.getLogger(__name__)

# 创建指标收集器实例
metrics_collector: Optional[MetricsCollector] = None
last_collection_time = 0
collection_lock = Lock()

# 创建数据库表
Base.metadata.create_all(bind=engine)


def get_db():
    """
    获取数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    global metrics_collector
    
    # 启动时的初始化
    db = next(get_db())
    try:
        metrics_collector = MetricsCollector(db)
        logger.info("指标收集器初始化完成")
    finally:
        db.close()
    
    yield
    
    # 关闭时的清理
    logger.info("应用正在关闭")


# 创建FastAPI应用
app = FastAPI(
    title="DAS Session Exporter",
    description="阿里云DAS会话指标Prometheus Exporter",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """
    根路径，返回API信息
    """
    return {
        "message": "DAS Session Exporter is running",
        "endpoints": {
            "/metrics": "Prometheus metrics endpoint",
            "/health": "Health check endpoint"
        }
    }


@app.get("/health")
async def health():
    """
    健康检查端点
    """
    return {"status": "healthy"}


@app.get("/metrics")
async def get_metrics():
    """
    Prometheus指标端点
    """
    global last_collection_time, metrics_collector
    
    # 检查是否需要更新指标
    current_time = time.time()
    if current_time - last_collection_time >= settings.METRICS_UPDATE_INTERVAL:
        with collection_lock:
            # 双重检查，确保只有一个线程更新指标
            if current_time - last_collection_time >= settings.METRICS_UPDATE_INTERVAL:
                try:
                    # 使用现有的metrics_collector实例更新指标
                    if metrics_collector:
                        # 重新获取数据库会话以避免会话过期
                        db = next(get_db())
                        try:
                            # 临时创建一个收集器用于更新指标，但不重新注册指标
                            temp_collector = MetricsCollector(db)
                            await temp_collector.collect_all_metrics()
                            
                            # 更新全局收集器的缓存
                            metrics_collector.session_count_cache = temp_collector.session_count_cache
                            metrics_collector.session_count_cache_time = temp_collector.session_count_cache_time
                            metrics_collector.max_connections_cache = temp_collector.max_connections_cache
                            metrics_collector.max_connections_cache_time = temp_collector.max_connections_cache_time
                            
                            last_collection_time = current_time
                            logger.info("指标已更新")
                        finally:
                            db.close()
                    else:
                        logger.error("指标收集器未初始化")
                except Exception as e:
                    logger.error(f"更新指标时发生错误: {str(e)}")
                    # 如果更新失败，仍然返回当前指标
                    pass
    
    # 返回最新的指标
    return generate_latest()


@app.post("/refresh")
async def refresh_metrics():
    """
    手动刷新指标端点
    """
    global metrics_collector
    
    if metrics_collector:
        db = next(get_db())
        try:
            temp_collector = MetricsCollector(db)
            await temp_collector.manual_refresh()
            
            # 更新全局收集器的缓存
            metrics_collector.session_count_cache = temp_collector.session_count_cache
            metrics_collector.session_count_cache_time = temp_collector.session_count_cache_time
            metrics_collector.max_connections_cache = temp_collector.max_connections_cache
            metrics_collector.max_connections_cache_time = temp_collector.max_connections_cache_time
            
            logger.info("指标已手动刷新")
            return {"status": "success", "message": "指标已手动刷新"}
        finally:
            db.close()
    else:
        logger.error("指标收集器未初始化")
        return {"status": "error", "message": "指标收集器未初始化"}