from pydantic import BaseModel

from settings import Settings


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    settings: Settings = Settings()

    LOGGER_NAME: str = "CronJobScheduler"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = settings.LOG_LEVEL

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers = {
        "CronJobScheduler": {
            "handlers": ["default"],
            "level": LOG_LEVEL,
        },
    }
