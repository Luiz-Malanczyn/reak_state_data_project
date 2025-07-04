from loguru import logger
import sys

logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{extra[classname]}</cyan> - <level>{message}</level>"
)

__all__ = ["logger"]
