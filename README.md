# djangoproxy
Django application that acts as reverse proxy.

Use the proxy view to proxy requests to (internal) servers. This is useful when you want to make requests to internal servers from the browser. The proxy view will add the authentication token or any other param or header to the request and forward it to the internal server.

## Add a proxy view

Example for a proxy view that proxies requests to the example.com server and adds an authentication token to the request:

**secret_env.py**:

```python
example_auth_token = '1234567890'
```

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
    params['auth_token'] = secrets_env.example_auth_token
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return JsonResponse(response.json(), safe=False)
    else:
        return HttpResponse(status=response.status_code)
```

## Call the proxy view with React

```javascript	
fetch('https://djangoproxy.isof.se/example_api/?param1=value1&param2=value2')
    .then(response => response.json())
    .then(data => console.log(data));
```

