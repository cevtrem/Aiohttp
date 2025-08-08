# Aiohttp Advertisement API

REST API для управления объявлениями, построенный на aiohttp с асинхронной базой данных SQLAlchemy.

## Возможности

- 🔐 **Аутентификация пользователей** с JWT токенами
- 👥 **Система пользователей** с регистрацией и входом
- 📝 **CRUD операции** для объявлений
- 📄 **Пагинация** списка объявлений
- ✅ **Валидация данных** с Pydantic
- 🔒 **Проверка прав доступа** (только владелец может редактировать)
- 🐳 **Docker поддержка**

## Быстрый старт

### Локальная разработка

1. **Клонирование и настройка:**
```bash
git clone <repository>
cd Aiohttp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Создание базы данных:**
```bash
python create_tables.py
```

3. **Запуск сервера:**
```bash
python main.py
```

Сервер запустится на `http://localhost:8080`

### Docker

```bash
docker-compose up --build
```

## API Endpoints

### Аутентификация
- `POST /auth/register` - Регистрация пользователя
- `POST /auth/login` - Вход в систему

### Объявления
- `POST /ads` - Создание объявления (требует аутентификации)
- `GET /ads` - Список объявлений с пагинацией
- `GET /ads/{id}` - Получение конкретного объявления
- `PUT /ads/{id}` - Обновление объявления (требует аутентификации)
- `DELETE /ads/{id}` - Удаление объявления (требует аутентификации)

## Примеры использования

### Регистрация пользователя
```bash
curl -X POST http://localhost:8080/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "password123"
  }'
```

### Вход в систему
```bash
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "password123"
  }'
```

### Создание объявления
```bash
curl -X POST http://localhost:8080/ads \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Продаю iPhone 12",
    "description": "Отличное состояние, полный комплект",
    "owner_id": 1
  }'
```

### Получение списка объявлений
```bash
curl "http://localhost:8080/ads?page=1&per_page=10"
```

## Структура проекта

```
Aiohttp/
├── app/
│   ├── __init__.py      # Маршруты
│   ├── auth.py          # Аутентификация
│   ├── database.py      # База данных
│   ├── models.py        # SQLAlchemy модели
│   ├── schemas.py       # Pydantic схемы
│   └── views.py         # Обработчики
├── data/
│   └── ads.db          # SQLite база
├── main.py              # Точка входа
├── requirements.txt     # Зависимости
├── create_tables.py     # Создание таблиц
├── Dockerfile          # Docker
├── docker-compose.yml  # Docker Compose
└── README.md           # Документация
```

## Технологии

- **aiohttp** - асинхронный веб-фреймворк
- **SQLAlchemy** - ORM для работы с базой данных
- **Pydantic** - валидация данных
- **JWT** - аутентификация
- **bcrypt** - хеширование паролей
- **SQLite** - база данных

## База данных

Две таблицы:
- `users` - пользователи (id, username, email, password_hash, created_at)
- `advertisements` - объявления (id, title, description, created_at, owner_id)

## Коды ошибок

- `400` - Ошибка валидации
- `401` - Не авторизован
- `403` - Доступ запрещен
- `404` - Ресурс не найден
- `409` - Конфликт (пользователь уже существует)
- `500` - Внутренняя ошибка сервера
