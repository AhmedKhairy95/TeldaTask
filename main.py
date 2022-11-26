from logging.config import dictConfig

from launcher import launch_scheduler
from utils.logging_config import LogConfig

dictConfig(LogConfig().dict())

if __name__ == '__main__':
    launch_scheduler()
