"""Тесты для модуля bot/vk_api/decorators.py."""

from unittest.mock import MagicMock

import pytest
import requests.exceptions
import vk_api.exceptions
from tenacity import wait_none, RetryError

from bot.vk_api.decorators import should_retry, vk_api_call


class TestShouldRetry:
    """Тесты для функции should_retry."""

    def test_connection_error_returns_true(self):
        """ConnectionError требует повтора."""
        assert should_retry(requests.exceptions.ConnectionError()) is True

    def test_timeout_returns_true(self):
        """Timeout требует повтора."""
        assert should_retry(requests.exceptions.Timeout()) is True

    def test_api_http_error_returns_true(self):
        """ApiHttpError требует повтора."""
        # Используем MagicMock со spec, чтобы обойти сложный конструктор,
        # но при этом isinstance() в should_retry сработает корректно.
        error = MagicMock(spec=vk_api.exceptions.ApiHttpError)
        assert should_retry(error) is True

    def test_api_error_code_6_returns_true(self):
        """ApiError с кодом 6 (слишком много запросов) требует повтора."""
        error = vk_api.exceptions.ApiError(
            None, 'test', {}, {}, 
            {'error_code': 6, 'error_msg': 'too many requests'}
        )
        assert should_retry(error) is True

    def test_api_error_code_5_returns_false(self):
        """ApiError с кодом 5 (фатальная) не требует повтора."""
        error = vk_api.exceptions.ApiError(
            None, 'test', {}, {}, 
            {'error_code': 5, 'error_msg': 'auth failed'}
        )
        assert should_retry(error) is False

    def test_api_error_code_14_returns_false(self):
        """ApiError с кодом 14 (капча) не требует повтора."""
        error = vk_api.exceptions.ApiError(
            None, 'test', {}, {}, 
            {'error_code': 14, 'error_msg': 'captcha needed'}
        )
        assert should_retry(error) is False

    def test_api_error_code_113_returns_false(self):
        """ApiError с кодом 113 не требует повтора."""
        error = vk_api.exceptions.ApiError(
            None, 'test', {}, {}, 
            {'error_code': 113, 'error_msg': 'user not found'}
        )
        assert should_retry(error) is False

    def test_generic_exception_returns_false(self):
        """Обычное исключение не требует повтора."""
        assert should_retry(ValueError("oops")) is False

    def test_generic_api_error_returns_false(self):
        """ApiError с неизвестным кодом не требует повтора."""
        error = vk_api.exceptions.ApiError(
            None, 'test', {}, {}, 
            {'error_code': 999, 'error_msg': 'unknown'}
        )
        assert should_retry(error) is False


class TestVkApiCall:
    """Тесты для декоратора vk_api_call."""

    @pytest.fixture(autouse=True)
    def disable_retry_delays(self, monkeypatch):
        """Отключаем задержки между повторами для быстрых тестов."""
        monkeypatch.setattr(
            'bot.vk_api.decorators.wait_exponential', 
            lambda **kwargs: wait_none()
        )

    # === Успешные вызовы ===

    def test_successful_call_returns_result(self):
        """Успешный вызов возвращает результат."""
        @vk_api_call
        def success_func():
            return "success"
        
        assert success_func() == "success"

    def test_passes_args_and_kwargs(self):
        """Аргументы корректно передаются в обернутую функцию."""
        @vk_api_call
        def func_with_args(a, b, c=0):
            return a + b + c
        
        assert func_with_args(1, 2, c=3) == 6

    # === Обработка капчи и фатальных ошибок ===

    def test_captcha_returns_none(self):
        """Код 14 (капча) возвращает None."""
        error = vk_api.exceptions.ApiError(
            None, 'test', {}, {}, 
            {'error_code': 14, 'error_msg': 'captcha'}
        )
        
        @vk_api_call
        def captcha_func():
            raise error
        
        assert captcha_func() is None

    def test_fatal_error_5_returns_none(self):
        """Код 5 (фатальная ошибка авторизации) возвращает None."""
        error = vk_api.exceptions.ApiError(
            None, 'test', {}, {}, 
            {'error_code': 5, 'error_msg': 'auth'}
        )
        
        @vk_api_call
        def fatal_func():
            raise error
        
        assert fatal_func() is None

    def test_fatal_error_113_returns_none(self):
        """Код 113 (пользователь не найден) возвращает None."""
        error = vk_api.exceptions.ApiError(
            None, 'test', {}, {}, 
            {'error_code': 113, 'error_msg': 'user not found'}
        )
        
        @vk_api_call
        def fatal_func():
            raise error
        
        assert fatal_func() is None

    def test_access_denied_returns_none(self):
        """AccessDenied возвращает None."""
        @vk_api_call
        def access_func():
            # AccessDenied не принимает keyword arguments
            raise vk_api.exceptions.AccessDenied('test', {})
        
        assert access_func() is None

    def test_auth_error_returns_none(self):
        """AuthError возвращает None."""
        @vk_api_call
        def auth_func():
            raise vk_api.exceptions.AuthError("auth failed")
        
        assert auth_func() is None

    # === Пробрасывание необработанных ошибок ===

    def test_unexpected_exception_raises(self):
        """Непредвиденное исключение пробрасывается."""
        @vk_api_call
        def unexpected_func():
            raise ValueError("unexpected")
        
        with pytest.raises(ValueError, match="unexpected"):
            unexpected_func()

    def test_unknown_api_error_raises(self):
        """ApiError с неизвестным кодом пробрасывается."""
        error = vk_api.exceptions.ApiError(
            None, 'test', {}, {}, 
            {'error_code': 999, 'error_msg': 'unknown'}
        )
        
        @vk_api_call
        def unknown_error_func():
            raise error
        
        with pytest.raises(vk_api.exceptions.ApiError):
            unknown_error_func()

    # === Повторные попытки ===

    def test_retries_on_connection_error(self):
        """Повтор при ConnectionError."""
        call_count = {'n': 0}
        
        @vk_api_call
        def flaky_func():
            call_count['n'] += 1
            if call_count['n'] < 2:
                raise requests.exceptions.ConnectionError()
            return "success"
        
        assert flaky_func() == "success"
        assert call_count['n'] == 2

    def test_retries_on_code_6_then_success(self):
        """Повтор при коде 6 (слишком много запросов)."""
        call_count = {'n': 0}
        
        @vk_api_call
        def rate_limited_func():
            call_count['n'] += 1
            if call_count['n'] < 2:
                raise vk_api.exceptions.ApiError(
                    None, 'test', {}, {}, 
                    {'error_code': 6, 'error_msg': 'too many'}
                )
            return "success"
        
        assert rate_limited_func() == "success"
        assert call_count['n'] == 2

    def test_retries_on_timeout_then_success(self):
        """Повтор при Timeout."""
        call_count = {'n': 0}
        
        @vk_api_call
        def timeout_func():
            call_count['n'] += 1
            if call_count['n'] < 3:
                raise requests.exceptions.Timeout()
            return "success"
        
        assert timeout_func() == "success"
        assert call_count['n'] == 3

    def test_gives_up_after_max_retries(self):
        """После исчерпания попыток исключение пробрасывается."""

        call_count = {'n': 0}
        error = vk_api.exceptions.ApiError(
            None, 'test', {}, {}, 
            {'error_code': 6, 'error_msg': 'too many'}
        )
        
        @vk_api_call
        def always_fails():
            call_count['n'] += 1
            raise error
        
        # Tenacity оборачивает исключение в RetryError после исчерпания попыток
        with pytest.raises(RetryError):
            always_fails()
        
        # stop_after_attempt(3) — всего 3 попытки
        assert call_count['n'] == 3

    def test_non_retryable_error_not_retried(self):
        """Неповторяемая ошибка пробрасывается сразу без повторов."""
        call_count = {'n': 0}
        error = vk_api.exceptions.ApiError(
            None, 'test', {}, {}, 
            {'error_code': 999, 'error_msg': 'unknown'}
        )
        
        @vk_api_call
        def unknown_error_func():
            call_count['n'] += 1
            raise error
        
        with pytest.raises(vk_api.exceptions.ApiError):
            unknown_error_func()
        
        # Только одна попытка — повтор не нужен
        assert call_count['n'] == 1

    # === Сохранение метаданных функции ===

    def test_preserves_function_name(self):
        """Декоратор сохраняет имя оригинальной функции."""
        @vk_api_call
        def my_func():
            """My docstring"""
            return 42
        
        assert my_func.__name__ == 'my_func'
        assert my_func.__doc__ == 'My docstring'