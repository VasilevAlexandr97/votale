import os

from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class PostgresSettings:
    user: str = ""
    password: str = ""
    host: str = ""
    port: int = 5432
    database: str = ""

    @property
    def psycopg_dsn(self) -> str:
        return (
            f"postgresql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )


@dataclass(frozen=True)
class GeminiSettings:
    api_key: str = ""
    model: str = "gemini-2.5-pro-preview-03-25"


@dataclass(frozen=True)
class TelegramSettings:
    token: str = ""


@dataclass(frozen=True)
class AppSettings:
    project_path: Path = Path(__file__).parent.parent.parent.parent
    postgres: PostgresSettings = field(default_factory=PostgresSettings)
    gemini: GeminiSettings = field(default_factory=GeminiSettings)
    telegram: TelegramSettings = field(default_factory=TelegramSettings)

    @property
    def scenarios_path(self) -> Path:
        return self.project_path / "src/scenarios/"


def load_app_settings(env_file: Path | None = None):
    in_docker = os.getenv("DOCKER_ENV", "false") == "true"
    if not in_docker:
        load_dotenv(dotenv_path=env_file)

    postgres_settings = PostgresSettings(
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", ""),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=os.getenv("POSTGRES_DATABASE", "postgres"),
    )
    gemini_settings = GeminiSettings(
        api_key=os.getenv("GEMINI_API_KEY", ""),
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-pro-preview-03-25"),
    )
    telegram_settings = TelegramSettings(
        token=os.getenv("TG_TOKEN", ""),
    )
    return AppSettings(
        postgres=postgres_settings,
        gemini=gemini_settings,
        telegram=telegram_settings,
    )
