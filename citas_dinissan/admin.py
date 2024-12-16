from django.contrib import admin

from .models import ActividadesCitas, AgenciaTablero, FallaSintoma, MotivoIngreso, MotivoIngresoMazda, VCitasUsuarios


@admin.register(AgenciaTablero)
class AgenciaTableroAdmin(admin.ModelAdmin):
    list_display = ("id_agencia", "nombre", "ciudad", "url_api_tablero")


@admin.register(MotivoIngreso)
class MotivoIngresoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "descripcion_motivo",
        "estado",
        "categoria_paquete",
        "nit_aseguradora",
        "adjuntos",
        "observacion",
        "tipo",
        "grupo",
        "sintoma",
    )

@admin.register(MotivoIngresoMazda)
class MotivoIngresoMazdaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "descripcion_motivo",
        "estado",
        "categoria_paquete",
        "nit_aseguradora",
        "adjuntos",
        "observacion",
        "tipo",
        "grupo",
        "sintoma",
    )

@admin.register(FallaSintoma)
class FallaSintomaAdmin(admin.ModelAdmin):
    list_display = ("id", "descripcion_motivo", "tipo", "descripcion", "descripcion_auxiliar", "estado", "modelo_tasa")


@admin.register(ActividadesCitas)
class ActividadesCitasAdmin(admin.ModelAdmin):
    list_display = ("id", "no_cita", "no_placas", "servicio", "fecha_cita", "hora_cita")

@admin.register(VCitasUsuarios)
class VCitasUsuariosAdmin(admin.ModelAdmin):
    list_display = ("cveasesor", "nombre", "id_agencia", "activo")
    list_filter = ("id_agencia", "activo")
