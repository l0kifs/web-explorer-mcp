import sys

from loguru import logger

from web_explorer_mcp.config.settings import LoggingSettings


def logging_config(settings: LoggingSettings) -> None:
    """
    Настройка логирования.

    Args:
        log_file: Путь к файлу для записи логов. Если не указан, логирование будет только в консоль.
    """

    logger.remove()

    logger.add(
        sys.stdout,
        level=settings.console_log_level,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}:{line}</cyan> - <white>{message}</white> | {extra}",
    )

    if settings.log_file_path:
        if settings.log_file_format.lower() == "json":
            logger.add(
                settings.log_file_path,
                level="DEBUG",
                rotation="10 MB",
                retention=1,
                enqueue=True,
                serialize=True,  # JSON format for machine parsing
            )
        elif settings.log_file_format.lower() == "text":
            logger.add(
                settings.log_file_path,
                level=settings.file_log_level,
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message} | {extra}",
                rotation="10 MB",
                retention=1,
                enqueue=True,
                serialize=False,
            )
        else:
            raise ValueError(
                f"Invalid log_file_format. Use 'text' or 'json'. Current value: {settings.log_file_format}"
            )
