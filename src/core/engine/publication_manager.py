from typing import Any

from core.infra.db.models.message import Message
from core.infra.repositories.message import MessageRepository
from core.integrations.telegram import TelegramClient
from core.types import MessageType


class PublicationManager:
    def __init__(
        self,
        telegram_client: TelegramClient,
        message_repository: MessageRepository,
    ):
        self.telegram_client = telegram_client
        self.message_repo = message_repository

    def publish_message(
        self,
        chat_id: int,
        text: str,
    ) -> dict[str, Any]:
        return self.telegram_client.send_message(chat_id=chat_id, text=text)

    def publish_poll(
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

    def publish_state(
        self,
        state_id: int,
        chat_id: int,
        content: str,
        question: str,
        options: list[str],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        message = self.publish_message(chat_id=chat_id, text=content)
        poll = self.publish_poll(
            chat_id=chat_id,
            question=question,
            options=options,
        )
        self.add_state_message(
            state_id=state_id,
            message_id=message["message_id"],
        )
        self.add_poll_message(
            state_id=state_id,
            message_id=poll["message_id"],
        )
        return message, poll

    def add_state_message(
        self,
        state_id: int,
        message_id: int,
    ) -> None:
        self.message_repo.add_message(
            m_type=MessageType.STATE,
            message_id=message_id,
            state_id=state_id,
        )

    def add_poll_message(
        self,
        state_id: int,
        message_id: int,
    ) -> None:
        self.message_repo.add_message(
            m_type=MessageType.POLL,
            message_id=message_id,
            state_id=state_id,
        )

    def get_poll_message_by_state_id(self, state_id: int) -> Message | None:
        return self.message_repo.get_poll_message_by_state_id(
            state_id=state_id,
        )
