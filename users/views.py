from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_yasg import openapi
from datetime import datetime
from django.db.models import Sum
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.pagination import PageNumberPagination
import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from django.conf import settings

from .models import *
from orders.models import Order, KPIEarning
from orders.serializers import OrderSerializer
from .serializers import *

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UsersAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('role', openapi.IN_QUERY, description="Search by role", type=openapi.TYPE_STRING),
        openapi.Parameter('warehouse_id', openapi.IN_QUERY, description="Search by warehouse id", type=openapi.TYPE_STRING),
        openapi.Parameter('page', openapi.IN_QUERY, description="Search by page", type=openapi.TYPE_STRING),
    ])
    def get(self, request):
        users = CustomUser.objects.filter(archived = False)
        roles = request.query_params.get("role")
        warehouse_id = request.query_params.get("warehouse_id")
        page = request.query_params.get("page")
        if warehouse_id:
            users = users.filter(warehouse__id = warehouse_id)
        if roles:
            roles = roles.split("-")
            users = users.filter(role=roles[0])
            for role in roles[1:]:
                users = users | CustomUser.objects.filter(role=role, archived=False)
        if page:
            paginator = PageNumberPagination()
            result_page = paginator.paginate_queryset(users, request)
            serializer = UserSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=UserSerializer)
    def post(self, request):
        user = request.data
        serializer = UserCreateSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        SalaryParams.objects.create(
            user=user,
            fixed=0,
            kpi_by_sales=0
        )
        return Response(serializer.data, status.HTTP_201_CREATED)


class UserAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        user = get_object_or_404(CustomUser.objects.all(), id=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=UserSerializer)
    def put(self, request, pk):
        saved_user = get_object_or_404(CustomUser.objects.all(), id=pk)
        data = request.data
        if saved_user.is_available and data.get("is_available") == False:
            orders = Order.objects.filter(driver=saved_user, status='Active')
            if orders:
                return Response({
                    "success": "false", "message": "Active orderlar mavjud",
                    "orders": OrderSerializer(orders, many=True).data
                }, status.HTTP_400_BAD_REQUEST)
        serializer = UserCreateSerializer(instance=saved_user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        user = get_object_or_404(CustomUser.objects.all(), id=pk)
        if request.user.role == 'admin' and user.archived:
            user.delete()
            return Response({"success": "true", "message": "deleted"})
        user.archived = True
        user.save()
        return Response({"success": "true", "message": "User arxivlandi"}, status.HTTP_200_OK)

class UserAPIView2(APIView):
    # User details based on the token
    def get(self, request, access_token):
        try:
            token = AccessToken(access_token)
            user_id = token.payload['user_id']
            user = CustomUser.objects.get(id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except Exception as e:
            return Response({"success": "false", "message": "User not found"}, status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=UserSerializer)
    def put(self, request, access_token):
        try:
            token = AccessToken(access_token)
            user_id = token.payload['user_id']
            saved_user = CustomUser.objects.get(id=user_id)
            data = request.data
            if saved_user.is_available and data.get("is_available") == False:
                orders = Order.objects.filter(driver = saved_user, status = 'Active')
                if orders:
                    return Response({
                        "success": "false", "message": "Active orderlar mavjud",
                        "orders": OrderSerializer(orders, many=True).data
                    }, status.HTTP_400_BAD_REQUEST)
            serializer = UserCreateSerializer(instance=saved_user, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except Exception as e:
            return Response({"success": "false", "message": "User not found"}, status.HTTP_400_BAD_REQUEST)


class UserSalaryPaymentsAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        salary_payments = SalaryPayment.objects.filter(user=user)
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(salary_payments, request)
        serializer = SalaryPaymentSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(request_body=SalaryPaymentSerializer)
    def post(self, request):
        data = request.data
        serializer = SalaryPaymentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        existing_payment = SalaryPayment.objects.filter(
            user=serializer.validated_data['user'],
            month=serializer.validated_data['month'],
            year=serializer.validated_data['year']
        ).exists()
        if existing_payment:
            return Response({
                "success": "false",
                "message": "Salary payment for this user and month already exists.",
                "salary_payment": SalaryPaymentSerializer(existing_payment).data
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(payer=request.user)
        return Response(serializer.data)

class CarUpdateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(request_body=CarSerializer)
    def put(self, request, pk):
        car = get_object_or_404(Car.objects.all(), id=pk)
        serializer = CarSerializer(instance=car, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            car = serializer.save()
        return Response({"Car updated": car})

class CarAddAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(request_body=CarSerializer)
    def post(self, request):
        serializer = CarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_406_NOT_ACCEPTABLE)

class ChangePasswordAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    def put(self, request):
        serializer = ChangePasswordSerializer(instance=self.request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


SERVICE_ACCOUNT_FILE = settings.BASE_DIR/'users'/'distrox-af8e1-c4bfd80e73be.json'
PROJECT_ID = 'distrox-af8e1'
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/firebase.messaging"]
)

def get_access_token():
    auth_req = Request()
    credentials.refresh(auth_req)
    return credentials.token

class TaskCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(request_body=TaskSerializer)
    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save(task_setter = request.user)

        access_token = get_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; UTF-8',
        }
        url = f'https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send'
        task_executors = task.task_executors.filter(role='driver', driver_device_token__isnull=False)
        temp = serializer.data
        if task_executors.exists():
            temp["task_setter"] = str(task.task_setter)
            for executor in task_executors:
                temp["task_executors"] = str(executor)
                message = {
                    'message': {
                        'token': executor.driver_device_token,
                        'notification': {
                            'title': "Test",
                            'body': "Sizga task biriktirildi!",
                        },
                        'data': {
                            'task': json.dumps(temp)
                        }
                    }
                }
                requests.post(url, headers=headers, data=json.dumps(message))
                Notification.objects.create(
                    driver = executor,
                    text = task.text,
                    deadline = task.deadline
                )
        return Response(serializer.data, status.HTTP_201_CREATED)

class UserReceivedTasks(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('status', openapi.IN_QUERY, description="Search by status", type=openapi.TYPE_STRING)
    ])
    def get(self, request, pk):
        user = get_object_or_404(CustomUser.objects.all(), id=pk)
        tasks = Task.objects.filter(task_executors = user)
        task_status = request.query_params.get("status")
        if task_status:
            tasks = tasks.filter(status = task_status)
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(tasks, request)
        serializer = TaskGetSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class UserAssignedTasks(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('status', openapi.IN_QUERY, description="Search by status", type=openapi.TYPE_STRING)
    ])
    def get(self, request, pk):
        user = get_object_or_404(CustomUser.objects.all(), id=pk)
        tasks = Task.objects.filter(task_setter = user)
        task_status = request.query_params.get("status")
        if task_status:
            tasks = tasks.filter(status = task_status)
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(tasks, request)
        serializer = TaskGetSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class TasksAllAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('status', openapi.IN_QUERY, description="Search by status", type=openapi.TYPE_STRING),
        openapi.Parameter('date_from', openapi.IN_QUERY, description="Search by date_from", type=openapi.TYPE_STRING),
        openapi.Parameter('date_to', openapi.IN_QUERY, description="Search by date_to", type=openapi.TYPE_STRING),
        openapi.Parameter('single_date', openapi.IN_QUERY, description="Search by single_date", type=openapi.TYPE_STRING),
        openapi.Parameter('warehouse_id', openapi.IN_QUERY, description="Search by warehouse id", type=openapi.TYPE_STRING),
        openapi.Parameter('role', openapi.IN_QUERY, description="Search by role", type=openapi.TYPE_STRING),
    ])
    def get(self, request):
        task_status = request.query_params.get("status")
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")
        single_date = request.query_params.get("single_date")
        warehouse_id = request.query_params.get("warehouse_id")
        role = request.query_params.get("role")
        tasks = Task.objects.all()
        if task_status:
            tasks = tasks.filter(status = task_status)
        if single_date:
            tasks = tasks.filter(created_at = single_date)
        if date_to and date_from:
            date_from = datetime.strptime(date_from, "%Y-%m-%d")
            date_to = datetime.strptime(date_to, "%Y-%m-%d")
            tasks = tasks.filter(created_at__range=[date_from, date_to])
        if role:
            tasks = tasks.filter(task_executors__role = role)
        if warehouse_id:
            tasks = tasks.filter(task_executors__warehouse__id = warehouse_id)
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(tasks, request)
        serializer = TaskGetSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class TaskDeleteAPIView(APIView):
    def delete(self, request, pk):
        task = get_object_or_404(Task.objects.all(), id=pk)
        task.delete()
        return Response({"message": "deleted", "message": "Task deleted"})

    @swagger_auto_schema(request_body=TaskSerializer)
    def put(self, request, pk):
        task = get_object_or_404(Task.objects.all(), id=pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class UserSalaryParamsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        user = get_object_or_404(CustomUser.objects.all(), id=pk)
        salary_params = get_object_or_404(SalaryParams.objects.all(), user=user)
        serializer = SalaryParamsSerializer(salary_params)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=SalaryParamsSerializer)
    def post(self, request, pk):
        user = get_object_or_404(CustomUser.objects.all(), id=pk)
        salary_params_data = request.data
        existing_salary_params = SalaryParams.objects.filter(user=user).first()
        if existing_salary_params:
            serializer = SalaryParamsSerializer(instance=existing_salary_params, data=salary_params_data)
        else:
            serializer = SalaryParamsSerializer(data=salary_params_data)

        serializer.is_valid(raise_exception=True)
        salary_params = serializer.save(user=user)
        serializer = SalaryParamsSerializer(salary_params)
        return Response(serializer.data)


class CalculateUserSalary(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, pk, year, month):
        user = get_object_or_404(CustomUser.objects.all(), id=pk)
        the_date = self.get_the_month(month, year)
        if not the_date:
            return Response({"success": "false", "message": "Month numbering is incorrect"})
        salary_params = get_object_or_404(SalaryParams.objects.all(), user=user)
        kpi_earnings = KPIEarning.objects.filter(
            user=user,
            date__startswith=the_date
        )
        kpi_earnings_sum = 0
        if kpi_earnings.exists():
            kpi_earnings_sum = kpi_earnings.aggregate(total_amount=Sum('amount')).get('total_amount', 0)
        data = {
            "user": UserSerializer(user).data,
            "kpi_amount": kpi_earnings_sum,
            "fixed_amount": salary_params.fixed,
            "total_amount": kpi_earnings_sum + salary_params.fixed
        }
        return Response(data)

    def get_the_month(self, month, year):
        months = {
            "1": "01",
            "2": "02",
            "3": "03",
            "4": "04",
            "5": "05",
            "6": "06",
            "7": "07",
            "8": "08",
            "9": "09",
            "10": "10",
            "11": "11",
            "12": "12"
        }
        month = months.get(month)
        if not month:
            return None
        return f"{year}-{month}"

class DriverLocationPostView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=DriverLocationSerializer)
    def post(self, request):
        """
        Driver location create
        """
        serializer = DriverLocationSerializer(data=request.data)
        if serializer.is_valid():
            driver = CustomUser.objects.filter(id=request.user.id).first()
            location = DriverLocation.objects.filter(driver__id=driver.id).first()
            if location:
                location.longitude = serializer.validated_data['longitude']
                location.latitude = serializer.validated_data['latitude']
                location.bearing = serializer.validated_data['bearing']
                location.date = datetime.now()

                location.save()

                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "driver_location_group",
                    {
                        "type": "add_new_driver_location",
                    },
                )

                return Response(serializer.data, status=201)
            serializer.save(driver=driver, date=datetime.now())

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "driver_location_group",
                {
                    "type": "add_new_driver_location",
                },
            )

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=401)

class ArchivedUsersView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        users = CustomUser.objects.filter(archived = True)
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(users, request)
        serializer = UserSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class UserNotificationsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        driver = request.user
        notifications = Notification.objects.filter(driver = driver)
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(notifications, request)
        serializer = NotificationSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
