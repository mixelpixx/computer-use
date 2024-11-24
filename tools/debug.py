import logging
import os
import platform
import sys
import psutil
from datetime import datetime
from pathlib import Path

# Configure logging directory
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Create loggers for different components
ui_logger = logging.getLogger('ui')
api_logger = logging.getLogger('api')
tool_logger = logging.getLogger('tool')
system_logger = logging.getLogger('system')

# Configure logging format
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=LOG_FORMAT, level=logging.DEBUG)

# Add file handlers
def setup_file_handlers():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    for logger_name in ['ui', 'api', 'tool', 'system']:
        logger = logging.getLogger(logger_name)
        handler = logging.FileHandler(LOG_DIR / f'{logger_name}_{timestamp}.log')
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)

def log_system_info():
    """Log system information and diagnostics."""
    system_logger.info(f"Platform: {platform.platform()}")
    system_logger.info(f"Python version: {sys.version}")
    system_logger.info(f"CPU count: {psutil.cpu_count()}")
    system_logger.info(f"Memory: {psutil.virtual_memory()}")
    system_logger.info(f"Disk usage: {psutil.disk_usage('/')}")

def log_performance(func):
    """Decorator to log function execution time."""
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        result = func(*args, **kwargs)
        execution_time = datetime.now() - start_time
        tool_logger.debug(f"{func.__name__} executed in {execution_time}")
        return result
    return wrapper

def monitor_resources():
    """Log current system resource usage."""
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    system_logger.info(f"CPU Usage: {cpu_percent}%")
    system_logger.info(f"Memory Usage: {memory.percent}%")
    return cpu_percent, memory.percent

setup_file_handlers()
