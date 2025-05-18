import logging

from core.engine.poll_manager import PollManager
from core.engine.publication_manager import PublicationManager
from core.engine.state_manager import StateManager
from core.infra.db.transaction_manager import TransactionManager
from core.interfaces import ScenarioProtocol

logger = logging.getLogger(__name__)

class ScenarioManager:
    def __init__(
        self,
        scenario: ScenarioProtocol,
        state_manager: StateManager,
        poll_manager: PollManager,
        publication_manager: PublicationManager,
        transaction_manager: TransactionManager,
    ):
        self.scenario = scenario
        self.state_mgr = state_manager
        self.poll_mgr = poll_manager
        self.pub_mgr = publication_manager
        self.tr_mgr = transaction_manager

        self._scenario_settings = self.scenario.get_settings()
        self._scenario_name = self._scenario_settings.scenario_name
        self._chat_id = self._scenario_settings.tg_chat_id

    def run_generation_cycle(self):
        with self.tr_mgr:
            latest_state = self.state_mgr.get_latest_state(
                scenario_name=self._scenario_name,
                response_schema_cls=self.scenario.get_schema(),
            )
            logger.info(f"latest_state: {latest_state}")
            if not latest_state:
                next_state_prompt = self.scenario.initialize_prompt()
            else:
                poll = self.poll_mgr.get_poll_by_state_id(
                    state_id=latest_state.id,
                )
                winning_poll_option = self.poll_mgr.get_winning_poll_option(
                    poll_id=poll.id,
                )
                if winning_poll_option is None:
                    return

                logger.info(f"winning_poll_option: {winning_poll_option}")
                next_state_prompt = self.scenario.next_state_prompt(
                    previous_state=latest_state,
                    chosen_option=winning_poll_option,
                )
            next_state = self.state_mgr.create_next_state(
                scenario_name=self._scenario_name,
                prompt=next_state_prompt,
                response_schema_cls=self.scenario.get_schema(),
                llm_temperature=0.95,
            )
            logger.info(f"next_state: {next_state}")
            self.poll_mgr.add_poll_from_state(state=next_state)
            post_text = self.scenario.build_post_content(
                state=next_state,
            )
            question, options = self.scenario.build_poll_payload(
                state=next_state,
            )
            self.pub_mgr.publish_state(
                state_id=next_state.id,
                chat_id=self._chat_id,
                text=post_text,
                question=question,
                options=options,
            )

    def run_poll_cycle(self):
        with self.tr_mgr:
            latest_state = self.state_mgr.get_latest_state(
                scenario_name=self._scenario_name,
                response_schema_cls=self.scenario.get_schema(),
            )
            if not latest_state:
                return
            poll = self.poll_mgr.get_poll_by_state_id(
                state_id=latest_state.id,
            )
            poll_message = self.pub_mgr.get_poll_message_by_state_id(
                state_id=latest_state.id,
            )
            poll_results = self.poll_mgr.get_poll_results(
                chat_id=self._chat_id,
                message_id=poll_message.message_id,
            )
            logger.info(f"poll_results: {poll_results}")
            self.poll_mgr.add_poll_results(
                poll_id=poll.id,
                results=poll_results,
            )

    def run_news_cycle(self):
        with self.tr_mgr:
            latest_state = self.state_mgr.get_latest_state(
                scenario_name=self._scenario_name,
                response_schema_cls=self.scenario.get_schema(),
            )
            print(f"latest_state: {latest_state}")
            news = latest_state.news
            news_text = self.scenario.build_news_content(state=latest_state)
            print(f"news: {news}")
            self.pub_mgr.publish_news(
                chat_id=self._chat_id,
                text=news_text,
            )
