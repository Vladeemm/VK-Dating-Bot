import pytest
from unittest.mock import patch, MagicMock
import requests

import config


class TestValidateConfig:
    """Тесты для функции validate_config."""

    def test_validate_config_success(self):
        """Проверка, что при наличии всех переменных исключение не возникает."""
        with patch.object(config, 'BOT_TOKEN', 'test_bot_token'), \
             patch.object(config, 'MY_VK_TOKEN', 'test_user_token'), \
             patch.object(config, 'DATABASE', '{"user": "test"}'):
            
            # Если исключение не возникло, тест пройден
            config.validate_config()

    def test_validate_config_missing_one_variable(self):
        """Проверка, что при отсутствии одной переменной выбрасывается RuntimeError."""
        with patch.object(config, 'BOT_TOKEN', None), \
             patch.object(config, 'MY_VK_TOKEN', 'test_user_token'), \
             patch.object(config, 'DATABASE', '{"user": "test"}'):
            
            with pytest.raises(RuntimeError) as exc_info:
                config.validate_config()
            
            assert 'BOT_TOKEN' in str(exc_info.value)

    def test_validate_config_missing_all_variables(self):
        """Проверка, что при отсутствии всех переменных сообщение содержит все имена."""
        with patch.object(config, 'BOT_TOKEN', None), \
             patch.object(config, 'MY_VK_TOKEN', None), \
             patch.object(config, 'DATABASE', None):
            
            with pytest.raises(RuntimeError) as exc_info:
                config.validate_config()
            
            error_message = str(exc_info.value)
            assert 'BOT_TOKEN' in error_message
            assert 'MY_VK_TOKEN' in error_message
            assert 'DATABASE' in error_message


class TestValidity:
    """Тесты для функции validity (проверка токенов)."""

    def test_validity_success(self):
        """Проверка валидного токена (успешный ответ от API)."""
        mock_response = MagicMock()
        mock_response.json.return_value = {'response': [{'id': 1}]}
        
        with patch('config.requests.get', return_value=mock_response):
            # Исключение не должно возникнуть
            config.validity('fake_valid_token')

    def test_validity_expired_token(self):
        """Проверка просроченного токена (код ошибки 5)."""
        mock_response = MagicMock()
        mock_response.json.return_value = {'error': {'error_code': 5}}
        
        with patch('config.requests.get', return_value=mock_response):
            with pytest.raises(RuntimeError) as exc_info:
                config.validity('fake_expired_token')
            
            assert 'просрочен' in str(exc_info.value)

    def test_validity_no_internet(self):
        """Проверка отсутствия интернета (ConnectionError)."""
        with patch('config.requests.get', side_effect=requests.exceptions.ConnectionError):
            with pytest.raises(RuntimeError) as exc_info:
                config.validity('fake_token')
            
            assert 'Нет интернета' in str(exc_info.value)

    def test_validity_unknown_error(self):
        """Проверка неизвестной ошибки API."""
        mock_response = MagicMock()
        mock_response.json.return_value = {'error': {'error_code': 999, 'error_msg': 'Unknown'}}
        
        with patch('config.requests.get', return_value=mock_response):
            with pytest.raises(RuntimeError) as exc_info:
                config.validity('fake_token')
            
            assert 'Ошибка' in str(exc_info.value)