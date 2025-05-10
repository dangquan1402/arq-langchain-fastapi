import sys
from loguru import logger
from pathlib import Path

def setup_logging():
    # Remove default logger
    logger.remove()
    
    # Create logs directory if it doesn't exist
    log_path = Path("logs")
    log_path.mkdir(exist_ok=True)
    
    # Add console logger
    logger.add(
        sys.stderr,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        level="INFO"
    )
    
    # Add file logger
    logger.add(
        "logs/app.log",
        rotation="50 MB",
        retention="10 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        level="INFO"
    )

    logger.info("Logging configured successfully")
