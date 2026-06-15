import psycopg2
import json
import os
from dotenv import load_dotenv


try:
    load_file = load_dotenv()
    if not load_file:
        print("Файл не найден")

    config = os.getenv("DATABASE")
    bd = json.loads(config)
except Exception as e:
    print(f'Ошибка чтения файла {e}')
    exit(100)

try:
    conn = psycopg2.connect(
        host=bd['host'],
        database='postgres',
        user=bd['user'],
        password=bd['password'],
        port=bd['port']
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

