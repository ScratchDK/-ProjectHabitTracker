# Project Online School - Django с Docker

Проект онлайн-школы на Django, развертываемый с помощью Docker.


## Требования

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.12 (уже включен в образ)


## Быстрый старт

1. Склонируйте репозиторий:
    ```bash
    git clone https://github.com/ScratchDK/online-school.git
    cd projectonlineschool
   
2. Создайте файл .env на основе .env.example:
    ```bash
    cp .env.example .env
   
3. Запустите проект:
    ```bash
    docker-compose up -d --build
   

## Проверка работы сервисов

1. Django (веб-сервер)
- URL: http://localhost:8000
- Проверить статус:
    ```bash
    docker-compose exec web python manage.py check
  
2. PostgreSQL (база данных)
- Проверить подключение:
    ```bash
    docker-compose exec db psql -U ваш_пользователь -d ваша_база
  
3. Redis
- Проверить работу:
    ```bash
    docker-compose exec redis redis-cli ping
Должен вернуть PONG

4. Celery (воркер)
- Просмотр логов:
    ```bash
    docker-compose logs celery
  
5. Celery Beat (планировщик)
- Просмотр логов:
    ```bash
  docker-compose logs celery_beat
Должны быть сообщения beat: Starting...


## Управление сервисами
- Остановить все сервисы:
    ```bash
    docker-compose down

- Очистить кеш:
    ```bash
    docker builder prune -af
Удаляет все данные сборщика, включая неиспользуемые и используемые кэши.

- Перезапустить конкретный сервис (например, web):
    ```bash
    docker-compose restart web

- Просмотр логов всех сервисов:
    ```bash
    docker-compose logs -f
  

## Дополнительные команды
- Django миграции
    ```bash
    docker-compose exec web python manage.py makemigrations
    docker-compose exec web python manage.py migrate
  
- Создание суперпользователя
    ```bash
    docker-compose exec web python manage.py createsuperuser
  
- Пересбор контейнеров:
    ```bash
    docker-compose up -d --build