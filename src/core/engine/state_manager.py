import logging

from typing import Any

from core.infra.db.models.scenario import ScenarioState
from core.infra.repositories.scenario_state import ScenarioStateRepository
from core.integrations.gemini import GeminiClient
from core.schemas import BaseState

logger = logging.getLogger(__name__)



class StateManager:
    def __init__(
        self,
        state_repository: ScenarioStateRepository,
        gemini_client: GeminiClient,
    ):
        self.state_repository = state_repository
        self.gemini_client = gemini_client

    def generate_state(
        self,
        prompt: str,
        response_schema_cls: type[BaseState],
        *,
        llm_temperature: float,
    ) -> BaseState:
        return self.gemini_client.generate_structured(
            prompt=prompt,
            response_schema_cls=response_schema_cls,
            temperature=llm_temperature,
        )

    def add_state(
        self,
        scenario_name: str,
        state_data: dict[str, Any],
    ) -> ScenarioState:
        return self.state_repository.add_state(
            scenario_name=scenario_name,
            state_data=state_data,
        )

    def create_next_state(
        self,
        scenario_name: str,
        prompt: str,
        response_schema_cls: type[BaseState],
        *,
        llm_temperature: float,
    ):
        next_state = self.generate_state(
            prompt=prompt,
            response_schema_cls=response_schema_cls,
            llm_temperature=llm_temperature,
        )
        new_state = self.add_state(
            scenario_name=scenario_name,
            state_data=next_state.model_dump(),
        )
        next_state.id = new_state.id
        return next_state

    def get_latest_state(
        self,
        scenario_name: str,
        response_schema_cls: type[BaseState],
    ) -> BaseState | None:
        state = self.state_repository.get_latest_state(
            scenario_name=scenario_name,
        )
        if state is None:
            return None

        response_schema = response_schema_cls(**state.state_data)
        response_schema.id = state.id
        return response_schema
