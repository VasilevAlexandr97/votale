from core.config.scenarios import ScenarioSettings
from core.engine.prompt_manager import PromptManager
from core.engine.state_manager import StateManager
from core.interfaces import Scenario
from scenarios.astrocatcoin.schemas import StateSchema


class AstroCatCoinScenario(Scenario):
    def __init__(
        self,
        settings: ScenarioSettings,
        prompt_manager: PromptManager,
        state_manager: StateManager,
    ):
        self.scenario_settings = settings
        self.prompt_manager = prompt_manager
        self.state_manager = state_manager

    def start_story_prompt(self):
        base_context = self.prompt_manager.get_base_context()
        updated_context = self.prompt_manager.update_context(
            base_context=base_context,
            new_values={
                "previous_state": "Предыдущего состояния нет.",
                "chosen_option": "Ничего не выбрано",
                "trigger_major_event": False,
            },
        )
        return self.prompt_manager.render_prompt(context=updated_context)

    def continue_story(self) -> StateSchema:
        prompt = self.start_story_prompt()
        state = self.state_manager.generate_state(
            prompt=prompt,
            response_model_cls=StateSchema,
            llm_temperature=0.85,
        )
        return self.save_story_state(state=state)

    def save_story_state(
        self,
        state: StateSchema,
    ) -> StateSchema:
        state_model = self.state_manager.save_state(
            state_data=state.model_dump(),
            scenario_name=self.scenario_settings.scenario_name,
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
        question = "<b>Выберите действие, для дальнейшего развития</b>\n\n"
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
