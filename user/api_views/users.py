from django.http import JsonResponse
from django.views.decorators.http import require_GET
from user.models import CustomUser
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator


@csrf_exempt
@require_GET
def get_users(request):
    if not request.user.has_perm("user.view_user"):
        raise PermissionDenied

    try:
        users = CustomUser.objects.values(
            "profile_id", "email", "first_name", "last_name", "maker"
        ).order_by("email")

        # Get the page parameter from the request
        page_number = request.GET.get("page", 1)

        # Create a paginator object
        paginator = Paginator(users, 10)  # Show 10 users per page

        # Get the page of users for the requested page number
        page_obj = paginator.get_page(page_number)

        # Prepare the response data
        response_data = {
            "users": list(page_obj.object_list),
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number,
        }

        return JsonResponse(response_data, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
