from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from user.utils import generate_password
from user.tasks import send_user_credentials
from django.contrib.auth import get_user_model
from user.exceptions.exception import MissingRequiredFields
from django.core.exceptions import PermissionDenied

CustomUser = get_user_model()


@csrf_exempt
@require_POST
def signup(request):
    try:
        if not request.user.has_perm("user.create_user"):
            raise PermissionDenied

        data = json.loads(request.body)
        email = data.get("email")
        first_name = data.get("first_name")
        last_name = data.get("last_name")

        if not email:
            raise MissingRequiredFields("email")
        if not first_name:
            raise MissingRequiredFields("first_name")
        if not last_name:
            raise MissingRequiredFields("last_name")

        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already exists"}, status=400)

        password = generate_password()

        user = CustomUser.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            maker=request.user.email,
        )

        user.set_password(password)
        user.save()

        send_user_credentials.delay(email=email, password=password)

        return JsonResponse(
            {"message": "User created successfully, check your email"}, status=201
        )

    except PermissionDenied:
        return JsonResponse({"error": "Permission denied."}, status=403)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
