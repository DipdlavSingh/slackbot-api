from django.urls import path
from .views import *

urlpatterns = [
    path('', Events.as_view()),
    path('channels/', Channels.as_view()),
    path('message/', Message.as_view()),
    path('login/', Login.as_view()),
    path('auth/', Auth.as_view()),
]
