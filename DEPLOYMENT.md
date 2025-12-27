# Deployment Guide

## 1. Prerequisites
- Docker & Docker Compose
- AWS Account (EC2/RDS) or Render/Railway
- Domain name

## 2. Docker Compose (`docker-compose.yml`)
```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: food_delivery
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7

  web:
    build: .
    command: daphne -b 0.0.0.0 -p 8000 food_delivery.asgi:application
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    env_file:
      - .env

  celery:
    build: .
    command: celery -A food_delivery worker -l info
    depends_on:
      - redis
    env_file:
      - .env

volumes:
  postgres_data:
```

## 3. Production Settings
- Set `DEBUG = False`.
- Set `ALLOWED_HOSTS` to your domain.
- Configure `DATABASES` to point to RDS/Postgres container.
- Configure `CHANNEL_LAYERS` to use `channels_redis`.

## 4. Nginx Configuration
Use Nginx as a reverse proxy to handle SSL and route traffic.
- `/static/` -> serve static files.
- `/ws/` -> proxy_pass to `http://web:8000` with Upgrade headers.
- `/` -> proxy_pass to `http://web:8000`.

## 5. CI/CD
- Use GitHub Actions to build Docker images and push to ECR/DockerHub.
- Use `watchtower` or SSH commands to pull new images on the server.
