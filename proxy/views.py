import mimetypes
from django.http import JsonResponse, HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
import requests
from bs4 import BeautifulSoup

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

@xframe_options_exempt
def folke_kontext_api(request):
    """
    Returns the content from the isof-sitevision-path that is specified
    in the params "path" with an appropriate MIME type.
    """
    path = request.GET.get("path")

    if not path:
        return JsonResponse({"error": "Missing path parameter"}, status=400)

    try:
        base_url = "https://www.isof.se/"
        full_url = f"{base_url}{path}"

        # Set a timeout for the request
        response = requests.get(full_url, timeout=10)
        response.raise_for_status()  # This will raise an HTTPError for bad responses

        # Parse the response content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all <a> and <img> tags to update their 'href' and 'src' attributes
        for a in soup.find_all('a', href=True):
            if not a['href'].startswith(('http://', 'https://', '//')):
                a['href'] = "/folke_kontext_api?path=" + a['href'].lstrip('/')
                
        for img in soup.find_all('img', src=True):
            if not img['src'].startswith(('http://', 'https://', '//')):
                img['src'] = base_url + img['src'].lstrip('/')

        for script in soup.find_all('script', src=True):
            if not script['src'].startswith(('http://', 'https://', '//')):
                script['src'] = base_url + script['src'].lstrip('/')

        for link in soup.find_all('link', href=True):
            if not link['href'].startswith(('http://', 'https://', '//')):
                link['href'] = base_url + link['href'].lstrip('/')

        # Guess the MIME type based on the file extension
        mime_type, _ = mimetypes.guess_type(full_url)
        if mime_type is None:
            # Default to 'text/html' if MIME type could not be guessed
            mime_type = "text/html"

        # Return modified HTML content
        return HttpResponse(str(soup), content_type=mime_type)

    except requests.exceptions.Timeout:
        return JsonResponse({"error": "The request timed out"}, status=504)
    except requests.exceptions.HTTPError as e:
        return JsonResponse(
            {"error": f"HTTP Error: {e}"}, status=e.response.status_code
        )
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": f"Request exception: {e}"}, status=500)


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
