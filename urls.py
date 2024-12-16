from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Django
    path("admin/", admin.site.urls),
    path("auth/", include("django.contrib.auth.urls")),
    # Capnet Apps
    path("citas/", include("citas_dinissan.urls")),
    path("tracker/", include("tracker_pro_toyota_mx.urls")),
]

admin.site.site_header = settings.AGENCIA
admin.site.site_title = settings.AGENCIA
admin.site.index_title = ""
