"""Тесты для модуля bot/core/handlers.py."""

import pytest
from unittest.mock import patch, MagicMock

from bot.core.handlers import (
    initial_launch,
    send_help,
    MessageHandler,
)
from bot.core.states import (
    START,
    START_MESSAGING,
    VIEWING_FAVORITE_QUESTIONNAIRE,
    VIEWING_QUESTIONNAIRES,
)
from bot.database.models import Status
from bot.ui.messages import HELP_LINES


class TestInitialLaunch:
    """Тесты для функции initial_launch."""

    @patch('bot.core.handlers.write_message')
    @patch('bot.core.handlers.build_menu_keyboard')
    @patch('bot.core.handlers.send_welcome')
    @patch('bot.core.handlers.get_status_by_user_id')
    def test_sends_welcome_when_status_is_start(
        self, mock_get_status, mock_send_welcome, mock_keyboard, mock_write
    ):
        """Отправляет приветствие, если статус равен START."""
        mock_status = MagicMock(spec=Status)
        mock_status.step = START
        mock_get_status.return_value = mock_status
        mock_keyboard.return_value = 'keyboard_json'
        
        initial_launch(12345)
        
        mock_send_welcome.assert_called_once_with(12345)
        mock_keyboard.assert_called_once_with(
            ['🎬 Начать', '🆘 Помощь', '🆒 Избранное'], 
            one_time=True
        )
        assert mock_write.call_count == 1

    @patch('bot.core.handlers.write_message')
    @patch('bot.core.handlers.send_welcome')
    @patch('bot.core.handlers.get_status_by_user_id')
    def test_does_nothing_when_status_not_start(self, mock_get_status, mock_send_welcome, mock_write):
        """Не отправляет ничего, если статус не равен START."""
        mock_status = MagicMock(spec=Status)
        mock_status.step = START_MESSAGING
        mock_get_status.return_value = mock_status
        
        initial_launch(12345)
        
        mock_send_welcome.assert_not_called()
        mock_write.assert_not_called()

    @patch('bot.core.handlers.write_message')
    @patch('bot.core.handlers.send_welcome')
    @patch('bot.core.handlers.get_status_by_user_id')
    def test_does_nothing_when_status_is_none(self, mock_get_status, mock_send_welcome, mock_write):
        """Не отправляет ничего, если статус не найден."""
        mock_get_status.return_value = None
        
        initial_launch(12345)
        
        mock_send_welcome.assert_not_called()
        mock_write.assert_not_called()


class TestSendHelp:
    """Тесты для функции send_help."""

    @patch('bot.core.handlers.write_message')
    @patch('bot.core.handlers.build_menu_keyboard')
    def test_sends_all_help_lines(self, mock_keyboard, mock_write):
        """Отправляет все строки помощи."""
        mock_keyboard.return_value = 'keyboard_json'
        
        send_help(12345)
        
        # Должно быть вызовов: len(HELP_LINES) + 1 (финальное сообщение)
        assert mock_write.call_count == len(HELP_LINES) + 1
        
        # Проверяем, что все строки HELP_LINES были отправлены
        for i, line in enumerate(HELP_LINES):
            mock_write.assert_any_call(12345, line)
        
        # Проверяем финальное сообщение
        mock_write.assert_any_call(12345, 'Выберите действие:', keyboard='keyboard_json')

    @patch('bot.core.handlers.write_message')
    @patch('bot.core.handlers.build_menu_keyboard')
    def test_builds_keyboard_with_correct_buttons(self, mock_keyboard, mock_write):
        """Создает клавиатуру с правильными кнопками."""
        mock_keyboard.return_value = 'keyboard_json'
        
        send_help(12345)
        
        mock_keyboard.assert_called_once_with(
            ['🟢 Главное меню', '🆒 Избранное'], 
            one_time=True
        )


class TestMessageHandler:
    """Тесты для класса MessageHandler."""

    @patch('bot.core.handlers.send_help')
    @patch('bot.core.handlers.write_message')
    def test_handle_help(self, mock_write, mock_send_help):
        """Метод handle_help отправляет помощь."""
        handler = MessageHandler()
        mock_status = MagicMock(spec=Status)
        
        handler.handle_help(12345, mock_status)
        
        mock_write.assert_called_once_with(12345, 'Всегда рад помочь!')
        mock_send_help.assert_called_once_with(12345)

    @patch('bot.core.handlers.start_favorite_flow')
    def test_handle_favorites(self, mock_start_favorites):
        """Метод handle_favorites запускает поток избранного."""
        handler = MessageHandler()
        mock_status = MagicMock(spec=Status)
        
        handler.handle_favorites(12345, mock_status)
        
        mock_start_favorites.assert_called_once_with(12345)

    @patch('bot.core.handlers.write_message')
    @patch('bot.core.handlers.build_menu_keyboard')
    @patch('bot.core.handlers.update_status_step')
    def test_handle_main_menu_from_viewing_favorites(
        self, mock_update_step, mock_keyboard, mock_write
    ):
        """Метод handle_main_menu показывает правильные кнопки при просмотре избранного."""
        handler = MessageHandler()
        mock_status = MagicMock(spec=Status)
        mock_status.step = VIEWING_FAVORITE_QUESTIONNAIRE
        mock_keyboard.return_value = 'keyboard_json'
        mock_update_step.return_value = mock_status
        
        handler.handle_main_menu(12345, mock_status)
        
        mock_keyboard.assert_called_once_with(
            ['👀 Продолжить просмотр', '🆘 Помощь', '🪪 К просмотру кандидатов'],
            one_time=True
        )
        mock_write.assert_called_once_with(12345, 'Что вы хотите?', keyboard='keyboard_json')
        mock_update_step.assert_called_once_with(mock_status, START)

    @patch('bot.core.handlers.write_message')
    @patch('bot.core.handlers.build_menu_keyboard')
    @patch('bot.core.handlers.update_status_step')
    def test_handle_main_menu_from_other_state(
        self, mock_update_step, mock_keyboard, mock_write
    ):
        """Метод handle_main_menu показывает правильные кнопки из других состояний."""
        handler = MessageHandler()
        mock_status = MagicMock(spec=Status)
        mock_status.step = START_MESSAGING
        mock_keyboard.return_value = 'keyboard_json'
        mock_update_step.return_value = mock_status
        
        handler.handle_main_menu(12345, mock_status)
        
        mock_keyboard.assert_called_once_with(
            ['🔎 Новый поиск', '🆘 Помощь', '🆒 Избранное'],
            one_time=True
        )
        mock_update_step.assert_called_once_with(mock_status, START)

    @patch('bot.core.handlers.start_preference_flow')
    @patch('bot.core.handlers.update_status_step')
    def test_handle_new_search(self, mock_update_step, mock_start_preference):
        """Метод handle_new_search запускает поток предпочтений."""
        handler = MessageHandler()
        mock_status = MagicMock(spec=Status)
        mock_update_step.return_value = mock_status
        
        handler.handle_new_search(12345, mock_status)
        
        mock_update_step.assert_called_once_with(mock_status, START_MESSAGING)
        mock_start_preference.assert_called_once_with(12345)

    @patch('bot.core.handlers.start_preference_flow')
    @patch('bot.core.handlers.update_status_step')
    def test_handle_start(self, mock_update_step, mock_start_preference):
        """Метод handle_start запускает поток предпочтений."""
        handler = MessageHandler()
        mock_status = MagicMock(spec=Status)
        mock_update_step.return_value = mock_status
        
        handler.handle_start(12345, mock_status)
        
        mock_update_step.assert_called_once_with(mock_status, START_MESSAGING)
        mock_start_preference.assert_called_once_with(12345)

    @patch('bot.core.handlers.write_message')
    def test_handle_returns_true_for_known_button(self, mock_write):
        """Метод handle возвращает True для известной кнопки."""
        handler = MessageHandler()
        mock_status = MagicMock(spec=Status)
        
        result = handler.handle(12345, '🆘 Помощь', mock_status)
        
        assert result is True
        # Проверяем, что handle_help был вызван (через write_message)
        mock_write.assert_any_call(12345, 'Всегда рад помочь!')

    @patch('bot.core.handlers.write_message')
    @patch('bot.core.handlers.send_help')
    @patch('bot.core.handlers.start_favorite_flow')
    @patch('bot.core.handlers.build_menu_keyboard')
    @patch('bot.core.handlers.update_status_step')
    @patch('bot.core.handlers.start_preference_flow')
    def test_handle_dispatches_to_correct_handler(
        self, mock_start_pref, mock_update_step, mock_keyboard, 
        mock_start_fav, mock_send_help, mock_write
    ):
        """Метод handle диспетчеризует к правильному обработчику."""
        handler = MessageHandler()
        mock_status = MagicMock(spec=Status)
        mock_status.step = START_MESSAGING
        mock_keyboard.return_value = 'keyboard_json'
        mock_update_step.return_value = mock_status
        
        test_cases = [
            ('🆘 Помощь', mock_send_help),
            ('🆒 Избранное', mock_start_fav),
            ('🟢 Главное меню', mock_write),
            ('🔎 Новый поиск', mock_start_pref),
            ('🎬 Начать', mock_start_pref),
        ]
        
        for button_text, mock_func in test_cases:
            # Сбрасываем счетчики вызовов
            mock_send_help.reset_mock()
            mock_start_fav.reset_mock()
            mock_write.reset_mock()
            mock_start_pref.reset_mock()
            
            handler.handle(12345, button_text, mock_status)
            
            # Проверяем, что соответствующая функция была вызвана
            assert mock_func.called, f"Функция для кнопки '{button_text}' не была вызвана"

    def test_handle_returns_false_for_unknown_button(self):
        """Метод handle возвращает False для неизвестной кнопки."""
        handler = MessageHandler()
        mock_status = MagicMock(spec=Status)
        
        result = handler.handle(12345, 'Неизвестная кнопка', mock_status)
        
        assert result is False