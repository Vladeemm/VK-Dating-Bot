"""Тесты для модуля bot/database/repositories/user_repo.py."""

import pytest
from unittest.mock import patch, MagicMock

from bot.database.repositories.user_repo import (
    get_user_by_id,
    create_user,
    ensure_user,
)
from bot.database.models import Users


class TestGetUserById:
    """Тесты для функции get_user_by_id."""

    @patch('bot.database.repositories.user_repo.get_session')
    def test_returns_user_when_found(self, mock_get_session):
        """Возвращает пользователя, если он найден."""
        mock_user = MagicMock(spec=Users)
        mock_user.id = 12345
        mock_user.name = 'Иван'
        
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        result = get_user_by_id(12345)
        
        assert result == mock_user
        assert result.id == 12345
        assert result.name == 'Иван'
        mock_session.query.assert_called_once_with(Users)

    @patch('bot.database.repositories.user_repo.get_session')
    def test_returns_none_when_not_found(self, mock_get_session):
        """Возвращает None, если пользователь не найден."""
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        result = get_user_by_id(99999)
        
        assert result is None


class TestCreateUser:
    """Тесты для функции create_user."""

    @patch('bot.database.repositories.user_repo.get_session')
    def test_creates_and_returns_user(self, mock_get_session):
        """Создает нового пользователя и возвращает его."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        result = create_user(12345, 'Иван')
        
        assert isinstance(result, Users)
        assert result.id == 12345
        assert result.name == 'Иван'
        mock_session.add.assert_called_once_with(result)


class TestEnsureUser:
    """Тесты для функции ensure_user."""

    @patch('bot.database.repositories.user_repo.get_session')
    def test_returns_existing_user(self, mock_get_session):
        """Возвращает существующего пользователя, если он найден."""
        mock_user = MagicMock(spec=Users)
        mock_user.id = 12345
        mock_user.name = 'Иван'
        
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        result = ensure_user(12345, 'Иван')
        
        assert result == mock_user
        # Новый пользователь не должен создаваться
        mock_session.add.assert_not_called()

    @patch('bot.database.repositories.user_repo.get_session')
    def test_creates_new_user_when_not_exists(self, mock_get_session):
        """Создает нового пользователя, если он не найден."""
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        result = ensure_user(12345, 'Иван')
        
        assert isinstance(result, Users)
        assert result.id == 12345
        assert result.name == 'Иван'
        mock_session.add.assert_called_once_with(result)

    @patch('bot.database.repositories.user_repo.get_session')
    def test_uses_provided_name_for_new_user(self, mock_get_session):
        """Использует переданное имя для нового пользователя."""
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        result = ensure_user(12345, 'Петр')
        
        assert result.name == 'Петр'