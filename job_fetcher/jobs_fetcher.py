from abc import ABC, abstractmethod

from models.cron_job import CronJobs


class JobsFetcher(ABC):
    @abstractmethod
    def fetch_jobs(self) -> CronJobs:
        pass
