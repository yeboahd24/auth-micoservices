import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib.auth import login
from django.core.cache import cache
from django.conf import settings
from user.utils import get_user_from_token, generate_token
from django.core.exceptions import ValidationError
from user.exceptions.exception import MissingRequiredFields


@csrf_exempt
@require_POST
def otp_verification_view(request):
    token = request.headers.get("Authorization", "").split(" ")[-1]
    try:
        user = get_user_from_token(token)
    except ValidationError as e:
        return JsonResponse({"message": "Invalid token", "status": 401}, status=401)

    try:
        data = json.loads(request.body)
        otp = data.get("otp")
    except (json.JSONDecodeError, KeyError):
        return JsonResponse(
            {"message": "Invalid request data", "status": 400}, status=400
        )

    if not otp:
        return JsonResponse({"message": "OTP is required", "status": 400}, status=400)

    email = user.email

    # Verify the OTP
    email_cache_key = f"{email}_otp"
    code = cache.get(email_cache_key)

    if code != otp:
        return JsonResponse(
            {"message": "Invalid OTP provided.", "status": 400}, status=400
        )

    otp_expiration_time = settings.OTP_CACHE_TIMEOUT
    current_time = timezone.now()
    sent_time = cache.get(f"email_sent_at_{email}")

    if (
        sent_time is None
        or (current_time - sent_time).total_seconds() > otp_expiration_time
    ):
        return JsonResponse(
            {"error": "OTP has expired. Please request for a new code.", "status": 400},
            status=400,
        )

    # Delete the OTP key from cache once verified
    cache.delete(email_cache_key)

    token = generate_token(user)
    login(request, user, backend="user.custom_backend.AuthenticateUser")

    return JsonResponse(
        {
            "message": f"OTP verified for {email}. User logged in.",
            "status": 200,
            "data": {
                "profile_id": user.profile_id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
        },
        status=200,
    )
