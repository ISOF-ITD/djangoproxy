from django.http import JsonResponse

def api_root(request):
    """Returns a JSON response containing a list of all API endpoints."""
    return JsonResponse(
        {
            "matomo_api": request.build_absolute_uri("matomo_api"),
            "folke_kontext_api": request.build_absolute_uri("folke_kontext_api"),
            "google_search_keywords_api": request.build_absolute_uri("google_search_keywords_api"),
        }
    )

