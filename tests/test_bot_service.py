"""Тесты для модуля bot/bot_service.py."""

import pytest
from unittest.mock import patch, MagicMock

from bot.bot_service import write_message


class TestWriteMessage:
    """Тесты для функции write_message."""

    @patch('bot.bot_service.randrange')
    @patch('bot.bot_service.vk_group_api')
    def test_sends_basic_message(self, mock_vk_api, mock_randrange):
        """Отправляет базовое сообщение без вложений и клавиатуры."""
        mock_randrange.return_value = 1234567
        
        write_message(12345, 'Привет!')
        
        mock_vk_api.messages.send.assert_called_once_with(
            user_id=12345,
            message='Привет!',
            random_id=1234567
        )

    @patch('bot.bot_service.randrange')
    @patch('bot.bot_service.vk_group_api')
    def test_sends_message_with_attachments(self, mock_vk_api, mock_randrange):
        """Отправляет сообщение с вложениями."""
        mock_randrange.return_value = 7654321
        
        write_message(12345, 'Фото', attachments='photo123_456')
        
        mock_vk_api.messages.send.assert_called_once_with(
            user_id=12345,
            message='Фото',
            random_id=7654321,
            attachment='photo123_456'
        )

    @patch('bot.bot_service.randrange')
    @patch('bot.bot_service.vk_group_api')
    def test_sends_message_with_keyboard(self, mock_vk_api, mock_randrange):
        """Отправляет сообщение с клавиатурой."""
        mock_randrange.return_value = 9876543
        
        write_message(12345, 'Выберите:', keyboard='{"buttons": []}')
        
        mock_vk_api.messages.send.assert_called_once_with(
            user_id=12345,
            message='Выберите:',
            random_id=9876543,
            keyboard='{"buttons": []}'
        )

    @patch('bot.bot_service.randrange')
    @patch('bot.bot_service.vk_group_api')
    def test_sends_message_with_attachments_and_keyboard(self, mock_vk_api, mock_randrange):
        """Отправляет сообщение с вложениями и клавиатурой."""
        mock_randrange.return_value = 1111111
        
        write_message(
            12345, 
            'Полное сообщение', 
            attachments='photo123_456',
            keyboard='{"buttons": []}'
        )
        
        mock_vk_api.messages.send.assert_called_once_with(
            user_id=12345,
            message='Полное сообщение',
            random_id=1111111,
            attachment='photo123_456',
            keyboard='{"buttons": []}'
        )

    @patch('bot.bot_service.randrange')
    @patch('bot.bot_service.vk_group_api')
    def test_generates_random_id(self, mock_vk_api, mock_randrange):
        """Генерирует случайный random_id."""
        mock_randrange.return_value = 9999999
        
        write_message(12345, 'Тест')
        
        mock_randrange.assert_called_once_with(10 ** 7)
        call_args = mock_vk_api.messages.send.call_args
        assert call_args[1]['random_id'] == 9999999

    @patch('bot.bot_service.randrange')
    @patch('bot.bot_service.vk_group_api')
    def test_does_not_include_attachments_when_none(self, mock_vk_api, mock_randrange):
        """Не включает attachment, если он None."""
        mock_randrange.return_value = 1234567
        
        write_message(12345, 'Тест', attachments=None)
        
        call_args = mock_vk_api.messages.send.call_args
        assert 'attachment' not in call_args[1]

    @patch('bot.bot_service.randrange')
    @patch('bot.bot_service.vk_group_api')
    def test_does_not_include_keyboard_when_none(self, mock_vk_api, mock_randrange):
        """Не включает keyboard, если он None."""
        mock_randrange.return_value = 1234567
        
        write_message(12345, 'Тест', keyboard=None)
        
        call_args = mock_vk_api.messages.send.call_args
        assert 'keyboard' not in call_args[1]

    @patch('bot.bot_service.randrange')
    @patch('bot.bot_service.vk_group_api')
    def test_handles_empty_string_attachments(self, mock_vk_api, mock_randrange):
        """Не включает attachment, если он пустая строка."""
        mock_randrange.return_value = 1234567
        
        write_message(12345, 'Тест', attachments='')
        
        call_args = mock_vk_api.messages.send.call_args
        assert 'attachment' not in call_args[1]

    @patch('bot.bot_service.randrange')
    @patch('bot.bot_service.vk_group_api')
    def test_handles_empty_string_keyboard(self, mock_vk_api, mock_randrange):
        """Не включает keyboard, если он пустая строка."""
        mock_randrange.return_value = 1234567
        
        write_message(12345, 'Тест', keyboard='')
        
        call_args = mock_vk_api.messages.send.call_args
        assert 'keyboard' not in call_args[1]

    @patch('bot.bot_service.randrange')
    @patch('bot.bot_service.vk_group_api')
    def test_passes_correct_user_id(self, mock_vk_api, mock_randrange):
        """Передает правильный user_id."""
        mock_randrange.return_value = 1234567
        
        write_message(987654, 'Тест')
        
        call_args = mock_vk_api.messages.send.call_args
        assert call_args[1]['user_id'] == 987654

    @patch('bot.bot_service.randrange')
    @patch('bot.bot_service.vk_group_api')
    def test_passes_correct_message(self, mock_vk_api, mock_randrange):
        """Передает правильное сообщение."""
        mock_randrange.return_value = 1234567
        
        write_message(12345, 'Длинное сообщение с эмодзи 🎉')
        
        call_args = mock_vk_api.messages.send.call_args
        assert call_args[1]['message'] == 'Длинное сообщение с эмодзи 🎉'