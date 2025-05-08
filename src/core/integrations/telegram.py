import json
import logging

from typing import Any

import requests

logger = logging.getLogger(__name__)


class TelegramClientError(Exception):
    """Custom exception for errors during Telegram posting using requests."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_data: dict | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class TelegramClient:
    BASE_API_URL = "https://api.telegram.org/bot"

    def __init__(self, token: str, request_timeout: int = 10):
        if not token:
            raise ValueError("Telegram bot token cannot be empty.")
        self._token = token
        self._base_url = f"{self.BASE_API_URL}{self._token}/"
        self._timeout = request_timeout
        self._session = requests.Session()
        self._session.headers["Content-Type"] = "application/json"

        self._parse_mode = "HTML"
        logger.info("Telegram Poster (requests) initialized.")

    def _make_request(
        self,
        method_name: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        url = f"{self._base_url}{method_name}"
        try:
            response = self._session.post(
                url,
                json=data,
                timeout=self._timeout,
            )
            response.raise_for_status()
            response_data = response.json()

            if response_data.get("ok"):
                logger.debug(
                    f"Request successful. Response result: "
                    f"{response_data.get('result')}",
                )
                return response_data.get("result", {})
            error_description = response_data.get(
                "description",
                "Unknown API error",
            )
            error_code = response_data.get("error_code")
            logger.error(
                f"Telegram API error: {error_description} "
                f"(Code: {error_code})",
            )
            raise TelegramClientError(
                f"Telegram API error: {error_description}",
                status_code=response.status_code,
                response_data=response_data,
            )
        except requests.exceptions.Timeout as e:
            logger.exception(
                f"Request timeout error calling {method_name}",
            )
            raise TelegramClientError(f"Request timed out: {e}") from e
        except requests.exceptions.RequestException as e:
            logger.exception(f"Request error calling {method_name}")
            status_code = (
                e.response.status_code if e.response is not None else None
            )
            raise TelegramClientError(
                f"Network or request error: {e}",
                status_code=status_code,
            ) from e
        except json.JSONDecodeError as e:
            logger.exception(
                f"Failed to decode JSON response from {method_name}",
            )
            raise TelegramClientError(
                f"Invalid JSON response received: {e}",
            ) from e
        except Exception as e:
            # Перехват других неожиданных ошибок
            logger.exception(
                f"An unexpected error occurred during "
                f"request to {method_name}",
            )
            raise TelegramClientError(
                f"An unexpected error occurred: {e}",
            ) from e

    def stop_poll(
        self,
        chat_id: int | str,
        message_id: int,
        **kwargs,
    ) -> dict[str, Any]:
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            **kwargs,
        }
        logger.info(
            f"Stopping poll with message_id {message_id} in chat_id {chat_id}",
        )
        result = self._make_request("stopPoll", data=payload)
        logger.info(f"Poll stopped successfully for message_id {message_id}")
        return result

    def send_message(
        self,
        chat_id: int | str,
        text: str,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Отправляет текстовое сообщение в указанный чат. (Синхронно)

        Args:
            chat_id: Уникальный идентификатор целевого чата или username.
            text: Текст сообщения.
            **kwargs: Дополнительные параметры для API метода sendMessage.

        Returns:
            Словарь, представляющий объект Message из ответа API.

        Raises:
            TelegramPostingError: В случае ошибки.
        """
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": self._parse_mode,
            **kwargs,
        }
        logger.info(f"Sending message to chat_id: {chat_id}")
        result = self._make_request("sendMessage", data=payload)
        logger.info(
            f"Message sent successfully to chat_id: {chat_id} "
            f"(Message ID: {result.get('message_id')})",
        )
        return result

    def send_poll(
        self,
        chat_id: int | str,
        question: str,
        options: list[str],
        **kwargs,
    ) -> dict[str, Any]:
        question_min_length = 1
        question_max_length = 300
        min_options = 2
        max_options = 10
        # Валидация базовых параметров
        if not (min_options <= len(options) <= max_options):
            msg = (
                f"Poll must have between 2 and 10 options, got {len(options)}."
            )
            logger.error(msg)
            raise TelegramClientError(msg)
        if not (question_min_length <= len(question) <= question_max_length):
            msg = (f"Poll question length must be between 1 and 300 chars, "
                   f"got {len(question)}.")
            logger.error(msg)
            raise TelegramClientError(msg)

        payload = {
            "chat_id": chat_id,
            "question": question,
            "question_parse_mode": self._parse_mode,
            "options": options,
            "type": "regular",  # 'quiz' or 'regular'
            **kwargs,
        }
        logger.info(
            f"Sending poll to chat_id: {chat_id} with question: '{question}'",
        )
        result = self._make_request("sendPoll", data=payload)
        logger.info(
            f"Poll sent successfully to chat_id: {chat_id} "
            f"(Message ID: {result.get('message_id')})",
        )
        return result
