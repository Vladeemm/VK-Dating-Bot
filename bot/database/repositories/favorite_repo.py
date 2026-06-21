"""Репозиторий для операций с избранным."""

from datetime import datetime
from typing import Optional

from ..models import Favorite
from ..session import get_session


def get_favorites_by_user(user_id: int) -> list[Favorite]:
    with get_session() as session:
        return session.query(Favorite).filter(Favorite.user_vk_id == user_id).all()


def get_favorite(user_id: int, favorite_vk_id: int) -> Optional[Favorite]:
    with get_session() as session:
        return session.query(Favorite).filter(
            Favorite.user_vk_id == user_id,
            Favorite.favorite_user_vk_id == favorite_vk_id,
        ).first()


def add_favorite(
    user_id: int,
    favorite_vk_id: int,
    name: str,
    surname: str,
    gender: str,
    photos: Optional[dict] = None,
) -> Favorite:
    with get_session() as session:
        favorite = Favorite(
            user_vk_id=user_id,
            favorite_user_vk_id=favorite_vk_id,
            name=name,
            surname=surname,
            gender=gender,
            photos=photos,
            datetime_update=datetime.now(),
        )
        session.add(favorite)
        return favorite


def remove_favorite(user_id: int, favorite_vk_id: int) -> bool:
    with get_session() as session:
        favorite = session.query(Favorite).filter(
            Favorite.user_vk_id == user_id,
            Favorite.favorite_user_vk_id == favorite_vk_id,
        ).first()
        if not favorite:
            return False
        session.delete(favorite)
        return True
