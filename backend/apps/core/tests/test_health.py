from unittest.mock import patch

import pytest
from django.test import override_settings
from rest_framework.test import APIClient


@pytest.mark.django_db
@override_settings(REDIS_URL="redis://test:6379/0")
@patch("apps.core.views.Redis.from_url")
def test_health_returns_dependencies(mock_redis):
    mock_redis.return_value.ping.return_value = True
    response = APIClient().get("/api/v1/health/")
    assert response.status_code == 200
    assert response.data["status"] == "ok"
    assert response.data["checks"] == {"database": "ok", "redis": "ok"}

