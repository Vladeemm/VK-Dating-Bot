from DatingBotBase import session
from actions import write_message
from models import Favorite


def get_favorite_questionnaire(user_vk):
    """Формирует анкету с данными и отправляет её в чат"""
    user_favorite = session.query(Favorite).filter(Favorite.favorite_user_vk_id == user_vk).all()
    if not user_favorite:
        write_message(user_vk, "Извините, вы еще никого не добавили в избранное!")

    write_message(user_vk, "=== Тут будет логика на показ фаворитов ===")
    return