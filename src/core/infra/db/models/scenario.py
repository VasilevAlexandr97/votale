from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.infra.db.models.base import Base
from core.infra.db.models.mixins import TimestampsMixin


class ScenarioState(Base, TimestampsMixin):
    __tablename__ = "scenario_states"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenario_name: Mapped[str] = mapped_column(nullable=False)
    state_data: Mapped[dict] = mapped_column(JSON, nullable=False)

    poll: Mapped["Poll"] = relationship(
        uselist=False,
        back_populates="state",
        cascade="all, delete-orphan",
    )
    messages: Mapped[list["Message"]] = relationship(
        back_populates="state",
        cascade="all, delete-orphan",
    )
