import random

from typing import Any

from core.config.scenarios import ScenarioSettings
from core.engine.prompt_manager import PromptManager
from core.interfaces import ScenarioProtocol
from scenarios.astrocatcoin.schemas import StateSchema


class AstroCatCoinScenario(ScenarioProtocol):
    def __init__(
        self,
        settings: ScenarioSettings,
        prompt_manager: PromptManager,
    ):
        self.settings = settings
        self.prompt_manager = prompt_manager

    def get_settings(self) -> ScenarioSettings:
        return self.settings

    def get_schema(self) -> StateSchema:
        return StateSchema

    def set_trigger_major_event(self, default: bool | None = None) -> bool:
        if default is not None:
            return default
        random_value = random.randint(0, 50)
        return random_value == 0

    def initialize_prompt(self) -> str:
        base_context = self.prompt_manager.get_base_context()
        updated_context = self.prompt_manager.update_context(
            base_context=base_context,
            new_values={
                "previous_state": "Предыдущего состояния нет.",
                "chosen_option": "Ничего не выбрано",
                "trigger_major_event": self.set_trigger_major_event(
                    default=False,
                ),
            },
        )
        return self.prompt_manager.render_prompt(context=updated_context)

    def next_state_prompt(
        self,
        previous_state: StateSchema,
        chosen_option: dict[str, Any],
    ) -> str:
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

    def build_post_content(
        self,
        state: StateSchema,
    ) -> str:
        return (
            f"<b><i>{state.title}</i></b>\n\n"
            f"Текущая цена: <code>${state.current_price}</code>\n\n"
            f"{state.text}\n\n"
        )

    def build_poll_payload(
        self,
        state: StateSchema,
    ) -> tuple[str, list[str]]:
        question = f"<b>{state.question}</b>\n\n"
        options = [
            opt.text for opt in state.options
        ]
        return question, options

    def build_news_content(
        self,
        state: StateSchema,
    ) -> str:
        return "<b>Главные новости:</b>\n\n" + "\n\n".join(
            news.text for news in state.news
        )
