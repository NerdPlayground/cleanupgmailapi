from decouple import config
from drf_yasg import openapi 
from django.contrib import admin 
from django.urls import path,include
from rest_framework import permissions 
from drf_yasg.views import get_schema_view 

schema_view = get_schema_view(
    openapi.Info(
        title="Clean Up Gmail",
        default_version='v1',
        description=(
            "This API intergrates the GMail API and "+
            "sorts the emails contained in the "+
            "selected Gmail Account based on the senders."
        ),
        contact=openapi.Contact(email="georgemobisa23@outlook.com"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

admin.site.site_header="Clean Up Gmail Administration"

urlpatterns = [ 
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'), 
    path('redoc', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'), 
    path(f"{config('ADMIN_SITE_URL')}/",admin.site.urls),
    path("gmail/",include("gmail.urls")),
   #  path("/",include(".urls")),
]