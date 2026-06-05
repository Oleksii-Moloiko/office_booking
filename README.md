# 🏢 Office Booking API

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)]()
[![Django](https://img.shields.io/badge/Django-5.0-darkgreen?logo=django)]()
[![DRF](https://img.shields.io/badge/DRF-REST_API-red)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)]()
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)]()
[![Coverage](https://img.shields.io/badge/Coverage-91%25-brightgreen)]()
[![Tests](https://img.shields.io/badge/Tests-30_Passed-success)]()
[![License](https://img.shields.io/badge/License-MIT-yellow)]()

REST API для бронювання робочих місць в офісі або коворкінгу.

Проєкт демонструє побудову production-ready backend-сервісу з:

- JWT Authentication with access and refresh tokens
- бізнес-логікою бронювання
- захистом від конфліктів часу
- ролями користувачів
- OpenAPI документацією
- Docker контейнеризацією
- автоматизованим тестуванням

---

## 🎯 Business Problem

У великих офісах та коворкінгах співробітники повинні бронювати робочі місця заздалегідь.

Основні проблеми:

- подвійне бронювання одного столу;
- складність пошуку вільних місць;
- контроль доступу користувачів;
- масштабування системи під велику кількість бронювань.

Office Booking API вирішує ці задачі через централізований REST API.

---

## 🏗️ Architecture

```bash
Client
   │
   ▼
Django REST Framework
   │
   ├── Authentication
   ├── Permissions
   ├── Validation Layer
   │
   ▼
Business Logic
   │
   ├── Booking Conflict Detection
   ├── Availability Calculation
   └── User Access Rules
   │
   ▼
PostgreSQL
```

---

### Main Components

| Layer | Responsibility |
|---------|--------------|
| Models | Data structure |
| Serializers | Validation and transformation |
| Views | API endpoints |
| Permissions | Access control |
| Security | Password & email validation |
| Tests | Business logic verification |

---

## 🚀 Features

### Authentication

- User Registration
- JWT Authentication
- Access and Refresh Tokens
- Password Validation
- Rate Limiting

### Booking Management

- Create Booking
- Cancel Booking
- Update Booking
- View Own Bookings

### Workspace Search

- Filter by date
- Filter by room
- Filter by monitor availability
- Filter by time range

### Security

- Environment variables
- CSRF protection
- Secure cookies
- Conflict prevention
- Logging

---

## 🛠️ Tech Stack

### Backend

- Python 3.11
- Django 5
- Django REST Framework

### Database

- PostgreSQL
- SQLite (development)

### DevOps

- Docker
- Docker Compose
- Gunicorn
- WhiteNoise

### Documentation

- OpenAPI 3
- drf-spectacular
- Swagger UI

### Testing

- Django TestCase
- APIClient
- Coverage.py

---

## 🧪 Testing & Quality

### Test Results

```bash
Ran 30 tests in 5.5s

OK
```

### Coverage
```bash
TOTAL 91%
```

```bash
Module

Coverage

Models

90%

Views

91%

Security

95%

Tests

100%

Total

91%
```

Project quality is verified through automated tests covering:

* authentication
* permissions
* booking conflicts
* validation rules
* security checks

---

## Authentication

The API uses JWT authentication via `djangorestframework-simplejwt`.

After registration or login, the API returns two tokens:

- `access` — used to authorize API requests.
- `refresh` — used to obtain a new access token.

### Register

```http
POST /api/auth/register/
Content-Type: application/json
```

```json
{
  "username": "user@example.com",
  "password": "SecurePass123!"
}
```

Response:

```json
{
  "refresh": "refresh_token_here",
  "access": "access_token_here"
}
```

### Login

```http
POST /api/auth/login/
Content-Type: application/json
```

```json
{
  "username": "user@example.com",
  "password": "SecurePass123!"
}
```

Response:

```json
{
  "refresh": "refresh_token_here",
  "access": "access_token_here"
}
```

### Authorized requests

Use the access token in the Authorization header:

```http
Authorization: Bearer your_access_token_here
```

Example:

```bash
curl http://127.0.0.1:8000/api/workspaces/ \
  -H "Authorization: Bearer your_access_token_here"
```

### Refresh access token

```http
POST /api/auth/token/refresh/
Content-Type: application/json
```

```json
{
  "refresh": "your_refresh_token_here"
}
```

Response:

```json
{
  "access": "new_access_token_here"
}
```

---

## 📚 What I Learned From This Project

While building this project I gained practical experience with:

### Django & DRF

- designing REST APIs

- serializers and validation

- authentication & permissions

- custom business logic

### Database Design

- model relationships

- query optimization

- uniqueness constraints

- conflict detection

### Security

- environment-based configuration

- password validation

- secure cookies

- rate limiting

### Testing

- unit testing

- API testing

- coverage analysis

- edge-case validation

### DevOps

- Docker containerization

- environment variables

- production configuration

### Software Engineering

- clean project structure

- separation of concerns

- API documentation

- maintainable codebase

---

## ⭐ Portfolio Highlights

This project demonstrates:

✔ REST API Development

✔ Backend Architecture

✔ Database Design

✔ Authentication & Authorization

✔ Automated Testing

✔ Docker Deployment

✔ API Documentation

✔ Production Security Practices