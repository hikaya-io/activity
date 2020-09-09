from django.views.generic import TemplateView
from django.urls import path


urlpatterns = [
    path('comingsoon', TemplateView.as_view(template_name='formlibrary/comingsoon.html')),
]
