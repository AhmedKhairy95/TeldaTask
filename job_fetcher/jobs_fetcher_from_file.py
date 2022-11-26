from typing import Dict

from file_reader.file_reader import FileReader
from file_reader.file_reader_factory import FileReaderFactory
from job_fetcher.jobs_fetcher import JobsFetcher
from models.cron_job import CronJobs
from settings import Settings


class JobsFetcherFromFile(JobsFetcher):
    def __init__(self, settings: Settings, file_path: str):
        self.file_path: str = file_path
        file_extension: str = file_path.split(".")[-1]
        self.file_reader: FileReader = FileReaderFactory.get_instance(settings=settings, file_extension=file_extension)

    def fetch_jobs(self) -> CronJobs:
        """
        Function reads a file and parse it back into a pydantic model representing the jobs to run
        :return: a pydantic model (CronJobs)
        """
        content: Dict = self.file_reader.read_file(path=self.file_path)
        return CronJobs.parse_obj(content)
