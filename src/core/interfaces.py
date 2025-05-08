from typing import Protocol

from core.schemas import BaseState
from core.types import ScenarioStateSchemaT


class Scenario(Protocol):
    def continue_story(
        self,
    ) -> BaseState:
        ...

    def compose_publication(
        self,
        state: ScenarioStateSchemaT,
    ) -> tuple[str, list[str]]:
        ...
