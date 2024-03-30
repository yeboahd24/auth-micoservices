from django.http import JsonResponse
from user.exceptions.exception import MissingRequiredFields


def handle_exception(get_response):
    def middleware(request):
        try:
            response = get_response(request)
        except MissingRequiredFields as exc:
            response_data = {
                "errors": {
                    "fields": exc.fields,
                    "message": exc.message,
                    "code": exc.code,
                }
            }
            return JsonResponse(response_data, status=400)
        return response

    return middleware

