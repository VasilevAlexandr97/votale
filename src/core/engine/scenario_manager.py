from core.engine.publication_manager import PublicationManager
from core.interfaces import Scenario


class ScenarioManager:
    def __init__(
        self,
        scenario: Scenario,
        publication_manager: PublicationManager,
    ):
        self.scenario = scenario
        self.publish_manager = publication_manager

    def run_generation_cycle(self):
        next_state = self.scenario.continue_story()
        post_content, question, options = self.scenario.compose_publication(
            state=next_state,
        )
        chat_id = self.scenario.scenario_settings.tg_chat_id
        self.publish_manager.publish_message_and_poll(
            state_id=next_state.id,
            chat_id=chat_id,
            text=post_content,
            question=question,
            options=options,
        )
