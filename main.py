from config import validate_config, validate_token
from bot.core.bot import run_bot


def main() -> None:
    validate_config()
    validate_token()
    run_bot()


if __name__ == '__main__':
    main()
