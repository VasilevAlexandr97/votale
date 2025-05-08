from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScenarioSettings:
    scenario_name: str
    scenario_dir_path: Path
    tg_chat_id: int | str
