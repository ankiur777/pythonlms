from django.db import connection
from django.utils import timezone
from redis import Redis
from rest_framework.response import Response
from rest_framework.views import APIView

from config.settings import REDIS_URL


class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        checks: dict[str, str] = {}
        status_code = 200
        try:
            connection.ensure_connection()
            checks["database"] = "ok"
        except Exception:
            checks["database"] = "unavailable"
            status_code = 503
        try:
            Redis.from_url(REDIS_URL, socket_connect_timeout=1).ping()
            checks["redis"] = "ok"
        except Exception:
            checks["redis"] = "unavailable"
            status_code = 503
        response = {
            "status": "ok" if status_code == 200 else "degraded",
            "checks": checks,
            "timestamp": timezone.now(),
        }
        return Response(response, status=status_code)
