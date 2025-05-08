from typing import Any

from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.infra.db.models.base import Base
from core.infra.db.models.mixins import TimestampsMixin


class ScenarioState(Base, TimestampsMixin):
    __tablename__ = "scenario_states"

    id: Mapped[int] = mapped_column(primary_key=True)

    state: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
    )
    scenario_name: Mapped[str] = mapped_column(nullable=False)

    messages: Mapped[list["ScenarioMessage"]] = relationship(
        back_populates="state",
        cascade="all, delete-orphan",
    )
    poll_results: Mapped[list["ScenarioPollResult"]] = relationship(
        back_populates="state",
        cascade="all, delete-orphan",
    )


class ScenarioPollResult(Base, TimestampsMixin):
    __tablename__ = "scenario_poll_results"

    id: Mapped[int] = mapped_column(primary_key=True)

    message_id: Mapped[int] = mapped_column(nullable=False)
    result: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
    )

    state_id: Mapped[int] = mapped_column(
        ForeignKey("scenario_states.id", ondelete="CASCADE"),
        nullable=False,
    )
    state: Mapped["ScenarioState"] = relationship(
        back_populates="poll_results",
    )


class ScenarioMessage(Base, TimestampsMixin):
    __tablename__ = "scenario_messages"

    id: Mapped[int] = mapped_column(primary_key=True)

    message_id: Mapped[int] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=False)

    state_id: Mapped[int] = mapped_column(
        ForeignKey("scenario_states.id", ondelete="CASCADE"),
        nullable=False,
    )
    state: Mapped["ScenarioState"] = relationship(back_populates="messages")
