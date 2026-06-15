import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
MY_VK_TOKEN = os.getenv('MY_VK_TOKEN')
DATABASE = os.getenv('DATABASE')

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


def validate_config() -> None:
    missing = [name for name in ('BOT_TOKEN', 'MY_VK_TOKEN', 'DATABASE') if not globals()[name]]
    if missing:
        raise RuntimeError(f"Missing required configuration variables: {', '.join(missing)}")
