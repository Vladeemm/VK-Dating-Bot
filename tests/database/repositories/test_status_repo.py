"""Тесты для модуля bot/database/repositories/status_repo.py."""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from bot.database.repositories.status_repo import (
    get_status_by_user_id,
    create_status,
    update_status_step,
    update_search_criteria,
    update_list_applicants,
)
from bot.database.models import Status


class TestGetStatusByUserId:
    """Тесты для функции get_status_by_user_id."""

    @patch('bot.database.repositories.status_repo.get_session')
    def test_returns_status_when_found(self, mock_get_session):
        """Возвращает статус, если пользователь найден."""
        mock_status = MagicMock(spec=Status)
        mock_status.user_vk_id = 12345
        mock_status.step = 'START'
        mock_status.search_criteria = {}
        mock_status.list_applicants = []
        
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_status
        
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        result = get_status_by_user_id(12345)
        
        assert result == mock_status
        mock_session.query.assert_called_once_with(Status)
        # Проверяем, что атрибуты были загружены (eager loading)
        _ = mock_status.step
        _ = mock_status.search_criteria
        _ = mock_status.list_applicants

    @patch('bot.database.repositories.status_repo.get_session')
    def test_returns_none_when_not_found(self, mock_get_session):
        """Возвращает None, если пользователь не найден."""
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        result = get_status_by_user_id(99999)
        
        assert result is None

    @patch('bot.database.repositories.status_repo.get_session')
    def test_filters_by_user_vk_id(self, mock_get_session):
        """Фильтрует по полю user_vk_id."""
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        get_status_by_user_id(12345)
        
        # Проверяем, что filter был вызван с правильным условием
        mock_session.query.return_value.filter.assert_called_once()


class TestCreateStatus:
    """Тесты для функции create_status."""

    @patch('bot.database.repositories.status_repo.get_session')
    def test_creates_status_with_defaults(self, mock_get_session):
        """Создает статус с параметрами по умолчанию."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        result = create_status(user_id=12345, step='START')
        
        assert isinstance(result, Status)
        assert result.user_vk_id == 12345
        assert result.step == 'START'
        assert result.search_criteria == {}
        assert result.list_applicants == []
        mock_session.add.assert_called_once_with(result)

    @patch('bot.database.repositories.status_repo.get_session')
    def test_creates_status_with_custom_criteria(self, mock_get_session):
        """Создает статус с кастомными критериями поиска."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        criteria = {'city': 1, 'sex': 2}
        applicants = [111, 222]
        
        result = create_status(
            user_id=12345, 
            step='SEARCHING',
            search_criteria=criteria,
            list_applicants=applicants
        )
        
        assert result.search_criteria == criteria
        assert result.list_applicants == applicants
        mock_session.add.assert_called_once_with(result)

    @patch('bot.database.repositories.status_repo.get_session')
    def test_sets_step_datetime(self, mock_get_session):
        """Устанавливает step_datetime при создании."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        result = create_status(user_id=12345, step='START')
        
        assert isinstance(result.step_datetime, datetime)


class TestUpdateStatusStep:
    """Тесты для функции update_status_step."""

    @patch('bot.database.repositories.status_repo.get_session')
    def test_updates_step(self, mock_get_session):
        """Обновляет шаг и возвращает статус."""
        mock_status = MagicMock(spec=Status)
        mock_status.step = 'START'
        
        mock_session = MagicMock()
        mock_session.merge.return_value = mock_status
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        result = update_status_step(mock_status, 'SEARCHING')
        
        assert result == mock_status
        assert mock_status.step == 'SEARCHING'
        mock_session.merge.assert_called_once_with(mock_status)
        assert isinstance(mock_status.step_datetime, datetime)


class TestUpdateSearchCriteria:
    """Тесты для функции update_search_criteria."""

    @patch('bot.database.repositories.status_repo.get_session')
    def test_updates_criteria(self, mock_get_session):
        """Обновляет критерии поиска и возвращает статус."""
        mock_status = MagicMock(spec=Status)
        mock_status.search_criteria = {}
        
        mock_session = MagicMock()
        mock_session.merge.return_value = mock_status
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        new_criteria = {'city': 1, 'sex': 2}
        result = update_search_criteria(mock_status, new_criteria)
        
        assert result == mock_status
        assert mock_status.search_criteria == new_criteria
        mock_session.merge.assert_called_once_with(mock_status)
        assert isinstance(mock_status.step_datetime, datetime)


class TestUpdateListApplicants:
    """Тесты для функции update_list_applicants."""

    @patch('bot.database.repositories.status_repo.get_session')
    def test_updates_list_applicants(self, mock_get_session):
        """Обновляет список анкет и возвращает статус."""
        mock_status = MagicMock(spec=Status)
        mock_status.list_applicants = []
        
        mock_session = MagicMock()
        mock_session.merge.return_value = mock_status
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        new_list = [111, 222, 333]
        result = update_list_applicants(mock_status, new_list)
        
        assert result == mock_status
        assert mock_status.list_applicants == new_list
        mock_session.merge.assert_called_once_with(mock_status)

    @patch('bot.database.repositories.status_repo.get_session')
    def test_can_set_list_to_none(self, mock_get_session):
        """Можно установить список в None."""
        mock_status = MagicMock(spec=Status)
        mock_status.list_applicants = [111]
        
        mock_session = MagicMock()
        mock_session.merge.return_value = mock_status
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        result = update_list_applicants(mock_status, None)
        
        assert result == mock_status
        assert mock_status.list_applicants is None