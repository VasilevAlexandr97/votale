from typing import Any
from core.config.scenarios import ScenarioSettings
from core.engine.prompt_manager import PromptManager
from core.engine.state_manager import StateManager
from core.interfaces import ScenarioProtocol
from scenarios.astrocatcoin.schemas import StateSchema
import random

class AstroCatCoinScenario(ScenarioProtocol):
    def __init__(
        self,
        settings: ScenarioSettings,
        prompt_manager: PromptManager,
        state_manager: StateManager,
    ):
        self.settings = settings
        self.prompt_manager = prompt_manager
        self.state_manager = state_manager

    def get_settings(self) -> ScenarioSettings:
        return self.settings

    def get_schema(self) -> type[StateSchema]:
        return StateSchema

    def set_trigger_major_event(self, default: bool | None = None):
        if default is not None:
            return default
        random_value = random.randint(0, 1)
        return random_value == 0

    def initialize_prompt(self):
        base_context = self.prompt_manager.get_base_context()
        updated_context = self.prompt_manager.update_context(
            base_context=base_context,
            new_values={
                "previous_state": "Предыдущего состояния нет.",
                "chosen_option": "Ничего не выбрано",
                "trigger_major_event": self.set_trigger_major_event(
                    default=False
                ),
            },
        )
        return self.prompt_manager.render_prompt(context=updated_context)

    def next_state_prompt(
        self,
        previous_state: StateSchema,
        chosen_option: dict[str, Any],
    ) -> StateSchema:
        base_context = self.prompt_manager.get_base_context()
        updated_context = self.prompt_manager.update_context(
            base_context=base_context,
            new_values={
                "previous_state": previous_state,
                "chosen_option": chosen_option,
                "trigger_major_event": self.set_trigger_major_event(),
            },
        )
        return self.prompt_manager.render_prompt(context=updated_context)

        # latest_state = self.state_manager.get_latest_state(
        #     self.settings.scenario_name,
        #     response_schema_cls=StateSchema,
        # )
        # print(latest_state)
        # prompt = self.initialize()
        # state = self.state_manager.generate_state(
        #     prompt=prompt,
        #     response_schema_cls=StateSchema,
        #     llm_temperature=0.95,
        # )
        # return self.save_story_state(state=state)

    def save_story_state(
        self,
        state: StateSchema,
    ) -> StateSchema:
        state_model = self.state_manager.add_state(
            state_data=state.model_dump(),
            scenario_name=self.settings.scenario_name,
        )
        state.id = state_model.id
        return state

    def _build_post_content(
        self,
        state: StateSchema,
    ) -> str:
        return (
            f"<b><i>{state.title}</i></b>\n\n"
            f"Текущая цена: <code>${state.current_price}</code>\n\n"
            f"{state.text}\n\n"
        )

    def _build_poll_content(
        self,
        state: StateSchema,
    ) -> tuple[str, list[str]]:
        question = f"<b>{state.question}</b>\n\n"
        options = [
            opt.text for opt in state.options
        ]
        return question, options

    def compose_publication(
        self,
        state: StateSchema,
    ) -> tuple[str, str, list[str]]:
        print("AstroCatCoinScenario")
        post_content = self._build_post_content(state=state)
        question, options = self._build_poll_content(state=state)
        return post_content, question, options
