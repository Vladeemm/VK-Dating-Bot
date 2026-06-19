import psycopg2
import sqlalchemy
import json
import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from models import Base

try:
    load_file = load_dotenv()
    if not load_file:
        print("Файл не найден")

    config = os.getenv("DATABASE")
    db = json.loads(config)
except Exception as e:
    print(f'Ошибка чтения файла {e}')
    exit(100)

try:
    conn = psycopg2.connect(
        host=db['host'],
        database='postgres',
        user=db['user'],
        password=db['password'],
        port=db['port']
    )
    print("поздравляю с подключением к БД")
except Exception as e:
    print(f'Ошибка подключения {e}')
    exit(100)

conn.autocommit = True

with conn.cursor() as cur:
    try:
        cur.execute('CREATE DATABASE "DatingBotBase" ENCODING "UTF8"')
        print('База данных DatingBotBase создана!')
    except Exception:
        print('База данных DatingBotBase уже создана! Продолжайте работу')

conn.close()

try:
    DSN = (f"postgresql://{db['user']}:{db['password']}"
           f"@{db['host']}:{db['port']}/DatingBotBase")
    engine = sqlalchemy.create_engine(DSN)

except Exception:
    raise Exception("Вы где-то ошиблись! Создание ENGINE невозможно")

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
session.commit()

session.close()
