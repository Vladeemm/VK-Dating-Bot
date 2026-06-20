"""Модуль управления сессиями SQLAlchemy.

Предоставляет подключение к базе данных и контекстный менеджер
для безопасной работы с транзакциями.
"""

import json
import os
from contextlib import contextmanager
from typing import Generator

import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy.orm import Session, sessionmaker

from .models import Base

load_dotenv()

config = os.getenv('DATABASE')
if not config:
    raise RuntimeError('DATABASE environment variable is not set')

try:
    db_config = json.loads(config)
except json.JSONDecodeError as exc:
    raise RuntimeError('DATABASE must be valid JSON') from exc

DSN = (
    f"postgresql://{db_config['user']}:{db_config['password']}"
    f"@{db_config['host']}:{db_config['port']}/DatingBotBase"
)

engine = sqlalchemy.create_engine(DSN)
SessionLocal = sessionmaker(bind=engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Получить сессию БД с автоматическим управлением транзакцией.

    Создаёт новую сессию, выполняет commit при успешном завершении
    блока, rollback при ошибке и закрывает сессию в любом случае.

    Yields:
        Session: Активная сессия SQLAlchemy для работы с БД.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Создать все таблицы в базе данных, если они ещё не существуют."""
    Base.metadata.create_all(engine)
