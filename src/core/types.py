from enum import StrEnum
from typing import TypeVar

from pydantic import BaseModel

ScenarioStateSchemaT = TypeVar("ScenarioStateSchemaT", bound=BaseModel)


class ScenarioMessageType(StrEnum):
    STATE = "state"
    POLL = "poll"
