FROM python:3.12-slim-bookworm

# Установка системных зависимостей для psycopg2-binary и других пакетов
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry с оптимизацией кэша
RUN pip install --no-cache-dir --upgrade pip poetry

# Настройка Poetry
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Рабочая директория
WORKDIR /code

# Создаем README.md если его нет (чтобы избежать ошибки)
RUN touch README.md

# Копируем зависимости отдельно для кэширования
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости без текущего проекта
RUN poetry install --only main --no-interaction --no-ansi --no-root

# Копируем остальные файлы проекта
COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]