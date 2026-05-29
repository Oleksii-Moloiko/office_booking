# Office Booking API

![Python](https://img.shields.io/badge/Python-3.11-blue) ![Django](https://img.shields.io/badge/Django-5.0-darkgreen) ![Tests](https://img.shields.io/badge/Tests-14%20passed-brightgreen)

REST API для бронювання робочих місць в офісі. Побудовано на Django + Django REST Framework.

## Можливості

- Реєстрація та авторизація через токен
- Перегляд робочих місць з фільтрацією по даті та наявності монітора
- Бронювання столу на конкретну дату
- Скасування бронювання (`status=cancelled`)
- Захист від подвійного бронювання (overbooking)
- Кожен користувач бачить тільки свої бронювання
- Інтерактивна документація OpenAPI (Swagger / ReDoc)

## Технології

- Python 3.11
- Django 5.x
- Django REST Framework
- PostgreSQL (рекомендовано) або SQLite
- drf-spectacular, django-filter, python-decouple

---

## Швидкий старт

### 1. Клонуй репозиторій

```bash
git clone https://github.com/Oleksii-Moloiko/office_booking.git
cd office_booking
```

### 2. Віртуальне середовище та залежності

```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate    # Windows

pip install django djangorestframework django-filter drf-spectacular python-decouple psycopg2-binary
```

### 3. Налаштування змінних середовища

```bash
cp .env.example .env
```

Відредагуй `.env` — згенеруй свій `SECRET_KEY` (не використовуй `change-me` у продакшені).

> **Важливо:** файл `.env` не комітиться в git. У репозиторії лише шаблон `.env.example`.

### 4. База даних

#### Варіант A: PostgreSQL у Docker (рекомендовано)

```bash
docker run --name office-pg \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=office_booking \
  -p 5432:5432 \
  -d postgres:16
```

У `.env` мають бути (як у `.env.example`):

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=office_booking
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

Якщо контейнер уже створений:

```bash
docker start office-pg
```

#### Варіант B: SQLite (швидкий локальний старт)

У `.env`:

```env
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

### 5. Міграції та адмін

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Запуск

```bash
python manage.py runserver
```

| Сервіс | URL |
|--------|-----|
| Home (JSON) | http://127.0.0.1:8000/ |
| API root | http://127.0.0.1:8000/api/ |
| Swagger UI | http://127.0.0.1:8000/api/docs/ |
| ReDoc | http://127.0.0.1:8000/api/redoc/ |
| OpenAPI schema | http://127.0.0.1:8000/api/schema/ |
| Django Admin | http://127.0.0.1:8000/admin/ |

### 7. Тести

```bash
python manage.py test bookings
```

---

## API Ендпоінти

### Автентифікація

Публічні ендпоінти (без токена):

#### Реєстрація

```
POST /api/auth/register/
```

```json
{
  "username": "testuser",
  "password": "testpass123"
}
```

Відповідь `201`:

```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

#### Логін

```
POST /api/auth/login/
```

Тіло — те саме. Відповідь `200` з полем `token`.

---

### Робочі місця

> Потрібен заголовок: `Authorization: Token <ваш_токен>`

```
GET /api/workspaces/?date=YYYY-MM-DD&has_monitor=true&room=1
```

| Параметр | Тип | Опис |
|----------|-----|------|
| `date` | string | Дата `YYYY-MM-DD` — додає поле `is_available` |
| `has_monitor` | boolean | Фільтр по монітору |
| `room` | integer | ID кімнати |

Приклад відповіді `200`:

```json
[
  {
    "id": 1,
    "number": "A-01",
    "room": 1,
    "has_monitor": true,
    "is_available": true
  }
]
```

---

### Бронювання

#### Створити

```
POST /api/bookings/
```

```json
{
  "workspace": 1,
  "booking_date": "2026-05-28"
}
```

Відповідь `201` — об'єкт бронювання з `status: "active"`.

Помилка `400` (стіл зайнятий):

```json
{
  "non_field_errors": ["Цей стіл вже зайнятий на цю дату."]
}
```

#### Мої бронювання

```
GET /api/bookings/
```

#### Скасувати бронювання

```
POST /api/bookings/{id}/cancel/
```

Відповідь `200`:

```json
{
  "status": "Бронювання скасовано."
}
```

---

## Приклади (curl)

```bash
# Реєстрація
curl -s -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'

# Збережи токен
TOKEN="твій_токен_тут"

# Вільні столи на дату
curl -s "http://127.0.0.1:8000/api/workspaces/?date=2026-05-28" \
  -H "Authorization: Token $TOKEN"

# Забронювати
curl -s -X POST http://127.0.0.1:8000/api/bookings/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"workspace": 1, "booking_date": "2026-05-28"}'

# Скасувати
curl -s -X POST http://127.0.0.1:8000/api/bookings/1/cancel/ \
  -H "Authorization: Token $TOKEN"
```

У Swagger UI: **Authorize** → введи `Token <твій_токен>`.

---

## Структура проєкту

```
office_booking/
├── office_booking/
│   ├── settings.py       # конфігурація, .env, БД
│   └── urls.py           # admin, swagger, bookings
├── bookings/
│   ├── models.py         # Room, Workspace, Booking
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── tests.py
│   └── admin.py
├── .env.example          # шаблон змінних (комітиться)
├── manage.py
└── README.md
```

---

## Змінні середовища

| Змінна | Опис |
|--------|------|
| `SECRET_KEY` | Секретний ключ Django |
| `DEBUG` | `True` / `False` |
| `ALLOWED_HOSTS` | Через кому, напр. `127.0.0.1,localhost` |
| `DB_ENGINE` | `django.db.backends.sqlite3` або `django.db.backends.postgresql` |
| `DB_NAME` | Ім'я БД або файл SQLite |
| `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Для PostgreSQL |

---

## Автор

[Oleksii Mololiko](https://github.com/Oleksii-Mololiko)
