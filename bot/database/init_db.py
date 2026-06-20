"""Инициализация базы данных и создание таблиц."""

from .models import Base
from .session import engine


def initialize_database() -> None:
    Base.metadata.create_all(engine)
