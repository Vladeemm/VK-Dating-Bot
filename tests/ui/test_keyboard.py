"""Тесты для модуля bot/ui/keyboard.py."""

import json
import pytest
from bot.ui.keyboard import build_menu_keyboard


class TestBuildMenuKeyboard:
    """Тесты для функции build_menu_keyboard."""

    def test_returns_valid_json(self):
        """Функция возвращает валидный JSON."""
        result = build_menu_keyboard(['Кнопка 1', 'Кнопка 2'])
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_single_button(self):
        """Клавиатура с одной кнопкой."""
        result = build_menu_keyboard(['Одна кнопка'])
        parsed = json.loads(result)
        
        assert len(parsed['buttons']) == 1
        assert len(parsed['buttons'][0]) == 1
        # В VkKeyboard текст кнопки хранится в поле 'label', а не 'text'
        assert parsed['buttons'][0][0]['action']['label'] == 'Одна кнопка'

    def test_multiple_buttons_in_one_row(self):
        """Клавиатура с несколькими кнопками в одной строке."""
        buttons = ['Кнопка 1', 'Кнопка 2', 'Кнопка 3']
        result = build_menu_keyboard(buttons)
        parsed = json.loads(result)
        
        # VkKeyboard по умолчанию добавляет все кнопки в одну строку (ряд)
        assert len(parsed['buttons']) == 1
        assert len(parsed['buttons'][0]) == 3
        for i, button_text in enumerate(buttons):
            assert parsed['buttons'][0][i]['action']['label'] == button_text

    def test_one_time_false_by_default(self):
        """Параметр one_time по умолчанию равен False."""
        result = build_menu_keyboard(['Кнопка'])
        parsed = json.loads(result)
        assert parsed['one_time'] is False

    def test_one_time_true(self):
        """Параметр one_time=True корректно передается."""
        result = build_menu_keyboard(['Кнопка'], one_time=True)
        parsed = json.loads(result)
        assert parsed['one_time'] is True

    def test_one_time_false_explicit(self):
        """Параметр one_time=False передается явно."""
        result = build_menu_keyboard(['Кнопка'], one_time=False)
        parsed = json.loads(result)
        assert parsed['one_time'] is False

    def test_empty_buttons_list(self):
        """Клавиатура без кнопок."""
        result = build_menu_keyboard([])
        parsed = json.loads(result)
        
        # VkKeyboard возвращает список с одной пустой строкой
        assert len(parsed['buttons']) == 1
        assert len(parsed['buttons'][0]) == 0

    def test_buttons_have_primary_color(self):
        """Все кнопки имеют цвет PRIMARY."""
        result = build_menu_keyboard(['Кнопка 1', 'Кнопка 2'])
        parsed = json.loads(result)
        
        for row in parsed['buttons']:
            for button in row:
                assert button['color'] == 'primary'

    def test_buttons_have_text_action_type(self):
        """Все кнопки имеют тип действия 'text'."""
        result = build_menu_keyboard(['Кнопка 1', 'Кнопка 2'])
        parsed = json.loads(result)
        
        for row in parsed['buttons']:
            for button in row:
                assert button['action']['type'] == 'text'

    def test_buttons_with_emoji(self):
        """Кнопки с эмодзи корректно обрабатываются."""
        buttons = ['🟢 Главное меню', '🆒 Избранное', '🆘 Помощь']
        result = build_menu_keyboard(buttons)
        parsed = json.loads(result)
        
        assert len(parsed['buttons']) == 1
        assert len(parsed['buttons'][0]) == 3
        for i, button_text in enumerate(buttons):
            assert parsed['buttons'][0][i]['action']['label'] == button_text