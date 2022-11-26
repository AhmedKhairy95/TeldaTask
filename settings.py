from typing import List

from pydantic import BaseSettings


class Settings(BaseSettings):
    GRANULARITY: str = "s"
    SUPPORTED_EXTENSIONS: List[str] = ["json", "yaml", "yml"]
    LOG_LEVEL: str = "INFO"
    LOGS_BASE_DIRECTORY: str = "logs"
    JOBS_FILE_PATH: str = "jobs.json"
