"""Тесты для модуля bot/user/favorites.py."""

import pytest
from unittest.mock import patch, MagicMock

from bot.user.favorites import (
    get_favorite_index,
    set_favorite_index,
    send_favorite_questionnaire,
    start_favorite_flow,
    show_next_favorite,
    show_previous_favorite,
    delete_current_favorite,
    add_to_favorites,
    remove_from_favorites,
)
from bot.database.models import Status, Favorite
from bot.core.states import START, VIEWING_FAVORITE_QUESTIONNAIRE


class TestGetFavoriteIndex:
    """Тесты для функции get_favorite_index."""

    def test_returns_index_when_exists(self):
        """Возвращает индекс, если он есть в критериях."""
        status = MagicMock(spec=Status)
        status.search_criteria = {'favorite_index': 5}
        
        result = get_favorite_index(status)
        
        assert result == 5

    def test_returns_zero_when_not_exists(self):
        """Возвращает 0, если индекс не установлен."""
        status = MagicMock(spec=Status)
        status.search_criteria = {}
        
        result = get_favorite_index(status)
        
        assert result == 0

    def test_returns_zero_when_search_criteria_is_none(self):
        """Возвращает 0, если search_criteria равен None."""
        status = MagicMock(spec=Status)
        status.search_criteria = None
        
        result = get_favorite_index(status)
        
        assert result == 0


class TestSetFavoriteIndex:
    """Тесты для функции set_favorite_index."""

    @patch('bot.user.favorites.update_search_criteria')
    def test_sets_index(self, mock_update):
        """Устанавливает индекс в критерии."""
        status = MagicMock(spec=Status)
        status.search_criteria = {'city': 1}
        mock_update.return_value = status
        
        result = set_favorite_index(status, 5)
        
        expected_criteria = {'city': 1, 'favorite_index': 5}
        mock_update.assert_called_once_with(status, expected_criteria)
        assert result == status


class TestSendFavoriteQuestionnaire:
    """Тесты для функции send_favorite_questionnaire."""

    @patch('bot.user.favorites.build_menu_keyboard')
    @patch('bot.user.favorites.write_message')
    @patch('bot.user.favorites.three_best_photos')
    @patch('bot.user.favorites.get_favorite')
    def test_returns_false_when_no_favorites(self, mock_get_fav, mock_photos, mock_write, mock_keyboard):
        """Возвращает False, если список избранного пуст."""
        status = MagicMock(spec=Status)
        status.list_applicants = []
        
        result = send_favorite_questionnaire(999, status)
        
        assert result is False
        mock_write.assert_called_once_with(999, 'У вас пока нет анкет в избранном.')

    @patch('bot.user.favorites.build_menu_keyboard')
    @patch('bot.user.favorites.write_message')
    @patch('bot.user.favorites.format_questionnaire_message')
    @patch('bot.user.favorites.three_best_photos')
    @patch('bot.user.favorites.get_favorite')
    def test_sends_questionnaire_with_photos(
        self, mock_get_fav, mock_photos, mock_format, mock_write, mock_keyboard
    ):
        """Отправляет анкету с фото, если они доступны."""
        status = MagicMock(spec=Status)
        status.list_applicants = [111, 222]
        status.search_criteria = {'favorite_index': 0}
        
        mock_favorite = MagicMock(spec=Favorite)
        mock_get_fav.return_value = mock_favorite
        
        mock_photos.return_value = {
            111: {
                'photos': [(1, 100, 10)],
                'name': 'Иван',
                'surname': 'Иванов',
                'age': 25,
                'user_vk_id': 111
            }
        }
        mock_format.return_value = 'Иван Иванов, 25'
        mock_keyboard.return_value = 'keyboard_json'
        
        result = send_favorite_questionnaire(999, status)
        
        assert result is True
        mock_get_fav.assert_called_once_with(999, 111)
        mock_photos.assert_called_once_with(111)
        assert mock_write.call_count >= 2  # Сообщение + клавиатура

    @patch('bot.user.favorites.build_menu_keyboard')
    @patch('bot.user.favorites.write_message')
    @patch('bot.user.favorites.format_favorite_item')
    @patch('bot.user.favorites.get_user_profile')
    @patch('bot.user.favorites.three_best_photos')
    @patch('bot.user.favorites.get_favorite')
    def test_sends_questionnaire_without_photos(
        self, mock_get_fav, mock_photos, mock_profile, mock_format, mock_write, mock_keyboard
    ):
        """Отправляет анкету без фото, если фото недоступны."""
        status = MagicMock(spec=Status)
        status.list_applicants = [111]
        status.search_criteria = {'favorite_index': 0}
        
        mock_favorite = MagicMock(spec=Favorite)
        mock_favorite.name = 'Иван'
        mock_favorite.surname = 'Иванов'
        mock_get_fav.return_value = mock_favorite
        
        mock_photos.return_value = None
        mock_profile.return_value = {'age': 25}
        mock_format.return_value = 'Иван Иванов, 25'
        mock_keyboard.return_value = 'keyboard_json'
        
        result = send_favorite_questionnaire(999, status)
        
        assert result is True
        mock_profile.assert_called_once_with(111)
        mock_format.assert_called_once_with('Иван', 'Иванов', 111, age=25)

    @patch('bot.user.favorites.write_message')
    @patch('bot.user.favorites.get_favorite')
    def test_returns_false_when_favorite_not_found(self, mock_get_fav, mock_write):
        """Возвращает False, если анкета не найдена в БД."""
        status = MagicMock(spec=Status)
        status.list_applicants = [111]
        status.search_criteria = {'favorite_index': 0}
        
        mock_get_fav.return_value = None
        
        result = send_favorite_questionnaire(999, status)
        
        assert result is False
        mock_write.assert_called_once_with(999, 'Не удалось загрузить анкету из избранного.')

    @patch('bot.user.favorites.build_menu_keyboard')
    @patch('bot.user.favorites.write_message')
    @patch('bot.user.favorites.three_best_photos')
    @patch('bot.user.favorites.get_favorite')
    @patch('bot.user.favorites.set_favorite_index')
    def test_clamps_negative_index(self, mock_set_index, mock_get_fav, mock_photos, mock_write, mock_keyboard):
        """Корректирует отрицательный индекс до 0."""
        status = MagicMock(spec=Status)
        status.list_applicants = [111]
        status.search_criteria = {'favorite_index': -5}
        mock_set_index.return_value = status
        
        mock_get_fav.return_value = MagicMock(spec=Favorite)
        mock_photos.return_value = {111: {'photos': [], 'name': 'Test', 'user_vk_id': 111}}
        mock_keyboard.return_value = 'keyboard_json'
        
        send_favorite_questionnaire(999, status)
        
        mock_set_index.assert_called_once_with(status, 0)

    @patch('bot.user.favorites.build_menu_keyboard')
    @patch('bot.user.favorites.write_message')
    @patch('bot.user.favorites.three_best_photos')
    @patch('bot.user.favorites.get_favorite')
    @patch('bot.user.favorites.set_favorite_index')
    def test_clamps_index_beyond_length(self, mock_set_index, mock_get_fav, mock_photos, mock_write, mock_keyboard):
        """Корректирует индекс, выходящий за пределы списка."""
        status = MagicMock(spec=Status)
        status.list_applicants = [111]
        status.search_criteria = {'favorite_index': 10}
        mock_set_index.return_value = status
        
        mock_get_fav.return_value = MagicMock(spec=Favorite)
        mock_photos.return_value = {111: {'photos': [], 'name': 'Test', 'user_vk_id': 111}}
        mock_keyboard.return_value = 'keyboard_json'
        
        send_favorite_questionnaire(999, status)
        
        mock_set_index.assert_called_once_with(status, 0)  # len - 1 = 0


class TestStartFavoriteFlow:
    """Тесты для функции start_favorite_flow."""

    @patch('bot.user.favorites.send_favorite_questionnaire')
    @patch('bot.user.favorites.update_status_step')
    @patch('bot.user.favorites.set_favorite_index')
    @patch('bot.user.favorites.update_list_applicants')
    @patch('bot.user.favorites.get_favorites_by_user')
    @patch('bot.user.favorites.get_status_by_user_id')
    def test_starts_flow_with_favorites(
        self, mock_get_status, mock_get_favs, mock_update_list, mock_set_index,
        mock_update_step, mock_send
    ):
        """Запускает поток просмотра, если есть избранные анкеты."""
        mock_status = MagicMock(spec=Status)
        mock_get_status.return_value = mock_status
        
        mock_fav1 = MagicMock(spec=Favorite)
        mock_fav1.favorite_user_vk_id = 111
        mock_fav2 = MagicMock(spec=Favorite)
        mock_fav2.favorite_user_vk_id = 222
        mock_get_favs.return_value = [mock_fav1, mock_fav2]
        
        mock_update_list.return_value = mock_status
        mock_set_index.return_value = mock_status
        mock_update_step.return_value = mock_status
        
        start_favorite_flow(999)
        
        mock_get_status.assert_called_once_with(999)
        mock_get_favs.assert_called_once_with(999)
        mock_update_list.assert_called_once_with(mock_status, [111, 222])
        mock_set_index.assert_called_once_with(mock_status, 0)
        mock_update_step.assert_called_once_with(mock_status, VIEWING_FAVORITE_QUESTIONNAIRE)
        mock_send.assert_called_once_with(999, mock_status)

    @patch('bot.user.favorites.write_message')
    @patch('bot.user.favorites.get_favorites_by_user')
    @patch('bot.user.favorites.get_status_by_user_id')
    def test_returns_when_no_favorites(self, mock_get_status, mock_get_favs, mock_write):
        """Не запускает поток, если избранное пусто."""
        mock_get_status.return_value = MagicMock(spec=Status)
        mock_get_favs.return_value = []
        
        start_favorite_flow(999)
        
        mock_write.assert_called_once_with(999, 'У вас пока нет анкет в избранном.')

    @patch('bot.user.favorites.get_favorites_by_user')
    @patch('bot.user.favorites.get_status_by_user_id')
    def test_returns_when_no_status(self, mock_get_status, mock_get_favs):
        """Не запускает поток, если статус не найден."""
        mock_get_status.return_value = None
        
        start_favorite_flow(999)
        
        mock_get_favs.assert_not_called()


class TestShowNextFavorite:
    """Тесты для функции show_next_favorite."""

    @patch('bot.user.favorites.send_favorite_questionnaire')
    @patch('bot.user.favorites.set_favorite_index')
    @patch('bot.user.favorites.get_status_by_user_id')
    def test_shows_next_favorite(self, mock_get_status, mock_set_index, mock_send):
        """Показывает следующую анкету."""
        mock_status = MagicMock(spec=Status)
        mock_status.list_applicants = [111, 222, 333]
        mock_status.search_criteria = {'favorite_index': 1}
        mock_get_status.return_value = mock_status
        mock_set_index.return_value = mock_status
        
        show_next_favorite(999)
        
        mock_set_index.assert_called_once_with(mock_status, 2)
        mock_send.assert_called_once_with(999, mock_status)

    @patch('bot.user.favorites.write_message')
    @patch('bot.user.favorites.get_status_by_user_id')
    def test_returns_when_at_last_favorite(self, mock_get_status, mock_write):
        """Не переключается, если это последняя анкета."""
        mock_status = MagicMock(spec=Status)
        mock_status.list_applicants = [111, 222]
        mock_status.search_criteria = {'favorite_index': 1}
        mock_get_status.return_value = mock_status
        
        show_next_favorite(999)
        
        mock_write.assert_called_once_with(999, 'Это последняя анкета. Больше анкет нет.')

    @patch('bot.user.favorites.get_status_by_user_id')
    def test_returns_when_no_status(self, mock_get_status):
        """Не выполняет действия, если статус не найден."""
        mock_get_status.return_value = None
        
        show_next_favorite(999)
        
        mock_get_status.assert_called_once_with(999)


class TestShowPreviousFavorite:
    """Тесты для функции show_previous_favorite."""

    @patch('bot.user.favorites.send_favorite_questionnaire')
    @patch('bot.user.favorites.set_favorite_index')
    @patch('bot.user.favorites.get_status_by_user_id')
    def test_shows_previous_favorite(self, mock_get_status, mock_set_index, mock_send):
        """Показывает предыдущую анкету."""
        mock_status = MagicMock(spec=Status)
        mock_status.list_applicants = [111, 222, 333]
        mock_status.search_criteria = {'favorite_index': 2}
        mock_get_status.return_value = mock_status
        mock_set_index.return_value = mock_status
        
        show_previous_favorite(999)
        
        mock_set_index.assert_called_once_with(mock_status, 1)
        mock_send.assert_called_once_with(999, mock_status)

    @patch('bot.user.favorites.write_message')
    @patch('bot.user.favorites.get_status_by_user_id')
    def test_returns_when_at_first_favorite(self, mock_get_status, mock_write):
        """Не переключается, если это первая анкета."""
        mock_status = MagicMock(spec=Status)
        mock_status.list_applicants = [111, 222]
        mock_status.search_criteria = {'favorite_index': 0}
        mock_get_status.return_value = mock_status
        
        show_previous_favorite(999)
        
        mock_write.assert_called_once_with(999, 'Это первая анкета в избранном.')


class TestDeleteCurrentFavorite:
    """Тесты для функции delete_current_favorite."""

    @patch('bot.user.favorites.send_favorite_questionnaire')
    @patch('bot.user.favorites.set_favorite_index')
    @patch('bot.user.favorites.update_list_applicants')
    @patch('bot.user.favorites.remove_favorite')
    @patch('bot.user.favorites.write_message')
    @patch('bot.user.favorites.get_status_by_user_id')
    def test_deletes_favorite_and_shows_next(
        self, mock_get_status, mock_write, mock_remove, mock_update_list,
        mock_set_index, mock_send
    ):
        """Удаляет анкету и показывает следующую."""
        mock_status = MagicMock(spec=Status)
        mock_status.list_applicants = [111, 222, 333]
        mock_status.search_criteria = {'favorite_index': 1}
        mock_get_status.return_value = mock_status
        mock_update_list.return_value = mock_status
        mock_set_index.return_value = mock_status
        
        delete_current_favorite(999)
        
        mock_remove.assert_called_once_with(999, 222)
        mock_write.assert_any_call(999, 'Анкета удалена из избранного.')
        mock_update_list.assert_called_once_with(mock_status, [111, 333])
        mock_set_index.assert_called_once_with(mock_status, 1)
        mock_send.assert_called_once_with(999, mock_status)

    @patch('bot.user.favorites.build_menu_keyboard')
    @patch('bot.user.favorites.update_status_step')
    @patch('bot.user.favorites.update_list_applicants')
    @patch('bot.user.favorites.remove_favorite')
    @patch('bot.user.favorites.write_message')
    @patch('bot.user.favorites.get_status_by_user_id')
    def test_returns_to_start_when_last_favorite_deleted(
        self, mock_get_status, mock_write, mock_remove, mock_update_list,
        mock_update_step, mock_keyboard
    ):
        """Возвращается в главное меню, если удалена последняя анкета."""
        mock_status = MagicMock(spec=Status)
        mock_status.list_applicants = [111]
        mock_status.search_criteria = {'favorite_index': 0}
        mock_get_status.return_value = mock_status
        mock_update_list.return_value = mock_status
        mock_update_step.return_value = mock_status
        mock_keyboard.return_value = 'keyboard_json'
        
        delete_current_favorite(999)
        
        mock_remove.assert_called_once_with(999, 111)
        mock_update_list.assert_called_once_with(mock_status, None)
        mock_update_step.assert_called_once_with(mock_status, START)
        # Добавляем keyboard в ожидаемый вызов
        mock_write.assert_any_call(999, 'Избранное пустое. Возвращаемся в главное меню.', keyboard='keyboard_json')

    @patch('bot.user.favorites.write_message')
    @patch('bot.user.favorites.get_status_by_user_id')
    def test_returns_when_no_favorites(self, mock_get_status, mock_write):
        """Не выполняет действия, если список пуст."""
        mock_status = MagicMock(spec=Status)
        mock_status.list_applicants = []
        mock_get_status.return_value = mock_status
        
        delete_current_favorite(999)
        
        mock_write.assert_called_once_with(999, 'У вас пока нет анкет в избранном.')


class TestAddToFavorites:
    """Тесты для функции add_to_favorites."""

    @patch('bot.user.favorites.add_favorite')
    @patch('bot.user.favorites.get_favorite')
    @patch('bot.user.favorites.write_message')
    def test_adds_favorite_when_not_exists(self, mock_write, mock_get_fav, mock_add):
        """Добавляет анкету, если её нет в избранном."""
        mock_get_fav.return_value = None
        
        add_to_favorites(999, 111, 'Иван', 'Иванов', '2', {'photo1': 'url'})
        
        mock_add.assert_called_once_with(999, 111, 'Иван', 'Иванов', '2', {'photo1': 'url'})
        mock_write.assert_called_once_with(999, 'Анкета добавлена в избранное')

    @patch('bot.user.favorites.write_message')
    @patch('bot.user.favorites.get_favorite')
    def test_does_not_add_if_exists(self, mock_get_fav, mock_write):
        """Не добавляет анкету, если она уже есть в избранном."""
        mock_get_fav.return_value = MagicMock(spec=Favorite)
        
        add_to_favorites(999, 111, 'Иван', 'Иванов', '2', {'photo1': 'url'})
        
        mock_write.assert_called_once_with(999, 'Эта анкета уже есть в избранном.')

    @patch('bot.user.favorites.add_favorite')
    @patch('bot.user.favorites.get_favorite')
    @patch('bot.user.favorites.write_message')
    def test_handles_exception(self, mock_write, mock_get_fav, mock_add):
        """Обрабатывает исключение при добавлении."""
        mock_get_fav.return_value = None
        mock_add.side_effect = Exception('DB error')
        
        add_to_favorites(999, 111, 'Иван', 'Иванов', '2', {'photo1': 'url'})
        
        mock_write.assert_called_once_with(999, 'Не удалось добавить анкету в избранное. Попробуйте позже.')


class TestRemoveFromFavorites:
    """Тесты для функции remove_from_favorites."""

    @patch('bot.user.favorites.remove_favorite')
    @patch('bot.user.favorites.write_message')
    def test_removes_favorite_when_exists(self, mock_write, mock_remove):
        """Удаляет анкету, если она есть в избранном."""
        mock_remove.return_value = True
        
        remove_from_favorites(999, 111)
        
        mock_remove.assert_called_once_with(999, 111)
        mock_write.assert_called_once_with(999, 'Анкета удалена из избранного')

    @patch('bot.user.favorites.remove_favorite')
    @patch('bot.user.favorites.write_message')
    def test_shows_message_when_not_found(self, mock_write, mock_remove):
        """Показывает сообщение, если анкета не найдена."""
        mock_remove.return_value = False
        
        remove_from_favorites(999, 111)
        
        mock_write.assert_called_once_with(999, 'Анкета не найдена в избранном')