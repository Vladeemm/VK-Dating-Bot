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
    db_config  = json.loads(config)

    DSN = (f"postgresql://{db_config['user']}:{db_config['password']}"
           f"@{db_config['host']}:{db_config['port']}/DatingBotBase")
    engine = sqlalchemy.create_engine(DSN)
    # print('Объект engine создан')

except Exception:
    raise Exception("Вы где-то ошиблись! Создание ENGINE невозможно")

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


session.commit()



session.close()
