# djangoproxy
Django application that acts as reverse proxy.

Use the proxy view to proxy requests to (internal) servers. This is useful when you want to make requests to internal servers from the browser. The proxy view will add the authentication token or any other param or header to the request and forward it to the internal server.

## Add a proxy view

Example for a proxy view that proxies requests to the example.com server:

**urls.py**:

```python
urlpatterns = [
    url(r'^example_api/', views.example_api, name='example_api'),
]
```

**views.py**:

```python
def example_api(request):
    url = 'http://example.com/api/'
    params = request.GET.copy()
    # add params to the request
    params['param1'] = 'value1'
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return JsonResponse(response.json(), safe=False)
    else:
        return HttpResponse(status=response.status_code)
```
