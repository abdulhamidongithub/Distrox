from django.urls import path

from .views import *

urlpatterns = [
    path('get_token/', MyTokenObtainPairView.as_view()),
    path('refresh_token/', MyTokenRefreshView.as_view()),
    path('change_password/', ChangePasswordAPIView.as_view()),

    path('salary_payments/', UserSalaryPaymentsAPIView.as_view()),
    path('details/<str:pk>/', UserAPIView.as_view()),
    path('all/', UsersAPIView.as_view()),
    path('car/<str:pk>/', CarUpdateAPIView.as_view()),
    path('task_create/', TaskCreateAPIView.as_view()),
]

