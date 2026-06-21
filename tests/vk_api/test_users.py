"""Тесты для модуля bot/vk_api/users.py."""

import pytest
from unittest.mock import patch, MagicMock

from bot.vk_api.users import get_user_info_from_vk, get_city_id


class TestGetUserInfoFromVk:
    """Тесты для функции get_user_info_from_vk."""

    @patch('bot.vk_api.users.time.sleep')
    @patch('bot.vk_api.users.vk')
    def test_returns_user_info_when_success(self, mock_vk, mock_sleep):
        """Возвращает список [user_vk_id, first_name] при успешном запросе."""
        mock_vk.users.get.return_value = [{'first_name': 'Иван'}]
        
        result = get_user_info_from_vk(12345)
        
        assert result == [12345, 'Иван']
        mock_vk.users.get.assert_called_once_with(user_ids=12345)

    @patch('bot.vk_api.users.time.sleep')
    @patch('bot.vk_api.users.vk')
    def test_returns_none_when_empty_response(self, mock_vk, mock_sleep):
        """Возвращает None, если API вернул пустой ответ."""
        mock_vk.users.get.return_value = []
        
        result = get_user_info_from_vk(12345)
        
        assert result is None

    @patch('bot.vk_api.users.time.sleep')
    @patch('bot.vk_api.users.vk')
    def test_returns_none_when_no_first_name(self, mock_vk, mock_sleep):
        """Возвращает None, если first_name отсутствует."""
        mock_vk.users.get.return_value = [{'first_name': ''}]
        
        result = get_user_info_from_vk(12345)
        
        assert result is None

    @patch('bot.vk_api.users.time.sleep')
    @patch('bot.vk_api.users.vk')
    def test_returns_none_when_first_name_missing(self, mock_vk, mock_sleep):
        """Возвращает None, если ключ first_name отсутствует в ответе."""
        mock_vk.users.get.return_value = [{}]
        
        result = get_user_info_from_vk(12345)
        
        assert result is None

    @patch('bot.vk_api.users.time.sleep')
    @patch('bot.vk_api.users.vk')
    def test_calls_sleep(self, mock_vk, mock_sleep):
        """Вызывает sleep после запроса к API."""
        mock_vk.users.get.return_value = [{'first_name': 'Иван'}]
        
        get_user_info_from_vk(12345)
        
        mock_sleep.assert_called_once_with(0.35)


class TestGetCityId:
    """Тесты для функции get_city_id."""

    @patch('bot.vk_api.users.time.sleep')
    @patch('bot.vk_api.users.vk')
    def test_returns_city_id_when_found(self, mock_vk, mock_sleep):
        """Возвращает ID города, если он найден."""
        mock_vk.database.getCities.return_value = {
            'items': [{'id': 123, 'title': 'Москва'}]
        }
        
        result = get_city_id('Москва')
        
        assert result == 123
        mock_vk.database.getCities.assert_called_once_with(q='Москва')

    @patch('bot.vk_api.users.time.sleep')
    @patch('bot.vk_api.users.vk')
    def test_returns_first_city_id_when_multiple_found(self, mock_vk, mock_sleep):
        """Возвращает ID первого города, если найдено несколько."""
        mock_vk.database.getCities.return_value = {
            'items': [
                {'id': 123, 'title': 'Москва'},
                {'id': 456, 'title': 'Московский'}
            ]
        }
        
        result = get_city_id('Москва')
        
        assert result == 123

    @patch('bot.vk_api.users.time.sleep')
    @patch('bot.vk_api.users.vk')
    def test_returns_none_when_city_not_found(self, mock_vk, mock_sleep):
        """Возвращает None, если город не найден."""
        mock_vk.database.getCities.return_value = {'items': []}
        
        result = get_city_id('НесуществующийГород')
        
        assert result is None

    @patch('bot.vk_api.users.time.sleep')
    @patch('bot.vk_api.users.vk')
    def test_returns_none_when_items_missing(self, mock_vk, mock_sleep):
        """Возвращает None, если ключ items отсутствует в ответе."""
        mock_vk.database.getCities.return_value = {}
        
        result = get_city_id('Москва')
        
        assert result is None

    @patch('bot.vk_api.users.time.sleep')
    @patch('bot.vk_api.users.vk')
    def test_calls_sleep(self, mock_vk, mock_sleep):
        """Вызывает sleep после запроса к API."""
        mock_vk.database.getCities.return_value = {'items': []}
        
        get_city_id('Москва')
        
        mock_sleep.assert_called_once_with(0.35)

    @patch('bot.vk_api.users.time.sleep')
    @patch('bot.vk_api.users.vk')
    def test_passes_city_name_correctly(self, mock_vk, mock_sleep):
        """Передаёт название города в правильном формате."""
        mock_vk.database.getCities.return_value = {'items': []}
        
        get_city_id('Санкт-Петербург')
        
        mock_vk.database.getCities.assert_called_once_with(q='Санкт-Петербург')