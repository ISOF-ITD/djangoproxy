from django.http import JsonResponse, HttpResponse
import requests

import secrets_env


# this function is used to proxy requests to the matomo api
# it is used to to not expose the matomo token_auth to the client
def matomo_api(request):
    """Returns a JSON response containing the result of a request to the ISOF Matomo API.

    Args:
        request: A Django HTTP request object.

    Returns:
        A JsonResponse object containing the result of the request to the ISOF Matomo API.

    Raises:
        N/A
    """
    # link to matomo api docs:
    # https://developer.matomo.org/api-reference/reporting-api
    url = "https://matomo.isof.se/"
    params = request.GET.copy()
    params["token_auth"] = secrets_env.MATOMO_TOKEN_AUTH
    response = requests.get(url, params=params, timeout=5)
    # print the whole url sent to matomo
    print(response.url)
    if response.status_code == 200:
        return JsonResponse(response.json(), safe=False)
    else:
        return HttpResponse(status=response.status_code)
    # when not providing any params, view a list of possible parameters


def folke_kontext_api(request):
    """
    Returns the HTML-content from the isof-sitevision-path that is specified
    in the params "path"
    """
    path = request.GET.get('path')
    
    if not path:
        return JsonResponse({'error': 'Missing path parameter'}, status=400)
    
    try:
        base_url = "https://www.isof.se/"
        full_url = f"{base_url}{path}"
        
        # Set a timeout for the request
        response = requests.get(full_url, timeout=10)
        
        response.raise_for_status()  # This will raise an HTTPError for bad responses
        return HttpResponse(response.text, content_type="text/html")
    
    except requests.exceptions.Timeout:
        return JsonResponse({'error': 'The request timed out'}, status=504)
    except requests.exceptions.HTTPError as e:
        # Handle different HTTP errors separately or all at once
        return JsonResponse({'error': f'HTTP Error: {e}'}, status=e.response.status_code)
    except requests.exceptions.RequestException as e:
        # A base class for all requests' exceptions
        # This can be used to catch all the specific exceptions
        return JsonResponse({'error': f'Request exception: {e}'}, status=500)


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
            "folke-kontext-api": request.build_absolute_url("folke-kontext-api"),
        }
    )
