"""Репозиторий для операций с избранным."""

from typing import Optional
from datetime import datetime
from bot.database.models import Favorite
from bot.database.session import session


def get_favorites_by_user(user_id: int) -> list[Favorite]:
    return session.query(Favorite).filter(Favorite.user_vk_id == user_id).all()


def get_favorite(user_id: int, favorite_vk_id: int) -> Optional[Favorite]:
    return session.query(Favorite).filter(
        Favorite.user_vk_id == user_id,
        Favorite.favorite_user_vk_id == favorite_vk_id
    ).first()


def add_favorite(user_id: int, favorite_vk_id: int, name: str, surname: str,
                 gender: str, photos: Optional[dict] = None) -> Favorite:
    favorite = Favorite(
        user_vk_id=user_id,
        favorite_user_vk_id=favorite_vk_id,
        name=name,
        surname=surname,
        gender=gender,
        photos=photos,
        datetime_update=datetime.now()
    )
    session.add(favorite)
    session.commit()
    return favorite


def remove_favorite(user_id: int, favorite_vk_id: int) -> bool:
    favorite = get_favorite(user_id, favorite_vk_id)
    if not favorite:
        return False
    session.delete(favorite)
    session.commit()
    return True
