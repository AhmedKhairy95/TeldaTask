import json
import logging
from datetime import datetime

import pykka
from pykka import ActorRef

from actors.task_actor import TaskActor
from models.string_patterns import EXECUTION_TIME_LOG, TASK_EXECUTION_TIMED_OUT
from models.actor_message import ActorMessage, MessageTypes
from models.actors import Actors
from utils.os_helpers import create_directory


class TaskMonitorActor(pykka.ThreadingActor):
    def __init__(self, base_directory: str, scheduler_actor_ref: ActorRef, identifier, run_id, target):
        super().__init__()
        self.base_directory = base_directory
        self.scheduler_actor_ref = scheduler_actor_ref
        self.identifier = identifier
        self.run_id = run_id
        self.task_identifier = f'{self.identifier}:{self.run_id}'
        self.target = target
        self.file = None
        self.start_time = None
        self.timed_out = True
        self.task_actor_ref = None
        self.logs = None
        self.create_file()

    def create_file(self):
        """
        Function creates an append only file
        :return: None
        """
        create_directory(f'{self.base_directory}/{self.identifier}')
        self.file = open(f'{self.base_directory}/{self.identifier}/{self.run_id}.txt', 'a')

    def on_receive(self, message):
        msg = ActorMessage.parse_obj(json.loads(message))
        if msg.sender == Actors.TASK_ACTOR.value and msg.type == MessageTypes.FINISHED_EXECUTION.value:
            self.logs = msg.logs
            self.send_finish_event_to_scheduler()
            self.timed_out = False
            self.task_actor_ref.stop()
            self.stop()

    def send_finish_event_to_scheduler(self):
        """
        Function notifies the scheduler that the task has finished execution
        :return:
        """
        msg = ActorMessage(sender=f"{Actors.TASK_MONITOR_ACTOR.value}:{self.task_identifier}",
                           job_identifier=self.task_identifier,
                           type=MessageTypes.FINISHED_EXECUTION.value)
        self.scheduler_actor_ref.tell(json.dumps(msg.dict()))
        logging.debug(f'Task {self.task_identifier} finished execution & sending finish event to scheduler')

    def on_start(self):
        self.start_time = datetime.now()
        self.task_actor_ref = TaskActor.start(task_monitor_actor_ref=self.actor_ref, identifier=self.task_identifier,
                                              target=self.target)

    def on_stop(self):
        end_time = datetime.now()
        if self.timed_out:
            logging.info(f'Task stopped due to timeout with job identifier = {self.identifier}')
            self.file.write(f'{EXECUTION_TIME_LOG.format(end_time - self.start_time)}\n')
            self.file.write(TASK_EXECUTION_TIMED_OUT)
        else:
            if self.logs is not None:
                self.file.write(self.logs)
            self.file.write(f'{EXECUTION_TIME_LOG.format(end_time - self.start_time)}')
            logging.info(f'Task stopped with job identifier = {self.identifier}')
        self.file.close()
