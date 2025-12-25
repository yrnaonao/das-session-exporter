"""FastAPI应用主文件"""
import logging
import time
import asyncio
from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from contextlib import asynccontextmanager

from models.database import SessionLocal, engine
from models.instance import Base
from services.metrics_collector import get_metrics_collector
from config.settings import settings


logger = logging.getLogger(__name__)

# 状态管理
_last_collection_time: float = 0
_collection_lock = asyncio.Lock()

# 创建数据库表
Base.metadata.create_all(bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("应用启动，初始化指标收集器")
    yield
    logger.info("应用正在关闭")


app = FastAPI(
    title="DAS Session Exporter",
    description="阿里云DAS会话Prometheus Exporter",
    version="2.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "DAS Session Exporter is running",
        "version": "2.0.0",
        "endpoints": {
            "/metrics": "Prometheus metrics endpoint",
            "/health": "Health check endpoint",
            "/refresh": "Manual refresh endpoint (POST)"
        }
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


@app.get("/metrics")
async def get_metrics():
    """获取Prometheus指标"""
    global _last_collection_time
    
    current_time = time.time()
    should_update = current_time - _last_collection_time >= settings.METRICS_UPDATE_INTERVAL
    
    if should_update:
        async with _collection_lock:
            # 双重检查
            if current_time - _last_collection_time >= settings.METRICS_UPDATE_INTERVAL:
                try:
                    db = SessionLocal()
                    try:
                        collector = get_metrics_collector(db)
                        await collector.collect_all_metrics()
                        _last_collection_time = time.time()
                    finally:
                        db.close()
                except Exception as e:
                    logger.error(f"更新指标失败: {e}")
    
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.post("/refresh")
async def refresh_metrics():
    """手动刷新指标"""
    try:
        db = SessionLocal()
        try:
            collector = get_metrics_collector(db)
            await collector.manual_refresh()
            return {"status": "success", "message": "指标已刷新"}
        finally:
            db.close()
    except Exception as e:
        logger.error(f"刷新指标失败: {e}")
        return {"status": "error", "message": str(e)}