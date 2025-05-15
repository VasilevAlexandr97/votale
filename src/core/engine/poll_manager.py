from typing import Any

from core.infra.db.models.poll import Poll, PollResult
from core.infra.repositories.poll import PollRepository
from core.integrations.telegram import TelegramClient
from core.schemas import BaseState


class PollManager:
    def __init__(
        self,
        poll_repository: PollRepository,
        telegram_client: TelegramClient,

    ):
        self.poll_repository = poll_repository
        self.telegram_client = telegram_client

    def add_poll_from_state(
        self,
        state: BaseState,
    ) -> Poll:
        return self.poll_repository.add_poll(
            question=state.question,
            options=state.options,
            state_id=state.id,
        )
    
    def get_poll_by_state_id(
        self,
        state_id: int,
    ) -> Poll | None:
        return self.poll_repository.get_poll_by_state_id(state_id=state_id)

    def get_poll_results(
        self,
        chat_id: int,
        message_id: int,
    ) -> dict[str, Any]:
        poll_object = self.telegram_client.stop_poll(
            chat_id=chat_id,
            message_id=message_id,
        )
        return poll_object["options"]

    def add_poll_results(
        self,
        poll_id: int,
        results: dict[str, Any],
    ) -> PollResult:
        return self.poll_repository.add_poll_results(
            poll_id=poll_id,
            results=results,
        )

    def get_winning_poll_option(
        self,
        poll_id: int,
    ) -> dict[str, str] | None:
        poll_results = self.poll_repository.get_poll_results(poll_id=poll_id)
        if not poll_results:
            return None

        win_option = max(
            poll_results.results,
            key=lambda option: option["voter_count"],
        )
        poll_option = self.poll_repository.get_poll_option_by_text(
            poll_id=poll_id,
            text=win_option["text"],
        )
        return {"text": poll_option.text, "effect": poll_option.effect}
