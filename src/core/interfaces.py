from abc import abstractmethod
from typing import Protocol

from core.config.scenarios import ScenarioSettings
from core.engine.prompt_manager import PromptManager
from core.schemas import BaseState


class ScenarioProtocol(Protocol):
    """
    Интерфейс любого сценария в Votale.
    Сценарий отвечает за:
      — свои настройки (settings),
      — управление шаблоном (prompt_manager),
      — сборку запросов к LLM (initialize_prompt / next_state_prompt),
      — формирование контента для публикаций (build_*).
    """
    settings: ScenarioSettings
    prompt_manager: PromptManager

    def __init__(
        self,
        settings: ScenarioSettings,
        prompt_manager: PromptManager,
    ):
        ...

    @abstractmethod
    def get_settings(self) -> ScenarioSettings:
        """
        Возвращает текущие настройки сценария.
        Обычно просто `return self.settings`.
        """

    @abstractmethod
    def get_schema(self) -> type[BaseState]:
        """
        Возвращает Pydantic-класс схемы состояния мира
        (подкласс BaseState), который используется для валидации
        и парсинга ответа LLM.
        """

    @abstractmethod
    def initialize_prompt(self) -> str:
        """
        Составляет и возвращает текст промпта для первого шага,
        когда previous_state отсутствует.
        """

    @abstractmethod
    def next_state_prompt(self) -> str:
        """
        Составляет и возвращает текст промпта для генерации следующего
        состояния мира, когда есть previous_state и выбранная опция.
        """

    @abstractmethod
    def build_post_content(
        self,
        state: BaseState,
    ) -> str:
        """
        Формирует основной текст поста для публикации:
        заголовок, цену, описание состояния.
        """

    @abstractmethod
    def build_poll_payload(
        self,
        state: BaseState,
    ) -> tuple[str, list[str]]:
        """
        Формирует вопрос и список вариантов для опроса:
        — question: str
        — options: List[str]
        """

    @abstractmethod
    def build_news_content(
        self,
        state: BaseState,
    ) -> str:
        """
        Формирует единый блок текста с новостями,
        готовый для публикации одним сообщением.
        """
