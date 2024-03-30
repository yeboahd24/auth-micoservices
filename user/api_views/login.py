from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from user.exceptions.exception import MissingRequiredFields
import json
from user.utils import generate_and_send_otp, generate_token


@csrf_exempt
@require_POST
def login_view(request):
    try:
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")

        if not email:
            raise MissingRequiredFields("email")
        if not password:
            raise MissingRequiredFields("password")

        user = authenticate(request, email=email, password=password)

        if user is None:
            return JsonResponse({"error": "Invalid credentials"}, status=401)

        if not user.is_active:
            return JsonResponse({"error": "User is not active"}, status=401)

        token = generate_token(user)

        is_otp_sent = generate_and_send_otp(user.email)

        if is_otp_sent:
            return JsonResponse(
                {"message": f"OTP sent to {user.email}", "token": token}, status=200
            )

        return JsonResponse({"error": "Unexpected error occurred"}, status=500)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
