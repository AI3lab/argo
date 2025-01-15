# agent_engine.py
import multiprocessing

import uvicorn

from argo.configs import logger
from argo.env_settings import settings

class AgentEngine(object):
    def __init__(self):
        self._started = False

    def start(self, dev_mode: bool = False):
        if self._started:
            logger.error("Container already started")
            return

        config = {
            "app": "argo.main:app",
            "host": settings.API_HOST,
            "port": settings.API_PORT,
            "workers": 1 if dev_mode else multiprocessing.cpu_count(),
            "reload": dev_mode,
            "log_level": "debug" if dev_mode else "info",

        }
        self._started = True
        uvicorn.run(**config)