from typing import Any

from sqlalchemy import select
from sqlalchemy.sql.operators import eq

from core.infra.db.models.scenario import ScenarioState
from core.infra.repositories.base import BaseRepository


class ScenarioStateRepository(BaseRepository):
    def add_state(
        self,
        scenario_name: str,
        state_data: dict[str, Any],
    ) -> ScenarioState:
        model = ScenarioState(
            scenario_name=scenario_name,
            state_data=state_data,
        )
        self.session.add(model)
        self.session.flush()
        return model

    def get_latest_state(self, scenario_name: str) -> ScenarioState | None:
        stmt = (
            select(ScenarioState)
            .where(eq(ScenarioState.scenario_name, scenario_name))
            .order_by(ScenarioState.id.desc())
        )
        return self.session.scalars(stmt).first()
