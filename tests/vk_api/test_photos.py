"""Тесты для модуля bot/vk_api/photos.py."""

import pytest
import datetime
from unittest.mock import patch, MagicMock

from bot.vk_api.photos import _get_age_from_bdate, get_user_profile, three_best_photos


class TestGetAgeFromBdate:
    """Тесты для функции _get_age_from_bdate."""

    def test_returns_age_when_bdate_valid(self):
        """Возвращает возраст при валидной дате рождения."""
        # Мокаем сегодняшнюю дату для стабильности теста
        today = datetime.date(2026, 6, 21)
        with patch('bot.vk_api.photos.datetime') as mock_datetime:
            mock_datetime.date.today.return_value = today
            # Дата рождения: 21 июня 1990 = 36 лет
            result = _get_age_from_bdate('21.6.1990')
            assert result == 36

    def test_returns_none_when_bdate_is_none(self):
        """Возвращает None, если дата рождения не предоставлена."""
        assert _get_age_from_bdate(None) is None

    def test_returns_none_when_bdate_empty(self):
        """Возвращает None, если дата рождения пустая строка."""
        assert _get_age_from_bdate('') is None

    def test_returns_none_when_invalid_format(self):
        """Возвращает None при неверном формате даты."""
        assert _get_age_from_bdate('1990-06-21') is None

    def test_returns_none_when_only_day_month(self):
        """Возвращает None, если нет года (только день и месяц)."""
        assert _get_age_from_bdate('21.6') is None

    def test_returns_none_when_non_numeric(self):
        """Возвращает None при нечисловых значениях."""
        assert _get_age_from_bdate('abc.def.ghi') is None

    def test_returns_age_before_birthday(self):
        """Возвращает возраст до дня рождения (еще не исполнилось)."""
        today = datetime.date(2026, 6, 20)
        with patch('bot.vk_api.photos.datetime') as mock_datetime:
            mock_datetime.date.today.return_value = today
            # Дата рождения: 21 июня 1990, завтра день рождения
            result = _get_age_from_bdate('21.6.1990')
            assert result == 35

    def test_returns_age_on_birthday(self):
        """Возвращает возраст в день рождения."""
        today = datetime.date(2026, 6, 21)
        with patch('bot.vk_api.photos.datetime') as mock_datetime:
            mock_datetime.date.today.return_value = today
            result = _get_age_from_bdate('21.6.1990')
            assert result == 36


class TestGetUserProfile:
    """Тесты для функции get_user_profile."""

    @patch('bot.vk_api.photos.time.sleep')
    @patch('bot.vk_api.photos.vk')
    def test_returns_profile_when_api_success(self, mock_vk, mock_sleep):
        """Возвращает профиль при успешном запросе к API."""
        mock_vk.users.get.return_value = [{
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'sex': 2,
            'bdate': '21.6.1990'
        }]
        
        today = datetime.date(2026, 6, 21)
        with patch('bot.vk_api.photos.datetime') as mock_datetime:
            mock_datetime.date.today.return_value = today
            result = get_user_profile(12345)
        
        assert result is not None
        assert result['user_vk_id'] == 12345
        assert result['name'] == 'Иван'
        assert result['surname'] == 'Иванов'
        assert result['gender'] == 2
        assert result['age'] == 36
        mock_vk.users.get.assert_called_once_with(user_ids=12345, fields='sex,bdate')

    @patch('bot.vk_api.photos.time.sleep')
    @patch('bot.vk_api.photos.vk')
    def test_returns_none_when_api_returns_empty(self, mock_vk, mock_sleep):
        """Возвращает None, если API вернул пустой ответ."""
        mock_vk.users.get.return_value = None
        
        result = get_user_profile(12345)
        
        assert result is None

    @patch('bot.vk_api.photos.time.sleep')
    @patch('bot.vk_api.photos.vk')
    def test_returns_none_when_api_returns_empty_list(self, mock_vk, mock_sleep):
        """Возвращает None, если API вернул пустой список."""
        mock_vk.users.get.return_value = []
        
        result = get_user_profile(12345)
        
        assert result is None

    @patch('bot.vk_api.photos.time.sleep')
    @patch('bot.vk_api.photos.vk')
    def test_handles_missing_last_name(self, mock_vk, mock_sleep):
        """Обрабатывает отсутствие фамилии."""
        mock_vk.users.get.return_value = [{
            'first_name': 'Иван',
            'sex': 2,
            'bdate': '21.6.1990'
        }]
        
        result = get_user_profile(12345)
        
        assert result is not None
        assert result['surname'] == ''

    @patch('bot.vk_api.photos.time.sleep')
    @patch('bot.vk_api.photos.vk')
    def test_handles_missing_bdate(self, mock_vk, mock_sleep):
        """Обрабатывает отсутствие даты рождения."""
        mock_vk.users.get.return_value = [{
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'sex': 2
        }]
        
        result = get_user_profile(12345)
        
        assert result is not None
        assert result['age'] is None

    @patch('bot.vk_api.photos.time.sleep')
    @patch('bot.vk_api.photos.vk')
    def test_calls_sleep(self, mock_vk, mock_sleep):
        """Вызывает sleep после запроса к API."""
        mock_vk.users.get.return_value = [{
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'sex': 2,
            'bdate': '21.6.1990'
        }]
        
        get_user_profile(12345)
        
        mock_sleep.assert_called_once_with(0.35)


class TestThreeBestPhotos:
    """Тесты для функции three_best_photos."""

    @patch('bot.vk_api.photos.time.sleep')
    @patch('bot.vk_api.photos.vk')
    @patch('bot.vk_api.photos.get_user_profile')
    def test_returns_three_best_photos(self, mock_get_profile, mock_vk, mock_sleep):
        """Возвращает три лучшие фотографии по лайкам."""
        mock_get_profile.return_value = {
            'user_vk_id': 12345,
            'name': 'Иван',
            'surname': 'Иванов',
            'gender': 2,
            'age': 36
        }
        
        mock_vk.photos.get.return_value = {
            'count': 5,
            'items': [
                {'id': 100, 'owner_id': 12345, 'likes': {'count': 10}},
                {'id': 101, 'owner_id': 12345, 'likes': {'count': 50}},
                {'id': 102, 'owner_id': 12345, 'likes': {'count': 30}},
                {'id': 103, 'owner_id': 12345, 'likes': {'count': 5}},
                {'id': 104, 'owner_id': 12345, 'likes': {'count': 20}},
            ]
        }
        
        result = three_best_photos(12345)
        
        assert result is not None
        assert 12345 in result
        assert result[12345]['name'] == 'Иван'
        
        # Проверяем, что фото отсортированы по лайкам (по убыванию)
        photos = result[12345]['photos']
        assert len(photos) == 3
        assert photos[0] == (12345, 101, 50)  # Больше всего лайков
        assert photos[1] == (12345, 102, 30)
        assert photos[2] == (12345, 104, 20)

    @patch('bot.vk_api.photos.get_user_profile')
    def test_returns_none_when_profile_not_found(self, mock_get_profile):
        """Возвращает None, если профиль не найден."""
        mock_get_profile.return_value = None
        
        result = three_best_photos(12345)
        
        assert result is None
        mock_get_profile.assert_called_once_with(12345)

    @patch('bot.vk_api.photos.time.sleep')
    @patch('bot.vk_api.photos.vk')
    @patch('bot.vk_api.photos.get_user_profile')
    def test_returns_none_when_less_than_3_photos(self, mock_get_profile, mock_vk, mock_sleep):
        """Возвращает None, если фотографий меньше 3."""
        mock_get_profile.return_value = {
            'user_vk_id': 12345,
            'name': 'Иван',
            'surname': 'Иванов',
            'gender': 2,
            'age': 36
        }
        
        mock_vk.photos.get.return_value = {
            'count': 2,
            'items': [
                {'id': 100, 'owner_id': 12345, 'likes': {'count': 10}},
                {'id': 101, 'owner_id': 12345, 'likes': {'count': 50}},
            ]
        }
        
        result = three_best_photos(12345)
        
        assert result is None

    @patch('bot.vk_api.photos.time.sleep')
    @patch('bot.vk_api.photos.vk')
    @patch('bot.vk_api.photos.get_user_profile')
    def test_skips_photos_without_id(self, mock_get_profile, mock_vk, mock_sleep):
        """Пропускает фотографии без ID или owner_id."""
        mock_get_profile.return_value = {
            'user_vk_id': 12345,
            'name': 'Иван',
            'surname': 'Иванов',
            'gender': 2,
            'age': 36
        }
        
        mock_vk.photos.get.return_value = {
            'count': 5,
            'items': [
                {'id': 100, 'owner_id': 12345, 'likes': {'count': 10}},
                {'id': None, 'owner_id': 12345, 'likes': {'count': 50}},  # Нет ID
                {'id': 102, 'owner_id': None, 'likes': {'count': 30}},    # Нет owner_id
                {'id': 103, 'owner_id': 12345, 'likes': {'count': 5}},
                {'id': 104, 'owner_id': 12345, 'likes': {'count': 20}},
            ]
        }
        
        result = three_best_photos(12345)
        
        assert result is not None
        photos = result[12345]['photos']
        # Должно быть только 3 валидных фото
        assert len(photos) == 3

    @patch('bot.vk_api.photos.time.sleep')
    @patch('bot.vk_api.photos.vk')
    @patch('bot.vk_api.photos.get_user_profile')
    def test_handles_missing_likes(self, mock_get_profile, mock_vk, mock_sleep):
        """Обрабатывает отсутствие информации о лайках."""
        mock_get_profile.return_value = {
            'user_vk_id': 12345,
            'name': 'Иван',
            'surname': 'Иванов',
            'gender': 2,
            'age': 36
        }
        
        mock_vk.photos.get.return_value = {
            'count': 3,
            'items': [
                {'id': 100, 'owner_id': 12345},  # Нет likes
                {'id': 101, 'owner_id': 12345, 'likes': {'count': 50}},
                {'id': 102, 'owner_id': 12345, 'likes': {'count': 30}},
            ]
        }
        
        result = three_best_photos(12345)
        
        assert result is not None
        photos = result[12345]['photos']
        assert len(photos) == 3
        # Фото без лайков должно иметь 0 лайков
        assert (12345, 100, 0) in photos

    @patch('bot.vk_api.photos.time.sleep')
    @patch('bot.vk_api.photos.vk')
    @patch('bot.vk_api.photos.get_user_profile')
    def test_calls_sleep_after_photos_request(self, mock_get_profile, mock_vk, mock_sleep):
        """Вызывает sleep после запроса фотографий."""
        mock_get_profile.return_value = {
            'user_vk_id': 12345,
            'name': 'Иван',
            'surname': 'Иванов',
            'gender': 2,
            'age': 36
        }
        
        mock_vk.photos.get.return_value = {
            'count': 3,
            'items': [
                {'id': 100, 'owner_id': 12345, 'likes': {'count': 10}},
                {'id': 101, 'owner_id': 12345, 'likes': {'count': 50}},
                {'id': 102, 'owner_id': 12345, 'likes': {'count': 30}},
            ]
        }
        
        three_best_photos(12345)
        
        # Sleep вызывается только один раз внутри three_best_photos,
        # так как get_user_profile замокан и его внутренний sleep не выполняется.
        assert mock_sleep.call_count == 1
        mock_sleep.assert_called_with(0.35)