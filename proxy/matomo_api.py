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
