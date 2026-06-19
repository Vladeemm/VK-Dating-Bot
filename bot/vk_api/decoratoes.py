"""Декораторы для обработки повторных попыток и ошибок VK API.

Модуль предоставляет декораторы для вызовов VK API с автоматической логикой повторов
и комплексной обработкой различных исключений VK API.
"""

import logging
from typing import Any, Callable, TypeVar
import requests.exceptions
import vk_api.exceptions

from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential
from functools import wraps

logger: logging.Logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


def should_retry(exception: Exception) -> bool:
    """Определить, должно ли исключение вызвать повторную попытку.

    Args:
        exception: Исключение для оценки.

    Returns:
        bool: True, если исключение требует повтора, иначе False.

    Повторные попытки для:
        - Ошибок подключения и таймаутов
        - HTTP ошибок VK API
        - Кода ошибки VK API 6 (слишком много запросов)
    """
    if isinstance(exception, (
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        vk_api.exceptions.ApiHttpError
    )):
        return True
    
    if isinstance(exception, vk_api.exceptions.ApiError):
        if exception.code == 6:
            return True
    
    return False

def vk_api_call(func: F) -> :
    """Декоратор для вызовов VK API с логикой повтора и обработкой ошибок.

    Оборачивает функции VK API автоматической логикой повтора, обрабатывающей
    временные сбои и обеспечивающей комплексное логирование различных сбоев.

    Args:
        func: Функция для обертывания. Обычно функция вызова VK API.

    Returns:
        Callable: Обернутая функция с логикой повтора и обработки ошибок.

    Обработка ошибок:
        - Код 6: Автоматический повтор (слишком много запросов)
        - Код 14: Требуется капча (возвращает None)
        - Коды 5, 113: Фатальные ошибки (возвращает None)
        - AccessDenied, AuthError: Ошибки авторизации (возвращает None)
        - Другие ошибки VK API: Логируются и пробрасываются
        - Неожиданные ошибки: Логируются и пробрасываются

    Raises:
        Exception: Пробрасывает необработанные исключения после логирования.
    """
    @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception(should_retry)  # type: ignore
    )
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Выполнить обернутую функцию с обработкой ошибок.

        Args:
            *args: Позиционные аргументы для обернутой функции.
            **kwargs: Именованные аргументы для обернутой функции.

        Returns:
            Any: Результат обернутой функции или None при обработанных ошибках.

        Raises:
            Exception: Пробрасывает необработанные ошибки VK API или неожиданные исключения.
        """
        try:
            return func(*args, **kwargs)
        except vk_api.exceptions.ApiError as e:
            if e.code == 14:
                logger.warning(f"Нужно пройти Captcha, {func.__name__}: {e}")
                return None
            if e.code in (5, 113):
                logger.warning(f"Фатальная ошибка в {func.__name__}: {e}")
                return None
            logger.error(f"Необработанная ошибка VK API в {func.__name__}: {e}", exc_info=True)
            raise
        except (vk_api.exceptions.AccessDenied, vk_api.exceptions.AuthError) as e:
            logger.warning(f"Ошибка авторизации в {func.__name__}: {e}")
            return None
        except Exception as e:
            logger.error(f"Непредвиденная ошибка в {func.__name__}: {e}", exc_info=True)
            raise

    return wrapper