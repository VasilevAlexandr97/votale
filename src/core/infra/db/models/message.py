from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.infra.db.models.base import Base
from core.infra.db.models.mixins import TimestampsMixin


class Message(Base, TimestampsMixin):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)

    type: Mapped[str] = mapped_column(nullable=False)
    message_id: Mapped[int] = mapped_column(nullable=False)

    state_id: Mapped[int] = mapped_column(
        ForeignKey("scenario_states.id", ondelete="CASCADE"),
        nullable=False,
    )
    state: Mapped["ScenarioState"] = relationship(back_populates="messages")
