# План реструктуризации проекта VK Dating Bot

## Цель

Создать модульную структуру с разделением ответственности: бот, БД, VK API, бизнес-логика и UI.

## Шаг 1: Подготовка инфраструктуры

1. Создать `config.py` для централизованной конфигурации.
2. Создать `.env.example`.
3. Создать `README.md` (переименовать `readmi.md`).
4. Создать пакет `bot/` и подпапки:
   - `bot/core/`
   - `bot/database/`
   - `bot/vk_api/`
   - `bot/user/`
   - `bot/ui/`
5. Создать точки входа и каркасы модулей.

## Шаг 2: Реализация базы данных

1. Перенести ORM модели в `bot/database/models.py`.
2. Создать `bot/database/session.py` для SQLAlchemy.
3. Создать `bot/database/init_db.py` для создания базы.
4. Создать репозитории:
   - `bot/database/repositories/user_repo.py`
   - `bot/database/repositories/status_repo.py`
   - `bot/database/repositories/favorite_repo.py`

## Шаг 3: Работа с VK API

1. Создать клиент VK в `bot/vk_api/client.py`.
2. Перенести функции поиска в `bot/vk_api/search.py`.
3. Перенести работу с фотографиями в `bot/vk_api/photos.py`.
4. Перенести работу с пользователями и городами в `bot/vk_api/users.py`.

## Шаг 4: UI и бизнес-логика

1. Создать `bot/ui/keyboard.py` для кнопок.
2. Создать `bot/ui/messages.py` для шаблонов сообщений.
3. Создать `bot/user/preferences.py` для логики формирования предпочтений.
4. Создать `bot/user/favorites.py` для логики избранного.
5. Создать `bot/user/service.py` для общей бизнес-логики.

## Шаг 5: Основной цикл и обработчики

1. Перенести основной цикл в `bot/core/bot.py`.
2. Вынести обработчики сообщений в `bot/core/handlers.py`.
3. Обновить `main.py` как минимальную точку входа.

## Шаг 6: Очистка и документация

1. Удалить или архивировать ненужные файлы:
   - `experiments.py`
   - `for_main.py`
   - `create_tables.py`
   - `DatingBotBase.py`
   - `actions.py`
   - `bd_actions.py`
   - `vk_actions.py`
   - `statuses.py`
   - `readmi.md`
2. Переименовать документацию:
   - `user_expirience.md` → `user_experience.md`
   - `technical_expirience.md` → `technical_experience.md`
3. Добавить `docs/architecture.md`.
4. Добавить `docs/SETUP.md`.
5. Добавить проверку и обработку ошибок VK API.

## Дополнительный шаг

6. Добавить логирование ошибок и метрики запросов VK API.
   - Объяснение: это поможет быстро понять, почему пропадают анкеты или когда VK API отвечает нестабильно, а также упростит отладку при реальном запуске.

## Шаг 7: Тесты и качество

1. Создать `tests/`.
2. Добавить `pytest` в `requirements.txt`.
3. Написать базовые тесты для:
   - `bot/database/session.py`
   - `bot/vk_api/search.py`
   - `bot/core/handlers.py`

## Важные приоритеты

1. Убрать дублирование БД.
2. Сделать единую точку входа `main.py`.
3. Перенести статусы в `bot/core/states.py`.
4. Реализовать UI/логку отдельно от БД и API.
5. Сохранить старый код до полной миграции.
