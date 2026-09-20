from celery import shared_task


@shared_task(name="apps.core.health_check")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

