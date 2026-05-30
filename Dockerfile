# 1. Беремо офіційний легкий образ Python
FROM python:3.11-slim

# 2. Встановлюємо змінні оточення, щоб Python не писав .pyc файли і відразу виводив логи
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Створюємо робочу директорію всередині контейнера
WORKDIR /app

# 4. Встановлюємо системні залежності, необхідні для компіляції деяких пакетів (наприклад, для PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Копіюємо файл із залежностями та встановлюємо їх
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 6. Копіюємо весь код проекту в контейнер
COPY . /app/