*Описание функций, методов класса(если будут), их названия. Что принимают на вход, что на выходе*

**Методы для работы с базой:**

1. create_user(user_vk_id, name, city) -> bool:

2. create_favorite_questionnaire(user_vk_id, favorite_vk_id, name, surname, city, age, photos) -> bool:

    *Внутри метода, также с помощью datetime добавляются данные datetime_update*

3. update_status(user_vk_id, step, **kwargs) -> bool:

    *Через **kwargs, в зависимости от действия User добавляется именованный аргумент в поле search_criteria*

    *Внутри метода, с помощью datetime добавляем step_datetime*

4. get_status(user_vk_id) -> str:

5. get_favorite_questionnaire(user_vk_id, favorite_vk_id) -> list[name, surname, age, city, photos, favorite_link]: 

    *В методе также формируется ссылка на вк страницу, с помощью favorite_vk_id*

    **ВАЖНО! Можем собирать не список, а словарь**

6. get_favorites_list(user_vk_id) -> list[of favorites_vk_ids]:

7. get_search_criteria(user_vk_id) -> dict[search_criteria]:

8. delete_favorite_questionnaire(favorite_vk_id) -> bool:

**Работа с VK API:**

1.  add_user_to_db(user_vk_id) -> None:

2. get_questionnaires_by_criteria(age_from, age_to, city, gender) -> list[dicts by vk_ids]:
    *Получаем JSON, преобразовываем, фильтруем что бы аккаунты были открыты.
    Через fields=counters пытаемся также фильтровать людей с фото больше 3**

3. get_questionnaire_photos(questionnaire_vk_id) -> dict[photos]:

4. update_questionnaire_info(questionnaire_vk_id) -> bool: