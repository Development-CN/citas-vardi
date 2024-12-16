from django.urls import path
from .views import *


urlpatterns = [
    path("login/", TrackerProLogin.as_view(), name="tracker_pro_login"),
    path("cliente/", TrackerProView.as_view(), name="tracker_pro"),
    path("preinventario/", PreInventarioView.as_view(), name="tracker_pro_preinventario"),
    path("prediagnostico/", PreDiagnosticoView.as_view(), name="tracker_pro_prediagnostico"),
    path("api/citas/", TrackerProAPI.as_view(), name="tracker_pro_api"),
    path("api/informacion_vin/", TrackerProEstados.as_view(), name="tracker_pro_api_estados"),
    path("logout/", TrackerProLogout.as_view(), name="tracker_pro_logout"),
]
