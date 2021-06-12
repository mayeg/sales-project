from django.urls import path

from swagger.views import yaml_to_html

urlpatterns = [
    path('', yaml_to_html),
]
