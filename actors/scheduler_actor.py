import json
import logging
from datetime import datetime, timezone
from typing import Dict

import pykka

from actors.task_monitor_actor import TaskMonitorActor
from models.actor_message import ActorMessage, MessageTypes
from models.actors import Actors
from models.cron_job import CronJob, CronJobs
from models.string_patterns import STATISTICS_COLLECTOR
from models.task_actor_details import TaskActorDetails
from settings import Settings
from utils.os_helpers import get_target_function


class SchedulerActor(pykka.ThreadingActor):
    def __init__(self, settings: Settings, cron_jobs: CronJobs, pevent=None, **kwargs):
        super().__init__(pevent, **kwargs)
        self.settings = settings
        self.cron_jobs = cron_jobs
        self.tasks_monitors_actors_ref: Dict[str, TaskActorDetails] = {}
        self.task_metrics: Dict[str, int] = {}
        self.ticks = 0

    def on_receive(self, message):
        """
        :param message: a message which is received by other actors
        :return:
        """
        msg = ActorMessage.parse_obj(json.loads(message))
        if msg.sender.startswith(Actors.TASK_MONITOR_ACTOR.value) and msg.type == MessageTypes.FINISHED_EXECUTION.value:
            # Here we're receiving a FinishExecution event sent by a task monitor actor,
            # indicating that a function has finished execution successfully
            logging.debug(
                f'Received {MessageTypes.FINISHED_EXECUTION.value} event from task with identifier {msg.job_identifier}')
            if msg.job_identifier in self.tasks_monitors_actors_ref:
                self.tasks_monitors_actors_ref.pop(msg.job_identifier)
        elif msg.sender == Actors.TIMER_ACTOR.value and msg.type == MessageTypes.TICK.value:
            logging.debug(f'Received timer event')
            logging.debug(
                f'Time taken for scheduler to receive the tick event is {datetime.utcnow().timestamp() - msg.ingestion_time} seconds')
            self.check_if_to_schedule_tasks()
            self.check_timeouts()
            self.ticks += 1
        elif msg.sender == STATISTICS_COLLECTOR and msg.type == MessageTypes.NUM_RUNS.value:
            reply_msg = ActorMessage(sender=Actors.SCHEDULER_ACTOR.value,
                                     num_runs=self.task_metrics[
                                         msg.job_identifier] if msg.job_identifier in self.task_metrics else 0)
            return json.dumps(reply_msg.dict())
        elif msg.sender == STATISTICS_COLLECTOR and msg.type == MessageTypes.CURRENT_TICKS.value:
            reply_msg = ActorMessage(sender=Actors.SCHEDULER_ACTOR.value,
                                     ticks=self.ticks)
            return json.dumps(reply_msg.dict())

    def stop_task_monitor(self, job_identifier: str) -> None:
        """
        :param job_identifier: the job's unique identifier
        :return: None

        Function simply kills the task monitor actor
        Function is called when the task times out
        """
        self.tasks_monitors_actors_ref[job_identifier].actor_ref.stop(block=True)
        if job_identifier in self.tasks_monitors_actors_ref:
            self.tasks_monitors_actors_ref.pop(job_identifier)

    def launch_task(self, job: CronJob) -> None:
        """

        :param job: the job model holding all its configuration
        :return: None
        Function launches a Task Monitor actor which in turn launches a Task Actor
        Also, it adds the task metadata to the state
        """
        target = get_target_function(job.path, job.function_name)

        run_id = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        job_identifier = f'{job.identifier}:{run_id}'

        # Launching a task monitor actor
        task_actor_ref = TaskMonitorActor.start(base_directory=self.settings.LOGS_BASE_DIRECTORY,
                                                scheduler_actor_ref=self.actor_ref, identifier=job.identifier,
                                                run_id=run_id, target=target)

        self.tasks_monitors_actors_ref[job_identifier] = TaskActorDetails(actor_ref=task_actor_ref, timeout=job.timeout,
                                                                          tick_of_launching_job=self.ticks)
        if job.identifier not in self.task_metrics:
            self.task_metrics[job.identifier] = 1
        else:
            self.task_metrics[job.identifier] = self.task_metrics[job.identifier] + 1
        logging.debug(f"Task is launched with the following configs {job}")

    def check_timeouts(self) -> None:
        """
        Function iterates over its state to check whether it should trigger a timeout event for a task if any
        :return: None
        """
        jobs_to_stop = []
        for job_identifier, job_details in self.tasks_monitors_actors_ref.items():
            if self.ticks != job_details.tick_of_launching_job:
                job_details.timeout = job_details.timeout - 1
                if job_details.timeout == 0:
                    jobs_to_stop.append(job_identifier)
                    logging.error(f'Task with the following identifier {job_identifier} is timed out')
        for job_identifier in jobs_to_stop:
            self.stop_task_monitor(job_identifier)

    def check_if_to_schedule_tasks(self) -> None:
        """
        Function iterates over jobs fetched
        It checks whether the job is eligible to be running or not
        This is done by checking the job's intended start date vs the current date,
        and whether it should be scheduled again during this tick or not
        :return: None
        """
        if self.cron_jobs is not None:
            current_date = datetime.utcnow().replace(tzinfo=timezone.utc, hour=0, minute=0, second=0, microsecond=0)
            for job in self.cron_jobs.jobs:
                job_start_date = datetime.strptime(job.start_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                if job_start_date <= current_date and self.ticks % job.periodicity == 0:
                    self.launch_task(job=job)

    def on_stop(self) -> None:
        for job_identifier in self.tasks_monitors_actors_ref:
            try:
                self.tasks_monitors_actors_ref[job_identifier].actor_ref.stop(block=True)
            except Exception as e:
                logging.error(f"Faced an error while trying to stop the TaskActor for identifier {job_identifier}")
                pass
