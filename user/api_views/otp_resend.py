from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from user.utils import generate_and_send_otp, get_user_from_token
from django.core.exceptions import ValidationError


@csrf_exempt
@require_POST
def resend_otp(request):
    token = request.headers.get("Authorization", "").split(" ")[-1]

    try:
        user = get_user_from_token(token)

    except ValidationError:
        return JsonResponse({"message": "Invalid token", "status": 401}, status=401)

    email = user.email
    is_otp_sent = generate_and_send_otp(email)

    if is_otp_sent:
        return JsonResponse(
            {"message": f"OTP sent to {email}", "status": 200}, status=200
        )

    return JsonResponse({"message": "OTP could not be sent", "status": 400}, status=400)
