import asyncio
import logging
import threading
import time
from contextlib import contextmanager

import uvicorn
from prometheus_client import REGISTRY, GC_COLLECTOR, PLATFORM_COLLECTOR, PROCESS_COLLECTOR

from config.settings import settings
from models.database import SessionLocal
from services.metrics_collector import MetricsCollector


# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 移除默认收集器
try:
    REGISTRY.unregister(GC_COLLECTOR)
    REGISTRY.unregister(PLATFORM_COLLECTOR)
    REGISTRY.unregister(PROCESS_COLLECTOR)
except KeyError:
    # 某些收集器可能未注册
    pass


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


def run_periodic_collection():
    """
    定时收集指标的后台任务
    """
    global last_collection_time
    logger.info("启动定时指标收集任务")
    
    while True:
        try:
            time.sleep(settings.METRICS_UPDATE_INTERVAL)
            
            with get_db() as db:
                collector = MetricsCollector(db)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(collector.collect_all_metrics())
                finally:
                    loop.close()
                    
            logger.info("定时指标收集完成")
        except Exception as e:
            logger.error(f"定时指标收集时发生错误: {str(e)}")


def main():
    """
    主函数
    """
    logger.info("启动MySQL Session Prometheus Exporter")
    
    # 启动后台定时收集任务
    collection_thread = threading.Thread(target=run_periodic_collection, daemon=True)
    collection_thread.start()
    
    # 启动FastAPI服务器
    uvicorn.run(
        "core.app:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        log_level=settings.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()