import datetime
import re
from typing import List

from pydantic import BaseModel, validator

from exceptions.custom_exceptions import DuplicateJobIdentifier, InvalidStartDateFormat, InvalidValueDefined
from settings import Settings

settings = Settings()


def periodicity_transform(raw: str) -> int:
    granularity: str = settings.GRANULARITY
    unit = raw.strip()[-1].lower()
    if raw.strip()[0:-1].isnumeric():
        periodicity = int(raw.strip()[0:-1])
        if granularity != unit:
            if granularity == "h":
                if unit == "m":
                    periodicity /= 60
                elif unit == "s":
                    periodicity /= 3600
            elif granularity == "m":
                if unit == "h":
                    periodicity *= 60
                elif unit == "s":
                    periodicity /= 60
            elif granularity == "s":
                if unit == "m":
                    periodicity *= 60
                elif unit == "h":
                    periodicity *= 3600
    else:
        raise ValueError("periodicity is invalid")
    return periodicity


def timeout_transform(raw: str) -> int:
    granularity: str = settings.GRANULARITY
    unit = raw.strip()[-1].lower()
    if raw.strip()[0:-1].isnumeric():
        timeout = int(raw.strip()[0:-1])
        if granularity != unit:
            if granularity == "h":
                if unit == "m":
                    if timeout % 60 == 0:
                        timeout /= 60
                    else:
                        raise InvalidValueDefined(field_name="timeout", multiple=60)
                elif unit == "s":
                    if timeout % 3600 == 0:
                        timeout /= 3600
                    else:
                        raise InvalidValueDefined(field_name="timeout", multiple=3600)
            elif granularity == "m":
                if unit == "h":
                    timeout *= 60
                elif unit == "s":
                    if timeout % 60 == 0:
                        timeout /= 60
                    else:
                        raise InvalidValueDefined(field_name="timeout", multiple=60)
            elif granularity == "s":
                if unit == "m":
                    timeout *= 60
                elif unit == "h":
                    timeout *= 3600
    else:
        raise ValueError("timeout is invalid")
    return timeout


class CronJob(BaseModel):
    identifier: str
    path: str
    function_name: str
    periodicity: int
    timeout: int
    start_date: str
    periodicity_as_ticks = validator('periodicity', pre=True, allow_reuse=True)(periodicity_transform)
    timeout_as_ticks = validator('timeout', pre=True, allow_reuse=True)(timeout_transform)

    @validator("start_date")
    def start_date_validator(cls, v):
        if not bool(re.match(pattern=r'\d{4}-\d{2}-\d{2}', string=v)):
            raise InvalidStartDateFormat()
        else:
            try:
                datetime.datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                raise InvalidStartDateFormat()
        return v


class CronJobs(BaseModel):
    jobs: List[CronJob]

    @validator("jobs")
    def start_date_validator(cls, v):
        job_identifiers = set()
        for job in v:
            if job.identifier not in job_identifiers:
                job_identifiers.add(job.identifier)
            else:
                raise DuplicateJobIdentifier(identifier=job.identifier)
        del job_identifiers
        return v
