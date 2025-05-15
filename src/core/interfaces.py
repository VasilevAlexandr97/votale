from typing import Protocol

from core.config.scenarios import ScenarioSettings
from core.schemas import BaseState
from core.types import ScenarioStateSchemaT


class ScenarioProtocol(Protocol):
    def get_settings(self) -> ScenarioSettings: ...
    def initialize(self) -> BaseState: ...
    def generate_next_state(self) -> BaseState: ...

    def compose_publication(
        self,
        state: type[ScenarioStateSchemaT],
    ) -> tuple[str, list[str]]:
        ...
