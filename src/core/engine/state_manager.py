import logging

from typing import Any

from core.infra.db.models.scenario import ScenarioState
from core.infra.repositories.scenario import ScenarioStateRepository
from core.integrations.gemini import GeminiClient
from core.types import ScenarioStateSchemaT

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
        response_model_cls: type[ScenarioStateSchemaT],
        *,
        llm_temperature: float,
    ) -> ScenarioStateSchemaT:
        return self.gemini_client.generate_structured(
            prompt=prompt,
            response_model_cls=response_model_cls,
            temperature=llm_temperature,
        )

    def save_state(
        self,
        state_data: dict[str, Any],
        scenario_name: str,
    ) -> ScenarioState:
        return self.state_repository.create_state(
            state=state_data,
            scenario_name=scenario_name,
        )
