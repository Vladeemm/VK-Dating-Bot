import logging
from config import validate_config, validate_token
from bot.core.bot import run_bot

def main() -> None:
    logging.basicConfig(level=logging.INFO, filename='bot.log', filemode='a', format="%(name)s %(asctime)s %(levelname)s %(message)s")
    
    validate_config()
    validate_token()
    run_bot()

if __name__ == '__main__':
    main()