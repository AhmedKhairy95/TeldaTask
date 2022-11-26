import re
import time
from typing import List

import pytest as pytest

from exceptions.custom_exceptions import DuplicateJobIdentifier, FileReaderFactoryException, InvalidStartDateFormat, \
    JobFetcherNotSupported
from models.jobs_fetcher_type import JobsFetcherType
from scheduler import Scheduler
from tests.initializer import DevSettings, DevSettingsV2, DevSettingsV3
from utils.os_helpers import clear_directory, get_files_in_directory


def test_scheduler():
    dict = {
        "jobs": [
            {
                "identifier": "job1",
                "path": "tests.periodic_functions.functions",
                "function_name": "func1",
                "timeout": "5s",
                "periodicity": "1s",
                "start_date": "2022-11-21"
            },
            {
                "identifier": "job2",
                "path": "tests.periodic_functions.functions",
                "function_name": "print_string",
                "timeout": "20s",
                "periodicity": "5s",
                "start_date": "2022-11-21"
            }
        ]
    }
    settings = DevSettings()
    scheduler = Scheduler(settings=settings, max_ticks=5, job_fetcher_type=JobsFetcherType.DICT, dict=dict,
                          test_mode_enabled=True).launch()

    while scheduler.get_current_ticks(timeout=2) != 5:
        continue

    tasks_ran_for_job1 = scheduler.get_num_runs_for_job(job_identifier="job1")
    tasks_ran_for_job2 = scheduler.get_num_runs_for_job(job_identifier="job2")

    scheduler.clean_up()

    clear_directory(directory=settings.LOGS_BASE_DIRECTORY)
    assert tasks_ran_for_job1 == 5
    assert tasks_ran_for_job2 == 1


def test_blocking_task():
    dict = {
        "jobs": [
            {
                "identifier": "job1",
                "path": "tests.periodic_functions.functions",
                "function_name": "blocking_task",
                "timeout": "2s",
                "periodicity": "5s",
                "start_date": "2022-11-21"
            }
        ]
    }

    settings = DevSettings()

    scheduler = Scheduler(settings=settings, max_ticks=3, job_fetcher_type=JobsFetcherType.DICT, dict=dict,
                          test_mode_enabled=True).launch()

    while scheduler.get_current_ticks(timeout=2) != 3:
        continue

    tasks_ran_for_job1 = scheduler.get_num_runs_for_job(job_identifier="job1")

    scheduler.clean_up()

    files: List[str] = get_files_in_directory(directory=f'{settings.LOGS_BASE_DIRECTORY}/job1')

    did_timeout = False
    with open(files[0], 'r') as f:
        lines = f.readlines()
        for line in lines:
            if bool(re.match(pattern=r'Task Execution Timed Out', string=line)):
                did_timeout = True
                break

    clear_directory(directory=settings.LOGS_BASE_DIRECTORY)
    assert tasks_ran_for_job1 == 1
    assert did_timeout is True


def test_job_with_duplicate_identifier():
    with pytest.raises(DuplicateJobIdentifier):
        dict = {
            "jobs": [
                {
                    "identifier": "job1",
                    "path": "tests.periodic_functions.functions",
                    "function_name": "func1",
                    "timeout": "5s",
                    "periodicity": "1s",
                    "start_date": "2022-11-21"
                },
                {
                    "identifier": "job1",
                    "path": "tests.periodic_functions.functions",
                    "function_name": "print_string",
                    "timeout": "20s",
                    "periodicity": "5s",
                    "start_date": "2022-11-21"
                }
            ]
        }

        settings = DevSettings()

        Scheduler(settings=settings, max_ticks=3, job_fetcher_type=JobsFetcherType.DICT, dict=dict,
                  test_mode_enabled=True).launch()
    clear_directory(directory=settings.LOGS_BASE_DIRECTORY)


def test_fetching_json():
    settings = DevSettings()

    scheduler = Scheduler(settings=settings, max_ticks=5, job_fetcher_type=JobsFetcherType.FILE,
                          test_mode_enabled=True).launch()

    while scheduler.get_current_ticks(timeout=2) != 5:
        continue

    tasks_ran_for_job1 = scheduler.get_num_runs_for_job(job_identifier="job1")
    tasks_ran_for_job2 = scheduler.get_num_runs_for_job(job_identifier="job2")

    scheduler.clean_up()

    clear_directory(directory=settings.LOGS_BASE_DIRECTORY)
    assert tasks_ran_for_job1 == 5
    assert tasks_ran_for_job2 == 1


def test_fetching_yaml():
    settings = DevSettingsV2()

    scheduler = Scheduler(settings=settings, max_ticks=5, job_fetcher_type=JobsFetcherType.FILE,
                          test_mode_enabled=True).launch()

    time.sleep(2)

    tasks_ran_for_job1 = scheduler.get_num_runs_for_job(job_identifier="job1")
    tasks_ran_for_job2 = scheduler.get_num_runs_for_job(job_identifier="job2")

    scheduler.clean_up()
    clear_directory(directory=settings.LOGS_BASE_DIRECTORY)
    assert tasks_ran_for_job1 == 5
    assert tasks_ran_for_job2 == 1


def test_fetching_file_unsupported_extension():
    with pytest.raises(FileReaderFactoryException):
        settings = DevSettingsV3()
        Scheduler(settings=settings, max_ticks=5, job_fetcher_type=JobsFetcherType.FILE,
                  test_mode_enabled=True).launch()
    clear_directory(directory=settings.LOGS_BASE_DIRECTORY)


def test_job_with_invalid_start_date():
    with pytest.raises(InvalidStartDateFormat):
        dict = {
            "jobs": [
                {
                    "identifier": "job1",
                    "path": "tests.periodic_functions.functions",
                    "function_name": "func1",
                    "timeout": "5s",
                    "periodicity": "1s",
                    "start_date": "2022-15-21"
                }
            ]
        }

        settings = DevSettings()

        Scheduler(settings=settings, max_ticks=5, job_fetcher_type=JobsFetcherType.DICT, dict=dict,
                  test_mode_enabled=True).launch()

    clear_directory(directory=settings.LOGS_BASE_DIRECTORY)


def test_job_with_invalid_start_date_v2():
    with pytest.raises(InvalidStartDateFormat):
        dict = {
            "jobs": [
                {
                    "identifier": "job1",
                    "path": "tests.periodic_functions.functions",
                    "function_name": "func1",
                    "timeout": "5s",
                    "periodicity": "1s",
                    "start_date": "2022/11/21"
                }
            ]
        }

        settings = DevSettings()

        Scheduler(settings=settings, max_ticks=5, job_fetcher_type=JobsFetcherType.DICT, dict=dict,
                  test_mode_enabled=True).launch()

    clear_directory(directory=settings.LOGS_BASE_DIRECTORY)


def test_scheduler_with_granularity_unlike_unit():
    dict = {
        "jobs": [
            {
                "identifier": "job1",
                "path": "tests.periodic_functions.functions",
                "function_name": "func1",
                "timeout": "300s",
                "periodicity": "60s",
                "start_date": "2022-11-21"
            }
        ]
    }

    settings = DevSettings()

    scheduler = Scheduler(settings=settings, max_ticks=1, job_fetcher_type=JobsFetcherType.DICT, dict=dict,
                          test_mode_enabled=True).launch()

    while scheduler.get_current_ticks(timeout=2) != 1:
        continue

    tasks_ran_for_job1 = scheduler.get_num_runs_for_job(job_identifier="job1")

    scheduler.clean_up()

    clear_directory(directory=settings.LOGS_BASE_DIRECTORY)
    assert tasks_ran_for_job1 == 1


def test_execution_time_is_written():
    dict = {
        "jobs": [
            {
                "identifier": "job1",
                "path": "tests.periodic_functions.functions",
                "function_name": "func1",
                "timeout": "10s",
                "periodicity": "1s",
                "start_date": "2022-11-21"
            }
        ]
    }

    settings = DevSettings()

    scheduler = Scheduler(settings=settings, max_ticks=1, job_fetcher_type=JobsFetcherType.DICT, dict=dict,
                          test_mode_enabled=True).launch()

    while scheduler.get_current_ticks(timeout=2) != 1:
        continue

    tasks_ran_for_job1 = scheduler.get_num_runs_for_job(job_identifier="job1")

    scheduler.clean_up()

    files: List[str] = get_files_in_directory(directory=f'{settings.LOGS_BASE_DIRECTORY}/job1')

    was_written = False
    with open(files[0], 'r') as f:
        lines = f.readlines()
        for line in lines:
            if bool(re.match(pattern=r'^Execution\sTime\s=.+$', string=line)):
                was_written = True
                break

    clear_directory(directory=settings.LOGS_BASE_DIRECTORY)
    assert tasks_ran_for_job1 == 1
    assert was_written is True


def test_unsupported_job_fetcher_type():
    with pytest.raises(JobFetcherNotSupported):
        dict = {
            "jobs": [
                {
                    "identifier": "job1",
                    "path": "tests.periodic_functions.functions",
                    "function_name": "func1",
                    "timeout": "5s",
                    "periodicity": "1s",
                    "start_date": "2022-11-21"
                },
                {
                    "identifier": "job2",
                    "path": "tests.periodic_functions.functions",
                    "function_name": "print_string",
                    "timeout": "20s",
                    "periodicity": "5s",
                    "start_date": "2022-11-21"
                }
            ]
        }

        settings = DevSettings()

        Scheduler(settings=settings, max_ticks=3, job_fetcher_type=JobsFetcherType.API, dict=dict,
                  test_mode_enabled=True).launch()
    clear_directory(directory=settings.LOGS_BASE_DIRECTORY)
