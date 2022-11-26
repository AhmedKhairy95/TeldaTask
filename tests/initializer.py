from typing import List

import pytest as pytest

from settings import Settings


class DevSettings(Settings):
    GRANULARITY: str = "s"
    SUPPORTED_EXTENSIONS: List[str] = ["json", "yaml", "yml"]
    LOG_LEVEL: str = "DEBUG"
    LOGS_BASE_DIRECTORY: str = "logs_test"
    JOBS_FILE_PATH: str = "tests/jobs.json"


class DevSettingsV2(DevSettings):
    JOBS_FILE_PATH: str = "tests/jobs.yaml"


class DevSettingsV3(DevSettings):
    JOBS_FILE_PATH: str = "tests/jobs.csv"


@pytest.fixture(scope="session", autouse=True)
def settings():
    settings = DevSettings()
    print(settings)
    return settings
