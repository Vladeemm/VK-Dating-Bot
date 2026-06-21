"""Тесты для модуля bot/user/preferences.py."""

import pytest
from unittest.mock import patch, MagicMock

from bot.user.preferences import (
    _validate_age_input,
    _update_criteria,
    AgeNotDigitError,
    AgeOutOfRange,
    AgeLessThanMinError,
)


class TestValidateAgeInput:
    """Тесты для функции _validate_age_input."""

    # === Успешная валидация ===

    def test_valid_age_returns_int(self):
        """Валидный возраст возвращается как int."""
        assert _validate_age_input("25") == 25

    def test_valid_min_age(self):
        """Минимально допустимый возраст (18) проходит валидацию."""
        assert _validate_age_input("18") == 18

    def test_valid_max_age(self):
        """Максимально допустимый возраст (99) проходит валидацию."""
        assert _validate_age_input("99") == 99

    def test_strips_whitespace(self):
        """Пробелы по краям строки обрезаются."""
        assert _validate_age_input("  30  ") == 30

    # === Не-цифры ===

    def test_non_digit_raises_error(self):
        """Строка с буквами вызывает AgeNotDigitError."""
        with pytest.raises(AgeNotDigitError):
            _validate_age_input("abc")

    def test_empty_string_raises_error(self):
        """Пустая строка вызывает AgeNotDigitError."""
        with pytest.raises(AgeNotDigitError):
            _validate_age_input("")

    def test_negative_number_raises_error(self):
        """Отрицательное число вызывает AgeNotDigitError."""
        with pytest.raises(AgeNotDigitError):
            _validate_age_input("-5")

    def test_decimal_raises_error(self):
        """Десятичное число вызывает AgeNotDigitError."""
        with pytest.raises(AgeNotDigitError):
            _validate_age_input("25.5")

    def test_mixed_content_raises_error(self):
        """Смешанное содержимое (цифры и буквы) вызывает AgeNotDigitError."""
        with pytest.raises(AgeNotDigitError):
            _validate_age_input("25abc")

    # === Диапазон ===

    def test_age_below_min_raises_error(self):
        """Возраст меньше 18 вызывает AgeOutOfRange."""
        with pytest.raises(AgeOutOfRange):
            _validate_age_input("17")

    def test_age_above_max_raises_error(self):
        """Возраст больше 99 вызывает AgeOutOfRange."""
        with pytest.raises(AgeOutOfRange):
            _validate_age_input("100")

    def test_too_long_string_raises_error(self):
        """Слишком длинная строка (3+ символа) вызывает AgeOutOfRange."""
        with pytest.raises(AgeOutOfRange):
            _validate_age_input("1234")

    # === Проверка min_age ===

    def test_age_less_than_min_age_raises_error(self):
        """Возраст меньше min_age вызывает AgeLessThanMinError."""
        with pytest.raises(AgeLessThanMinError):
            _validate_age_input("20", min_age=25)

    def test_age_equal_to_min_age_passes(self):
        """Возраст равный min_age проходит валидацию."""
        assert _validate_age_input("25", min_age=25) == 25

    def test_age_greater_than_min_age_passes(self):
        """Возраст больше min_age проходит валидацию."""
        assert _validate_age_input("30", min_age=25) == 30

    def test_min_age_none_ignored(self):
        """min_age=None игнорируется, используется только диапазон 18-99."""
        assert _validate_age_input("50", min_age=None) == 50


class TestUpdateCriteria:
    """Тесты для функции _update_criteria."""

    @patch('bot.user.preferences.update_search_criteria')
    def test_update_criteria_with_empty_search_criteria(self, mock_update):
        """Обновление критериев при пустом search_criteria."""
        mock_status = MagicMock()
        mock_status.search_criteria = None
        mock_update.return_value = mock_status

        result = _update_criteria(mock_status, 'city', 123)

        mock_update.assert_called_once_with(mock_status, {'city': 123})
        assert result == mock_status

    @patch('bot.user.preferences.update_search_criteria')
    def test_update_criteria_merges_with_existing(self, mock_update):
        """Новый ключ добавляется к существующим критериям."""
        mock_status = MagicMock()
        mock_status.search_criteria = {'city': 123}
        mock_update.return_value = mock_status

        result = _update_criteria(mock_status, 'sex', 2)

        mock_update.assert_called_once_with(mock_status, {'city': 123, 'sex': 2})
        assert result == mock_status

    @patch('bot.user.preferences.update_search_criteria')
    def test_update_criteria_overwrites_existing_key(self, mock_update):
        """Существующий ключ перезаписывается новым значением."""
        mock_status = MagicMock()
        mock_status.search_criteria = {'city': 123, 'sex': 1}
        mock_update.return_value = mock_status

        result = _update_criteria(mock_status, 'sex', 2)

        mock_update.assert_called_once_with(mock_status, {'city': 123, 'sex': 2})
        assert result == mock_status

    @patch('bot.user.preferences.update_search_criteria')
    def test_update_criteria_preserves_other_keys(self, mock_update):
        """Другие ключи сохраняются при обновлении."""
        mock_status = MagicMock()
        mock_status.search_criteria = {'city': 123, 'sex': 2, 'age_from': 25}
        mock_update.return_value = mock_status

        result = _update_criteria(mock_status, 'age_to', 35)

        expected = {'city': 123, 'sex': 2, 'age_from': 25, 'age_to': 35}
        mock_update.assert_called_once_with(mock_status, expected)
        assert result == mock_status