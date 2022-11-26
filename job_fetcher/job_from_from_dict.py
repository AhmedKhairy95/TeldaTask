from typing import Dict

from job_fetcher.jobs_fetcher import JobsFetcher
from models.cron_job import CronJobs


class JobsFetcherFromDict(JobsFetcher):
    def __init__(self, dict: Dict):
        self.dict = dict

    def fetch_jobs(self) -> CronJobs:
        return CronJobs.parse_obj(self.dict)
