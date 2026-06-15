"""Форматирование текстов и анкет для сообщений."""

from typing import Dict, Optional


def format_questionnaire_message(questionnaire: Dict) -> str:
    full_name = f"{questionnaire['name']} {questionnaire.get('surname', '')}".strip()
    age = questionnaire.get('age')
    name_and_age = f"{full_name}, {age}" if age is not None else full_name

    return (
        f"{name_and_age}\n"
        f"https://vk.com/id{questionnaire['user_vk_id']}"
    )


def format_favorite_item(name: str, surname: str, vk_id: int, age: Optional[int] = None) -> str:
    full_name = f"{name} {surname}".strip()
    age_suffix = f", {age}" if age is not None else ""
    return f"{full_name}{age_suffix} — https://vk.com/id{vk_id}"
