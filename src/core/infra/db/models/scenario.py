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

    chosen_option: Mapped["ScenarioChosenOption"] = relationship(
        uselist=False,
        back_populates="scenario_state",
        cascade="all, delete-orphan",
    )
    messages: Mapped[list["ScenarioMessage"]] = relationship(
        back_populates="state",
        cascade="all, delete-orphan",
    )


class ScenarioChosenOption(Base, TimestampsMixin):
    __tablename__ = "scenario_chosen_options"

    id: Mapped[int] = mapped_column(primary_key=True)

    option: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
    )

    state_id: Mapped[int] = mapped_column(
        ForeignKey("scenario_states.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    scenario_state: Mapped[ScenarioState] = relationship(
        back_populates="chosen_option",
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
