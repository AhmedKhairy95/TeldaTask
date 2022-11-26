import logging

from models.jobs_fetcher_type import JobsFetcherType
from scheduler import Scheduler
from settings import Settings


def launch_scheduler():
    scheduler = None
    try:
        settings = Settings()
        scheduler = Scheduler(settings=settings, job_fetcher_type=JobsFetcherType.FILE).launch()
    except Exception as e:
        logging.error(f"Scheduler exited due to an exception occurring with the following details {str(e)}")
        if scheduler is not None:
            scheduler.clean_up()
