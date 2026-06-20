"""Репозиторий для операций с пользователями."""

from typing import Optional

from ..models import Users
from ..session import get_session


def get_user_by_id(user_id: int) -> Optional[Users]:
    with get_session() as session:
        return session.query(Users).filter(Users.id == user_id).first()


def create_user(user_id: int, name: str) -> Users:
    with get_session() as session:
        user = Users(id=user_id, name=name)
        session.add(user)
        return user


def ensure_user(user_id: int, name: str) -> Users:
    with get_session() as session:
        user = session.query(Users).filter(Users.id == user_id).first()
        if user:
            return user
        user = Users(id=user_id, name=name)
        session.add(user)
        return user
