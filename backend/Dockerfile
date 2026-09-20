FROM python:3.13-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
RUN addgroup --system app && adduser --system --ingroup app app
COPY requirements/base.txt /tmp/requirements/base.txt
RUN pip install --no-cache-dir -r /tmp/requirements/base.txt
COPY . .
RUN chown -R app:app /app
USER app
FROM base AS development
USER root
COPY requirements/dev.txt /tmp/requirements/dev.txt
RUN pip install --no-cache-dir -r /tmp/requirements/dev.txt
USER app
FROM base AS production
RUN python manage.py collectstatic --noinput

