from django.urls import path

from .views import *

urlpatterns = [
    path('<str:pk>/products/', WarehouseProductsAPIView.as_view()),
    path('<str:ware_pk>/products/<str:pr_pk>/', WarehouseProductDetailAPIView.as_view()),
    path('<str:pk>/customers/', WarehouseCustomersAPIView.as_view()),
    path('<str:pk>/employees/', WarehouseEmployeesAPIView.as_view()),
    path('<str:pk>/orders/', WarehouseOrdersAPIView.as_view()),
    path('<str:pk>/tasks/', WarehouseTasksAPIView.as_view()),
    path('all/', WarehousesAPIView.as_view()),
    path('details/<str:pk>/', WarehouseDetailsView.as_view()),
    path('warehouse_product/create/', WarehouseProductCreate.as_view()),
    path('warehouse_product/arrival/', WarehouseProductArrivalView.as_view()),
]
