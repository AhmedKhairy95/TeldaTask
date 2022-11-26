from pydantic import BaseModel
from pykka import ActorRef


class TaskActorDetails(BaseModel):
    actor_ref: ActorRef
    timeout: int
    tick_of_launching_job: int

    class Config:
        arbitrary_types_allowed = True
