import logging
import threading
import time
from typing import Optional
from contextlib import contextmanager
from fastapi import FastAPI, HTTPException, Depends
from prometheus_client import generate_latest, REGISTRY
from prometheus_client.core import CollectorRegistry
from prometheus_client.exposition import choose_encoder
import uvicorn

from models.database import SessionLocal
from services.metrics_collector import MetricsCollector
from config.settings import settings


# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 移除默认收集器
try:
    from prometheus_client import (
        REGISTRY, 
        GC_COLLECTOR, 
        PLATFORM_COLLECTOR, 
        PROCESS_COLLECTOR
    )
    REGISTRY.unregister(GC_COLLECTOR)
    REGISTRY.unregister(PLATFORM_COLLECTOR)
    REGISTRY.unregister(PROCESS_COLLECTOR)
except KeyError:
    # 某些收集器可能未注册
    pass

# 创建FastAPI应用
app = FastAPI(title="MySQL Session Prometheus Exporter", description="导出阿里云RDS/PolarDB MySQL实例的用户会话数指标")

# 全局指标收集器
metrics_collector: Optional[MetricsCollector] = None
collection_lock = threading.Lock()
last_collection_time = 0


@contextmanager
def get_db():
    """
    获取数据库会话的上下文管理器
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_metrics_collector():
    """
    初始化指标收集器
    """
    global metrics_collector
    with get_db() as db:
        metrics_collector = MetricsCollector(db)


@app.on_event('startup')
async def startup_event():
    """
    应用启动事件
    """
    logger.info("应用启动中...")
    init_metrics_collector()
    logger.info("应用启动完成")


@app.get("/")
async def root():
    """
    根路径，返回服务信息
    """
    return {
        "message": "MySQL Session Prometheus Exporter",
        "description": "基于 FastAPI 的 Prometheus 自定义 Exporter,用于导出阿里云 RDS/PolarDB MySQL 实例的用户会话数指标"
    }


@app.get("/metrics")
async def get_metrics():
    """
    Prometheus指标端点
    """
    global last_collection_time
    
    # 检查是否需要更新指标
    current_time = time.time()
    if current_time - last_collection_time >= settings.METRICS_UPDATE_INTERVAL:
        with collection_lock:
            # 双重检查，确保只有一个线程更新指标
            if current_time - last_collection_time >= settings.METRICS_UPDATE_INTERVAL:
                try:
                    with get_db() as db:
                        temp_collector = MetricsCollector(db)
                        await temp_collector.collect_all_metrics()
                        last_collection_time = current_time
                        logger.info("指标已更新")
                except Exception as e:
                    logger.error(f"更新指标时发生错误: {str(e)}")
                    # 如果更新失败，仍然返回当前指标
                    pass
    
    # 生成并返回指标
    encoder, content_type = choose_encoder(None)
    output = encoder(REGISTRY)
    return output


@app.post("/refresh")
async def refresh_metrics():
    """
    手动触发指标更新
    """
    global last_collection_time
    
    with collection_lock:
        try:
            with get_db() as db:
                temp_collector = MetricsCollector(db)
                await temp_collector.manual_refresh()
                last_collection_time = time.time()
            logger.info("手动刷新指标完成")
            return {"message": "指标刷新成功"}
        except Exception as e:
            logger.error(f"手动刷新指标时发生错误: {str(e)}")
            raise HTTPException(status_code=500, detail=f"刷新指标失败: {str(e)}")


@app.get("/health")
async def health_check():
    """
    健康检查端点
    """
    return {"status": "healthy", "message": "MySQL Session Exporter is running"}


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True
    )