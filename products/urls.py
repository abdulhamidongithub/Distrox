from django.urls import path

from .views import *

urlpatterns = [
    path('all/', ProductsAPIView.as_view()),
]

