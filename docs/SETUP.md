# SETUP

## Требования

- Python 3.9+
- PostgreSQL
- Виртуальное окружение

## Установка

1. Создайте виртуальное окружение:
   ```bash
   python -m venv .venv
   ```
2. Активируйте окружение:
   - Windows PowerShell:
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - Windows CMD:
     ```cmd
     .venv\Scripts\activate.bat
     ```
   - macOS / Linux:
     ```bash
     source .venv/bin/activate
     ```
3. Установите зависимости:
   ```bash
   python -m pip install -r requirements.txt
   ```

## Конфигурация

1. Скопируйте файл `.env.example` в `.env`.
2. Заполните:
   - `BOT_TOKEN` — токен сообщества ВКонтакте
   - `MY_VK_TOKEN` — токен пользователя ВКонтакте
   - `DATABASE` — JSON-строка с данными доступа к базе

Пример:
```text
BOT_TOKEN=your_vk_group_bot_token
MY_VK_TOKEN=your_vk_user_token
DATABASE={"user": "db_user", "password": "db_password", "host": "localhost", "port": 5432}
```

## Запуск

```bash
python main.py
```

## Инициализация базы данных

Если необходимо, запустите `bot/database/init_db.py` как модуль или создайте схему вручную.
