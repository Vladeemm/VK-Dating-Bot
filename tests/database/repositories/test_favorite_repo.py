"""Тесты для модуля bot/database/repositories/favorite_repo.py."""

import pytest
from unittest.mock import patch, MagicMock

from bot.database.repositories.favorite_repo import (
    get_favorites_by_user,
    get_favorite,
    add_favorite,
    remove_favorite,
)
from bot.database.models import Favorite


class TestGetFavoritesByUser:
    """Тесты для функции get_favorites_by_user."""

    @patch('bot.database.repositories.favorite_repo.get_session')
    def test_returns_list_of_favorites(self, mock_get_session):
        """Возвращает список избранных анкет пользователя."""
        mock_favorites = [MagicMock(spec=Favorite), MagicMock(spec=Favorite)]
        
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = mock_favorites
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        result = get_favorites_by_user(12345)
        
        assert result == mock_favorites
        mock_session.query.assert_called_once_with(Favorite)

    @patch('bot.database.repositories.favorite_repo.get_session')
    def test_returns_empty_list_when_none(self, mock_get_session):
        """Возвращает пустой список, если анкет нет."""
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        result = get_favorites_by_user(12345)
        
        assert result == []


class TestGetFavorite:
    """Тесты для функции get_favorite."""

    @patch('bot.database.repositories.favorite_repo.get_session')
    def test_returns_favorite_when_found(self, mock_get_session):
        """Возвращает анкету, если она найдена."""
        mock_favorite = MagicMock(spec=Favorite)
        
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_favorite
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        result = get_favorite(12345, 67890)
        
        assert result == mock_favorite

    @patch('bot.database.repositories.favorite_repo.get_session')
    def test_returns_none_when_not_found(self, mock_get_session):
        """Возвращает None, если анкета не найдена."""
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        result = get_favorite(12345, 67890)
        
        assert result is None


class TestAddFavorite:
    """Тесты для функции add_favorite."""

    @patch('bot.database.repositories.favorite_repo.get_session')
    def test_creates_and_returns_favorite(self, mock_get_session):
        """Создает новую запись в избранном и возвращает её."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        result = add_favorite(
            user_id=12345,
            favorite_vk_id=67890,
            name='Иван',
            surname='Иванов',
            gender='2',
            photos={'photo1': 'url'}
        )
        
        assert isinstance(result, Favorite)
        assert result.user_vk_id == 12345
        assert result.favorite_user_vk_id == 67890
        assert result.name == 'Иван'
        assert result.surname == 'Иванов'
        assert result.gender == '2'
        assert result.photos == {'photo1': 'url'}
        mock_session.add.assert_called_once_with(result)


class TestRemoveFavorite:
    """Тесты для функции remove_favorite."""

    @patch('bot.database.repositories.favorite_repo.get_session')
    def test_returns_true_and_deletes_when_found(self, mock_get_session):
        """Удаляет анкету и возвращает True, если она найдена."""
        mock_favorite = MagicMock(spec=Favorite)
        
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_favorite
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        result = remove_favorite(12345, 67890)
        
        assert result is True
        mock_session.delete.assert_called_once_with(mock_favorite)

    @patch('bot.database.repositories.favorite_repo.get_session')
    def test_returns_false_when_not_found(self, mock_get_session):
        """Возвращает False и не удаляет ничего, если анкета не найдена."""
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        result = remove_favorite(12345, 67890)
        
        assert result is False
        mock_session.delete.assert_not_called()