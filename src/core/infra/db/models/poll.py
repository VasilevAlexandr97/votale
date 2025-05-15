from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.infra.db.models.base import Base
from core.infra.db.models.mixins import TimestampsMixin


class Poll(Base, TimestampsMixin):
    __tablename__ = "polls"

    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str] = mapped_column(String(255), nullable=False)

    state_id: Mapped[int] = mapped_column(
        ForeignKey("scenario_states.id", ondelete="CASCADE"),
        nullable=False,
    )
    state: Mapped["ScenarioState"] = relationship(back_populates="poll")

    options: Mapped[list["PollOption"]] = relationship(
        back_populates="poll",
        cascade="all, delete-orphan",
    )
    result: Mapped["PollResult"] = relationship(
        uselist=False,
        back_populates="poll",
        cascade="all, delete-orphan",
    )


class PollOption(Base):
    __tablename__ = "poll_options"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(nullable=False)
    effect: Mapped[str] = mapped_column(nullable=False)

    poll_id: Mapped[int] = mapped_column(
        ForeignKey("polls.id", ondelete="CASCADE"),
        nullable=False,
    )
    poll: Mapped["Poll"] = relationship(back_populates="options")


class PollResult(Base):
    __tablename__ = "poll_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    results: Mapped[dict] = mapped_column(JSON, nullable=False)
    poll_id: Mapped[int] = mapped_column(
        ForeignKey("polls.id", ondelete="CASCADE"),
        nullable=False,
    )
    poll: Mapped["Poll"] = relationship(back_populates="result")
