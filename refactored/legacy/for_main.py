import random

from statuses import VIEWING_QUESTIONNAIRES
from vk_actions import get_questionnaires_by_criteria, three_best_photos

# ----- просто что бы в этом файле не было красноты
# На самом деле эти данные дергаются из БД
user_vk_id = 2846903
city_id = 60
age_from = 31
age_to = 32
gender = 1
# ---------------

# Это строка мне нужна только в этом файле что бы красных строчек ошибок не было
user_status = VIEWING_QUESTIONNIARES

if user_status == VIEWING_QUESTIONNAIRES:
    # Начало просмотра анкет по выбранному поиску
    # Собираем 1000 id
    ids_list = get_questionnaires_by_criteria(city_id, gender, age_from, age_to)

    # Проверяем что у нас есть какие то анкеты после запроса. Если нет то нужно написать, что к сожалению по вашему запросу анкет не нашлось, измените критерии поиска
    if not ids_list:
        pass
    
    # Для совсем упоротых пользователей перемешиваем id, что бы они с каждым одинаковым запросом выводили в разном порядке анкеты
    random.shuffle(ids_list)
    
    # В цикле находим анкету из списка с 3-мя фотографиями
    while ids_list:
    # Берем анкету из списка
        if ids_list:
            questionnaire_vk_id = ids_list.pop()
            questionnaire_info = three_best_photos(questionnaire_vk_id)
            # Находим анкету с 3-мя фотками и выходим из цикла
            if questionnaire_info:
                break
        else:
            # В списке с id не нашли анкет с 3-мя фотками и пишем Юзеру, сорян измени критерии
            pass

    # Показываем анкету. Здесь логика показа какая та. Типа:
    def show_questionnaire(questionnaire_info):
        pass

    # Также обрабатываем кнопку Дальше, в этом же user_status
    if message == 'Дальше':

        # В цикле находим анкету из списка с 3-мя фотографиями
        while ids_list:
        # Берем анкету из списка
            if ids_list:
                questionnaire_vk_id = ids_list.pop()
                questionnaire_info = three_best_photos(questionnaire_vk_id)
                # Находим анкету с 3-мя фотками и выходим из цикла
                if questionnaire_info:
                    break
            else:
                # В списке с id не нашли анкет с 3-мя фотками и пишем Юзеру, сорян измени критерии
                pass

        # Показываем анкету. Здесь логика показа какая та. Типа:
        def show_questionnaire(questionnaire_info):
            pass

    # Формируем кнопки и показ анкеты.