from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
   openapi.Info(
      title="Distrox API",
      default_version='v1',
      description="web-API's for a distribution firm called Distrox",
      contact=openapi.Contact(email="1997abdulhamid@gmail.com"),
   ),
   public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger_docs/', schema_view.with_ui('swagger', cache_timeout=0)),

    path('users/', include('users.urls')),
    path('orders/', include('orders.urls')),
    path('customers/', include('customers.urls')),
    path('products/', include('products.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)