from django.http import JsonResponse
from django.db import connections
from django.core.cache import caches
from django.utils import timezone

HEALTH_CHECK_CACHE_KEY = "health_check"
HEALTH_CHECK_CACHE_TIMEOUT = 30


def health_check(request):
    cache = caches["default"]
    cached_data = cache.get(HEALTH_CHECK_CACHE_KEY)

    if cached_data and cached_data["expires"] > timezone.now():
        return JsonResponse(cached_data["data"])

    data = {"status": "ok", "message": "Application is running.", "checks": []}

    # Check database connection
    try:
        connections["default"].cursor().execute("SELECT 1")
        data["checks"].append({"name": "database", "status": "ok"})
    except Exception as e:
        data["status"] = "error"
        data["checks"].append(
            {"name": "database", "status": "error", "message": str(e)}
        )

    # Check cache
    try:
        cache.set(HEALTH_CHECK_CACHE_KEY, "ok", timeout=HEALTH_CHECK_CACHE_TIMEOUT)
        data["checks"].append({"name": "cache", "status": "ok"})
    except Exception as e:
        data["status"] = "error"
        data["checks"].append({"name": "cache", "status": "error", "message": str(e)})

    cache_expires = timezone.now() + timezone.timedelta(
        seconds=HEALTH_CHECK_CACHE_TIMEOUT
    )
    cache.set(
        HEALTH_CHECK_CACHE_KEY,
        {"data": data, "expires": cache_expires},
        timeout=HEALTH_CHECK_CACHE_TIMEOUT,
    )

    return JsonResponse(data)

