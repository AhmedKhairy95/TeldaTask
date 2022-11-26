import json
from typing import Dict

from actors.scheduler_actor import SchedulerActor
from actors.timer_actor import TimerActor
from exceptions.custom_exceptions import SchedulerNotInitialized
from job_fetcher.jobs_fetcher import JobsFetcher
from job_fetcher.jobs_fetcher_factory import JobsFetcherFactory
from models.actor_message import ActorMessage, MessageTypes
from models.jobs_fetcher_type import JobsFetcherType
from models.string_patterns import STATISTICS_COLLECTOR
from settings import Settings


class Scheduler:

    def __init__(self, settings: Settings, max_ticks: int = None,
                 job_fetcher_type: JobsFetcherType = JobsFetcherType.FILE,
                 dict: Dict = None, test_mode_enabled: bool = False):
        self.settings = settings
        self.job_fetcher: JobsFetcher = JobsFetcherFactory.get_instance(settings=self.settings,
                                                                        job_fetcher_type=job_fetcher_type,
                                                                        file_path=self.settings.JOBS_FILE_PATH,
                                                                        dict=dict)
        self.scheduler_actor_ref = None
        self.timer_actor_ref = None
        self.max_ticks = max_ticks
        self.test_mode_enabled = test_mode_enabled

    def launch(self):
        self.scheduler_actor_ref = SchedulerActor.start(settings=self.settings, cron_jobs=self.job_fetcher.fetch_jobs())
        self.timer_actor_ref = TimerActor.start(scheduler_actor_ref=self.scheduler_actor_ref,
                                                granularity=60 if self.settings.GRANULARITY == "m" else 1 if self.settings.GRANULARITY == "s" else 60,
                                                max_ticks=self.max_ticks, test_mode_enabled=self.test_mode_enabled)
        return self

    def get_num_runs_for_job(self, job_identifier: str) -> int:
        if self.scheduler_actor_ref is not None:
            msg = ActorMessage(sender=STATISTICS_COLLECTOR, type=MessageTypes.NUM_RUNS.value,
                               job_identifier=job_identifier, )
            response = self.scheduler_actor_ref.ask(json.dumps(msg.dict()))
            return ActorMessage.parse_obj(json.loads(response)).num_runs
        else:
            raise SchedulerNotInitialized()

    def get_current_ticks(self, timeout=None) -> int:
        if self.scheduler_actor_ref is not None:
            msg = ActorMessage(sender=STATISTICS_COLLECTOR, type=MessageTypes.CURRENT_TICKS.value)
            response = self.scheduler_actor_ref.ask(json.dumps(msg.dict()), timeout=timeout)
            return ActorMessage.parse_obj(json.loads(response)).ticks
        else:
            raise SchedulerNotInitialized()

    def clean_up(self):
        if self.scheduler_actor_ref is not None:
            self.scheduler_actor_ref.stop(block=True)
        if self.timer_actor_ref is not None:
            self.timer_actor_ref.stop(block=True)
