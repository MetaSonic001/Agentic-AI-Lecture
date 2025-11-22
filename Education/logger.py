"""
Logging configuration using Loguru for clean, readable logs.
"""
import sys
from pathlib import Path
from loguru import logger
from config import LOG_FILE, LOG_LEVEL

def setup_logger():
    """Configure loguru logger with file and console output."""
    
    # Remove default handler
    logger.remove()
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Console handler with colors
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=LOG_LEVEL
    )
    
    # File handler for persistent logs
    logger.add(
        LOG_FILE,
        rotation="10 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )
    
    return logger

# Initialize logger
log = setup_logger()
