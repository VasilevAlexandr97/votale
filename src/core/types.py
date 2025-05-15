from enum import StrEnum
from typing import TypeVar

from core.schemas import BaseState

ScenarioStateSchemaT = TypeVar("ScenarioStateSchemaT", bound=BaseState)


class MessageType(StrEnum):
    STATE = "state"
    POLL = "poll"
