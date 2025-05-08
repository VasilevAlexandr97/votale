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
from core.engine.prompt_manager import PromptManager
from core.engine.publication_manager import PublicationManager
from core.engine.scenario_manager import ScenarioManager
from core.engine.state_manager import StateManager
from core.infra.db.database import new_session_maker
from core.infra.repositories.scenario import ScenarioMessageRepository, ScenarioStateRepository
from core.integrations.gemini import GeminiClient
from core.integrations.telegram import TelegramClient
from core.interfaces import Scenario


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
    def get_scenario_state_repository(
        self,
        session: Session,
    ) -> ScenarioStateRepository:
        return ScenarioStateRepository(session=session)

    @provide(scope=Scope.REQUEST)
    def get_scenario_message_repository(
        self,
        session: Session,
    ) -> ScenarioMessageRepository:
        return ScenarioMessageRepository(session=session)


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
        scenario_cls: type[Scenario],
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

    @provide
    def get_scenario_manager(
        self,
        scenario: Scenario,
        publication_manager: PublicationManager,
    ) -> ScenarioManager:
        return ScenarioManager(
            scenario=scenario,
            publication_manager=publication_manager,
        )

    @provide
    def get_configured_scenario(
        self,
        scenario_settings: ScenarioSettings,
        prompt_manager: PromptManager,
        state_manager: StateManager,
    ) -> Scenario:
        return self._scenario_cls(
            settings=scenario_settings,
            prompt_manager=prompt_manager,
            state_manager=state_manager,
        )

    @provide
    def get_prompt_manager(
        self,
        scenario_settings: ScenarioSettings,
    ) -> PromptManager:
        return PromptManager(dir_path=scenario_settings.scenario_dir_path)

    @provide
    def get_state_manager(
        self,
        state_repository: ScenarioStateRepository,
        gemini_client: GeminiClient,
    ) -> StateManager:
        return StateManager(
            state_repository=state_repository,
            gemini_client=gemini_client,
        )

    @provide
    def get_publication_manager(
        self,
        telegram_client: TelegramClient,
        message_repository: ScenarioMessageRepository,
    ) -> PublicationManager:
        return PublicationManager(
            telegram_client=telegram_client,
            message_repository=message_repository,
        )
