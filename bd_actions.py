from typing import Any, Dict, Optional
from DatingBotBase import session
from actions import get_random_id, menu_buttons, write_message
from models import Favorite, Status
from sqlalchemy import select

from vk_actions import three_best_photos, vk


def get_favorite_questionnaire(user_vk):
    """Формирует анкету с данными и отправляет её в чат"""
    user_favorite = session.query(Favorite).filter(Favorite.favorite_user_vk_id == user_vk).all()
    if not user_favorite:
        write_message(user_vk, "Извините, вы еще никого не добавили в избранное!")

    write_message(user_vk, "=== Тут будет логика на показ фаворитов ===")
    return

def get_search_criteria(session, user_vk_id: int) -> Optional[Dict[str, Any]]:
    """ Получение критериев поиска из БД """
    search_criteria = select(Status.search_criteria).where(Status.user_vk_id == user_vk_id)

    criteria = session.scalar(search_criteria)
    
    return criteria

def send_next_questionnaire(session, user_vk: int, user_status) -> bool:
    """
    Отправляет следующую анкету из списка.
    
    Args:
        session: SQLAlchemy сессия
        user_vk: ID пользователя ВКонтакте
        user_status: Объект Status из БД
        
    Returns:
        True - если анкета найдена и отправлена
        False - если анкет больше нет
    """
    ids_list = user_status.list_applicants or []
    
    if not ids_list:
        return False
    
    # Ищем анкету с 3+ фотографиями
    while ids_list:
        questionnaire_vk_id = ids_list.pop()
        questionnaire_info = three_best_photos(questionnaire_vk_id)
        
        if questionnaire_info:
            questionnaire = questionnaire_info[questionnaire_vk_id]
            
            # Формируем attachments
            attachments = ",".join(
                f"photo{owner_id}_{photo_id}" 
                for owner_id, photo_id, likes in questionnaire['photos']
            )
            
            # Формируем текст сообщения
            message_text = (
                f"{questionnaire['name']} {questionnaire['surname']}\n"
                f"https://vk.com/id{questionnaire['user_vk_id']}"
            )
            
            # Отправляем сообщение
            vk.method(
                'messages.send', # type: ignore
                {
                    'user_id': user_vk,
                    'message': message_text,
                    'attachment': attachments,
                    'random_id': get_random_id()
                }
            )
            
            # Показываем меню навигации (one_time=False, чтобы кнопки оставались)
            menu_buttons(
                user_vk, 
                'Анкета из поиска:', 
                '🟢 Главное меню', 
                '⏩ Далее', 
                '🆒 Избранное', 
                one_time=False
            )
            
            # Сохраняем обновлённый список в БД
            user_status.list_applicants = ids_list
            session.commit()
            
            return True
    
    # Если дошли сюда, значит анкет с 3 фото не осталось
    user_status.list_applicants = None
    session.commit()
    return False