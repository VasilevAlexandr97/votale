from typing import Any

from core.infra.db.models.scenario import ScenarioMessage, ScenarioState
from core.infra.repositories.base import BaseRepository
from core.types import ScenarioMessageType


class ScenarioStateRepository(BaseRepository):
    def create_state(
        self,
        state: dict[str, Any],
        scenario_name: str,
    ) -> ScenarioState:
        model = ScenarioState(state=state, scenario_name=scenario_name)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return model

    def get_last_state(self):
        pass


class ScenarioMessageRepository(BaseRepository):
    def create_message(
        self,
        message_id: int,
        message_type: ScenarioMessageType,
        state_id: int,
    ) -> ScenarioMessage:
        model = ScenarioMessage(
            message_id=message_id,
            type=message_type,
            state_id=state_id,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return model