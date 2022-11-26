from typing import Dict

from exceptions.custom_exceptions import JobFetcherNotSupported
from job_fetcher.job_from_from_dict import JobsFetcherFromDict
from job_fetcher.jobs_fetcher import JobsFetcher
from job_fetcher.jobs_fetcher_from_file import JobsFetcherFromFile
from models.jobs_fetcher_type import JobsFetcherType
from settings import Settings


class JobsFetcherFactory:
    @staticmethod
    def get_instance(settings: Settings, job_fetcher_type: JobsFetcherType, file_path: str = None,
                     endpoint: str = None, dict: Dict = None) -> JobsFetcher:
        """
        Function creates an instance of the job fetcher according to the passed JobFetcherType
        :param settings: holds all the application configurations
        :param job_fetcher_type: the type of the job fetcher, whether it's a FILE, or just a DICT or maybe fetch it from an endpoint
        :param file_path: the path to the file if the job fetcher type was a FILE
        :param endpoint: the endpoint to call if the job fetcher type was API
        :param dict: the dict to parse if the job fetcher type was DICT
        :return: an instance of JobFetcher
        """
        if job_fetcher_type == JobsFetcherType.FILE:
            return JobsFetcherFromFile(settings=settings, file_path=file_path)
        elif job_fetcher_type == JobsFetcherType.DICT:
            return JobsFetcherFromDict(dict=dict)
        else:
            raise JobFetcherNotSupported()
