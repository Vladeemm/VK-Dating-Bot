"""Инициализация SQLAlchemy session."""

import json
import os
import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from bot.database.models import Base

load_dotenv()

config = os.getenv('DATABASE')
if not config:
    raise RuntimeError('DATABASE environment variable is not set')

try:
    db_config = json.loads(config)
except json.JSONDecodeError as exc:
    raise RuntimeError('DATABASE must be valid JSON') from exc

DSN = (
    f"postgresql://{db_config['user']}:{db_config['password']}"
    f"@{db_config['host']}:{db_config['port']}/DatingBotBase"
)

engine = sqlalchemy.create_engine(DSN)
Session = sessionmaker(bind=engine)
session = Session()


def init_db() -> None:
    Base.metadata.create_all(engine)
