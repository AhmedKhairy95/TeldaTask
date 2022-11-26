import json
import logging
import time
from datetime import datetime

import pykka
from pykka import ActorRef

from models.actor_message import ActorMessage, MessageTypes
from models.actors import Actors


class TimerActor(pykka.ThreadingActor):
    def __init__(self, scheduler_actor_ref: ActorRef, granularity: int, max_ticks: int = None,
                 test_mode_enabled: bool = False):
        super().__init__()
        self.granularity = granularity
        self.scheduler_actor_ref = scheduler_actor_ref
        self.max_ticks = max_ticks
        self.test_mode_enabled = test_mode_enabled

    def send_timer_event_to_scheduler(self):
        """
        Function sends a tick event to the scheduler
        :return:
        """
        msg = ActorMessage(sender=Actors.TIMER_ACTOR.value, type=MessageTypes.TICK.value,
                           ingestion_time=datetime.utcnow().timestamp())
        self.scheduler_actor_ref.tell(json.dumps(msg.dict()))

    def on_start(self):
        while True if self.max_ticks is None else self.max_ticks != 0:
            self.send_timer_event_to_scheduler()
            if not self.test_mode_enabled:
                time.sleep(self.granularity)
            logging.debug('Sending timer event')
            if self.max_ticks is not None:
                self.max_ticks -= 1
