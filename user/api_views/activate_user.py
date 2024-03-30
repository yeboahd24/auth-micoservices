from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

User = get_user_model()


@csrf_exempt
@require_http_methods(["POST"])
def activate_user(request):
    if not request.user.has_perm("user.suspend_user"):
        return JsonResponse({"error": "Permission denied."}, status=403)

    try:
        data = json.loads(request.body)
        user = User.objects.get(profile_id=data.get("profile_id"))
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)

    if not user.is_active:
        user.is_active = True
        user.save()
        return JsonResponse(
            {"success": f"User '{user.first_name}' has been activated."}, status=200
        )
    else:
        return JsonResponse(
            {"error": f"User '{user.first_name}' is already active."}, status=400
        )
