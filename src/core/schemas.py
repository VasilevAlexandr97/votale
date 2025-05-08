from typing import Literal

from pydantic import BaseModel


class News(BaseModel):
    text: str


class Option(BaseModel):
    text: str
    effect: Literal["positive", "negative", "neutral"]


class BaseState(BaseModel):
    id: int | None = None
    title: str
    text: str
    options: list[Option]
    news: list[News]
