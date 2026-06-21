"""Тесты для модуля bot/ui/formatter.py."""

import pytest
from bot.ui.formatter import format_questionnaire_message, format_favorite_item


class TestFormatQuestionnaireMessage:
    """Тесты для функции format_questionnaire_message."""

    def test_full_questionnaire(self):
        """Полная анкета со всеми полями."""
        questionnaire = {
            'name': 'Иван',
            'surname': 'Иванов',
            'age': 25,
            'user_vk_id': 123456
        }
        result = format_questionnaire_message(questionnaire)
        assert result == "Иван Иванов, 25\nhttps://vk.com/id123456"

    def test_questionnaire_without_surname(self):
        """Анкета без фамилии."""
        questionnaire = {
            'name': 'Мария',
            'age': 30,
            'user_vk_id': 789012
        }
        result = format_questionnaire_message(questionnaire)
        assert result == "Мария, 30\nhttps://vk.com/id789012"

    def test_questionnaire_without_age(self):
        """Анкета без возраста."""
        questionnaire = {
            'name': 'Петр',
            'surname': 'Петров',
            'user_vk_id': 345678
        }
        result = format_questionnaire_message(questionnaire)
        assert result == "Петр Петров\nhttps://vk.com/id345678"

    def test_questionnaire_without_surname_and_age(self):
        """Анкета без фамилии и возраста."""
        questionnaire = {
            'name': 'Анна',
            'user_vk_id': 901234
        }
        result = format_questionnaire_message(questionnaire)
        assert result == "Анна\nhttps://vk.com/id901234"

    def test_questionnaire_with_empty_surname(self):
        """Анкета с пустой строкой в качестве фамилии."""
        questionnaire = {
            'name': 'Сергей',
            'surname': '',
            'age': 28,
            'user_vk_id': 567890
        }
        result = format_questionnaire_message(questionnaire)
        assert result == "Сергей, 28\nhttps://vk.com/id567890"


class TestFormatFavoriteItem:
    """Тесты для функции format_favorite_item."""

    def test_full_favorite_item(self):
        """Полный элемент избранного со всеми полями."""
        result = format_favorite_item('Елена', 'Сидорова', 111222, age=27)
        assert result == "Елена Сидорова, 27 — https://vk.com/id111222"

    def test_favorite_item_without_age(self):
        """Элемент избранного без возраста."""
        result = format_favorite_item('Дмитрий', 'Козлов', 333444)
        assert result == "Дмитрий Козлов — https://vk.com/id333444"

    def test_favorite_item_without_surname(self):
        """Элемент избранного без фамилии (пустая строка)."""
        result = format_favorite_item('Ольга', '', 555666, age=32)
        assert result == "Ольга, 32 — https://vk.com/id555666"

    def test_favorite_item_without_surname_and_age(self):
        """Элемент избранного без фамилии и возраста."""
        result = format_favorite_item('Алексей', '', 777888)
        assert result == "Алексей — https://vk.com/id777888"

    def test_favorite_item_with_none_age(self):
        """Элемент избранного с age=None."""
        result = format_favorite_item('Наталья', 'Волкова', 999000, age=None)
        assert result == "Наталья Волкова — https://vk.com/id999000"