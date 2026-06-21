"""Тесты для модуля bot/vk_api/search.py."""

import pytest
from unittest.mock import patch, MagicMock

from bot.vk_api.search import get_questionnaires_by_criteria


class TestGetQuestionnairesByCriteria:
    """Тесты для функции get_questionnaires_by_criteria."""

    @patch('bot.vk_api.search.time.sleep')
    @patch('bot.vk_api.search.vk')
    def test_returns_filtered_ids(self, mock_vk, mock_sleep):
        """Возвращает ID только открытых профилей с фото."""
        mock_vk.users.search.return_value = {
            'items': [
                {'id': 1, 'is_closed': False, 'has_photo': 1},  # Включить
                {'id': 2, 'is_closed': True, 'has_photo': 1},   # Закрыт
                {'id': 3, 'is_closed': False, 'has_photo': 0},  # Нет фото
                {'id': 4, 'is_closed': False, 'has_photo': 1},  # Включить
                {'id': 5, 'is_closed': True, 'has_photo': 0},   # Закрыт и нет фото
            ]
        }
        
        result = get_questionnaires_by_criteria(1, 2, 18, 30)
        
        assert result == [1, 4]
        mock_vk.users.search.assert_called_once_with(
            city=1,
            sex=2,
            age_from=18,
            age_to=30,
            fields='is_closed,has_photo',
            count=100
        )

    @patch('bot.vk_api.search.time.sleep')
    @patch('bot.vk_api.search.vk')
    def test_returns_empty_list_when_no_items(self, mock_vk, mock_sleep):
        """Возвращает пустой список, если API вернул пустой результат."""
        mock_vk.users.search.return_value = {'items': []}
        
        result = get_questionnaires_by_criteria(1, 2, 18, 30)
        
        assert result == []

    @patch('bot.vk_api.search.time.sleep')
    @patch('bot.vk_api.search.vk')
    def test_returns_empty_list_when_no_matching_profiles(self, mock_vk, mock_sleep):
        """Возвращает пустой список, если нет подходящих профилей."""
        mock_vk.users.search.return_value = {
            'items': [
                {'id': 1, 'is_closed': True, 'has_photo': 1},
                {'id': 2, 'is_closed': False, 'has_photo': 0},
            ]
        }
        
        result = get_questionnaires_by_criteria(1, 2, 18, 30)
        
        assert result == []

    @patch('bot.vk_api.search.time.sleep')
    @patch('bot.vk_api.search.vk')
    def test_handles_missing_fields(self, mock_vk, mock_sleep):
        """Обрабатывает отсутствие полей is_closed и has_photo."""
        mock_vk.users.search.return_value = {
            'items': [
                {'id': 1},  # Нет is_closed и has_photo
                {'id': 2, 'is_closed': False, 'has_photo': 1},
            ]
        }
        
        result = get_questionnaires_by_criteria(1, 2, 18, 30)
        
        # Первый профиль должен быть исключен (is_closed по умолчанию True, has_photo по умолчанию 0)
        assert result == [2]

    @patch('bot.vk_api.search.time.sleep')
    @patch('bot.vk_api.search.vk')
    def test_calls_sleep(self, mock_vk, mock_sleep):
        """Вызывает sleep после запроса к API."""
        mock_vk.users.search.return_value = {'items': []}
        
        get_questionnaires_by_criteria(1, 2, 18, 30)
        
        mock_sleep.assert_called_once_with(0.35)

    @patch('bot.vk_api.search.time.sleep')
    @patch('bot.vk_api.search.vk')
    def test_returns_all_matching_ids(self, mock_vk, mock_sleep):
        """Возвращает все подходящие ID при большом количестве результатов."""
        items = [
            {'id': i, 'is_closed': False, 'has_photo': 1}
            for i in range(1, 101)
        ]
        mock_vk.users.search.return_value = {'items': items}
        
        result = get_questionnaires_by_criteria(1, 2, 18, 30)
        
        assert len(result) == 100
        assert result == list(range(1, 101))

    @patch('bot.vk_api.search.time.sleep')
    @patch('bot.vk_api.search.vk')
    def test_correct_parameters_passed(self, mock_vk, mock_sleep):
        """Передаёт правильные параметры в VK API."""
        mock_vk.users.search.return_value = {'items': []}
        
        get_questionnaires_by_criteria(
            city_id=123,
            gender=1,
            age_from=25,
            age_to=35
        )
        
        mock_vk.users.search.assert_called_once_with(
            city=123,
            sex=1,
            age_from=25,
            age_to=35,
            fields='is_closed,has_photo',
            count=100
        )