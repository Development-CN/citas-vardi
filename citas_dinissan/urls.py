from django.urls import path

from .views import *

urlpatterns = [
    path("nuevacita/<str:vin>/", ClienteNuevaCita.as_view(), name="client_new"),
    path("cancelar/", ClienteCancelarCita.as_view(), name="client_delete"),
    path("reagendar/", ClienteReagendarCita.as_view(), name="client_reschedule"),
    # APIs
    path("api/dinissan", DinissanServices.as_view(), name="api_dinissan"),
    path("api/citas", CitasServices.as_view(), name="api_citas"),
    path("api/agenda", Agenda.as_view(), name="api_agenda"),
]
