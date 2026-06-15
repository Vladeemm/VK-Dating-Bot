from config import validate_config
from bot.core.bot import run_bot


def main() -> None:
    validate_config()
    run_bot()


if __name__ == '__main__':
    main()
