from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from user.utils import decode_token, validate_token
import logging
import re
import jwt

CustomUser = get_user_model()


# List of paths to exclude from authentication
EXCLUDED_PATHS = ["/api/v1/user/health-check/", "/api/v1/user/login/", "/admin/"]
EXCLUDED_PATHS_REGEX = re.compile(r"^(%s)" % "|".join(EXCLUDED_PATHS))
logger = logging.getLogger(__name__)


class AuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        print("process_request")
        # Exclude paths from authentication
        if EXCLUDED_PATHS_REGEX.match(request.path_info):
            return None

        # Get the token from the Authorization header
        token = request.headers.get("Authorization", "").split(" ")[-1]

        if not token:
            logger.warning(
                "Authentication credentials not provided for %s", request.path_info
            )
            return JsonResponse(
                {"error": "Authentication credentials were not provided."}, status=401
            )

        try:
            # Validate the token
            if not validate_token(token):
                logger.warning("Invalid token for %s", request.path_info)
                return JsonResponse({"error": "Invalid token."}, status=401)

            # Decode the token and get the payload
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            logger.warning("Expired token for %s", request.path_info)
            return JsonResponse({"error": "Token has expired."}, status=401)

        # Get the user from the payload
        user_id = payload.get("user_id")
        try:
            user = CustomUser.objects.get(profile_id=user_id)
        except CustomUser.DoesNotExist:
            logger.warning("User not found for %s", request.path_info)
            return JsonResponse({"error": "User not found."}, status=401)

        # Set the authenticated user on the request
        request.user = user

    def process_response(self, request, response):
        return response
