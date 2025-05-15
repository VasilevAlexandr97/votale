from sqlalchemy import select
from sqlalchemy.sql.operators import eq

from core.infra.db.models.message import Message
from core.infra.repositories.base import BaseRepository
from core.types import MessageType


class MessageRepository(BaseRepository):
    def add_message(
        self,
        m_type: MessageType,
        message_id: int,
        state_id: int,
    ) -> Message:
        message = Message(
            type=m_type,
            message_id=message_id,
            state_id=state_id,
        )
        self.session.add(message)
        self.session.flush()
        return message

    def get_poll_message_by_state_id(self, state_id: int) -> Message | None:
        stmt = (
            select(Message)
            .where(eq(Message.state_id, state_id))
            .where(eq(Message.type, MessageType.POLL))
        )
        return self.session.scalars(stmt).first()
