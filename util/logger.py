from loguru import logger
import sys

# Remove o logger padrão e adiciona um com formatação bonita
logger.remove()
logger.add(sys.stdout, colorize=True, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{module}</cyan> - <level>{message}</level>")

__all__ = ["logger"]
