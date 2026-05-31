# Office Booking API

![Python](https://img.shields.io/badge/Python-3.11-blue) ![Django](https://img.shields.io/badge/Django-5.0-darkgreen) ![Tests](https://img.shields.io/badge/Tests-14%20passed-brightgreen) ![License](https://img.shields.io/badge/License-MIT-yellow)

Сучасна **REST API** для управління бронюванням робочих місць у офісі з підтримкою часових інтервалів, захистом від конфліктів та можливістю фільтрації. Побудовано на **Django 5.x** + **Django REST Framework** з інтерактивною OpenAPI документацією.

**[📖 Документація](#api-ендпоінти)** | **[🚀 Швидкий старт](#швидкий-старт)** | **[🏗️ Архітектура](#архітектура)** | **[🧪 Тестування](#тестування)**

## Можливості

- 🔐 **Безпека**: Аутентифікація через токени, валідація паролів, защита від подвійного бронювання
- 📅 **Бронювання з часом**: Не просто дата, а точні часові інтервали (09:00-17:00)
- 🎯 **Фільтрація**: За датою, наявністю монітора, кімнатою, часовими інтервалами
- 📊 **Управління**: Перегляд, створення, редагування та скасування бронювань
- 👥 **Ролі**: Користувачі бачать тільки свої бронювання, адміністратори — всі
- 📚 **Документація**: Інтерактивна Swagger UI, ReDoc, OpenAPI schema
- 🐳 **Контейнеризація**: Docker Compose з PostgreSQL для запуску однією командою
- ✅ **Тестування**: Набір тестів для валідації, безпеки та бізнес-логіки
- 🌍 **Українізація**: Інтерфейс і помилки повністю українською

## Технології

- **Backend**: Python 3.11, Django 5.x, Django REST Framework 3.x
- **БД**: PostgreSQL (рекомендовано) або SQLite для локальної розробки
- **Документація**: drf-spectacular (OpenAPI 3.0)
- **Фільтрування**: django-filter
- **Безпека**: python-decouple для env vars, django-ratelimit для rate limiting
- **Deployment**: Docker, Gunicorn, WhiteNoise для static файлів
- **Тестування**: Django TestCase з DRF APIClient

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

pip install -r requirements.txt
```

Або за допомогою **pip-tools** для lock файлів:
```bash
pip install pip-tools
pip-compile requirements.in  # якщо є requirements.in
pip-sync
```

### 3. Налаштування змінних середовища

```bash
cp .env.example .env
```

Відредагуй `.env` — згенеруй свій `SECRET_KEY` (не використовуй `change-me` у продакшені).

> **Важливо:** файл `.env` не комітиться в git. У репозиторії лише шаблон `.env.example`.

**Генерація SECRET_KEY для продакшену:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

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

### Аутентифікація

> Публічні ендпоінти (без токена)

#### Реєстрація

```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "SecurePass123!"
}
```

**Вимоги до пароля:**
- Мінімум 8 символів
- Мінімум одна цифра (0-9)
- Мінімум один спеціальний символ (!@#$%^&* тощо)

**Успішна відповідь (201):**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

#### Логін

```http
POST /api/auth/login/
```

Те саме тіло, що й у реєстрації. Відповідь `200` з полем `token`.

**Примітка**: Rate limited на **5 запитів на годину** на IP адресу.



## Приклади (curl)

```bash
# Реєстрація
curl -s -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "SecurePass123!"}'

# Збережи токен з відповіді
TOKEN="9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"

# Список доступних столів на дату з часом
curl -s "http://127.0.0.1:8000/api/workspaces/?date=2026-05-28&time_start=09:00&time_end=12:00" \
  -H "Authorization: Token $TOKEN"

# Забронювати стіл
curl -s -X POST http://127.0.0.1:8000/api/bookings/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace": 1,
    "booking_date": "2026-05-28",
    "time_start": "09:00",
    "time_end": "12:00"
  }'

# Мої бронювання
curl -s http://127.0.0.1:8000/api/bookings/ \
  -H "Authorization: Token $TOKEN"

# Скасувати бронювання
curl -s -X POST http://127.0.0.1:8000/api/bookings/5/cancel/ \
  -H "Authorization: Token $TOKEN"

# Через Swagger (інтерактивно)
# 1. Перейди на http://127.0.0.1:8000/api/docs/
# 2. Натисни "Authorize" (верхньо-правий кут)
# 3. Введи: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
# 4. Спробуй запити безпосередньо у браузері
```

---

## Архітектура

```
┌─────────────────────────────────────────────────────────────┐
│                     REST API (DRF)                          │
│  /api/auth/register  /api/auth/login  /api/bookings ...    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Serializers & Validators                        │
│  - WorkspaceSerializer (is_available logic)                 │
│  - BookingSerializer (time conflict validation)             │
│  - PasswordValidator, EmailValidator                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      Django Models                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │  User    │  │  Room    │  │Workspace │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
│       ↑              ↑             ↑                        │
│       └──────────────┴─────────────┘                        │
│                     ↓                                       │
│            ┌──────────────────┐                            │
│            │  Booking Model   │                            │
│            │ (time_start/end) │                            │
│            └──────────────────┘                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL / SQLite                             │
│  - users_user, bookings_room, bookings_workspace           │
│  - bookings_booking (з часовими полями)                     │
└─────────────────────────────────────────────────────────────┘
```

### Ключові компоненти

| Файл | Призначення |
|------|------------|
| `models.py` | Три моделі: Room (офісні кімнати), Workspace (столи), Booking (бронювання з часом) |
| `serializers.py` | Валідація даних, перевірка конфліктів часу, вычисление доступності |
| `views.py` | Auth endpoints (register, login), ViewSets для Workspace і Booking |
| `security.py` | Валідація паролів та email, логування подій безпеки |
| `tests.py` | Unit тести для безпеки та функціональності |

---

## Тестування

### Запуск тестів

```bash
python manage.py test bookings
```

**Результат:** 14+ тестів, включаючи:
- ✅ Email валідація
- ✅ Пароль з вимогами (8+ символів, цифра, спецсимвол)
- ✅ Дублювання користувачів
- ✅ Конфлікти часу бронювань
- ✅ Ролі користувачів (звичайні vs адміни)

### Запуск тестів із покриттям

```bash
pip install coverage
coverage run --source='.' manage.py test bookings
coverage report
coverage html  # Генерує HTML звіт у htmlcov/index.html
```

### Написання нових тестів

```python
from django.test import TestCase
from rest_framework.test import APIClient

class MyTests(TestCase):
    def setUp(self):
        self.client = APIClient()
    
    def test_something(self):
        response = self.client.get('/api/bookings/')
        self.assertEqual(response.status_code, 200)
```

---

## Змінні середовища

| Змінна | Тип | Опис | Приклад |
|--------|-----|------|---------|
| `SECRET_KEY` | string | Секретний ключ Django (генерується) | `django-insecure-abc...` |
| `DEBUG` | boolean | Режим розробки | `True` (development), `False` (production) |
| `ALLOWED_HOSTS` | string | Дозволені хости, розділені комами | `127.0.0.1,localhost` |
| `DB_ENGINE` | string | Драйвер БД | `django.db.backends.sqlite3` або `django.db.backends.postgresql` |
| `DB_NAME` | string | Назва БД або файл SQLite | `office_booking` або `db.sqlite3` |
| `DB_USER` | string | Користувач БД (PostgreSQL) | `booking_user` |
| `DB_PASSWORD` | string | Пароль БД (PostgreSQL) | `secure_password_123` |
| `DB_HOST` | string | Хост БД (PostgreSQL) | `localhost` або `db` (Docker) |
| `DB_PORT` | integer | Порт БД (PostgreSQL) | `5432` |

**Приклад `.env`:**
```env
SECRET_KEY=your-super-secret-key-here-change-in-production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com

DB_ENGINE=django.db.backends.postgresql
DB_NAME=office_booking
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=db.yourdomain.com
DB_PORT=5432
```

---

## Структура проєкту

```
office_booking/
├── office_booking/
│   ├── settings.py          # Django конфіг, підключення .env
│   ├── urls.py              # Маршрути, Swagger, Admin
│   ├── wsgi.py              # WSGI для Gunicorn
│   └── asgi.py              # ASGI для async
│
├── bookings/
│   ├── models.py            # Room, Workspace, Booking (ORM)
│   ├── serializers.py       # DRF сериалайзери з валідацією
│   ├── views.py             # ViewSets, auth endpoints
│   ├── urls.py              # Роутер для API
│   ├── security.py          # Валідація, логування безпеки
│   ├── tests.py             # Unit тести (14+)
│   ├── admin.py             # Django Admin інтеграція
│   └── migrations/          # БД міграції
│
├── Dockerfile               # Multi-stage Docker образ
├── docker-compose.yml       # PostgreSQL + Django сервіс
├── requirements.txt         # Python залежності
├── manage.py                # Django CLI
├── .env.example             # Шаблон змінних (комітиться)
├── schema.yml               # OpenAPI schema (генерується)
└── README.md                # Цей файл
```

---

## Deployment

### Docker (Рекомендовано)

#### 1️⃣ За допомогою docker-compose (для локальної розробки)

```bash
docker-compose up -d
```

Це запустить:
- **PostgreSQL** на `localhost:5432`
- **Django API** на `http://localhost:8000`

Логи:
```bash
docker-compose logs -f web
```

Зупинка:
```bash
docker-compose down -v  # -v видалить volumes
```

#### 2️⃣ Production deployment

**Збірка Docker образу:**
```bash
docker build -t office-booking:latest .
```

**Запуск контейнера:**
```bash
docker run -d \
  --name office-booking \
  -p 8000:8000 \
  -e SECRET_KEY=your-secret \
  -e DEBUG=False \
  -e DB_NAME=office_booking \
  -e DB_USER=postgres \
  -e DB_PASSWORD=secure_pass \
  -e DB_HOST=postgres-host \
  office-booking:latest
```

**За Nginx (reverse proxy):**
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
    }
}
```

---

## API Документація

| Тип | URL | Описання |
|------|-----|----------|
| **Swagger UI** | `http://localhost:8000/api/docs/` | Інтерактивна документація з "Try it out" |
| **ReDoc** | `http://localhost:8000/api/redoc/` | Альтернативна документація |
| **OpenAPI Schema** | `http://localhost:8000/api/schema/` | JSON/YAML схема для генерації клієнтів |
| **Django Admin** | `http://localhost:8000/admin/` | Управління користувачами, бронюваннями, кімнатами |

---

## Поточні обмеження і майбутні покращення

### Поточні обмеження ✋

1. ❌ **Немає пагінації** — великі набори бронювань будуть повільними
2. ❌ **Немає кешування** — кожен запит до БД
3. ❌ **Мінімальне логування** — складно відстежувати проблеми
4. ❌ **Нема сповіщень** — користувачі не знають про статус
5. ❌ **Нема аналітики** — не видно обслуговування офісу

### Планові покращення 🚀

- [ ] **Пагінація** для бронювань і робочих місць
- [ ] **Redis кешування** для частих запитів
- [ ] **Структуроване логування** та моніторинг
- [ ] **Система сповіщень** (email/webhook)
- [ ] **API версіонування** (`/api/v1/`)
- [ ] **Аналітика** та звіти про використання
- [ ] **Розширена система дозволів** (ролі, затвердження)
- [ ] **GitHub Actions** для CI/CD

---

## Внесок у проект

Вітаємо pull requests! Для великих змін спочатку відкрийте issue для обговорення.

### Процес розробки

1. Форк репозиторію
2. Створи feature гілку (`git checkout -b feature/amazing-feature`)
3. Зміни та тести (`pytest bookings/tests.py`)
4. Комітуй (`git commit -m 'Add some amazing feature'`)
5. Push у гілку (`git push origin feature/amazing-feature`)
6. Відкрий Pull Request

### Вимоги до коду

- ✅ Повинні проходити всі тести
- ✅ Код має бути читаємим з коментарями (де потрібно)
- ✅ Дотримуйся PEP 8
- ✅ Обновлюй README для нових функцій

---

## Ліцензія

MIT License — див. файл [LICENSE](LICENSE)

---

## Контакти

- **Автор**: [Oleksii Moloiko](https://github.com/Oleksii-Moloiko)
- **Проект**: [office_booking](https://github.com/Oleksii-Moloiko/office_booking)
- **Issues**: [GitHub Issues](https://github.com/Oleksii-Moloiko/office_booking/issues)

---

## Подяки

Спасибі за використання Office Booking API! 🎉

Якщо проект вам допоміг, будь ласка:
- ⭐ Залиште зірку на GitHub
- 🐛 Повідомте про баги через Issues
- 💡 Пропозиції через Discussions
- 🤝 Контрибуйте через Pull Requests
