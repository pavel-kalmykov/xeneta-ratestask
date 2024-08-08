import logging

from rates_api.config import settings

logger = logging.getLogger("uvicorn.error")
logger.setLevel(settings.log_level)
