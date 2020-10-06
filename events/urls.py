from django.urls import path
from .views import *

urlpatterns = [
    path('', Events.as_view()),
]
