from typing import Any

from core.infra.repositories.scenario import ScenarioMessageRepository
from core.integrations.telegram import TelegramClient
from core.types import ScenarioMessageType


class PublicationManager:
    def __init__(
        self,
        telegram_client: TelegramClient,
        message_repository: ScenarioMessageRepository,
    ):
        self.telegram_client = telegram_client
        self.message_repo = message_repository

    def _publish_message(
        self,
        chat_id: int,
        text: str,
    ) -> dict[str, Any]:
        return self.telegram_client.send_message(chat_id=chat_id, text=text)

    def _publish_poll(
        self,
        chat_id: int,
        question: str,
        options: list[str],
    ) -> dict[str, Any]:
        return self.telegram_client.send_poll(
            chat_id=chat_id,
            question=question,
            options=options,
        )

    def publish_message_and_poll(
        self,
        state_id: int,
        chat_id: int,
        text: str,
        question: str,
        options: list[str],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        message = self._publish_message(chat_id=chat_id, text=text)
        poll = self._publish_poll(
            chat_id=chat_id,
            question=question,
            options=options,
        )
        self.message_repo.create_message(
            message_id=message["message_id"],
            message_type=ScenarioMessageType.STATE,
            state_id=state_id,
        )
        self.message_repo.create_message(
            message_id=poll["message_id"],
            message_type=ScenarioMessageType.POLL,
            state_id=state_id,
        )
        return message, poll
