"""
Logger System: Comprehensive logging throughout the application.
Provides structured logging with multiple output formats.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional
from config import get_config
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs logs in JSON format."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""
    
    # Color codes for different log levels
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[41m',   # Red background
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        level = record.levelname
        color = self.COLORS.get(level, '')
        
        # Format the message
        formatted = super().format(record)
        
        # Add color codes
        return f"{color}{formatted}{self.RESET}"


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    json_format: bool = False
) -> logging.Logger:
    """
    Set up a logger with console and file handlers.
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional log file path
        json_format: Use JSON format for file output
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent adding duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler with colored output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = ColoredFormatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler if log_file is provided
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use rotating file handler to prevent large log files
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # File captures all levels
        
        if json_format:
            file_formatter = JSONFormatter()
        else:
            file_formatter = logging.Formatter(
                fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


class LoggerManager:
    """Manages all loggers in the application."""
    
    _loggers = {}
    
    @classmethod
    def get_logger(
        cls,
        name: str,
        json_format: bool = False
    ) -> logging.Logger:
        """
        Get or create a logger instance.
        
        Args:
            name: Logger name
            json_format: Use JSON format for file output
            
        Returns:
            Logger instance
        """
        if name not in cls._loggers:
            config = get_config()
            logger = setup_logger(
                name,
                level=logging.DEBUG if config.app.debug else logging.INFO,
                log_file=str(config.paths.log_file),
                json_format=json_format
            )
            cls._loggers[name] = logger
        
        return cls._loggers[name]
    
    @classmethod
    def get_all_loggers(cls):
        """Get all registered loggers."""
        return cls._loggers.copy()
    
    @classmethod
    def set_level(cls, level: int):
        """Set log level for all loggers."""
        for logger in cls._loggers.values():
            logger.setLevel(level)
            for handler in logger.handlers:
                handler.setLevel(level)


# Create application loggers
app_logger = LoggerManager.get_logger("app")
agent_logger = LoggerManager.get_logger("agents")
memory_logger = LoggerManager.get_logger("memory")
ui_logger = LoggerManager.get_logger("ui")
api_logger = LoggerManager.get_logger("api")


def log_function_call(func_name: str, args: dict, logger: logging.Logger = None):
    """Log function call with arguments."""
    if logger is None:
        logger = app_logger
    
    logger.debug(f"Calling {func_name} with args: {args}")


def log_function_result(func_name: str, result: any, logger: logging.Logger = None):
    """Log function result."""
    if logger is None:
        logger = app_logger
    
    logger.debug(f"{func_name} returned: {type(result).__name__}")


def log_error(error_msg: str, exception: Exception = None, logger: logging.Logger = None):
    """Log error with optional exception details."""
    if logger is None:
        logger = app_logger
    
    if exception:
        logger.error(error_msg, exc_info=True)
    else:
        logger.error(error_msg)
