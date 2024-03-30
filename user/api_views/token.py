from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import permission_required
import json
from user.utils import validate_token, revoke_token
from user.exceptions.exception import MissingRequiredFields
import jwt


@csrf_exempt
@require_POST
@permission_required("user.view_user")
def verif_token(request):
    try:
        data = json.loads(request.body)
        token = data.get("token")
        if not token:
            raise MissingRequiredFields("token")

        if not validate_token(token):
            return JsonResponse({"error": "Invalid token."}, status=401)

        return JsonResponse({"message": "Token is valid."}, status=200)

    except json.decoder.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)

    except jwt.exceptions.InvalidTokenError:
        return JsonResponse({"error": "Token has been revoked."}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_POST
@permission_required("user.revoke_token")
def remove_token_view(request):
    try:
        data = json.loads(request.body)
        token = data.get("token")
        if not token:
            raise MissingRequiredFields("token")

        # Revoke the token
        revoke_token(token)

        return JsonResponse({"message": "Token revoked successfully."}, status=200)
    except jwt.exceptions.InvalidTokenError:
        return JsonResponse({"error": "Token has been revoked."}, status=400)
    except json.decoder.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
