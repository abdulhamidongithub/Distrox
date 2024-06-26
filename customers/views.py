from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .models import CustomerStore
from .serializers import *

class CustomersAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('search', openapi.IN_QUERY, description="You can search by name, address, phone", type=openapi.TYPE_STRING)
    ])
    def get(self, request):
        customers = CustomerStore.objects.filter(archived = False)
        search = request.query_params.get("search")
        if search:
            customers = customers.filter(name__icontains=search
                        ) | customers.filter(address__icontains = search
                        ) | customers.filter(phone__icontains = search)
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(customers, request)
        serializer = CustomerStoreSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(request_body=CustomerStoreSerializer)
    def post(self, request):
        serializer = CustomerStoreSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(added_by = request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)

class CustomerDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        customer = get_object_or_404(CustomerStore.objects.filter(archived = False), id=pk)
        serializer = CustomerStoreSerializer(customer)
        return Response(serializer.data)

    def delete(self, request, pk):
        customer = get_object_or_404(CustomerStore.objects.all(), id=pk)
        if request.user.role == 'admin' and customer.archived == True:
            customer.delete()
            return Response({"success": "true", "message": "Customer deleted"})
        customer.archived = True
        customer.save()
        return Response({"success": "true", "message": "Customer arxivlandi"})

    @swagger_auto_schema(request_body=CustomerStoreSerializer)
    def put(self, request, pk):
        customer = get_object_or_404(CustomerStore.objects.all(), id=pk)
        serializer = CustomerStoreSerializer(customer, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class ArchivedCustomersView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        customers = CustomerStore.objects.filter(archived = True)
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(customers, request)
        serializer = CustomerStoreSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


