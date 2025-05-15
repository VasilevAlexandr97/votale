import os

from collections.abc import Iterable

from dishka import Provider, Scope, from_context, provide
from sqlalchemy.orm import Session, sessionmaker

from core.config.scenarios import ScenarioSettings
from core.config.settings import (
    AppSettings,
    GeminiSettings,
    PostgresSettings,
    TelegramSettings,
)
from core.engine.poll_manager import PollManager
from core.engine.prompt_manager import PromptManager
from core.engine.publication_manager import PublicationManager
from core.engine.scenario_manager import ScenarioManager
from core.engine.state_manager import StateManager
from core.infra.db.database import new_session_maker
from core.infra.db.transaction_manager import TransactionManager
from core.infra.repositories.message import MessageRepository
from core.infra.repositories.poll import PollRepository
from core.infra.repositories.scenario_state import (
    ScenarioStateRepository,
)
from core.integrations.gemini import GeminiClient
from core.integrations.telegram import TelegramClient
from core.interfaces import ScenarioProtocol


class AppProvider(Provider):
    scope = Scope.REQUEST
    settings = from_context(provides=AppSettings, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def get_database_settings(
        self,
        settings: AppSettings,
    ) -> PostgresSettings:
        return settings.postgres

    @provide(scope=Scope.APP)
    def get_gemini_settings(
        self,
        settings: AppSettings,
    ) -> GeminiSettings:
        return settings.gemini

    @provide(scope=Scope.APP)
    def get_telegram_settings(
        self,
        settings: AppSettings,
    ) -> TelegramSettings:
        return settings.telegram


class DatabaseProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def get_session_maker(
        self,
        settings: PostgresSettings,
    ) -> sessionmaker[Session]:
        return new_session_maker(settings)

    @provide(scope=Scope.REQUEST)
    def get_session(
        self,
        session_maker: sessionmaker[Session],
    ) -> Iterable[Session]:
        with session_maker() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def get_transaction_manager(
        self,
        session: Session,
    ) -> TransactionManager:
        return TransactionManager(session=session)

    @provide(scope=Scope.REQUEST)
    def get_scenario_state_repository(
        self,
        session: Session,
    ) -> ScenarioStateRepository:
        return ScenarioStateRepository(session=session)

    @provide(scope=Scope.REQUEST)
    def get_poll_repository(
        self,
        session: Session,
    ) -> PollRepository:
        return PollRepository(session=session)

    @provide(scope=Scope.REQUEST)
    def get_message_repository(
        self,
        session: Session,
    ) -> MessageRepository:
        return MessageRepository(session=session)


class IntegrationsProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def get_gemini_client(
        self,
        settings: GeminiSettings,
    ) -> GeminiClient:
        return GeminiClient(
            api_key=settings.api_key,
            model="gemini-2.5-flash-preview-04-17",
        )

    @provide(scope=Scope.APP)
    def get_telegram_client(
        self,
        settings: TelegramSettings,
    ) -> TelegramClient:
        return TelegramClient(token=settings.token)


class ScenarioProvider(Provider):
    scope = Scope.REQUEST

    def __init__(
        self,
        scenario_name: str,
        scenario_cls: type[ScenarioProtocol],
    ):
        super().__init__()
        self._scenario_name = scenario_name
        self._scenario_cls = scenario_cls

    @provide(scope=Scope.APP)
    def get_scenario_settings(
        self,
        settings: AppSettings,
    ) -> ScenarioSettings:
        tg_chat_id = os.getenv(f"{self._scenario_name.upper()}_TG_CHAT_ID", "")
        return ScenarioSettings(
            scenario_name=self._scenario_name,
            scenario_dir_path=settings.scenarios_path / self._scenario_name,
            tg_chat_id=tg_chat_id,
        )

    @provide(scope=Scope.REQUEST)
    def get_scenario_manager(
        self,
        scenario: ScenarioProtocol,
        state_manager: StateManager,
        poll_manager: PollManager,
        publication_manager: PublicationManager,
        transaction_manager: TransactionManager,
    ) -> ScenarioManager:
        return ScenarioManager(
            scenario=scenario,
            state_manager=state_manager,
            poll_manager=poll_manager,
            publication_manager=publication_manager,
            transaction_manager=transaction_manager,
        )

    @provide(scope=Scope.REQUEST)
    def get_configured_scenario(
        self,
        scenario_settings: ScenarioSettings,
        prompt_manager: PromptManager,
        state_manager: StateManager,
    ) -> ScenarioProtocol:
        return self._scenario_cls(
            settings=scenario_settings,
            prompt_manager=prompt_manager,
            state_manager=state_manager,
        )

    @provide(scope=Scope.REQUEST)
    def get_prompt_manager(
        self,
        scenario_settings: ScenarioSettings,
    ) -> PromptManager:
        return PromptManager(dir_path=scenario_settings.scenario_dir_path)

    @provide(scope=Scope.REQUEST)
    def get_state_manager(
        self,
        state_repository: ScenarioStateRepository,
        gemini_client: GeminiClient,
    ) -> StateManager:
        return StateManager(
            state_repository=state_repository,
            gemini_client=gemini_client,
        )

    @provide(scope=Scope.REQUEST)
    def get_publication_manager(
        self,
        telegram_client: TelegramClient,
        message_repository: MessageRepository,
    ) -> PublicationManager:
        return PublicationManager(
            telegram_client=telegram_client,
            message_repository=message_repository,
        )

    @provide(scope=Scope.REQUEST)
    def get_poll_manager(
        self,
        poll_repository: PollRepository,
        telegram_client: TelegramClient,
    ) -> PollManager:
        return PollManager(
            poll_repository=poll_repository,
            telegram_client=telegram_client,
        )
