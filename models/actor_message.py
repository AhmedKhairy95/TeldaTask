from enum import Enum
from typing import Optional

from pydantic import BaseModel


class MessageTypes(Enum):
    TICK = "TICK"
    FINISHED_EXECUTION = "FINISHED_EXECUTION"
    NUM_RUNS = "NUM_RUNS"
    CURRENT_TICKS = "CURRENT_TICKS"


class ActorMessage(BaseModel):
    sender: str
    job_identifier: Optional[str]
    timeout_mins: Optional[int]
    type: Optional[str]
    logs: Optional[str]
    num_runs: Optional[int]
    ticks: Optional[int]
    ingestion_time: Optional[float]
