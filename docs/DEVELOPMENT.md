# Development Guide

## Prerequisites

Use Docker Desktop with Docker Compose for the full stack. For host execution, install Python 3.13+ and Node.js 22+; PostgreSQL 16 and Redis 7 must be reachable using the `.env` connection values.

Backend tests use SQLite through `DJANGO_USE_SQLITE=true`, so they remain deterministic without a local PostgreSQL service. Docker and all runtime environments use PostgreSQL.

## Start the stack

```powershell
Copy-Item .env.example .env
docker compose up --build
```

This starts PostgreSQL, Redis, Django/DRF, Celery, and Vite. The backend startup runs migrations. Open `http://localhost:5173`; query `http://localhost:8000/api/v1/health/` to confirm database and Redis status.

## Production configuration

Use `docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d` only with a production `.env` provided by a secret manager. Set `DJANGO_ENV=production`, `DJANGO_DEBUG=false`, a unique `DJANGO_SECRET_KEY`, production hosts/origins, strong database credentials, and a TLS-terminating reverse proxy/load balancer. PostgreSQL and Redis ports are deliberately not public in the production override.

## Quality checks

```powershell
docker compose exec backend python manage.py check
docker compose exec backend ruff check .
docker compose exec backend pytest
docker compose exec frontend npm run lint
docker compose exec frontend npm run test -- --run
docker compose exec frontend npm run build
docker compose exec worker celery -A config inspect ping
```
