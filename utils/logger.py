"""
Dify Plugin Unified Logging Tool Module
"""
import logging
from dify_plugin.config.logger_format import plugin_logger_handler


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Get configured logger instance

    Args:
        name: Logger name, usually use __name__
        level: Log level, default is INFO

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers
    if not logger.handlers:
        logger.addHandler(plugin_logger_handler)

    return logger
