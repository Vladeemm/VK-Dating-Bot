import logging
from config import validate_config
from bot.core.bot import run_bot

def main() -> None:
    logging.basicConfig(level=logging.WARNING, filename='bot.log', filemode='a', format="%(name)s %(asctime)s %(levelname)s %(message)s")
    
    validate_config()
    run_bot()

if __name__ == '__main__':
    main()
