import logging
import os
import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
MY_VK_TOKEN = os.getenv('MY_VK_TOKEN')
DATABASE = os.getenv('DATABASE')

def validate_config() -> None:
    missing = [name for name in ('BOT_TOKEN', 'MY_VK_TOKEN', 'DATABASE') if not globals()[name]]
    if missing:
        raise RuntimeError(f"Missing required configuration variables: {', '.join(missing)}")


def validity(token: str, name: str = 'Личный токен', get_method: str = 'users.get') -> None:
    """Проверяет один токен, выбрасывает исключение при ошибке"""
    try:
        resp = requests.get(
            f'https://api.vk.com/method/{get_method}',
            params={'access_token': token, 'v': '5.131'},
            timeout=5
        )
        data = resp.json()

        if 'error' in data:
            error_code = data['error'].get('error_code')
            error_msg = data['error'].get('error_msg', 'Неизвестная ошибка')

            if error_code == 5:
                raise RuntimeError(f"{name} просрочен!")
            raise RuntimeError(f"Ошибка API VK {error_code}: {error_msg}")

        logger.info(f"{name} валиден")

    except requests.exceptions.ConnectionError:
        raise RuntimeError("Нет интернета")
    except Exception as e:
        raise RuntimeError(f"Ошибка {name}: {e}")



def validate_token():
    validity(MY_VK_TOKEN)
    validity(BOT_TOKEN, 'Токен сообщества', 'groups.getById')
    logger.info("Все токены валидны!")
