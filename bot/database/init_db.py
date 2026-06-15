"""Инициализация базы данных и создание таблиц."""

from bot.database.models import Base
from bot.database.session import engine


def initialize_database() -> None:
    Base.metadata.create_all(engine)
