import io
import json
import logging
import logging as default_logger
from contextlib import redirect_stdout

import pykka

from models.actor_message import ActorMessage, MessageTypes
from models.actors import Actors


class TaskActor(pykka.ThreadingActor):
    def __init__(self, task_monitor_actor_ref, identifier, target):
        super().__init__()
        self.task_monitor_actor_ref = task_monitor_actor_ref
        self.identifier = identifier
        self.target = target

    def send_finish_event_to_task_monitor(self, logs):
        """
        Function notifies the TaskMonitor Actor that it has finished execution

        :param logs: the logs captured from the target function called
        :return: None
        """
        msg = ActorMessage(sender=Actors.TASK_ACTOR.value,
                           job_identifier=self.identifier, logs=logs,
                           type=MessageTypes.FINISHED_EXECUTION.value)
        self.task_monitor_actor_ref.tell(json.dumps(msg.dict()))
        default_logger.debug(f'Task {self.identifier} finished execution & sending finish event to task monitor')

    def on_start(self):
        with io.StringIO() as buf, redirect_stdout(buf):
            try:
                self.target()
            except Exception as e:
                exception_msg = f"Task with identifier {self.identifier} has faced the following exception, {str(e)}"
                buf.write(exception_msg + "\n")
                logging.error(exception_msg)
            logs = buf.getvalue()
        self.send_finish_event_to_task_monitor(logs=logs)

    def on_stop(self):
        default_logger.debug(f"Task actor with identifier {self.identifier} is being stopped")
