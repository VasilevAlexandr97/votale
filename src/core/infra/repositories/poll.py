from sqlalchemy import select
from sqlalchemy.sql.operators import eq

from core.infra.db.models.poll import Poll, PollOption, PollResult
from core.infra.repositories.base import BaseRepository
from core.schemas import Option


class PollRepository(BaseRepository):
    def add_poll(
        self,
        question: str,
        options: list[Option],
        state_id: int,
    ) -> Poll:
        poll = Poll(
            question=question,
            options=[
                PollOption(text=opt.text, effect=opt.effect)
                for opt in options
            ],
            state_id=state_id,
        )
        self.session.add(poll)
        self.session.flush()
        return poll

    def get_poll_by_state_id(
        self,
        state_id: int,
    ) -> Poll | None:
        stmt = select(Poll).where(eq(Poll.state_id, state_id))
        return self.session.scalars(stmt).first()

    def add_poll_results(
        self,
        poll_id: int,
        results: dict[str, int],
    ) -> PollResult:
        result = PollResult(
            results=results,
            poll_id=poll_id,
        )
        self.session.add(result)
        self.session.flush()
        return result

    def get_poll_results(
        self,
        poll_id: int,
    ) -> PollResult | None:
        stmt = select(PollResult).where(eq(PollResult.poll_id, poll_id))
        return self.session.scalars(stmt).first()

    def get_poll_option_by_text(
        self,
        poll_id: int,
        text: str,
    ) -> PollOption | None:
        stmt = (
            select(PollOption)
            .where(eq(PollOption.poll_id, poll_id))
            .where(eq(PollOption.text, text))
        )
        return self.session.scalars(stmt).first()
