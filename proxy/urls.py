"""proxy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.conf.urls import url

from . import views
from .matomo_api import matomo_api
from .folke_kontext_api import folke_kontext_api
from .google_search_keywords_api import get_search_keywords_api

urlpatterns = [
    url(r'^matomo_api/', matomo_api, name='matomo_api'),
    url(r'^folke_kontext_api/', folke_kontext_api, name='folke_kontext_api'),
    url(r'google_search_keywords_api/', get_search_keywords_api, name='google_search_keywords_api'),
]
