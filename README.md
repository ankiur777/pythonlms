# Python LMS

Production-oriented Python learning platform foundation.

## Services

- `backend`: Django/DRF API (`8000`)
- `frontend`: React/TypeScript/Tailwind (`5173`)
- `db`: PostgreSQL 16 (`5432`)
- `redis`: Redis 7 (`6379`)
- `worker`: Celery worker

Copy `.env.example` to `.env`, then run `docker compose up --build`. The API health endpoint is `http://localhost:8000/api/v1/health/` and the web UI is `http://localhost:5173`.

## Checks

```powershell
docker compose exec backend python manage.py check
docker compose exec backend pytest
docker compose exec backend ruff check .
docker compose exec frontend npm run lint
docker compose exec frontend npm run test -- --run
docker compose exec worker celery -A config inspect ping
```

*** Add File: C:\Users\nitee\Downloads\python-lms\docker-compose.yml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-lms}
      POSTGRES_USER: ${POSTGRES_USER:-lms}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-change-me}
    ports: ["${POSTGRES_PORT:-5432}:5432"]
    volumes: ["postgres_data:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 10
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 10
  backend:
    build: { context: ./backend, target: development }
    env_file: .env
    environment: { POSTGRES_HOST: db, REDIS_URL: redis://redis:6379/0 }
    command: >
      sh -c "python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"
    ports: ["8000:8000"]
    volumes: ["./backend:/app"]
    depends_on:
      db: { condition: service_healthy }
      redis: { condition: service_healthy }
  worker:
    build: { context: ./backend, target: development }
    env_file: .env
    environment: { POSTGRES_HOST: db, REDIS_URL: redis://redis:6379/0 }
    command: celery -A config worker --loglevel=INFO
    volumes: ["./backend:/app"]
    depends_on:
      db: { condition: service_healthy }
      redis: { condition: service_healthy }
  frontend:
    build: { context: ./frontend, target: development }
    environment: { VITE_API_BASE_URL: http://localhost:8000/api/v1 }
    command: npm run dev -- --host 0.0.0.0
    ports: ["5173:5173"]
    volumes: ["./frontend:/app", "/app/node_modules"]
    depends_on: [backend]
volumes:
  postgres_data:

