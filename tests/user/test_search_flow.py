"""Тесты для модуля bot/user/search_flow.py."""

import pytest
from unittest.mock import patch, MagicMock

from bot.user.search_flow import (
    get_current_questionnaire_id,
    set_current_questionnaire_id,
    _send_questionnaire_by_id,
    send_questionnaire,
    search_and_send_first_questionnaire,
)
from bot.database.models import Status
from bot.core.states import START


class TestGetCurrentQuestionnaireId:
    """Тесты для функции get_current_questionnaire_id."""

    def test_returns_id_when_exists(self):
        """Возвращает ID анкеты, если он есть в критериях."""
        status = MagicMock(spec=Status)
        status.search_criteria = {'current_questionnaire_id': 12345}
        
        result = get_current_questionnaire_id(status)
        
        assert result == 12345

    def test_returns_none_when_not_exists(self):
        """Возвращает None, если ID анкеты не установлен."""
        status = MagicMock(spec=Status)
        status.search_criteria = {}
        
        result = get_current_questionnaire_id(status)
        
        assert result is None

    def test_returns_none_when_search_criteria_is_none(self):
        """Возвращает None, если search_criteria равен None."""
        status = MagicMock(spec=Status)
        status.search_criteria = None
        
        result = get_current_questionnaire_id(status)
        
        assert result is None


class TestSetCurrentQuestionnaireId:
    """Тесты для функции set_current_questionnaire_id."""

    @patch('bot.user.search_flow.update_search_criteria')
    def test_sets_new_id(self, mock_update):
        """Устанавливает новый ID анкеты в критерии."""
        status = MagicMock(spec=Status)
        status.search_criteria = {'city': 1}
        mock_update.return_value = status
        
        result = set_current_questionnaire_id(status, 12345)
        
        expected_criteria = {'city': 1, 'current_questionnaire_id': 12345}
        mock_update.assert_called_once_with(status, expected_criteria)
        assert result == status

    @patch('bot.user.search_flow.update_search_criteria')
    def test_removes_id_when_none(self, mock_update):
        """Удаляет ID анкеты из критериев, если передан None."""
        status = MagicMock(spec=Status)
        status.search_criteria = {'city': 1, 'current_questionnaire_id': 12345}
        mock_update.return_value = status
        
        result = set_current_questionnaire_id(status, None)
        
        expected_criteria = {'city': 1}
        mock_update.assert_called_once_with(status, expected_criteria)
        assert result == status


class TestSendQuestionnaireById:
    """Тесты для функции _send_questionnaire_by_id."""

    @patch('bot.user.search_flow.set_current_questionnaire_id')
    @patch('bot.user.search_flow.build_menu_keyboard')
    @patch('bot.user.search_flow.write_message')
    @patch('bot.user.search_flow.format_questionnaire_message')
    @patch('bot.user.search_flow.three_best_photos')
    def test_returns_true_when_photos_available(
        self, mock_photos, mock_format, mock_write, mock_keyboard, mock_set_id
    ):
        """Возвращает True и отправляет анкету, если есть фото."""
        status = MagicMock(spec=Status)
        mock_photos.return_value = {
            12345: {
                'photos': [(1, 100, 10)],
                'name': 'Иван',
                'surname': 'Иванов',
                'age': 25,
                'user_vk_id': 12345
            }
        }
        mock_format.return_value = 'Иван Иванов, 25'
        mock_keyboard.return_value = 'keyboard_json'
        mock_set_id.return_value = status
        
        success, result_status = _send_questionnaire_by_id(999, status, 12345)
        
        assert success is True
        assert result_status == status
        mock_photos.assert_called_once_with(12345)
        assert mock_write.call_count == 2  # Сообщение + клавиатура
        mock_set_id.assert_called_once_with(status, 12345)

    @patch('bot.user.search_flow.three_best_photos')
    def test_returns_false_when_no_photos(self, mock_photos):
        """Возвращает False, если фото недоступны."""
        status = MagicMock(spec=Status)
        mock_photos.return_value = None
        
        success, result_status = _send_questionnaire_by_id(999, status, 12345)
        
        assert success is False
        assert result_status == status
        mock_photos.assert_called_once_with(12345)


class TestSendQuestionnaire:
    """Тесты для функции send_questionnaire."""

    @patch('bot.user.search_flow.update_list_applicants')
    @patch('bot.user.search_flow._send_questionnaire_by_id')
    def test_returns_true_when_questionnaire_sent(self, mock_send_by_id, mock_update_list):
        """Возвращает True, если анкета успешно отправлена."""
        status = MagicMock(spec=Status)
        status.list_applicants = [111, 222]
        mock_send_by_id.return_value = (True, status)
        mock_update_list.return_value = status
        
        success, result_status = send_questionnaire(999, status)
        
        assert success is True
        assert result_status == status
        mock_send_by_id.assert_called_once()
        mock_update_list.assert_called_once()

    @patch('bot.user.search_flow.set_current_questionnaire_id')
    @patch('bot.user.search_flow.update_list_applicants')
    @patch('bot.user.search_flow._send_questionnaire_by_id')
    def test_returns_false_when_list_empty(self, mock_send_by_id, mock_update_list, mock_set_id):
        """Возвращает False, если список анкет пуст."""
        status = MagicMock(spec=Status)
        status.list_applicants = []
        mock_update_list.return_value = status
        mock_set_id.return_value = status
        
        success, result_status = send_questionnaire(999, status)
        
        assert success is False
        assert result_status == status
        mock_send_by_id.assert_not_called()
        mock_update_list.assert_called_once_with(status, None)
        mock_set_id.assert_called_once_with(status, None)

    @patch('bot.user.search_flow.set_current_questionnaire_id')
    @patch('bot.user.search_flow.update_list_applicants')
    @patch('bot.user.search_flow._send_questionnaire_by_id')
    def test_returns_false_when_all_questionnaires_fail(self, mock_send_by_id, mock_update_list, mock_set_id):
        """Возвращает False, если все анкеты не удалось отправить."""
        status = MagicMock(spec=Status)
        status.list_applicants = [111, 222]
        mock_send_by_id.return_value = (False, status)
        mock_update_list.return_value = status
        mock_set_id.return_value = status
        
        success, result_status = send_questionnaire(999, status)
        
        assert success is False
        assert result_status == status
        assert mock_send_by_id.call_count == 2  # Пытался отправить обе анкеты

    @patch('bot.user.search_flow.update_list_applicants')
    @patch('bot.user.search_flow._send_questionnaire_by_id')
    def test_updates_list_applicants_after_success(self, mock_send_by_id, mock_update_list):
        """Обновляет список анкет после успешной отправки."""
        status = MagicMock(spec=Status)
        status.list_applicants = [111, 222, 333]
        mock_send_by_id.return_value = (True, status)
        mock_update_list.return_value = status
        
        send_questionnaire(999, status)
        
        # После pop() остается [111, 222]
        mock_update_list.assert_called_once_with(status, [111, 222])


class TestSearchAndSendFirstQuestionnaire:
    """Тесты для функции search_and_send_first_questionnaire."""

    @patch('bot.user.search_flow.write_message')
    @patch('bot.user.search_flow.build_menu_keyboard')
    def test_returns_false_when_missing_criteria(self, mock_keyboard, mock_write):
        """Возвращает False, если не хватает критериев поиска."""
        status = MagicMock(spec=Status)
        status.search_criteria = {'city': 1}  # Не хватает sex, age_from, age_to
        mock_keyboard.return_value = 'keyboard_json'
        
        success, result_status = search_and_send_first_questionnaire(999, status)
        
        assert success is False
        assert result_status == status
        mock_write.assert_called()

    @patch('bot.user.search_flow.update_status_step')
    @patch('bot.user.search_flow.write_message')
    @patch('bot.user.search_flow.build_menu_keyboard')
    @patch('bot.user.search_flow.get_questionnaires_by_criteria')
    def test_returns_false_when_no_questionnaires_found(
        self, mock_get_questionnaires, mock_keyboard, mock_write, mock_update_step
    ):
        """Возвращает False, если анкеты не найдены."""
        status = MagicMock(spec=Status)
        status.search_criteria = {'city': 1, 'sex': 2, 'age_from': 18, 'age_to': 30}
        mock_get_questionnaires.return_value = []
        mock_keyboard.return_value = 'keyboard_json'
        mock_update_step.return_value = status
        
        success, result_status = search_and_send_first_questionnaire(999, status)
        
        assert success is False
        assert result_status == status
        mock_get_questionnaires.assert_called_once_with(1, 2, 18, 30)
        mock_update_step.assert_called_once_with(status, START)

    @patch('bot.user.search_flow.send_questionnaire')
    @patch('bot.user.search_flow.update_list_applicants')
    @patch('bot.user.search_flow.shuffle')
    @patch('bot.user.search_flow.write_message')
    @patch('bot.user.search_flow.build_menu_keyboard')
    @patch('bot.user.search_flow.get_questionnaires_by_criteria')
    def test_returns_false_when_send_questionnaire_fails(
        self, mock_get_questionnaires, mock_keyboard, mock_write, mock_shuffle,
        mock_update_list, mock_send
    ):
        """Возвращает False, если send_questionnaire не удался."""
        status = MagicMock(spec=Status)
        status.search_criteria = {'city': 1, 'sex': 2, 'age_from': 18, 'age_to': 30}
        mock_get_questionnaires.return_value = [111, 222]
        mock_keyboard.return_value = 'keyboard_json'
        mock_update_list.return_value = status
        mock_send.return_value = (False, status)
        
        success, result_status = search_and_send_first_questionnaire(999, status)
        
        assert success is False
        assert result_status == status
        mock_shuffle.assert_called_once()
        mock_update_list.assert_called_once()
        mock_send.assert_called_once_with(999, status)

    @patch('bot.user.search_flow.send_questionnaire')
    @patch('bot.user.search_flow.update_list_applicants')
    @patch('bot.user.search_flow.shuffle')
    @patch('bot.user.search_flow.get_questionnaires_by_criteria')
    def test_returns_true_when_successful(
        self, mock_get_questionnaires, mock_shuffle, mock_update_list, mock_send
    ):
        """Возвращает True при успешном поиске и отправке."""
        status = MagicMock(spec=Status)
        status.search_criteria = {'city': 1, 'sex': 2, 'age_from': 18, 'age_to': 30}
        mock_get_questionnaires.return_value = [111, 222]
        mock_update_list.return_value = status
        mock_send.return_value = (True, status)
        
        success, result_status = search_and_send_first_questionnaire(999, status)
        
        assert success is True
        assert result_status == status
        mock_get_questionnaires.assert_called_once_with(1, 2, 18, 30)
        mock_shuffle.assert_called_once()
        mock_update_list.assert_called_once()
        mock_send.assert_called_once_with(999, status)

    @patch('bot.user.search_flow.send_questionnaire')
    @patch('bot.user.search_flow.update_list_applicants')
    @patch('bot.user.search_flow.shuffle')
    @patch('bot.user.search_flow.get_questionnaires_by_criteria')
    def test_shuffles_ids_list(
        self, mock_get_questionnaires, mock_shuffle, mock_update_list, mock_send
    ):
        """Перемешивает список найденных анкет."""
        status = MagicMock(spec=Status)
        status.search_criteria = {'city': 1, 'sex': 2, 'age_from': 18, 'age_to': 30}
        ids_list = [111, 222, 333]
        mock_get_questionnaires.return_value = ids_list
        mock_update_list.return_value = status
        mock_send.return_value = (True, status)
        
        search_and_send_first_questionnaire(999, status)
        
        mock_shuffle.assert_called_once_with(ids_list)

    @patch('bot.user.search_flow.send_questionnaire')
    @patch('bot.user.search_flow.update_list_applicants')
    @patch('bot.user.search_flow.shuffle')
    @patch('bot.user.search_flow.get_questionnaires_by_criteria')
    def test_updates_list_applicants(
        self, mock_get_questionnaires, mock_shuffle, mock_update_list, mock_send
    ):
        """Обновляет список анкет в статусе."""
        status = MagicMock(spec=Status)
        status.search_criteria = {'city': 1, 'sex': 2, 'age_from': 18, 'age_to': 30}
        ids_list = [111, 222]
        mock_get_questionnaires.return_value = ids_list
        mock_update_list.return_value = status
        mock_send.return_value = (True, status)
        
        search_and_send_first_questionnaire(999, status)
        
        mock_update_list.assert_called_once_with(status, ids_list)