"""DAS Session Exporter 入口文件"""
import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager

import uvicorn
from prometheus_client import REGISTRY, GC_COLLECTOR, PLATFORM_COLLECTOR, PROCESS_COLLECTOR

from config.settings import settings
from models.database import SessionLocal
from services.metrics_collector import get_metrics_collector


# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 移除默认收集器
for collector in [GC_COLLECTOR, PLATFORM_COLLECTOR, PROCESS_COLLECTOR]:
    try:
        REGISTRY.unregister(collector)
    except KeyError:
        pass


class MetricsScheduler:
    """指标采集调度器"""
    
    def __init__(self):
        self._running = False
        self._task = None
    
    async def _collect_loop(self):
        """定时采集循环"""
        while self._running:
            try:
                await asyncio.sleep(settings.METRICS_UPDATE_INTERVAL)
                
                if not self._running:
                    break
                    
                db = SessionLocal()
                try:
                    collector = get_metrics_collector(db)
                    await collector.collect_all_metrics()
                    logger.info("定时指标采集完成")
                except Exception as e:
                    logger.error(f"定时指标采集失败: {e}")
                finally:
                    db.close()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"采集循环异常: {e}")
    
    def start(self):
        """启动调度器"""
        self._running = True
        self._task = asyncio.create_task(self._collect_loop())
        logger.info("指标采集调度器已启动")
    
    async def stop(self):
        """停止调度器"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("指标采集调度器已停止")


# 全局调度器实例
scheduler = MetricsScheduler()


@asynccontextmanager
async def lifespan_wrapper(app):
    """应用生命周期管理"""
    scheduler.start()
    yield
    await scheduler.stop()


def main():
    """主函数"""
    logger.info("MySQL Session Prometheus Exporter 启动中...")
    logger.info(f"监听地址: {settings.APP_HOST}:{settings.APP_PORT}")
    logger.info(f"指标更新间隔: {settings.METRICS_UPDATE_INTERVAL}秒")
    
    # 修改app的lifespan
    from core.app import app
    app.router.lifespan_context = lifespan_wrapper
    
    uvicorn.run(
        app,
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        log_level=settings.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()