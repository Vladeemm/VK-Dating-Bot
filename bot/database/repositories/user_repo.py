"""Репозиторий для операций с пользователями."""

from typing import Optional
from bot.database.models import Users
from bot.database.session import session


def get_user_by_id(user_id: int) -> Optional[Users]:
    return session.query(Users).filter(Users.id == user_id).first()


def create_user(user_id: int, name: str) -> Users:
    user = Users(id=user_id, name=name)
    session.add(user)
    session.commit()
    return user


def ensure_user(user_id: int, name: str) -> Users:
    user = get_user_by_id(user_id)
    if user:
        return user
    return create_user(user_id, name)
