"""Тесты для модуля bot/user/service.py."""

import pytest
from unittest.mock import patch, MagicMock

from bot.user.service import add_user_to_db, send_welcome


class TestAddUserToDb:
    """Тесты для функции add_user_to_db."""

    @patch('bot.user.service.create_status')
    @patch('bot.user.service.get_status_by_user_id')
    @patch('bot.user.service.ensure_user')
    @patch('bot.user.service.get_user_info_from_vk')
    def test_creates_user_when_not_exists(self, mock_get_user_info, mock_ensure_user, 
                                          mock_get_status, mock_create_status):
        """Создает пользователя, если его нет в БД."""
        mock_get_user_info.return_value = (12345, 'Иван')
        mock_get_status.return_value = None
        
        add_user_to_db(12345)
        
        mock_get_user_info.assert_called_once_with(12345)
        mock_ensure_user.assert_called_once_with(12345, 'Иван')
        mock_get_status.assert_called_once_with(12345)
        mock_create_status.assert_called_once_with(12345, 'start')

    @patch('bot.user.service.create_status')
    @patch('bot.user.service.get_status_by_user_id')
    @patch('bot.user.service.ensure_user')
    @patch('bot.user.service.get_user_info_from_vk')
    def test_does_not_create_status_if_exists(self, mock_get_user_info, mock_ensure_user,
                                               mock_get_status, mock_create_status):
        """Не создает статус, если он уже существует."""
        mock_get_user_info.return_value = (12345, 'Иван')
        mock_get_status.return_value = MagicMock()  # Статус уже есть
        
        add_user_to_db(12345)
        
        mock_create_status.assert_not_called()

    @patch('bot.user.service.create_status')
    @patch('bot.user.service.get_status_by_user_id')
    @patch('bot.user.service.ensure_user')
    @patch('bot.user.service.get_user_info_from_vk')
    def test_uses_vk_id_as_name_when_no_name(self, mock_get_user_info, mock_ensure_user,
                                              mock_get_status, mock_create_status):
        """Использует VK ID как имя, если имя не получено."""
        mock_get_user_info.return_value = (12345,)  # Только ID, без имени
        mock_get_status.return_value = None
        
        add_user_to_db(12345)
        
        mock_ensure_user.assert_called_once_with(12345, '12345')

    @patch('bot.user.service.create_status')
    @patch('bot.user.service.get_status_by_user_id')
    @patch('bot.user.service.ensure_user')
    @patch('bot.user.service.get_user_info_from_vk')
    def test_uses_full_name(self, mock_get_user_info, mock_ensure_user,
                            mock_get_status, mock_create_status):
        """Использует полное имя из VK."""
        mock_get_user_info.return_value = (12345, 'Иван Иванов')
        mock_get_status.return_value = None
        
        add_user_to_db(12345)
        
        mock_ensure_user.assert_called_once_with(12345, 'Иван Иванов')


class TestSendWelcome:
    """Тесты для функции send_welcome."""

    @patch('bot.user.service.write_message')
    def test_sends_welcome_message(self, mock_write_message):
        """Отправляет приветственное сообщение."""
        from bot.ui.messages import WELCOME_TEXT
        
        send_welcome(12345)
        
        mock_write_message.assert_called_once_with(12345, WELCOME_TEXT)