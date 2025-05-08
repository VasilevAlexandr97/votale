import logging

from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class PromptManagerError(Exception):
    """Base exception for errors related to prompt management."""


class PromptLoadError(Exception):
    """Custom exception for errors related to loading prompts."""


class PromptRenderError(PromptManagerError):
    """Custom exception for errors related to rendering prompts."""


class PromptManager:
    def __init__(
        self,
        dir_path: Path,
        prompt_filename: str = "prompt.yaml",
    ):
        self.prompt_file_path = dir_path / prompt_filename
        self._base_context = self._load_base_context()

    def _validate_base_context(self, ctx: dict[str, str]) -> None:
        if not isinstance(ctx, dict):
            raise PromptLoadError(
                f"Invalid prompt format in {self.prompt_file_path}",
            )
        if "prompt" not in ctx or not isinstance(ctx["prompt"], str):
            raise PromptLoadError(
                "Key 'prompt' missing or not a string in "
                f"{self.prompt_file_path}",
            )

    def _load_base_context(self) -> dict[str, Any]:
        if not self.prompt_file_path.is_file():
            msg = f"Prompt file not found: {self.prompt_file_path}"
            logger.error(msg)
            raise PromptLoadError(msg)

        try:
            ctx = yaml.safe_load(
                self.prompt_file_path.read_text(encoding="utf-8"),
            )

        except yaml.YAMLError as e:
            msg = f"Error parsing YAML file {self.prompt_file_path}: {e}"
            logger.exception(msg)
            raise PromptLoadError(msg)
        except Exception as e:
            msg = f"Error loading prompt file {self.prompt_file_path}: {e}"
            logger.exception(msg)
            raise PromptLoadError(msg)
        else:
            self._validate_base_context(ctx=ctx)
            return ctx

    def get_base_context(self) -> dict[str, Any]:
        return self._base_context.copy()

    def update_context(
        self,
        base_context: dict[str, Any],
        new_values: dict[str, Any],
    ) -> dict[str, Any]:
        if not isinstance(new_values, dict):
            logger.warning(
                "update_context: new_values not a dict, "
                "returning base_context copy",
            )
            return base_context.copy()
        return {**base_context, **new_values}

    def render_prompt(self, context: dict[str, Any]) -> str:
        prompt = context.get("prompt")
        if not prompt or not isinstance(prompt, str):
            raise PromptRenderError(
                "Key 'prompt' with a non-empty string value not "
                "found in prompt_data for rendering.",
            )
        extras = [f"{k}: {v}" for k, v in context.items() if k != "prompt"]
        if extras:
            return "\n\n".join([*extras, prompt])
        return prompt
