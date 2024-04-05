from django.http import JsonResponse

def api_root(request):
    """Returns a JSON response containing a list of all API endpoints.

    Args:
        request: A Django HTTP request object.

    Returns:
        A JsonResponse object containing a dictionary with all API endpoints.

    Raises:
        N/A
    """
    return JsonResponse(
        {
            "matomo_api": request.build_absolute_uri("matomo_api"),
            "folke_kontext_api": request.build_absolute_uri("folke_kontext_api")
        }
    )
