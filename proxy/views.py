from django.http import JsonResponse, HttpResponse
import requests

import secrets_env


def matomo_api(request):
    # link to matomo api docs:
    # https://developer.matomo.org/api-reference/reporting-api
    url = "https://matomo.isof.se/"
    params = request.GET.copy()
    params['token_auth'] = secrets_env.MATOMO_TOKEN_AUTH
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return JsonResponse(response.json(), safe=False)
    else:
        return HttpResponse(status=response.status_code)