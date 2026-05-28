# Office Booking API

REST API для бронювання робочих місць в офісі. Побудовано на Django + Django REST Framework.

## Можливості

- Реєстрація та авторизація через токен
- Перегляд списку робочих місць з фільтрацією по даті та наявності монітора
- Бронювання столу на конкретну дату
- Захист від подвійного бронювання (overbooking)
- Кожен користувач бачить тільки свої бронювання

## Технології

- Python 3.11
- Django 5.x
- Django REST Framework
- SQLite (розробка)

## Швидкий старт

### 1. Клонуй репозиторій

```bash
git clone https://github.com/Oleksii-Moloiko/office_booking.git
cd office-booking
```

### 2. Створи віртуальне середовище та встанови залежності

```bash
python -m venv .venv
source .venv/bin/activate  # macOS / Linux
# .venv\Scripts\activate   # Windows

pip install django djangorestframework
```

### 3. Застосуй міграції

```bash
python manage.py migrate
```

### 4. Створи адміністратора

```bash
python manage.py createsuperuser
```

### 5. Запусти сервер

```bash
python manage.py runserver
```

API доступне на `http://127.0.0.1:8000/`  
Адмін-панель: `http://127.0.0.1:8000/admin`

---

## API Ендпоінти

### Автентифікація

#### Реєстрація
```
POST /api/auth/register/
```
**Тіло запиту:**
```json
{
  "username": "testuser",
  "password": "testpass123"
}
```
**Відповідь `201`:**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

---

#### Логін
```
POST /api/auth/login/
```
**Тіло запиту:**
```json
{
  "username": "testuser",
  "password": "testpass123"
}
```
**Відповідь `200`:**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

---

### Робочі місця

> Всі запити нижче потребують заголовка:  
> `Authorization: Token <ваш_токен>`

#### Список столів з доступністю
```
GET /api/workspaces/?date=YYYY-MM-DD
```
**Параметри:**
| Параметр | Тип | Опис |
|---|---|---|
| `date` | string | Дата у форматі `YYYY-MM-DD`. Якщо передана — показує поле `is_available` |
| `has_monitor` | boolean | Фільтр по наявності монітора |

**Відповідь `200`:**
```json
[
  {
    "id": 1,
    "number": "A-01",
    "room": 1,
    "has_monitor": true,
    "is_available": true
  },
  {
    "id": 2,
    "number": "A-02",
    "room": 1,
    "has_monitor": false,
    "is_available": false
  }
]
```

---

### Бронювання

#### Створити бронювання
```
POST /api/bookings/
```
**Тіло запиту:**
```json
{
  "workspace": 1,
  "booking_date": "2026-05-28"
}
```
**Відповідь `201`:**
```json
{
  "id": 1,
  "user": 2,
  "workspace": 1,
  "booking_date": "2026-05-28",
  "status": "active"
}
```
**Відповідь `400` (стіл зайнятий):**
```json
{
  "non_field_errors": ["Цей стіл вже зайнятий на цю дату."]
}
```

---

#### Мої бронювання
```
GET /api/bookings/
```
**Відповідь `200`:**
```json
[
  {
    "id": 1,
    "user": 2,
    "workspace": 1,
    "booking_date": "2026-05-28",
    "status": "active"
  }
]
```

---

#### Скасувати бронювання
```
DELETE /api/bookings/{id}/
```
**Відповідь `204 No Content`**

---

## Структура проєкту

```
office_booking/
├── office_booking/
│   ├── settings.py       ← конфігурація
│   └── urls.py           ← головні маршрути
├── bookings/
│   ├── models.py         ← Room, Workspace, Booking
│   ├── serializers.py    ← валідація та серіалізація
│   ├── views.py          ← бізнес-логіка
│   ├── urls.py           ← маршрути додатку
│   └── admin.py          ← адмін-панель
└── manage.py
```

## Приклади використання (curl)

```bash
# Збережи токен після реєстрації
TOKEN="твій_токен_тут"

# Список вільних столів на дату
curl -s "http://127.0.0.1:8000/api/workspaces/?date=2026-05-28" \
  -H "Authorization: Token $TOKEN"

# Забронювати стіл
curl -s -X POST http://127.0.0.1:8000/api/bookings/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"workspace": 1, "booking_date": "2026-05-28"}'
```

## Автор

[Твоє ім'я](https://github.com/YOUR_USERNAME)